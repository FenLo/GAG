import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime
import sqlite3
import os
import feedparser
from bs4 import BeautifulSoup
import re

# RSS Feed kaynakları
RSS_FEEDS = [
    "https://www.sozcu.com.tr/rss/tum-haberler.xml",
    "https://www.haberturk.com/rss",
    "https://www.cnnturk.com/feed/rss/news",
    "https://www.fotomac.com.tr/rss/anasayfa.xml",
    "https://www.fotomac.com.tr/rss/galatasaray.xml",
    "https://www.transfermarkt.com.tr/rss/news"
]

# Filtreleme anahtar kelimeleri
FILTER_KEYWORDS = [
    "spor", "futbol", "galatasaray", "gs", "türkiye", "turkey", "ags", "meb", 
    "milli eğitim", "eğitim", "öğrenci", "okul", "üniversite", "sınav",
    "lig", "şampiyon", "maç", "gol", "oyuncu", "teknik direktör", "transfer"
]

DB_PATH = os.path.join("config", "database", "news_rss_channel.db")

NEWS_RSS_LOOP_STARTED = False

def set_news_rss_channel(channel_id: int):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS channel (id INTEGER PRIMARY KEY)")
    c.execute("DELETE FROM channel")
    c.execute("INSERT INTO channel (id) VALUES (?)", (channel_id,))
    conn.commit()
    conn.close()

def get_news_rss_channel():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS channel (id INTEGER PRIMARY KEY)")
    c.execute("SELECT id FROM channel LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def clean_text(text):
    """HTML etiketlerini temizler ve metni düzenler"""
    if not text:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_keywords(title, description):
    """Haberin anahtar kelimeleri içerip içermediğini kontrol eder"""
    text = f"{title} {description}".lower()
    return any(keyword.lower() in text for keyword in FILTER_KEYWORDS)

class NewsRSSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_message_ids = []
        self.sent_news_urls = set()

    @commands.Cog.listener()
    async def on_ready(self):
        global NEWS_RSS_LOOP_STARTED
        if not NEWS_RSS_LOOP_STARTED:
            self.news_rss_loop.start()
            NEWS_RSS_LOOP_STARTED = True

    @tasks.loop(minutes=3)  # Test için 1 dakikada bir kontrol
    async def news_rss_loop(self):
        await self.send_news_rss_update()

    async def send_news_rss_update(self):
        channel_id = get_news_rss_channel()
        if channel_id is None:
            return
        
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return

        # Eski mesajları sil (son 10 mesaj)
        if len(self.last_message_ids) > 10:
            old_ids = self.last_message_ids[:-10]
            self.last_message_ids = self.last_message_ids[-10:]
            for msg_id in old_ids:
                try:
                    msg = await channel.fetch_message(msg_id)
                    await msg.delete()
                except Exception:
                    pass

        all_articles = []

        # RSS feed'lerden haberleri çek
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                feed_title = getattr(feed.feed, 'title', 'Bilinmeyen')
                
                for entry in feed.entries[:5]:  # Her feed'den en fazla 5 haber
                    if entry.link in self.sent_news_urls:
                        continue
                    
                    # Tarih bilgisini al
                    pub_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            parsed = entry.published_parsed
                            if len(parsed) >= 6:
                                pub_date = datetime(parsed[0], parsed[1], parsed[2], parsed[3], parsed[4], parsed[5])  # type: ignore
                        except (TypeError, ValueError, IndexError):
                            pass
                    
                    title = clean_text(entry.title)
                    description = clean_text(getattr(entry, 'summary', ''))
                    
                    # Anahtar kelime kontrolü
                    if not check_keywords(title, description):
                        continue
                    
                    article = {
                        'title': title,
                        'description': description,
                        'url': entry.link,
                        'source': feed_title,
                        'published': pub_date
                    }
                    
                    all_articles.append(article)
                    
            except Exception as e:
                # You might want to log this to a file in the future
                continue

        # Haberleri tarihe göre sırala (en yeni önce)
        all_articles.sort(key=lambda x: x['published'], reverse=True)

        # Yeni haberleri gönder (en fazla 5 tane)
        sent_count = 0
        for article in all_articles[:5]:
            # Açıklamayı kısalt
            desc = article['description'][:300] + ("... [devamı için tıkla]" if len(article['description']) > 300 else "")
            # Görsel bulmaya çalış
            image_url = None
            img_match = re.search(r'(https?://\S+\.(jpg|jpeg|png|gif))', article['description'])
            if img_match:
                image_url = img_match.group(1)

            embed = discord.Embed(
                title=f"📰 {article['title'][:240]}",
                description=f"{desc}",
                url=article['url'],
                color=discord.Color.gold(),
                timestamp=article['published']
            )

            embed.add_field(
                name="📡 Kaynak",
                value=f"{article['source']}",
                inline=True
            )

            embed.add_field(
                name="🗓️ Tarih",
                value=article['published'].strftime("%d.%m.%Y %H:%M"),
                inline=True
            )

            if image_url:
                embed.set_thumbnail(url=image_url)
            else:
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/21/21601.png")

            embed.set_footer(text="GAG RSS Haber | Filtreli Son Dakika", icon_url="https://cdn-icons-png.flaticon.com/512/21/21601.png")

            try:
                msg = await channel.send(embed=embed)
                self.last_message_ids.append(msg.id)
                self.sent_news_urls.add(article['url'])
                sent_count += 1
                await asyncio.sleep(3)  # Rate limit için bekle
            except Exception as e:
                # You might want to log this to a file in the future
                pass

        # Sent URLs listesini temizle
        if len(self.sent_news_urls) > 1000:
            self.sent_news_urls.clear()

async def setup(bot):
    await bot.add_cog(NewsRSSCog(bot)) 
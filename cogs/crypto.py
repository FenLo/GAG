import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
import asyncio
from datetime import datetime
import sqlite3
import os

# Popüler 12 kripto para (CoinGecko id'leri)
CRYPTO_IDS = [
    'bitcoin', 'ethereum',  'ripple',
    'avalanche-2', 'pancakeswap-token'
]

DB_PATH = os.path.join("config", "database", "crypto_channel.db")

CRYPTO_LOOP_STARTED = False

def set_crypto_channel(channel_id: int):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS channel (id INTEGER PRIMARY KEY)")
    c.execute("DELETE FROM channel")
    c.execute("INSERT INTO channel (id) VALUES (?)", (channel_id,))
    conn.commit()
    conn.close()

def get_crypto_channel():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS channel (id INTEGER PRIMARY KEY)")
    c.execute("SELECT id FROM channel LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

class CryptoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_message_ids = []

    @commands.Cog.listener()
    async def on_ready(self):
        global CRYPTO_LOOP_STARTED
        if not CRYPTO_LOOP_STARTED:
            self.crypto_loop.start()
            CRYPTO_LOOP_STARTED = True

    @tasks.loop(minutes=15)
    async def crypto_loop(self):
        await self.send_crypto_update(update_ids=True)

    async def send_crypto_update(self, update_ids=True):
        channel_id = get_crypto_channel()
        if channel_id is None:
            return
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return
        # Eski mesajları sil
        if update_ids:
            for msg_id in self.last_message_ids:
                try:
                    msg = await channel.fetch_message(msg_id)
                    await msg.delete()
                except Exception:
                    pass
            self.last_message_ids = []
        # Veri çek
        url = (
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
            f"&ids={','.join(CRYPTO_IDS)}&order=market_cap_desc&per_page=12&page=1&sparkline=false"
        )
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
        except Exception as e:
            print(f"CoinGecko API hatası: {e}")
            return
        coin_infos = []
        for coin in data:
            try:
                name = coin['name']
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                high = coin['high_24h']
                low = coin['low_24h']
                change = coin['price_change_24h']
                change_pct = coin['price_change_percentage_24h']
                volume = coin['total_volume']
                image = coin['image']
                last_updated = coin['last_updated']
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                coin_infos.append({
                    'name': name,
                    'symbol': symbol,
                    'price': price,
                    'high': high,
                    'low': low,
                    'change': change,
                    'change_pct': change_pct,
                    'volume': volume,
                    'image': image,
                    'dt': dt
                })
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"{coin.get('id', 'bilinmeyen')} için veri hatası: {e}")
        for coin in coin_infos:
            embed = discord.Embed(
                title=f"{coin['name']} ({coin['symbol']}) - 24 Saatlik Kripto Verisi",
                color=discord.Color.blue(),
                timestamp=coin['dt']
            )
            desc = (
                f"Fiyat: **${coin['price']:,.2f}**\n"
                f"Değişim: {coin['change']:+.2f} USD ({coin['change_pct']:+.2f}%)\n"
                f"En Yüksek: ${coin['high']:,.2f} | En Düşük: ${coin['low']:,.2f}\n"
                f"Hacim: ${coin['volume']:,.0f}"
            )
            embed.description = desc
            embed.set_thumbnail(url=coin['image'])
            embed.set_footer(text="Veriler CoinGecko üzerinden alınmıştır.")
            msg = await channel.send(embed=embed)
            if update_ids:
                self.last_message_ids.append(msg.id)
            await asyncio.sleep(1)

async def setup(bot):
    await bot.add_cog(CryptoCog(bot))
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import asyncio
import logging
import threading
import time
import sys
from dotenv import load_dotenv  
from cogs.database import init_db, init_moderation_db, init_otorol_db, init_birthdays_db, set_autorole, get_autorole
from cogs.pubg import start_pubg_tracking, stop_pubg_tracking
from cogs.fun import gayrate, coinflip, catfact, meme
from cogs.utility import weather, oyunlar, help_command
from cogs.images import alıntıolustur
from cogs.moderation import setup_moderation_events, timeout_member, unmute_member, ban_member, kick_member, unban_member, clear_messages, server_info, user_info, softban, slowmode, lock, unlock, purge, nick
from cogs.drawgame import drawgame, guess
from cogs.crypto import CryptoCog

load_dotenv("config/.env")

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# Animasyon kontrolü
running = True

def loading_animation():
    anim = ["   ", ".  ", ".. ", "..."]
    i = 0
    while running:
        sys.stdout.write("\rBot başlatılıyor" + anim[i % len(anim)])
        sys.stdout.flush()
        time.sleep(0.5)
        i += 1
    
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

# Komutlar
@tree.command(name="weather", description="Belirtilen şehir için hava durumu tahminini gösterir.")
async def weather_command(interaction: discord.Interaction, city: str, days: int):
    await weather(interaction, city, days)

@tree.command(name="timeout", description="Bir kullanıcıyı belirli dakika kadar susturur.")
@app_commands.checks.has_permissions(administrator=True)
async def timeout_command(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Sebep belirtilmedi"):
    await timeout_member(interaction, member, minutes, reason)

@tree.command(name="unmute", description="Bir kullanıcının susturmasını kaldırır.")
@app_commands.checks.has_permissions(administrator=True)
async def unmute_command(interaction: discord.Interaction, member: discord.Member):
    await unmute_member(interaction, member)

@tree.command(name="ban", description="Bir kullanıcıyı sunucudan yasaklar.")
@app_commands.checks.has_permissions(administrator=True)
async def ban_command(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await ban_member(interaction, member, reason)

@tree.command(name="kick", description="Bir kullanıcıyı sunucudan atar.")
@app_commands.checks.has_permissions(administrator=True)
async def kick_command(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await kick_member(interaction, member, reason)

@tree.command(name="unban", description="Banlanan bir kullanıcının yasağını kaldırır.")
@app_commands.checks.has_permissions(administrator=True)
async def unban_command(interaction: discord.Interaction, user: discord.User, reason: str = "Sebep belirtilmedi"):
    await unban_member(interaction, user, reason)

@tree.command(name="alıntıolustur", description="Seçilen kişi ve mesaj ile alıntı oluşturur")
async def alıntı_command(interaction: discord.Interaction, member: discord.Member, mesaj: str):
    await alıntıolustur(interaction, member, mesaj)

@tree.command(name="oyunlar", description="Sunucudaki kullanıcıların oynadığı oyunları gösterir.")
async def oyunlar_command(interaction: discord.Interaction):
    await oyunlar(interaction)

@tree.command(name="gayrate", description="Belirtilen kişinin gay oranını ölçer.")
async def gayrate_command(interaction: discord.Interaction, name: discord.Member):
    await gayrate(interaction, name)

@tree.command(name="clear", description="Sohbeti silmenize yarar.")
@app_commands.checks.has_permissions(administrator=True)
async def clear_command(interaction: discord.Interaction, amount: int):
    await clear_messages(interaction, amount)

@tree.command(name="yazıtura", description="Yazı-Tura atma simülasyonu.")
async def yazıtura_command(interaction: discord.Interaction):
    await coinflip(interaction)

# Sunucu bilgilerini görüntüleme komutu
@tree.command(name="serverinfo", description="Sunucu hakkında genel bilgileri gösterir.")
async def server_info_command(interaction: discord.Interaction):
    await server_info(interaction)

@tree.command(name="userinfo", description="Bir kullanıcının bilgilerini görüntüler.")
async def user_info_command(interaction: discord.Interaction, member: discord.Member):
    if member is None:
        await interaction.response.send_message("❌ Kullanıcı bulunamadı.", ephemeral=True)
        return
    await user_info(interaction, member)

@tree.command(name="pubgkanal", description="PUBG istatistiklerinin gönderileceği kanalı ayarlar.")
@app_commands.checks.has_permissions(administrator=True)
async def set_pubg_channel_command(interaction: discord.Interaction, kanal: discord.TextChannel):
    if interaction.guild is None:
        await interaction.response.send_message("❌ Bu komut sadece sunucularda kullanılabilir.", ephemeral=True)
        return
    from cogs.database import set_pubg_channel_db
    set_pubg_channel_db(interaction.guild.id, kanal.id)
    await interaction.response.send_message(
        f"✅ PUBG istatistikleri artık **{kanal.mention}** kanalına gönderilecek!",
        ephemeral=True)

@tree.command(name="pubg", description="PUBG istatistik takibini başlatır/durdurur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(action="başlatmak için 'start' durdurmak için 'stop' yazınız.")
async def pubg_command(
    interaction: discord.Interaction,
    action: str = "start"  # Varsayılan olarak başlat
):
    if action.lower() == "start":
        await start_pubg_tracking(bot, interaction)
    elif action.lower() == "stop":
        await stop_pubg_tracking(interaction)
    else:
        await interaction.response.send_message("❌ Geçersiz işlem. 'start' veya 'stop' kullanın.", ephemeral=True)

@tree.command(name="otorol", description="Sunucuya yeni katılanlar için otomatik rol ayarlar.")
@app_commands.checks.has_permissions(administrator=True)
async def autorole_command(interaction: discord.Interaction, user_role: discord.Role, bot_role: discord.Role):
    if user_role is None or bot_role is None:
        await interaction.response.send_message("❌ Roller bulunamadı.", ephemeral=True)
        return
    if interaction.guild is None:
        await interaction.response.send_message("❌ Bu komut sadece sunucularda kullanılabilir.", ephemeral=True)
        return
    set_autorole(interaction.guild.id, interaction.guild.name, user_role.id, bot_role.id)
    await interaction.response.send_message(
        f"✅ Otomatik roller güncellendi! Kullanıcılar için {user_role.mention}, botlar için {bot_role.mention} atanacak.",
        ephemeral=True
    )

@tree.command(name="help", description="Botun tüm komutlarını ve açıklamalarını listeler.")
async def help_command_wrapper(interaction: discord.Interaction):
    await help_command(interaction)

@tree.command(name="catfact", description="Rastgele bir kedi gerçeği gönderir.")
async def catfact_command(interaction: discord.Interaction):
    await catfact(interaction)

@tree.command(name="meme", description="Rastgele bir meme gönderir.")
async def meme_command(interaction: discord.Interaction):
    await meme(interaction)

@tree.command(name="softban", description="Kullanıcıyı softbanlar (banlayıp hemen unbanlar, mesajlarını siler).")
@app_commands.checks.has_permissions(ban_members=True)
async def softban_command(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await softban(interaction, member, reason)

@tree.command(name="slowmode", description="Kanalda yavaş mod süresi ayarlar (saniye cinsinden).")
@app_commands.describe(seconds="Yavaş mod süresi (saniye cinsinden)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode_command(interaction: discord.Interaction, seconds: int):
    await slowmode(interaction, seconds)

@tree.command(name="lock", description="Kanalı kilitler (mesaj gönderimini kapatır).")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock_command(interaction: discord.Interaction):
    await lock(interaction)

@tree.command(name="unlock", description="Kanalı açar (mesaj gönderimini tekrar açar).")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock_command(interaction: discord.Interaction):
    await unlock(interaction)

@tree.command(name="purge", description="Belirli sayıda mesajı topluca siler.")
@app_commands.describe(amount="Silinecek mesaj sayısı (1-100 arası)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge_command(interaction: discord.Interaction, amount: int):
    await purge(interaction, amount)

@tree.command(name="nick", description="Bir kullanıcının takma adını değiştirir.")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nick_command(interaction: discord.Interaction, member: discord.Member, new_nick: str):
    await nick(interaction, member, new_nick)

@tree.command(name="drawgame", description="Bir çizim oyunu başlatır. (Kelime DM ile gönderilir)")
async def drawgame_command(interaction: discord.Interaction):
    await drawgame(interaction)

@tree.command(name="guess", description="Çizim oyununda kelime tahmini yapar.")
async def guess_command(interaction: discord.Interaction, tahmin: str):
    await guess(interaction, tahmin)

@tree.command(name="crypto", description="Kripto embedlerinin gönderileceği kanalı seçer ve kaydeder.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(kanal="Embed mesajların gönderileceği kanal")
async def crypto_command(interaction: discord.Interaction, kanal: discord.TextChannel):
    from cogs.crypto import set_crypto_channel
    set_crypto_channel(kanal.id)
    await interaction.response.send_message(f"Kripto verileri artık otomatik olarak {kanal.mention} kanalına 10 dakikada bir gönderilecek.", ephemeral=True)

@tree.command(name="habertest", description="Haber sistemini manuel olarak test eder.")
@app_commands.checks.has_permissions(administrator=True)
async def news_test_command(interaction: discord.Interaction):
    await interaction.response.send_message("📰 Haber testi başlatılıyor...", ephemeral=True)
    await interaction.followup.send("🔧 Test komutu hazır. Bot yeniden başlatıldıktan sonra çalışacak.", ephemeral=True)

@tree.command(name="haberrss", description="RSS feed'lerden güncel haberlerin gönderileceği kanalı ayarlar.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(kanal="Haberlerin gönderileceği kanal")
async def news_rss_channel_command(interaction: discord.Interaction, kanal: discord.TextChannel):
    from cogs.news_rss import set_news_rss_channel
    set_news_rss_channel(kanal.id)
    await interaction.response.send_message(f"📰 RSS haberleri artık otomatik olarak {kanal.mention} kanalına 45 dakikada bir gönderilecek.", ephemeral=True)

# Bot olayları
@bot.event
async def on_ready():
    await tree.sync()
    init_db()
    init_moderation_db()
    init_otorol_db()
    init_birthdays_db()
    await bot.change_presence(activity=discord.Game(name="GAG | /help"))	
    global running
    running = False
    thread.join()
    setup_moderation_events(bot)
    print("\033[96mGAG BOT hazır ve komutlar senkronize edildi.\033[96m\n")

            
# Animasyon thread'i başlat
thread = threading.Thread(target=loading_animation)
thread.start()

logging.getLogger("discord.client").setLevel(logging.WARNING)  
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
token = os.getenv("DISCORD_TOKEN")
if not token:
    print("❌ Discord token bulunamadı. Lütfen config/.env dosyasını kontrol edin.")
    exit(1)

async def load_cogs():
    await bot.load_extension("cogs.crypto")
    await bot.load_extension("cogs.news_rss")
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.birthday")
    # Diğer cogs'lar burada yüklenebilir

if __name__ == "__main__":
    asyncio.run(load_cogs())
    bot.run(token)
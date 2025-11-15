import os
import requests
from datetime import datetime, timezone, timedelta
import openpyxl
from openpyxl import Workbook
import discord
import asyncio
from dotenv import load_dotenv 
from cogs.database import save_last_match_id, load_last_match_id, get_pubg_channels

load_dotenv("config/.env")

API_KEY = os.getenv("PUBG_API_KEY")
PLAYER_NAME = os.getenv("PUBG_PLAYER_NAME")
PLATFORM = os.getenv("PUBG_PLATFORM")

# Kontrol durumu için global değişken
is_checking = False

async def check_and_post_match(bot):
    global is_checking
    if not is_checking:
        return

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/vnd.api+json"
    }

    url = f"https://api.pubg.com/shards/{PLATFORM}/players?filter[playerNames]={PLAYER_NAME}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("❌ API hatası veya oyuncu bulunamadı.")
        return

    data = response.json()
    if not data["data"]:
        print("❌ Oyuncu verisi bulunamadı.")
        return

    player_id = data["data"][0]["id"]
    matches = data["data"][0]["relationships"]["matches"]["data"]

    if not matches:
        print("❌ Maç verisi bulunamadı.")
        return

    match_id = None
    for match in matches:
        match_url = f"https://api.pubg.com/shards/{PLATFORM}/matches/{match['id']}"
        match_response = requests.get(match_url, headers=headers)

        if match_response.status_code != 200:
            print(f"❌ Maç {match['id']} verisi alınamadı.")
            continue

        match_data = match_response.json()

        if match_data["data"]["attributes"]["gameMode"] == "squad-fpp":
            match_id = match["id"]
            break

    if match_id is None:
        print("❌ FPP Squad maçı bulunamadı.")
        return

    last_match_id = load_last_match_id()
    if match_id == last_match_id:
        print("\033[95m✅ Bu maç zaten paylaşıldı, tekrar gönderilmeyecek.\033[95m")
        return

    print(f"\033[91mYeni maç Bulundu!\033[91m")

    match_url = f"https://api.pubg.com/shards/{PLATFORM}/matches/{match_id}"
    match_response = requests.get(match_url, headers=headers)

    if match_response.status_code != 200:
        print("❌ Maç bilgileri alınamadı.")
        return

    match_data = match_response.json()
    participants = [p for p in match_data["included"] if p["type"] == "participant"]
    teams = [t for t in match_data["included"] if t["type"] == "roster"]

    player_stats = next((p for p in participants if p["attributes"]["stats"]["name"] == PLAYER_NAME), None)

    if not player_stats:
        print("❌ Oyuncu verisi bulunamadı.")
        return

    match_time_utc = datetime.fromisoformat(match_data["data"]["attributes"]["createdAt"].replace("Z", "+00:00"))
    match_time_tr = match_time_utc.astimezone(timezone(timedelta(hours=3)))

    team_id = player_stats["attributes"]["stats"].get("teamId", None)
    embed = discord.Embed(title="🎮Ekibin Son Maç performansı.", color=discord.Color.purple())
    embed.add_field(name="📅 Tarih", value=match_time_tr.strftime("%d %B %Y"), inline=True)
    embed.add_field(name="🕒 Saat", value=match_time_tr.strftime("%H:%M"), inline=True)
    embed.add_field(name="🗺️ Harita", value=match_data['data']['attributes']['mapName'], inline=True)

    teammates = []
    if team_id is not None:
        teammates = [p for p in participants if p["attributes"]["stats"].get("teamId") == team_id]
    else:
        for team in teams:
            team_members = team["relationships"]["participants"]["data"]
            if any(p["id"] == player_stats["id"] for p in team_members):
                teammates = [p for p in participants if p["id"] in [tm["id"] for tm in team_members]]
                break

    if teammates:
        placement = teammates[0]["attributes"]["stats"]["winPlace"]
        embed.add_field(name=f"Maç Sonuçlandı! Takım 🏆 {placement}. Oldu!", value="", inline=False)

        for teammate in teammates:
            mention_map = {
                "NoMercyGO": "<@383883923392036876>",
                "NobleKG": "<@230823820334727170>",
                "Michalengelo": "<@370222712414666772>",
                "Nrttbe": "<@681193775216984086>",
                "cathedrall": "<@385102807952392212>",
                "Erden7": "<@627909060791894017>",
                "Anhubat": "<@712314243424452619>"
            }
            name = teammate["attributes"]["stats"]["name"]
            kills = teammate["attributes"]["stats"]["kills"]
            damage = teammate["attributes"]["stats"]["damageDealt"]
            revives = teammate["attributes"]["stats"].get("revives", 0)
            dBNOs = teammate["attributes"]["stats"].get("DBNOs", 0)
            mention = mention_map.get(name, name)
            if mention in mention_map.values():
                mention = f"{mention}"
            embed.add_field(
                name="",
                value=f"🎯 {mention}\n🔫 {kills} Kill | 💪 {int(dBNOs)} Adam Devirdi | 💥 {int(damage)} Hasar | 🆙 {revives} Kaldırma",
                inline=False
            )

    channels = get_pubg_channels()
    for guild_id, channel_id in channels:
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
        except Exception as e:
            print(f"❌ {guild_id} sunucusunda kanal bulunamadı: {e}")

    save_last_match_id(match_id)

async def start_pubg_tracking(bot, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    global is_checking
    is_checking = True
    await interaction.followup.send("✅ PUBG istatistik takibi başlatıldı! 10 dakikada bir kontrol edilecek.", ephemeral=True)
    print("\033[93mPUBG istatistik takibi başlatıldı\033[93m")
    while is_checking:
        await check_and_post_match(bot)
        await asyncio.sleep(600)  # 10 dakika

async def stop_pubg_tracking(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    global is_checking
    is_checking = False
    await interaction.followup.send("⏹️ PUBG istatistik takibi durduruldu.", ephemeral=True)
    print("\033[93mPUBG istatistik takibi durduruldu\033[93m")
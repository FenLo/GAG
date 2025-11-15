import discord
import os
import requests

async def weather(interaction: discord.Interaction, city: str, days: int):
    await interaction.response.defer()
    if days < 1 or days > 5:
        await interaction.followup.send("❌ Gün sayısı 1 ile 5 arasında olmalıdır.", ephemeral=True)
        return

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    BASE_URL = "https://api.tomorrow.io/v4/weather/forecast"
    
    params = {
        "location": city,
        "apikey": WEATHER_API_KEY,
        "timesteps": "1d",
        "units": "metric"
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        await interaction.followup.send("❌ Hava durumu bilgisi alınamadı, lütfen şehri kontrol edin.", ephemeral=True)
        return

    data = response.json()
    forecasts = data.get("timelines", {}).get("daily", [])

    if not forecasts:
        await interaction.followup.send("❌ Geçerli bir hava durumu verisi bulunamadı.", ephemeral=True)
        return

    embed = discord.Embed(title=f"🌤️ {city} için {days} günlük hava tahmini", color=discord.Color.blue())

    for i in range(min(days, len(forecasts))):
        forecast = forecasts[i]["values"]
        date = forecasts[i]["time"].split("T")[0]
        temp = forecast["temperatureAvg"]
        humidity = forecast["humidityAvg"]
        wind_speed = forecast["windSpeedAvg"]
        precipitation = forecast["precipitationProbabilityAvg"]
        condition = forecast.get("weatherCodeMax", "Bilinmiyor")

        embed.add_field(
            name=f"📅 {date}",
            value=f"🌡️ **Sıcaklık:** {temp}°C\n💧 **Nem:** {humidity}%\n💨 **Rüzgar:** {wind_speed} km/h\n☔ **Yağış İhtimali:** {precipitation}%",
            inline=False
        )

    await interaction.followup.send(embed=embed)

async def oyunlar(interaction: discord.Interaction):
    await interaction.response.defer()
    oyun_sayaci = {}
    guild = interaction.guild
    if guild is None:
        await interaction.followup.send("❌ Sunucu bilgisi alınamadı.", ephemeral=True)
        return
    for member in guild.members:
        if member.bot:
            continue
        
        if member.activity:
            oyun_adi = None
            
            # Oyunlar (Discord Game)
            if isinstance(member.activity, discord.Game):
                oyun_adi = f"🎮 {member.activity.name}"
            
            # Yayınlar (Twitch, YouTube, vb.)
            elif isinstance(member.activity, discord.Streaming):
                oyun_adi = f"📺 {member.activity.game}" if member.activity.game else "🔴 Canlı Yayın"
            
            # Spotify
            elif isinstance(member.activity, discord.Spotify):
                oyun_adi = f"🎵 {member.activity.title}"
            
            # Diğer aktiviteler (Custom Status, Rich Presence)
            elif hasattr(member.activity, "name"):
                oyun_adi = f"🛠️ {member.activity.name}"
            
            if oyun_adi:
                oyun_sayaci[oyun_adi] = oyun_sayaci.get(oyun_adi, 0) + 1

    if not oyun_sayaci:
        await interaction.followup.send("🎮 Şu an sunucuda kimse bir etkinlikte değil.")
    else:
        embed = discord.Embed(
            title="🎮 Sunucudaki Aktif Etkinlikler",
            description="Şu anda oyun oynayan, yayın yapan veya müzik dinleyen kullanıcılar:",
            color=discord.Color.purple()
        )
        
        # En çok oynananları üste yerleştir
        for oyun, sayi in sorted(oyun_sayaci.items(), key=lambda x: x[1], reverse=True):
            embed.add_field(name=oyun, value=f"**{sayi}** kişi", inline=True)
        
        embed.set_footer(text=f"Toplam {len(oyun_sayaci)} farklı etkinlik")
        await interaction.followup.send(embed=embed)

async def help_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="✨ Yardım Menüsü | GAG Bot Komutları",
        description="Aşağıda botun tüm komutlarını kategorilere ayrılmış şekilde bulabilirsin.",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=interaction.client.user.display_avatar.url if interaction.client.user else None)
    embed.set_footer(text="GAG Discord Botu | /help ile bu menüyü tekrar görebilirsin.")

    # Eğlence & Oyunlar
    embed.add_field(
        name="🎲 Eğlence & Oyunlar",
        value="""
/gayrate <üye> — Rastgele gay oranı ölçer
/yazıtura — Yazı-tura simülasyonu
/oyunlar — Aktif oyunları listeler
/alıntıolustur <üye> <mesaj> — Alıntı oluşturur
/catfact — Rastgele kedi gerçeği
/drawgame — Çizim oyunu başlatır
/guess <kelime> — Çizim oyununda kelime tahmini
        """,
        inline=False
    )

    # Moderasyon
    embed.add_field(
        name="🛡️ Moderasyon",
        value="""
/ban <üye> [sebep] — Kullanıcıyı banlar
/kick <üye> [sebep] — Kullanıcıyı atar
/timeout <üye> <dakika> [sebep] — Kullanıcıyı süreli susturur
/unmute <üye> — Susturmayı kaldırır
/unban <kullanıcı> [sebep] — Banı kaldırır
/softban <üye> [sebep] — Softban (ban+unban)
/slowmode <saniye> — Yavaş mod ayarla
/lock — Kanalı kilitle
/unlock — Kanalı aç
/purge <adet> — Toplu mesaj sil
/nick <üye> <yeni ad> — Takma ad değiştir
/clear <adet> — Mesaj siler
        """,
        inline=False
    )

    # Bilgi & Yardımcı
    embed.add_field(
        name="ℹ️ Bilgi & Yardımcı",
        value="""
/weather <şehir> <gün> — Hava durumu
/serverinfo — Sunucu bilgisi
/userinfo <üye> — Kullanıcı bilgisi
/help — Yardım menüsü
        """,
        inline=False
    )

    # PUBG & Otomasyon
    embed.add_field(
        name="🎮 PUBG & Otomasyon",
        value="""
/pubgkanal <kanal> — PUBG kanal ayarla
/pubg <start|stop> — PUBG takibini başlat/durdur
/otorol <kullanıcı rolü> <bot rolü> — Otorol ayarla
        """,
        inline=False
    )

    # Kripto & Haber
    embed.add_field(
        name="💸 Kripto & Haber",
        value="""
/crypto <kanal> — Kripto kanalını ayarla
/haberrss <kanal> — RSS haber kanalını ayarla
/habertest — Haber sistemini test et
        """,
        inline=False
    )

    await interaction.followup.send(embed=embed, ephemeral=True)
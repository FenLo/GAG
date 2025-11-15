import discord
import random
from discord import app_commands

# Basit kelime listesi
WORDS = [
    "elma", "araba", "ev", "bilgisayar", "kedi", "köpek", "uçak", "masa", "telefon", "kitap",
    "sandalye", "çanta", "kalem", "defter", "buzdolabı", "televizyon", "ayna", "lamba", "çorap", "ayakkabı",
    "tabak", "kaşık", "çatal", "bardak", "yastık", "battaniye", "halı", "perde", "saat", "anahtar", "cüzdan",
    "bisiklet", "top", "futbol", "gözlük", "şemsiye", "mouse", "klavye", "monitör", "priz", "ampul",
    "makas", "tencere", "fırın", "mikrodalga", "çamaşır makinesi", "bulaşık makinesi", "dondurma", "pizza", "hamburger", "patates",
    "salata", "yumurta", "peynir", "süt", "yoğurt", "balık", "tavuk", "et", "ekmek", "zeytin",
    "domates", "salatalık", "biber", "soğan", "sarımsak", "havuç", "patlıcan", "kabak", "muz", "portakal",
    "çilek", "kiraz", "karpuz", "üzüm", "armut", "şeftali", "kayısı", "ananas", "limon", "mandalina",
    "uçurtma", "balon", "tren", "otobüs", "kamyon", "gemi", "helikopter", "roket", "kaykay", "paten",
    "çizme", "mont", "atkı", "bere", "eldiven", "pantolon", "etek", "gömlek", "ceket", "tişört",
    "düğme", "fermuar", "kemer", "kravat", "yüzük", "kolye", "bilezik", "küpe", "şapka", "güneş kremi",
    "diş fırçası", "diş macunu", "sabun", "şampuan", "havlu", "tarak", "ayna", "makyaj", "parfüm", "deodorant",
    "çöp kutusu", "fırça", "süpürge", "kovası", "temizlik bezi", "deterjan", "ütü", "ütü masası", "askı", "sepet",
    "oyuncak", "lego", "bebek", "araba oyuncağı", "topaç", "peluş", "bulmaca", "satranç", "dama", "iskambil",
    "bilgisayar faresi", "hoparlör", "kulaklık", "mikrofon", "webcam", "tablet", "yazıcı", "tarayıcı", "harddisk", "usb bellek"
]

# Oyun durumu (kanal bazlı)
drawgame_sessions = {}

async def drawgame(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.channel is None:
        await interaction.followup.send("❗ Bu komut sadece bir kanalda kullanılabilir.", ephemeral=True)
        return
    channel_id = interaction.channel.id
    if channel_id in drawgame_sessions:
        await interaction.followup.send("❗ Bu kanalda zaten bir çizim oyunu devam ediyor!", ephemeral=True)
        return
    word = random.choice(WORDS)
    drawer = interaction.user
    drawgame_sessions[channel_id] = {
        "word": word,
        "drawer": drawer.id,
        "guessed": False
    }
    try:
        await drawer.send(f"Çizeceğin kelime: **{word}**. Sunucuda kimseye söyleme!")
    except Exception:
        await interaction.followup.send("Çizim kelimesi DM ile gönderilemedi. Lütfen DM'lerini aç!", ephemeral=True)
        del drawgame_sessions[channel_id]
        return
    await interaction.followup.send(f"🎨 Bir çizim oyunu başladı! <@{drawer.id}> çiziyor. Kelimeyi tahmin edin! (Tahmin için: /guess <kelime>)", ephemeral=False)

async def guess(interaction: discord.Interaction, tahmin: str):
    await interaction.response.defer()
    if interaction.channel is None:
        await interaction.followup.send("❗ Bu komut sadece bir kanalda kullanılabilir.", ephemeral=True)
        return
    channel_id = interaction.channel.id
    session = drawgame_sessions.get(channel_id)
    if not session:
        await interaction.followup.send("❗ Bu kanalda aktif bir çizim oyunu yok!", ephemeral=True)
        return
    if session["guessed"]:
        await interaction.followup.send("✅ Kelime zaten doğru tahmin edildi!", ephemeral=True)
        return
    if interaction.user.id == session["drawer"]:
        await interaction.followup.send("❗ Kendi çizdiğin kelimeyi tahmin edemezsin!", ephemeral=True)
        return
    if tahmin.lower() == session["word"].lower():
        session["guessed"] = True
        await interaction.followup.send(f"🎉 Tebrikler! {interaction.user.mention} doğru tahmin etti: **{session['word']}**", ephemeral=False)
        del drawgame_sessions[channel_id]
    else:
        await interaction.followup.send("❌ Yanlış tahmin! Tekrar deneyin.", ephemeral=True)
import random
import discord
import requests

async def gayrate(interaction: discord.Interaction, name: discord.Member):
    await interaction.response.defer()
    rate = random.randint(0, 100)
    embed = discord.Embed(title="🏳️‍🌈 Gayrate Ölçümü", description=f"{name.display_name} % {rate} gay!", color=discord.Color.pink())
    embed.set_thumbnail(url=name.avatar.url if name.avatar else name.default_avatar.url)
    await interaction.followup.send(embed=embed)

async def coinflip(interaction: discord.Interaction):
    await interaction.response.defer()
    result = random.choice(["Yazı", "Tura"])
    heads_image = "heads.png"
    tails_image = "tails.png"
    
    if result == "Yazı":
        embed = discord.Embed(title="🪙 Yazı-Tura", description="Sonuç: **Yazı**!", color=discord.Color.green())
        image_path = f"yazıtura/{tails_image}"
        embed.set_image(url=f"attachment://{tails_image}")
    else:
        embed = discord.Embed(title="🪙 Yazı-Tura", description="Sonuç: **Tura**!", color=discord.Color.green())
        image_path = f"yazıtura/{heads_image}"
        embed.set_image(url=f"attachment://{heads_image}")        

    try:
        with open(image_path, "rb") as image_file:
            await interaction.followup.send(embed=embed, file=discord.File(image_file, filename=image_path.split("/")[-1]))
    except FileNotFoundError:
        await interaction.followup.send("❌ Görseller bulunamadı! Lütfen 'yazıtura' klasörünü kontrol edin.", ephemeral=True)

async def catfact(interaction: discord.Interaction):
    """Rastgele bir kedi bilgisi gönderir."""
    await interaction.response.defer()
    try:
        response = requests.get("https://catfact.ninja/fact", timeout=5)
        if response.status_code == 200:
            fact = response.json().get("fact", "Kedi hakkında bilgi alınamadı.")
        else:
            fact = "Kedi bilgisi alınamadı."
    except Exception:
        fact = "Kedi API'sine ulaşılamadı."
    embed = discord.Embed(title="🐱 Kedi Gerçeği!", description=fact, color=discord.Color.orange())
    await interaction.followup.send(embed=embed)

async def meme(interaction: discord.Interaction):
    """Fetches and sends a random meme."""
    await interaction.response.defer()
    try:
        response = requests.get("https://meme-api.com/gimme", timeout=5)
        if response.status_code == 200:
            data = response.json()
            meme_url = data.get("url")
            meme_title = data.get("title")
            meme_image = data.get("preview")[-1] # Get the highest resolution preview

            embed = discord.Embed(title=meme_title, url=meme_url, color=discord.Color.random())
            embed.set_image(url=meme_image)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Memeler yüklenirken bir sorun oluştu.", ephemeral=True)
    except Exception:
        await interaction.followup.send("❌ Meme API'sine ulaşılamadı.", ephemeral=True)
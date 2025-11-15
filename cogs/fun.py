import random
import discord
import aiohttp

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
        image_path = f"yazıtura/{heads_image}"
        embed.set_image(url=f"attachment://{heads_image}")
    else:
        embed = discord.Embed(title="🪙 Yazı-Tura", description="Sonuç: **Tura**!", color=discord.Color.green())
        image_path = f"yazıtura/{tails_image}"
        embed.set_image(url=f"attachment://{tails_image}")        

    try:
        with open(image_path, "rb") as image_file:
            await interaction.followup.send(embed=embed, file=discord.File(image_file, filename=image_path.split("/")[-1]))
    except FileNotFoundError:
        await interaction.followup.send("❌ Görseller bulunamadı! Lütfen 'yazıtura' klasörünü kontrol edin.", ephemeral=True)

async def catfact(interaction: discord.Interaction):
    """Rastgele bir kedi bilgisi gönderir."""
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://catfact.ninja/fact", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    fact = data.get("fact", "Kedi hakkında bilgi alınamadı.")
                else:
                    fact = "Kedi bilgisi alınamadı."
    except aiohttp.ClientError:
        fact = "Kedi API'sine ulaşılamadı."
    except Exception as e:
        fact = f"Bir hata oluştu: {str(e)}"
    embed = discord.Embed(title="🐱 Kedi Gerçeği!", description=fact, color=discord.Color.orange())
    await interaction.followup.send(embed=embed)

async def meme(interaction: discord.Interaction):
    """Fetches and sends a random meme."""
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    meme_url = data.get("url")
                    meme_title = data.get("title")
                    preview = data.get("preview", [])
                    
                    # Safely get the highest resolution preview
                    if isinstance(preview, list) and len(preview) > 0:
                        meme_image = preview[-1]
                    else:
                        meme_image = meme_url  # Fallback to main URL

                    embed = discord.Embed(title=meme_title, url=meme_url, color=discord.Color.random())
                    embed.set_image(url=meme_image)
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ Memeler yüklenirken bir sorun oluştu.", ephemeral=True)
    except aiohttp.ClientError:
        await interaction.followup.send("❌ Meme API'sine ulaşılamadı.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send("❌ Meme API'sine ulaşılamadı.", ephemeral=True)
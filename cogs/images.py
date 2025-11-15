import discord
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import io
import os

async def alıntıolustur(interaction: discord.Interaction, member: discord.Member, mesaj: str):
    await interaction.response.defer()
    
    # Font dosya yolları
    font_dir = "config/font"  # Fontların bulunduğu klasör
    times_new_roman_bold = os.path.join(font_dir, "Times New Roman Bold.ttf")  # Bold versiyonu
    times_new_roman_italic = os.path.join(font_dir, "Times New Roman Italic.ttf")  # Italic versiyonu
    times_new_roman_regular = os.path.join(font_dir, "Times New Roman.ttf")  # Regular versiyonu
    
    avatar_url = member.display_avatar.url
    
    # Download avatar with async HTTP
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    avatar_data = await response.read()
                    avatar = Image.open(io.BytesIO(avatar_data)).convert("RGB")
                else:
                    await interaction.followup.send("❌ Avatar yüklenirken bir hata oluştu.", ephemeral=True)
                    return
    except aiohttp.ClientError:
        await interaction.followup.send("❌ Avatar indirilemedi. Lütfen daha sonra tekrar deneyin.", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send("❌ Avatar işlenirken bir hata oluştu.", ephemeral=True)
        return
    
    avatar = avatar.convert("L").convert("RGB")
    
    img_width, img_height = 1200, 630
    avatar_width = int(img_width * 0.49)
    
    avatar_ratio = avatar.width / avatar.height
    avatar = avatar.resize((int(img_height * avatar_ratio), img_height))

    if avatar.width > avatar_width:
        left = (avatar.width - avatar_width) // 2
        avatar = avatar.crop((left, 0, left + avatar_width, img_height))
    
    img = Image.new('RGB', (img_width, img_height), color=(0, 0, 0))
    
    fade_width = 590
    mask = Image.new('L', (avatar_width, img_height), 255)
    
    for x in range(avatar_width):
        if x > avatar_width - fade_width:
            progress = (x - (avatar_width - fade_width)) / fade_width
            alpha = int(255 * (1 - progress**0.8))
            mask.paste(alpha, (x, 0, x+1, img_height))
    
    img.paste(avatar, (0, 0), mask)
    
    draw = ImageDraw.Draw(img)
    
    # Font yükleme (Times New Roman ile)
    try:
        # Önce Times New Roman fontlarını deneyelim
        if not os.path.exists(times_new_roman_bold):
            raise FileNotFoundError(f"Font dosyası bulunamadı: {times_new_roman_bold}")
        font_quote = ImageFont.truetype(times_new_roman_bold, 52)
        font_author = ImageFont.truetype(times_new_roman_italic, 32)
        font_custom = ImageFont.truetype(times_new_roman_regular, 27)
    except FileNotFoundError as e:
        await interaction.followup.send(f"❌ Font dosyası bulunamadı. Lütfen 'config/font' klasörünü kontrol edin.", ephemeral=True)
        return
    except Exception as e:
        print(f"Font yükleme hatası: {e}")
        try:
            # Times New Roman yoksa diğer alternatifler
            font_quote = ImageFont.truetype("arialbd.ttf", 52)
            font_author = ImageFont.truetype("ariali.ttf", 32)
            font_custom = ImageFont.truetype("arial.ttf", 27)
        except:
            try:
                # Linux alternatifleri
                font_quote = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
                font_author = ImageFont.truetype("DejaVuSans-Oblique.ttf", 32)
                font_custom = ImageFont.truetype("DejaVuSans.ttf", 27)
            except:
                # Son çare
                await interaction.followup.send("❌ Uygun font bulunamadı. Lütfen font dosyalarını kontrol edin.", ephemeral=True)
                return
    
    def draw_text_with_shadow(draw, position, text, font, text_color, shadow_color=(0,0,0), shadow_offset=(3,3)):
        x, y = position
        draw.text((x+shadow_offset[0], y+shadow_offset[1]), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=text_color)
    
    text_x = avatar_width + 30
    text_width = img_width - text_x - 30
    
    words = mesaj.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if draw.textlength(test_line, font=font_quote) <= text_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    y_position = 180
    for line in lines:
        draw_text_with_shadow(
            draw=draw,
            position=(text_x, y_position),
            text=line,
            font=font_quote,
            text_color=(255, 255, 255),
            shadow_color=(40, 40, 40)
        )
        y_position += 58
    
    draw_text_with_shadow(
        draw=draw,
        position=(text_x, y_position + 15),
        text=f'- {member.display_name}',
        font=font_author,
        text_color=(230, 230, 230),
        shadow_color=(50, 50, 50),
        shadow_offset=(2,2)
    )
    
    custom_text = "Custom Quote by GAG"
    text_length = draw.textlength(custom_text, font=font_custom)
    draw.text(
        (img_width - text_length - 25, img_height - 45),
        custom_text,
        font=font_custom,
        fill=(255, 50, 50)
    )
    
    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.followup.send(file=discord.File(fp=image_binary, filename='quote.png'))
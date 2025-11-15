import discord
from typing import Optional
from datetime import timedelta
from cogs.database import log_moderation_action, get_autorole

# Kullanıcıyı belirli bir süre susturur
async def timeout_member(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Sebep belirtilmedi"):
    await interaction.response.defer()
    if not interaction.guild or not member or not interaction.user:
        await interaction.followup.send("❌ Gerekli bilgiler alınamadı.", ephemeral=True)
        return
    try:
        await member.timeout(timedelta(minutes=minutes), reason=reason)
        await interaction.followup.send(f"🔇 {member.mention} adlı kullanıcı {minutes} dakika susturuldu. Sebep: {reason}")
        log_moderation_action(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            user_id=member.id,
            user_name=member.display_name,
            moderator_id=interaction.user.id,
            moderator_name=interaction.user.display_name,
            action="timeout",
            reason=reason
        )    
    except discord.Forbidden:
        await interaction.followup.send("❌ Bu kullanıcıyı susturmak için yetkim yok.", ephemeral=True)

# Kullanıcının suturmasını açar
async def unmute_member(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await interaction.response.defer()
    if not interaction.guild or not member or not interaction.user:
        await interaction.followup.send("❌ Gerekli bilgiler alınamadı.", ephemeral=True)
        return
    try:
        await member.edit(mute=False)
        await interaction.followup.send(f"🔊 {member.mention} adlı kullanıcının susturması kaldırıldı.")
        log_moderation_action(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            user_id=member.id,
            user_name=member.display_name,
            moderator_id=interaction.user.id,
            moderator_name=interaction.user.display_name,
            action="unmute",
            reason=reason
        )    
    except discord.Forbidden:
        await interaction.followup.send("❌ Bu kullanıcıyı susturmayı kaldırmak için yetkim yok.", ephemeral=True)

# Kullanıcıyı yasaklar
async def ban_member(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await interaction.response.defer()
    if not interaction.guild or not member or not interaction.user:
        await interaction.followup.send("❌ Gerekli bilgiler alınamadı.", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        await interaction.followup.send(f"⛔ {member.mention} adlı kullanıcı banlandı. Sebep: {reason}")
        log_moderation_action(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            user_id=member.id,
            user_name=member.display_name,
            moderator_id=interaction.user.id,
            moderator_name=interaction.user.display_name,
            action="ban",
            reason=reason
        )
    except discord.Forbidden:
        await interaction.followup.send("❌ Bu kullanıcıyı banlamak için yetkim yok.", ephemeral=True)

# Kullanıcıyı kickler
async def kick_member(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await interaction.response.defer()
    if not interaction.guild or not member or not interaction.user:
        await interaction.followup.send("❌ Gerekli bilgiler alınamadı.", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        await interaction.followup.send(f"🚪 {member.mention} adlı kullanıcı atıldı. Sebep: {reason}")
        log_moderation_action(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            user_id=member.id,
            user_name=member.display_name,
            moderator_id=interaction.user.id,
            moderator_name=interaction.user.display_name,
            action="kick",
            reason=reason
        )
    except discord.Forbidden:
        await interaction.followup.send("❌ Bu kullanıcıyı atmak için yetkim yok.", ephemeral=True)

# Kullanıcının banını kaldırır
async def unban_member(interaction: discord.Interaction, user: discord.User, reason: str = "Sebep belirtilmedi"):
    await interaction.response.defer()
    if not interaction.guild or not user or not interaction.user:
        await interaction.followup.send("❌ Gerekli bilgiler alınamadı.", ephemeral=True)
        return
    try:
        await interaction.guild.unban(user, reason=reason)
        await interaction.followup.send(f"✅ {user.mention} adlı kullanıcının banı kaldırıldı.")
        log_moderation_action(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            user_id=user.id,
            user_name=user.name,
            moderator_id=interaction.user.id,
            moderator_name=interaction.user.display_name,
            action="unban",
            reason=reason
        )    
    except discord.NotFound:
        await interaction.followup.send("❌ Bu kullanıcı banlı değil.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ Bu kullanıcının banını kaldırmak için yetkim yok.", ephemeral=True)

# Belirli sayıda mesajı siler
async def clear_messages(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    if not channel or not isinstance(channel, discord.TextChannel):
        await interaction.followup.send("❌ Bu komut sadece metin kanallarında kullanılabilir.", ephemeral=True)
        return
    try:
        deleted_messages = await channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 {len(deleted_messages)} mesaj silindi.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ Mesajları silmek için yetkim yok.", ephemeral=True)

# kullanıcının bilgilerini getirir
async def user_info(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    if not member:
        await interaction.followup.send("❌ Kullanıcı bulunamadı.", ephemeral=True)
        return
    embed = discord.Embed(title=f"{member.name} Bilgileri", color=discord.Color.blue())
    embed.add_field(name="🔹Kullanıcı Adı", value=member.name)
    embed.add_field(name="🔹Takma Ad", value=member.display_name)
    joined_at = member.joined_at.strftime("%d %b %Y, %H:%M:%S") if member.joined_at else "Bilinmiyor"
    created_at = member.created_at.strftime("%d %b %Y, %H:%M:%S") if member.created_at else "Bilinmiyor"
    embed.add_field(name="🔹Katılma Tarihi", value=joined_at)
    embed.add_field(name="🔹Sunucu Rolü", value=member.top_role.name)
    embed.add_field(name="🔹Hesap Oluşturulma Tarihi", value=created_at)
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    await interaction.followup.send(embed=embed)

# sunucunun bilgilerini getirir
async def server_info(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("❌ Sunucu bilgisi alınamadı.", ephemeral=True)
        return
    embed = discord.Embed(title=f"{guild.name} Sunucu Bilgileri", color=discord.Color.blue())
    
    # Sunucu hakkında daha detaylı bilgi ekliyoruz
    embed.add_field(name="🔹 Sunucu Adı", value=guild.name, inline=False)
    embed.add_field(name="🔹 Üye Sayısı", value=guild.member_count, inline=False)
    embed.add_field(name="🔹 Kanallar", value=f"📜 {len(guild.text_channels)} metin kanalı\n🔊 {len(guild.voice_channels)} sesli kanal", inline=False)
    embed.add_field(name="🔹 Sunucu Oluşturulma Tarihi", value=guild.created_at.strftime("%d %b %Y, %H:%M:%S"), inline=False)

    # Sunucu logosu varsa, onu da ekleyebiliriz
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    # Gönderi
    await interaction.followup.send(embed=embed)

async def softban(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild or not member:
        await interaction.followup.send("❌ Kullanıcı veya sunucu bulunamadı.", ephemeral=True)
        return
    try:
        await interaction.guild.ban(member, reason=reason, delete_message_days=7)
        await interaction.guild.unban(member, reason="Softban kaldırıldı.")
        await interaction.followup.send(f"{member.mention} kullanıcısı softbanlandı (mesajları silindi ve tekrar sunucuya katılabilir).", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Softban işlemi başarısız: {e}", ephemeral=True)

async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel):
        await interaction.followup.send("❌ Bu komut sadece metin kanallarında kullanılabilir.", ephemeral=True)
        return
    try:
        await channel.edit(slowmode_delay=seconds)
        await interaction.followup.send(f"⏳ Yavaş mod {seconds} saniye olarak ayarlandı.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Yavaş mod ayarlanamadı: {e}", ephemeral=True)

async def lock(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    guild = interaction.guild
    if not isinstance(channel, discord.TextChannel):
        await interaction.followup.send("❌ Bu komut sadece metin kanallarında kullanılabilir.", ephemeral=True)
        return
    if guild is None:
        await interaction.followup.send("❌ Sunucu bilgisi alınamadı.", ephemeral=True)
        return
    try:
        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(guild.default_role, overwrite=overwrite)
        await interaction.followup.send("🔒 Kanal kilitlendi. Artık mesaj gönderilemez.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Kanal kilitlenemedi: {e}", ephemeral=True)

async def unlock(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    guild = interaction.guild
    if not isinstance(channel, discord.TextChannel):
        await interaction.followup.send("❌ Bu komut sadece metin kanallarında kullanılabilir.", ephemeral=True)
        return
    if guild is None:
        await interaction.followup.send("❌ Sunucu bilgisi alınamadı.", ephemeral=True)
        return
    try:
        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(guild.default_role, overwrite=overwrite)
        await interaction.followup.send("🔓 Kanal açıldı. Artık mesaj gönderilebilir.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Kanal açılamadı: {e}", ephemeral=True)

async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel):
        await interaction.followup.send("❌ Bu komut sadece metin kanallarında kullanılabilir.", ephemeral=True)
        return
    try:
        deleted = await channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 {len(deleted)} mesaj silindi.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Mesajlar silinemedi: {e}", ephemeral=True)

async def nick(interaction: discord.Interaction, member: discord.Member, new_nick: str):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild or not member:
        await interaction.followup.send("❌ Kullanıcı veya sunucu bulunamadı.", ephemeral=True)
        return
    try:
        await member.edit(nick=new_nick)
        await interaction.followup.send(f"✏️ {member.mention} kullanıcısının yeni takma adı: {new_nick}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Takma ad değiştirilemedi: {e}", ephemeral=True)

def setup_moderation_events(bot):
    @bot.event
    async def on_member_join(member):
        print(f"Yeni üye katıldı: {member.name} sunucu: {member.guild.name}")
        
        roles = get_autorole(member.guild.id)
        if roles:
            user_role_id, bot_role_id = roles
            role_id = bot_role_id if member.bot else user_role_id
            role = discord.utils.get(member.guild.roles, id=role_id)
            if role:
                await member.add_roles(role)
                print(f"{member} kullanıcısına {role.name} rolü verildi.")
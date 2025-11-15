import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import calendar


class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_check_started = False
        self.last_check_date = None

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.birthday_check_started:
            self.birthday_checker.start()
            self.birthday_check_started = True
            print("🎂 Birthday checker task started")

    @tasks.loop(hours=24)
    async def birthday_checker(self):
        """Check for birthdays and send countdown messages daily at 00:00 UTC"""
        now = datetime.utcnow()
        today = now.date()
        
        # Prevent duplicate checks on the same day (in case of bot restart)
        if self.last_check_date == today:
            return
        
        self.last_check_date = today
        
        from cogs.database import get_all_birthdays, get_birthday_channel
        
        birthdays = get_all_birthdays()
        
        for guild_id, user_id, user_name, birth_month, birth_day in birthdays:
            channel_id = get_birthday_channel(guild_id)
            if not channel_id:
                continue
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            
            # Calculate days until birthday
            current_year = today.year
            try:
                birthday_this_year = datetime(current_year, birth_month, birth_day).date()
            except ValueError:
                # Handle Feb 29 on non-leap years
                if birth_month == 2 and birth_day == 29:
                    birthday_this_year = datetime(current_year, 2, 28).date()
                else:
                    continue
            
            # If birthday already passed this year, check next year
            if birthday_this_year < today:
                try:
                    birthday_this_year = datetime(current_year + 1, birth_month, birth_day).date()
                except ValueError:
                    # Handle Feb 29 on non-leap years
                    if birth_month == 2 and birth_day == 29:
                        birthday_this_year = datetime(current_year + 1, 2, 28).date()
                    else:
                        continue
            
            days_until = (birthday_this_year - today).days
            
            try:
                member = await guild.fetch_member(user_id)
                user_mention = member.mention
            except:
                user_mention = user_name
            
            # Send countdown messages
            if days_until == 3:
                embed = discord.Embed(
                    title="🎂 Doğum Günü Yaklaşıyor!",
                    description=f"3 gün sonra {user_mention}'un doğum günü!",
                    color=discord.Color.from_rgb(255, 182, 193)  # Pink
                )
                embed.set_footer(text="Kutlamaya hazır olun! 🎉")
                await channel.send(embed=embed)
            
            elif days_until == 2:
                embed = discord.Embed(
                    title="🎉 Doğum Günü Yaklaşıyor!",
                    description=f"2 gün sonra {user_mention}'un doğum günü!",
                    color=discord.Color.from_rgb(221, 160, 221)  # Plum
                )
                embed.set_footer(text="Heyecan artıyor! 🎈")
                await channel.send(embed=embed)
            
            elif days_until == 1:
                embed = discord.Embed(
                    title="🎈 Doğum Günü Yarın!",
                    description=f"Yarın {user_mention}'un doğum günü!",
                    color=discord.Color.from_rgb(186, 85, 211)  # Medium orchid
                )
                embed.set_footer(text="Hediyelerinizi hazırlayın! 🎁")
                await channel.send(embed=embed)
            
            elif days_until == 0:
                embed = discord.Embed(
                    title="🎊 DOĞUM GÜNÜ KUTLU OLSUN! 🎊",
                    description=f"Bugün {user_mention}'un doğum günü! Mutlu yıllar! 🎉",
                    color=discord.Color.from_rgb(138, 43, 226)  # Blue violet
                )
                embed.set_footer(text="🎂 Nice mutlu senelere! 🎂")
                await channel.send(embed=embed)
            
            await asyncio.sleep(0.5)  # Small delay between messages

    @birthday_checker.before_loop
    async def before_birthday_checker(self):
        """Wait until next 00:00 UTC to start the loop"""
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        # Calculate next midnight UTC
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = (next_midnight - now).total_seconds()
        print(f"⏰ Birthday checker will start in {seconds_until_midnight:.0f} seconds (at next 00:00 UTC)")
        await asyncio.sleep(seconds_until_midnight)

    @app_commands.command(name="birthday", description="Bir kullanıcının doğum gününü ayarlar.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        user="Doğum günü ayarlanacak kullanıcı",
        month="Ay (1-12 arası)",
        day="Gün (1-31 arası)"
    )
    async def birthday_command(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member, 
        month: int, 
        day: int
    ):
        """Set a user's birthday"""
        
        # Validate month
        if not 1 <= month <= 12:
            await interaction.response.send_message(
                "❌ Geçersiz ay! Lütfen 1-12 arası bir değer girin.",
                ephemeral=True
            )
            return
        
        # Validate day
        if not 1 <= day <= 31:
            await interaction.response.send_message(
                "❌ Geçersiz gün! Lütfen 1-31 arası bir değer girin.",
                ephemeral=True
            )
            return
        
        # Validate date combination (e.g., no Feb 31, no June 31, etc.)
        max_day = calendar.monthrange(2024, month)[1]  # Use 2024 (leap year) to allow Feb 29
        if day > max_day:
            month_names = [
                "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
            ]
            await interaction.response.send_message(
                f"❌ Geçersiz tarih! {month_names[month]} ayı en fazla {max_day} gün içerir.",
                ephemeral=True
            )
            return
        
        # Save birthday to database
        from cogs.database import set_birthday
        
        set_birthday(user.id, user.name, interaction.guild.id, month, day)
        
        # Send confirmation
        month_names = [
            "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        
        embed = discord.Embed(
            title="✅ Doğum Günü Kaydedildi",
            description=f"{user.mention}'un doğum günü **{day} {month_names[month]}** olarak ayarlandı.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Doğum günü kutlamaları otomatik olarak gönderilecek! 🎉")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="birthdaychatroom", description="Doğum günü duyurularının yapılacağı kanalı ayarlar.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Doğum günü duyurularının gönderileceği kanal")
    async def birthdaychatroom_command(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel
    ):
        """Set the channel for birthday announcements"""
        
        from cogs.database import set_birthday_channel
        
        set_birthday_channel(interaction.guild.id, channel.id)
        
        embed = discord.Embed(
            title="✅ Doğum Günü Kanalı Ayarlandı",
            description=f"Doğum günü duyuruları artık {channel.mention} kanalına gönderilecek.",
            color=discord.Color.green()
        )
        embed.set_footer(text="🎂 Doğum günü kutlamaları için hazır!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @birthday_command.error
    async def birthday_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ Bu komutu kullanmak için yönetici yetkisine sahip olmanız gerekiyor!",
                ephemeral=True
            )

    @birthdaychatroom_command.error
    async def birthdaychatroom_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ Bu komutu kullanmak için yönetici yetkisine sahip olmanız gerekiyor!",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))

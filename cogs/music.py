import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import sqlite3
import os
try:
    import yt_dlp
except ImportError:
    yt_dlp = None
import re
from typing import Optional, Dict, List, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicQueue:
    """Manages the music queue for a guild"""
    
    def __init__(self):
        self.queue: List[Dict] = []
        self.current_song: Optional[Dict] = None
        self.voice_client: Optional[discord.VoiceClient] = None
        self.is_playing = False
        self.loop = False
        self.cancel_queueing = False  # Flag to cancel background queueing operations
    
    def add_song(self, song: Dict) -> None:
        """Add a song to the queue"""
        self.queue.append(song)
    
    def get_next_song(self) -> Optional[Dict]:
        """Get the next song from the queue"""
        if self.queue:
            self.current_song = self.queue.pop(0)
            return self.current_song
        return None
    
    def clear_queue(self) -> None:
        """Clear the entire queue"""
        self.queue.clear()
        self.current_song = None
    
    def cancel_all_operations(self) -> None:
        """Cancel all ongoing operations including background queueing"""
        self.clear_queue()
        self.is_playing = False
        self.cancel_queueing = True
    
    def get_queue_length(self) -> int:
        """Get the number of songs in the queue"""
        return len(self.queue)

class PersistentReplayButton(discord.ui.Button):
    """Persistent button for replaying songs"""
    
    def __init__(self):
        super().__init__(
            label="Yeniden Cal",
            style=discord.ButtonStyle.secondary,
            custom_id="persistent_replay_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle button click to replay a song"""
        # Get the music cog from the bot
        music_cog = interaction.client.get_cog('MusicCog')  # type: ignore
        if not music_cog:
            await interaction.response.send_message("❌ Muzik sistemi su anda kullanilamiyor.", ephemeral=True)
            return
        
        # Get song data from database using message ID
        if interaction.message is None:
            await interaction.response.send_message("❌ Mesaj bulunamadi.", ephemeral=True)
            return
            
        song_data = music_cog.get_song_from_database(interaction.message.id)
        if not song_data:
            await interaction.response.send_message("❌ Bu sarki artik mevcut degil.", ephemeral=True)
            return
        
        # Check if user is in a voice channel
        if not interaction.user.voice:  # type: ignore
            await interaction.response.send_message("❌ Bir ses kanalinda olmalisiniz.", ephemeral=True)
            return
        
        # Add song to queue
        success = await music_cog.add_song_to_queue(interaction, song_data)
        if success:
            # Create new embed for the replayed song
            embed = await music_cog.create_music_embed(song_data, interaction.user)
            
            # Create new persistent view with replay button
            view = PersistentReplayView()
            
            # Send new message with embed and button
            if interaction.channel is None:
                await interaction.response.send_message("❌ Kanal bulunamadi.", ephemeral=True)
                return
            
            # Check if channel supports sending messages
            if not isinstance(interaction.channel, discord.TextChannel):
                await interaction.response.send_message("❌ Bu kanal turu desteklenmiyor.", ephemeral=True)
                return
            
            # Send new embed message
            new_message = await interaction.channel.send(embed=embed, view=view)
            
            # Save song to database for the new message with correct format
            if interaction.guild is None:
                await interaction.response.send_message("❌ Sunucu bilgisi bulunamadi.", ephemeral=True)
                return
            
            # Convert database format to proper format for saving
            save_song_data = {
                'title': song_data.get('song_title', 'Unknown Title'),
                'url': song_data.get('url', ''),
                'duration': song_data.get('duration', 'Unknown'),
                'thumbnail': song_data.get('thumbnail_url', ''),
                'uploader': song_data.get('uploader', 'Unknown'),
                'webpage_url': song_data.get('youtube_url', '')
            }
                
            music_cog.save_song_to_database(
                new_message.id,
                interaction.guild.id,
                save_song_data,
                interaction.user.display_name
            )
            
            # Acknowledge the interaction without sending any message
            await interaction.response.defer()
        else:
            await interaction.response.send_message(
                "❌ Sarki siraya eklenirken bir hata olustu.",
                ephemeral=True
            )

class PersistentPlaylistReplayButton(discord.ui.Button):
    """Persistent button for replaying playlists"""
    
    def __init__(self):
        super().__init__(
            label="Yeniden Cal",
            style=discord.ButtonStyle.secondary,
            custom_id="persistent_playlist_replay_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle button click to replay a playlist"""
        # Get the music cog from the bot
        music_cog = interaction.client.get_cog('MusicCog')  # type: ignore
        if not music_cog:
            await interaction.response.send_message("❌ Muzik sistemi su anda kullanilamiyor.", ephemeral=True)
            return
        
        # Get playlist data from database using message ID
        if interaction.message is None:
            await interaction.response.send_message("❌ Mesaj bulunamadi.", ephemeral=True)
            return
            
        playlist_data = music_cog.get_playlist_from_database(interaction.message.id)
        if not playlist_data:
            await interaction.response.send_message("❌ Bu playlist artik mevcut degil.", ephemeral=True)
            return
        
        # Check if user is in a voice channel
        if not interaction.user.voice:  # type: ignore
            await interaction.response.send_message("❌ Bir ses kanalinda olmalisiniz.", ephemeral=True)
            return
        
        # Acknowledge interaction immediately
        await interaction.response.defer()
        
        # Replay the playlist using the stored URL
        playlist_url = playlist_data.get('playlist_url')
        if playlist_url:
            # Call the play command logic for playlist
            await music_cog.play_playlist_internal(interaction, playlist_url)

class PersistentReplayView(discord.ui.View):
    """Persistent view for replay buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)  # Never timeout
        self.add_item(PersistentReplayButton())

class PersistentPlaylistReplayView(discord.ui.View):
    """Persistent view for playlist replay buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)  # Never timeout
        self.add_item(PersistentPlaylistReplayButton())

class MusicCog(commands.Cog):
    """Advanced music cog with persistent replay functionality"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: Dict[int, MusicQueue] = {}  # guild_id -> MusicQueue
        self.yt_dlp_options = {
            'format': 'bestaudio/best',
            'noplaylist': False,  # Changed to allow playlist extraction
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'force-ipv4': True,
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
        
        # Initialize database
        self.init_music_database()
        
        # Register persistent views
        self.bot.add_view(PersistentReplayView())
        self.bot.add_view(PersistentPlaylistReplayView())
        
        logger.info("MusicCog initialized with persistent replay functionality")
    
    def init_music_database(self):
        """Initialize the music database and create tables"""
        os.makedirs("config/database", exist_ok=True)
        conn = sqlite3.connect("config/database/music_persistence.db")
        cursor = conn.cursor()
        
        # Create replay_songs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replay_songs (
                message_id INTEGER PRIMARY KEY,
                guild_id INTEGER NOT NULL,
                song_url TEXT NOT NULL,
                song_title TEXT NOT NULL,
                requester_name TEXT NOT NULL,
                thumbnail_url TEXT,
                uploader TEXT,
                duration TEXT,
                youtube_url TEXT
            )
        """)
        
        # Create replay_playlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replay_playlists (
                message_id INTEGER PRIMARY KEY,
                guild_id INTEGER NOT NULL,
                playlist_url TEXT NOT NULL,
                playlist_title TEXT NOT NULL,
                requester_name TEXT NOT NULL,
                song_count INTEGER NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Music database initialized")
    
    def get_queue(self, guild_id: int) -> MusicQueue:
        """Get or create a queue for a guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]
    
    def format_duration(self, duration: int) -> str:
        """Format duration in seconds to MM:SS format"""
        minutes = duration // 60
        seconds = duration % 60
        return f"{minutes}:{seconds:02d}"
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def is_playlist(self, url: str) -> bool:
        """Check if URL is a YouTube playlist"""
        playlist_patterns = [
            r'[?&]list=([^&]+)',
            r'youtube\.com\/playlist\?list=([^&]+)',
            r'music\.youtube\.com\/playlist\?list=([^&]+)'
        ]
        
        for pattern in playlist_patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def _extract_playlist_info_sync(self, url: str) -> Optional[Dict]:
        """Synchronous helper to extract playlist info using yt-dlp"""
        try:
            playlist_options = self.yt_dlp_options.copy()
            playlist_options['extract_flat'] = 'in_playlist'
            
            with yt_dlp.YoutubeDL(playlist_options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"Error extracting playlist info: {e}")
            return None
    
    async def extract_playlist(self, url: str) -> Optional[List[Dict]]:
        """Extract all songs from a YouTube playlist"""
        if yt_dlp is None:
            logger.error("yt-dlp is not installed. Please install it with: pip install yt-dlp")
            return None
        
        try:
            # Run blocking yt-dlp operation in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._extract_playlist_info_sync, url)
            
            if not info:
                return None
            
            # Check if it's a playlist
            if 'entries' not in info:
                return None
            
            songs = []
            for entry in info['entries']:
                if entry is None:
                    continue
                
                # Get full info for each video
                try:
                    video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    video_info = await self.search_youtube(video_url)
                    
                    if video_info:
                        songs.append(video_info)
                except Exception as e:
                    logger.warning(f"Error extracting video from playlist: {e}")
                    continue
            
            return songs if songs else None
            
        except Exception as e:
            logger.error(f"Error extracting playlist: {e}")
            return None
    
    def _extract_info_sync(self, query: str) -> Optional[Dict]:
        """Synchronous helper to extract info using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_options) as ydl:
                # If query looks like a URL, extract info directly
                if 'youtube.com' in query or 'youtu.be' in query:
                    info = ydl.extract_info(query, download=False)
                else:
                    # Search for the query
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if info and 'entries' in info and info['entries']:
                        info = info['entries'][0]
                    else:
                        return None
                
                if not info:
                    return None
                
                # Extract audio URL
                audio_url = None
                formats = info.get('formats', [])
                for format_info in formats:
                    if format_info.get('acodec') != 'none' and format_info.get('vcodec') == 'none':
                        audio_url = format_info['url']
                        break
                
                if not audio_url:
                    # Fallback to best audio format
                    audio_url = info.get('url')
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'url': audio_url,
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'webpage_url': info.get('webpage_url', ''),
                    'video_id': self.extract_video_id(info.get('webpage_url', ''))
                }
        except Exception as e:
            logger.error(f"Error extracting info: {e}")
            return None
    
    async def search_youtube(self, query: str) -> Optional[Dict]:
        """Search YouTube for a song"""
        if yt_dlp is None:
            logger.error("yt-dlp is not installed. Please install it with: pip install yt-dlp")
            return None
            
        try:
            # Run blocking yt-dlp operation in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._extract_info_sync, query)
            return info
                
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return None
    
    def save_song_to_database(self, message_id: int, guild_id: int, song_data: Dict, requester_name: str):
        """Save song information to database for replay functionality"""
        try:
            conn = sqlite3.connect("config/database/music_persistence.db")
            cursor = conn.cursor()
            
            # Handle both database format and YouTube format
            title = song_data.get('title') or song_data.get('song_title', 'Unknown Title')
            url = song_data.get('url', '')
            thumbnail = song_data.get('thumbnail') or song_data.get('thumbnail_url', '')
            uploader = song_data.get('uploader', 'Unknown')
            duration = song_data.get('duration', 0)
            webpage_url = song_data.get('webpage_url', '')
            
            # Format duration if it's a number
            if isinstance(duration, int):
                duration_str = self.format_duration(duration)
            else:
                duration_str = str(duration)
            
            cursor.execute("""
                INSERT OR REPLACE INTO replay_songs 
                (message_id, guild_id, song_url, song_title, requester_name, 
                 thumbnail_url, uploader, duration, youtube_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id, guild_id, url, title,
                requester_name, thumbnail, uploader,
                duration_str, webpage_url
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Song saved to database: {title}")
            
        except Exception as e:
            logger.error(f"Error saving song to database: {e}")
    
    def get_song_from_database(self, message_id: int) -> Optional[Dict]:
        """Retrieve song information from database"""
        try:
            conn = sqlite3.connect("config/database/music_persistence.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT song_url, song_title, requester_name, thumbnail_url, 
                       uploader, duration, youtube_url
                FROM replay_songs 
                WHERE message_id = ?
            """, (message_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'url': result[0],
                    'song_title': result[1],
                    'requester_name': result[2],
                    'thumbnail_url': result[3],
                    'uploader': result[4],
                    'duration': result[5],
                    'webpage_url': result[6]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving song from database: {e}")
            return None
    
    def save_playlist_to_database(self, message_id: int, guild_id: int, playlist_url: str, 
                                   playlist_title: str, requester_name: str, song_count: int):
        """Save playlist information to database for replay functionality"""
        try:
            conn = sqlite3.connect("config/database/music_persistence.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO replay_playlists 
                (message_id, guild_id, playlist_url, playlist_title, requester_name, song_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, guild_id, playlist_url, playlist_title, requester_name, song_count))
            
            conn.commit()
            conn.close()
            logger.info(f"Playlist saved to database: {playlist_title}")
            
        except Exception as e:
            logger.error(f"Error saving playlist to database: {e}")
    
    def get_playlist_from_database(self, message_id: int) -> Optional[Dict]:
        """Retrieve playlist information from database"""
        try:
            conn = sqlite3.connect("config/database/music_persistence.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT playlist_url, playlist_title, requester_name, song_count
                FROM replay_playlists 
                WHERE message_id = ?
            """, (message_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'playlist_url': result[0],
                    'playlist_title': result[1],
                    'requester_name': result[2],
                    'song_count': result[3]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving playlist from database: {e}")
            return None
    
    async def create_music_embed(self, song_data: Dict, requester: Union[discord.Member, discord.User]) -> discord.Embed:
        """Create the music embed with song information"""
        # Handle both database format (song_title) and YouTube format (title)
        title = song_data.get('title') or song_data.get('song_title', 'Unknown Title')
        
        # 1. Embed başlığını "🎵 Simdi Caliyor:" olmadan, sadece şarkı adı olarak ayarla
        # 2. Rengi YouTube kırmızısı yap (discord.Color.red())
        embed = discord.Embed(
            title=title, # Sadece şarkı adı
            url=song_data.get('webpage_url', ''),
            color=discord.Color.red(), # YouTube Kırmızısı
        )
        
        # Add thumbnail
        thumbnail = song_data.get('thumbnail') or song_data.get('thumbnail_url')
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        # Sureyi formatla (saniye veya MM:SS olabilir)
        duration_value = song_data.get('duration', 'Unknown')
        if isinstance(duration_value, int):
            # Yazım hatası düzeltildi: format_dura -> format_duration
            duration_str = self.format_duration(duration_value)
        else:
            duration_str = str(duration_value)
            
        # 3. & 4. Mükerrer "Yükleyen" alanını kaldır ve daha kompakt bir görünüm için
        # bilgileri 'description' (açıklama) alanına taşı.
        
        # 'description'daki eski yükleyen satırı kaldırıldı.
        # 'add_field' ile eklenen "Yükleyen" ve "Süre" alanları kaldırıldı.
        
        # Tüm bilgileri 'description' (açıklama) alanına topluyoruz:
        description_lines = [
            f"📺 **Yukleyen:** {song_data.get('uploader', 'Unknown')}",
            f"⏱️ **Sure:** {duration_str}"
        ]
        embed.description = "\n".join(description_lines)
        
        # Add footer
        embed.set_footer(
            text=f"Isteyen: {requester.display_name}",
            icon_url=requester.display_avatar.url
        )
        
        return embed
    
    async def play_next_song(self, guild_id: int):
        """Play the next song in the queue"""
        queue = self.get_queue(guild_id)
        
        if not queue.voice_client or not queue.voice_client.is_connected():
            return
        
        # Check if operations were cancelled (stop command or disconnect)
        if queue.cancel_queueing:
            queue.is_playing = False
            return
        
        next_song = queue.get_next_song()
        if not next_song:
            queue.is_playing = False
            return
        
        try:
            queue.is_playing = True
            
            # FFmpeg options for better streaming stability
            # -b:a 192k (bitrate) seçeneğini kaldırarak
            # sesin orijinal kalitede (re-encode edilmeden) akışını sağlıyoruz.
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn' # '-b:a 192k' buradan kaldırıldı
            }
            
            # Play the audio
            queue.voice_client.play(
                discord.FFmpegPCMAudio(
                    next_song['url'],
                    **ffmpeg_options
                ),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next_song(guild_id), self.bot.loop
                ) if e is None else logger.error(f"Audio error: {e}")
            )
            
            logger.info(f"Now playing: {next_song['title']} in guild {guild_id}")
            
        except Exception as e:
            logger.error(f"Error playing song: {e}")
            queue.is_playing = False
            # Try to play next song
            await self.play_next_song(guild_id)
    
    async def add_song_to_queue(self, interaction: discord.Interaction, song_data: Dict) -> bool:
        """Add a song to the queue and start playing if needed"""
        if interaction.guild is None:
            return False
            
        guild_id = interaction.guild.id
        queue = self.get_queue(guild_id)
        
        # Convert database format to queue format if needed
        queue_song_data = {
            'title': song_data.get('title') or song_data.get('song_title', 'Unknown Title'),
            'url': song_data.get('url'),
            'duration': song_data.get('duration', 0),
            'thumbnail': song_data.get('thumbnail') or song_data.get('thumbnail_url'),
            'uploader': song_data.get('uploader', 'Unknown'),
            'webpage_url': song_data.get('webpage_url', ''),
            'video_id': song_data.get('video_id')
        }
        
        # Check if bot is in a voice channel
        if not queue.voice_client or not queue.voice_client.is_connected():
            # Join the user's voice channel
            try:
                if not interaction.user.voice:  # type: ignore
                    return False
                    
                voice_channel = interaction.user.voice.channel  # type: ignore
                if voice_channel is None:
                    return False
                    
                queue.voice_client = await voice_channel.connect()
            except Exception as e:
                logger.error(f"Error joining voice channel: {e}")
                return False
        
        # Add song to queue
        queue.add_song(queue_song_data)
        
        # If nothing is playing, start playing
        if not queue.is_playing:
            await self.play_next_song(guild_id)
        
        return True
    
    async def play_playlist_internal(self, interaction: discord.Interaction, playlist_url: str):
        """Internal method to handle playlist playback"""
        # Get playlist entries (fast with extract_flat)
        loop = asyncio.get_event_loop()
        playlist_info = await loop.run_in_executor(None, self._extract_playlist_info_sync, playlist_url)
        
        if not playlist_info or 'entries' not in playlist_info:
            if hasattr(interaction, 'followup'):
                await interaction.followup.send(
                    "❌ Playlist'ten sarki alinamadi. Lutfen farkli bir playlist deneyin.",
                    ephemeral=True
                )
            return
        
        entries = [e for e in playlist_info['entries'] if e is not None]
        if not entries:
            if hasattr(interaction, 'followup'):
                await interaction.followup.send(
                    "❌ Playlist bos veya sarkilar alinamadi.",
                    ephemeral=True
                )
            return
        
        # Reset cancellation flag for new playlist
        if interaction.guild:
            guild_id = interaction.guild.id
            queue = self.get_queue(guild_id)
            queue.cancel_queueing = False
        
        # Create embed with song titles from entries (fast, no need to extract full metadata)
        song_titles = [entry.get('title', 'Unknown Title') for entry in entries[:5]]
        embed = discord.Embed(
            title="✅ Playlist Siraya Eklendi",
            description=f"**{len(entries)}** sarki basariyla siraya eklendi ve ard arda calinacak!",
            color=discord.Color.green()
        )
        
        song_list = "\n".join([f"{i+1}. {title}" for i, title in enumerate(song_titles)])
        if len(entries) > 5:
            song_list += f"\n... ve {len(entries) - 5} sarki daha"
        embed.add_field(name="Sarkilar", value=song_list, inline=False)
        
        # Create persistent view with playlist replay button
        view = PersistentPlaylistReplayView()
        
        # Send embed using followup if interaction was deferred, otherwise send to channel
        if hasattr(interaction, 'followup') and interaction.response.is_done():
            # Interaction was deferred, use followup
            message = await interaction.followup.send(embed=embed, view=view, wait=True)
        elif isinstance(interaction.channel, discord.TextChannel):
            # Direct send to channel (for replay button callback)
            message = await interaction.channel.send(embed=embed, view=view)
        else:
            return
        
        # Save playlist to database
        if interaction.guild:
            playlist_title = playlist_info.get('title', 'Playlist')
            self.save_playlist_to_database(
                message.id,
                interaction.guild.id,
                playlist_url,
                playlist_title,
                interaction.user.display_name,
                len(entries)
            )
        
        # Now queue all songs in background - check cancellation flag
        for entry in entries:
            # Check if operation was cancelled
            if interaction.guild:
                queue = self.get_queue(interaction.guild.id)
                if queue.cancel_queueing:
                    logger.info(f"Playlist queueing cancelled for guild {interaction.guild.id}")
                    break
            
            try:
                video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                video_info = await self.search_youtube(video_url)
                
                if video_info:
                    await self.add_song_to_queue(interaction, video_info)
            except Exception as e:
                logger.warning(f"Error adding song from playlist: {e}")
                continue
    
    @app_commands.command(name="play", description="YouTube'dan sarki veya playlist calar")
    async def play_command(self, interaction: discord.Interaction, song: str):
        """Play a song or playlist from YouTube"""
        # Check if user is in a voice channel
        if not interaction.user.voice:  # type: ignore
            await interaction.response.send_message(
                "❌ Bir ses kanalinda olmalisiniz!",
                ephemeral=True
            )
            return
        
        # Defer response since this might take a while
        await interaction.response.defer()
        
        try:
            # Check if the URL is a playlist
            if self.is_playlist(song):
                # Handle playlist
                await self.play_playlist_internal(interaction, song)
                
            else:
                # Handle single song (existing functionality)
                song_data = await self.search_youtube(song)
                if not song_data:
                    await interaction.followup.send(
                        "❌ Sarki bulunamadi. Lutfen farkli bir arama terimi deneyin.",
                        ephemeral=True
                    )
                    return
                
                # Create embed
                embed = await self.create_music_embed(song_data, interaction.user)
                
                # Create persistent view with replay button
                view = PersistentReplayView()
                
                # Send the message with embed and button
                if interaction.channel is None:
                    await interaction.followup.send(
                        "❌ Kanal bulunamadi.",
                        ephemeral=True
                    )
                    return
                
                # Check if channel supports sending messages
                if not isinstance(interaction.channel, discord.TextChannel):
                    await interaction.followup.send(
                        "❌ Bu kanal turu desteklenmiyor.",
                        ephemeral=True
                    )
                    return
                    
                # "düşünüyor..." mesajını kaldırmak için 'followup.send' kullanıyoruz
                # 'wait=True' mesaj nesnesini (ID'si için) almamızı sağlar
                message = await interaction.followup.send(embed=embed, view=view, wait=True)
                
                # 'followup.send' zaten etkileşimi sonlandırdığı için
                # ek bir onaya (eski '✅') gerek yok.
                
                # Save song to database for replay functionality
                if interaction.guild is None:
                    await interaction.followup.send(
                        "❌ Sunucu bilgisi bulunamadi.",
                        ephemeral=True
                    )
                    return
                    
                self.save_song_to_database(
                    message.id,
                    interaction.guild.id,
                    song_data,
                    interaction.user.display_name
                )
                
                # Add song to queue and start playing
                success = await self.add_song_to_queue(interaction, song_data)
                
                if not success:
                    await interaction.followup.send(
                        "❌ Sarki calinirken bir hata olustu.",
                        ephemeral=True
                    )
                
        except Exception as e:
            logger.error(f"Error in play command: {e}")
            await interaction.followup.send(
                "❌ Sarki calinirken bir hata olustu.",
                ephemeral=True
            )
    
    @app_commands.command(name="skip", description="Su anda calan sarkiyi atlar")
    async def skip_command(self, interaction: discord.Interaction):
        """Skip the currently playing song"""
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.followup.send(
                "❌ Bu komut sadece sunucularda kullanilabilir.",
                ephemeral=True
            )
            return
            
        guild_id = interaction.guild.id
        queue = self.get_queue(guild_id)
        
        if not queue.voice_client or not queue.voice_client.is_connected():
            await interaction.followup.send(
                "❌ Bot su anda bir ses kanalinda degil.",
                ephemeral=True
            )
            return
        
        if not queue.is_playing:
            await interaction.followup.send(
                "❌ Su anda hicbir sarki calmıyor.",
                ephemeral=True
            )
            return
        
        # Stop current song
        queue.voice_client.stop()
        
        # 'defer' kullanıldığı için, bir 'followup' göndermek gerekir.
        # "✅" yerine daha açıklayıcı bir mesaj gönderelim.
        # await interaction.followup.send("⏭️ Sarki atlandi.", ephemeral=True)
        
        # YENİ: Başarılı olduğunda mesaj göndermek yerine "düşünüyor..." mesajını
        # silerek komutu tamamen sessiz hale getiriyoruz.
        await interaction.delete_original_response()
    
    @app_commands.command(name="stop", description="Muzigi durdurur ve botu ses kanalindan cikarir")
    async def stop_command(self, interaction: discord.Interaction):
        """Stop music and disconnect bot"""
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.followup.send(
                "❌ Bu komut sadece sunucularda kullanilabilir.",
                ephemeral=True
            )
            return
            
        guild_id = interaction.guild.id
        queue = self.get_queue(guild_id)
        
        if not queue.voice_client or not queue.voice_client.is_connected():
            await interaction.followup.send(
                "❌ Bot zaten bir ses kanalinda degil.",
                ephemeral=True
            )
            return
        
        # Cancel all operations including background playlist queueing
        queue.cancel_all_operations()
        
        # Stop currently playing audio
        if queue.voice_client.is_playing():
            queue.voice_client.stop()
        
        # Disconnect from voice channel
        await queue.voice_client.disconnect()
        queue.voice_client = None
        
        # Delete the interaction message silently
        await interaction.delete_original_response()
    
    @app_commands.command(name="queue", description="Sarki sirasini gosterir")
    async def queue_command(self, interaction: discord.Interaction):
        """Show the current music queue"""
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.followup.send(
                "❌ Bu komut sadece sunucularda kullanilabilir.",
                ephemeral=True
            )
            return
            
        guild_id = interaction.guild.id
        queue = self.get_queue(guild_id)
        
        if not queue.queue and not queue.current_song:
            await interaction.followup.send(
                "📭 Sarki sirasi bos.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🎵 Muzik Sirasi",
            color=discord.Color.blue()
        )
        
        # Show currently playing song
        if queue.current_song:
            embed.add_field(
                name="🎵 Simdi Caliyor",
                value=f"**{queue.current_song['title']}**",
                inline=False
            )
        
        # Show queue
        if queue.queue:
            queue_text = ""
            for i, song in enumerate(queue.queue[:10], 1):  # Show first 10 songs
                queue_text += f"{i}. **{song['title']}**\n"
            
            if len(queue.queue) > 10:
                queue_text += f"\n... ve {len(queue.queue) - 10} sarki daha"
            
            embed.add_field(
                name="📋 Siradaki Sarkilar",
                value=queue_text,
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state updates to detect bot disconnection"""
        # Check if the bot was disconnected
        if member.id == self.bot.user.id:  # type: ignore
            # Bot was in a voice channel and is now not
            if before.channel is not None and after.channel is None:
                # Bot was disconnected
                if member.guild:
                    guild_id = member.guild.id
                    queue = self.get_queue(guild_id)
                    
                    # Stop currently playing audio if any
                    if queue.voice_client and queue.voice_client.is_playing():
                        queue.voice_client.stop()
                    
                    # Cancel all operations and clear queue
                    queue.cancel_all_operations()
                    queue.voice_client = None
                    
                    logger.info(f"Bot disconnected from voice in guild {guild_id}, cancelled all operations")

async def setup(bot: commands.Bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(MusicCog(bot))
    logger.info("MusicCog loaded successfully")
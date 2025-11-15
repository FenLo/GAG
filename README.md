# GAG Discord Bot

A feature-rich Discord bot built with Python, offering moderation tools, entertainment features, gaming integration, and utility commands.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Features

### 🛡️ Moderation
- **Timeout/Unmute** - Temporarily mute users with time limits
- **Ban/Unban/Kick** - Comprehensive user management
- **Softban** - Remove user messages without permanent ban
- **Message Management** - Clear and purge messages in bulk
- **Channel Controls** - Lock/unlock channels and set slowmode
- **Nickname Management** - Change user nicknames
- **Auto-role** - Automatically assign roles to new members (separate roles for users and bots)

### 🎮 Gaming & Entertainment
- **PUBG Integration** - Track and display PUBG statistics in real-time
- **Drawing Game** - Interactive drawing and guessing game
- **Coin Flip** - Yazı-tura (heads/tails) simulation
- **Gay Rate** - Fun rating command
- **Cat Facts** - Random cat facts
- **Memes** - Random meme generator
- **Quote Creator** - Generate custom quote images

### 📊 Utility
- **Weather** - Multi-day weather forecasts for any city
- **Server Info** - Display comprehensive server statistics
- **User Info** - View detailed user information
- **Game Activity** - See what games server members are playing
- **Help Command** - Complete command reference

### 💰 Cryptocurrency
- **Crypto Tracking** - Automated cryptocurrency price updates every 10 minutes
- **Multiple Currencies** - Track various cryptocurrencies

### 📰 News
- **RSS Feed Integration** - Automated news updates every 45 minutes from RSS feeds

### 🎵 Music
- **Music Playback** - Play music from YouTube in voice channels
- **Playlist Support** - Add entire YouTube Music playlists to queue and play sequentially
- **Queue Management** - View current queue, skip songs, and manage playback
- **Persistent Replay** - Replay previously played songs with a button

### 🎂 Birthdays
- **Birthday Tracking** - Set and track member birthdays
- **Automated Reminders** - Automatic countdown messages (3 days, 2 days, 1 day before)
- **Birthday Announcements** - Celebrate birthdays with automated messages
- **Birthday List** - View all registered birthdays in the server


## Command List

| Command | Description | Permissions Required |
|---------|-------------|---------------------|
| `/help` | Display all available commands | None |
| `/weather <city> <days>` | Get weather forecast | None |
| `/timeout <member> <minutes> [reason]` | Mute a user temporarily | Administrator |
| `/unmute <member>` | Unmute a user | Administrator |
| `/ban <member> [reason]` | Ban a user from the server | Administrator |
| `/kick <member> [reason]` | Kick a user from the server | Administrator |
| `/unban <user> [reason]` | Unban a previously banned user | Administrator |
| `/softban <member> [reason]` | Softban a user | Ban Members |
| `/clear <amount>` | Delete messages in bulk | Administrator |
| `/purge <amount>` | Remove 1-100 messages | Manage Messages |
| `/serverinfo` | Display server information | None |
| `/userinfo <member>` | Show user details | None |
| `/slowmode <seconds>` | Set channel slowmode | Manage Channels |
| `/lock` | Lock the channel | Manage Channels |
| `/unlock` | Unlock the channel | Manage Channels |
| `/nick <member> <new_nick>` | Change user nickname | Manage Nicknames |
| `/otorol <user_role> <bot_role>` | Set auto-roles for new members | Administrator |
| `/pubgkanal <channel>` | Set PUBG stats channel | Administrator |
| `/pubg <start/stop>` | Start/stop PUBG tracking | Administrator |
| `/crypto <channel>` | Set crypto updates channel | Administrator |
| `/haberrss <channel>` | Set news RSS channel | Administrator |
| `/habertest` | Test news system | Administrator |
| `/gayrate <member>` | Fun rating command | None |
| `/yazıtura` | Flip a coin | None |
| `/alıntıolustur <member> <message>` | Create a quote image | None |
| `/oyunlar` | Show games being played | None |
| `/catfact` | Get a random cat fact | None |
| `/meme` | Get a random meme | None |
| `/drawgame` | Start a drawing game | None |
| `/guess <tahmin>` | Guess the drawing | None |
| `/play <song/url>` | Play a song or playlist from YouTube | None |
| `/skip` | Skip the currently playing song | None |
| `/stop` | Stop music and disconnect bot | None |
| `/queue` | Show the current music queue | None |
| `/birthday <user> <month> <day>` | Set a user's birthday | Administrator |
| `/birthdays` | View all registered birthdays | None |
| `/birthdaychatroom <channel>` | Set birthday announcements channel | Administrator |


## Technology Stack

- **Language**: Python 3.8+
- **Library**: discord.py 2.0+
- **Database**: SQLite (via cogs.database)
- **Environment**: python-dotenv for configuration

## Bot Structure

```
GAG/
├── bot.py                 # Main bot file
├── start.bat             # Windows startup script
├── cogs/                 # Feature modules
│   ├── database.py       # Database management
│   ├── moderation.py     # Moderation commands
│   ├── pubg.py          # PUBG integration
│   ├── fun.py           # Entertainment commands
│   ├── utility.py       # Utility commands
│   ├── images.py        # Image generation
│   ├── drawgame.py      # Drawing game
│   ├── crypto.py        # Cryptocurrency tracking
│   ├── news_rss.py      # RSS news feed
│   ├── music.py         # Music playback
│   └── birthday.py      # Birthday tracking and announcements
├── config/              # Configuration files
│   └── .env            # Environment variables
└── yazıtura/           # Coin flip assets
```

## Getting Started

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

## Configuration

After installation, configure the bot by:

1. Setting up your Discord bot token in `config/.env`
2. Inviting the bot to your server with appropriate permissions
3. Using setup commands like `/otorol`, `/pubgkanal`, `/crypto`, and `/haberrss`

## Required Permissions

The bot requires the following Discord permissions:
- Read Messages/View Channels
- Send Messages
- Manage Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Use Slash Commands
- Manage Roles (for auto-role)
- Moderate Members (for timeout)
- Ban Members
- Kick Members
- Manage Nicknames
- Manage Channels

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ using discord.py**

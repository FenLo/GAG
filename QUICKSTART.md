# Quick Start Guide

Get the GAG Discord Bot up and running in 5 minutes!

## Prerequisites
- Node.js 18.0 or higher installed
- A Discord bot token

## Steps

### 1. Clone/Download the Repository
```bash
git clone https://github.com/FenLo/GAG.git
cd GAG
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
Create a file `config/.env` with your Discord bot token:
```env
DISCORD_TOKEN=your_discord_bot_token_here
WEATHER_API_KEY=your_weather_api_key_here
```

### 4. Run the Bot
```bash
npm start
```

That's it! Your bot should now be online.

## First Commands to Try

Once the bot is running in your Discord server:

1. `/help` - See all available commands
2. `/serverinfo` - View your server information
3. `/gayrate @user` - Have some fun
4. `/weather Tokyo 3` - Get weather forecast
5. `/meme` - Get a random meme

## Setting Up Features

### Auto-Role for New Members
```
/otorol user_role:@Member bot_role:@Bots
```

### Birthday System
```
/birthdaychatroom channel:#birthdays
/birthday user:@John month:12 day:25
```

### Weather (requires API key)
Get a free API key from [Tomorrow.io](https://www.tomorrow.io/) and add it to `.env`

## Troubleshooting

**Bot won't start?**
- Check that your token is correct in `config/.env`
- Make sure Node.js 18+ is installed: `node --version`
- Ensure dependencies are installed: `npm install`

**Commands don't appear?**
- Wait 1-2 minutes for Discord to sync commands
- Make sure the bot has "Use Slash Commands" permission

**Need help?**
See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

## Production Deployment

For 24/7 operation, use PM2:
```bash
npm install -g pm2
pm2 start bot.js --name gag-bot
pm2 save
pm2 startup
```

---

**That's all! Enjoy your bot! 🎉**

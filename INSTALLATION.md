# Installation Guide

This guide will walk you through the process of setting up and running the GAG Discord Bot (JavaScript/Node.js version).

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18.0 or higher** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**
- **Git** (optional, for cloning) - [Download Git](https://git-scm.com/downloads/)
- **Discord Account** - To create a bot application

## Step 1: Clone or Download the Repository

### Option A: Using Git
```bash
git clone https://github.com/FenLo/GAG.git
cd GAG
```

### Option B: Manual Download
1. Download the repository as a ZIP file from GitHub
2. Extract the ZIP file to your desired location
3. Open a terminal/command prompt in the extracted folder

## Step 2: Install Node.js Dependencies

### All Platforms
```bash
npm install
```

Or if you prefer yarn:
```bash
yarn install
```

### Required Packages
The following packages will be installed automatically from `package.json`:
- `discord.js` - Discord API wrapper
- `dotenv` - Environment variable management
- `sqlite3` - Database
- `axios` - HTTP requests
- `canvas` - Image generation
- `node-cron` - Scheduled tasks
- `feedparser` - RSS parsing
- `@discordjs/voice` - Voice/music support
- `ytdl-core` / `play-dl` - YouTube playback

## Step 3: Create a Discord Bot Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name
3. Navigate to the **"Bot"** section in the left sidebar
4. Click **"Add Bot"** and confirm
5. Under the bot's username, click **"Reset Token"** and copy the token (keep this secure!)
6. Enable the following **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
7. Save your changes

## Step 4: Configure Environment Variables

1. Navigate to the `config` folder in your bot directory
2. Create a file named `.env` (note the dot at the beginning)
3. Add your Discord bot token:

```env
DISCORD_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with the token you copied in Step 3.

### Example `.env` file:
```env
DISCORD_TOKEN=
```

## Step 5: Invite the Bot to Your Server

1. Go back to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Navigate to the **"OAuth2"** → **"URL Generator"** section
4. Select the following **Scopes**:
   - ✅ `bot`
   - ✅ `applications.commands`
5. Select the following **Bot Permissions**:
   - ✅ Manage Roles
   - ✅ Manage Channels
   - ✅ Kick Members
   - ✅ Ban Members
   - ✅ Moderate Members
   - ✅ Send Messages
   - ✅ Manage Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use Slash Commands
   - ✅ Manage Nicknames

6. Copy the generated URL at the bottom and paste it into your browser
7. Select the server you want to add the bot to and authorize

## Step 6: Run the Bot

### All Platforms

#### Option A: Using npm
```bash
npm start
```

#### Option B: Using Node directly
```bash
node bot.js
```

#### Option C: Using the start script
```bash
node start.js
```

### Development Mode (with auto-restart)
```bash
npm run dev
```

## Step 7: Verify Installation

Once the bot is running, you should see:
```
GAG BOT hazır ve komutlar senkronize edildi.
```

In Discord:
1. The bot should appear online in your server
2. Type `/help` to see all available commands
3. The bot's status should show: "Playing GAG | /help"

## Step 8: Initial Configuration (Optional)

Configure these features based on your needs:

### Auto-role for New Members
```
/otorol user_role:@Member bot_role:@Bots
```

### PUBG Statistics Channel
```
/pubgkanal kanal:#pubg-stats
/pubg start
```

### Cryptocurrency Updates
```
/crypto kanal:#crypto
```

### RSS News Feed
```
/haberrss kanal:#news
```

## Troubleshooting

### Bot doesn't start
- Verify your token in `config/.env` is correct
- Ensure all required packages are installed: `npm install`
- Check Node.js version: `node --version` (must be 18.0+)

### Commands don't appear
- Wait a few minutes for Discord to sync slash commands
- Ensure the bot has "Use Slash Commands" permission
- Try running `/help` to verify bot is responsive

### "Token is invalid" error
- Double-check your token in `config/.env`
- Ensure there are no extra spaces or quotes around the token
- Regenerate the token in the Discord Developer Portal if needed

### Permission errors
- Verify the bot's role is higher than roles it needs to manage
- Check that the bot has all required permissions in server settings

### Module not found errors
```bash
npm install
```

### Canvas/image generation errors
On Linux, you may need to install additional dependencies:
```bash
sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev
```

On macOS:
```bash
brew install pkg-config cairo pango libpng jpeg giflib librsvg
```

## Updating the Bot

To update to the latest version:

```bash
git pull origin main
npm install
node bot.js
```

## Running the Bot 24/7

For continuous operation, consider:
- **Windows**: Use Task Scheduler or PM2
- **Linux**: Use systemd, PM2, screen, or tmux
- **Cloud Hosting**: Deploy on platforms like Heroku, Railway, Render, or AWS
- **VPS**: Rent a Virtual Private Server for dedicated hosting

### Using PM2 (Recommended for production)
```bash
npm install -g pm2
pm2 start bot.js --name gag-bot
pm2 save
pm2 startup
```

### Example: Using screen on Linux
```bash
screen -S gag-bot
node bot.js
# Press Ctrl+A then D to detach
# Use 'screen -r gag-bot' to reattach
```

## Need Help?

If you encounter any issues:
1. Check the console output for error messages
2. Verify all configuration steps were completed
3. Ensure your Discord bot has the necessary permissions
4. Open an issue on GitHub with details about your problem

---

**Congratulations! Your GAG Discord Bot is now ready to use.** 🎉

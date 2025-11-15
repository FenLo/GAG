# Migration Guide: Python to JavaScript

This document explains the migration from the Python (discord.py) version to JavaScript (discord.js) version of the GAG Discord Bot.

## What Changed

### Technology Stack
- **Language**: Python 3.8+ → JavaScript (Node.js 18+)
- **Discord Library**: discord.py 2.0+ → discord.js 14.14+
- **Database**: Python sqlite3 → Node.js sqlite3
- **Package Manager**: pip/requirements.txt → npm/package.json
- **Module System**: Python imports → Node.js require/modules

### File Structure
**Python Version:**
```
GAG/
├── bot.py (main file)
├── cogs/ (feature modules)
│   ├── database.py
│   ├── moderation.py
│   ├── fun.py
│   └── ...
└── requirements.txt
```

**JavaScript Version:**
```
GAG/
├── bot.js (main file)
├── src/
│   ├── commands/ (slash commands)
│   ├── events/ (event handlers)
│   ├── database.js
│   └── utils/
└── package.json
```

### Commands Implementation
- **Python**: Commands defined in cogs with decorators (`@tree.command`)
- **JavaScript**: Commands in separate files with SlashCommandBuilder
- All commands converted to modern slash command format
- Each command is now a standalone module for better organization

### Database
- Same SQLite database structure maintained
- Converted from Python's sqlite3 to Node.js sqlite3
- All database functions preserved (init, CRUD operations)
- Database files remain compatible

### Event Handlers
- **Python**: Events defined in main bot.py with `@bot.event`
- **JavaScript**: Events in separate files in `src/events/`
- Same event logic (ready, guildMemberAdd, etc.)

## Feature Parity

### ✅ Fully Implemented Features
1. **Moderation** (12 commands)
   - timeout, unmute, ban, kick, unban
   - softban, clear, purge
   - slowmode, lock, unlock, nick

2. **Utility** (5 commands)
   - help, weather, serverinfo, userinfo, oyunlar

3. **Fun & Entertainment** (4 commands)
   - gayrate, yazıtura, catfact, meme

4. **Image Generation** (1 command)
   - alıntıolustur (quote creator with Canvas)

5. **Birthday System** (3 commands)
   - birthday, birthdays, birthdaychatroom

6. **Settings** (2 commands)
   - otorol (auto-role), pubgkanal

### 🚧 Placeholder Implementations
These features have command structure but need full implementation:
1. **Music System** (play, skip, stop, queue)
2. **Drawing Game** (drawgame, guess)
3. **Cryptocurrency** (crypto tracking)
4. **RSS News** (haberrss, habertest)
5. **PUBG Integration** (pubg tracking)

## Configuration

### Environment Variables
Both versions use `.env` file in `config/` directory:
```
DISCORD_TOKEN=your_token
WEATHER_API_KEY=your_key
```

### Database
Database files remain in `config/database/`:
- `pubg_bot.db`
- `moderation.db`
- `otorol.db`
- `birthdays.db`
- `crypto_channel.db`

## Running the Bot

**Python:**
```bash
python bot.py
# or
start.bat
```

**JavaScript:**
```bash
npm start
# or
node bot.js
# or
node start.js
```

## Dependencies

**Python (requirements.txt):**
- discord.py
- python-dotenv
- aiohttp
- Pillow
- feedparser
- etc.

**JavaScript (package.json):**
- discord.js
- dotenv
- axios
- canvas
- feedparser
- etc.

## Key Code Differences

### Command Definition
**Python:**
```python
@tree.command(name="help", description="...")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(...)
```

**JavaScript:**
```javascript
module.exports = {
    data: new SlashCommandBuilder()
        .setName('help')
        .setDescription('...'),
    async execute(interaction) {
        await interaction.reply(...);
    }
};
```

### Database Operations
**Python:**
```python
conn = sqlite3.connect("config/database/pubg_bot.db")
cursor = conn.cursor()
cursor.execute("SELECT ...")
result = cursor.fetchall()
conn.close()
```

**JavaScript:**
```javascript
const db = new sqlite3.Database(PUBG_DB);
db.all('SELECT ...', [], (err, rows) => {
    // handle results
    db.close();
});
```

### Event Handling
**Python:**
```python
@bot.event
async def on_ready():
    print("Bot ready")
```

**JavaScript:**
```javascript
client.once('ready', () => {
    console.log('Bot ready');
});
```

## Testing Checklist

After migration, test these features:
- [ ] Bot connects and shows online
- [ ] Slash commands sync properly
- [ ] `/help` displays all commands
- [ ] Moderation commands work (timeout, ban, kick, etc.)
- [ ] Utility commands work (weather, serverinfo, etc.)
- [ ] Fun commands work (gayrate, meme, catfact)
- [ ] Auto-role assigns roles to new members
- [ ] Birthday system stores and retrieves birthdays
- [ ] Database operations complete successfully
- [ ] Image generation (quote creator) works
- [ ] Error handling works properly

## Notes

1. **Backward Compatibility**: Existing database files from Python version should work with JavaScript version
2. **Feature Additions**: Placeholder commands are ready for future implementation
3. **Performance**: Node.js async/event-driven nature may provide better performance
4. **Maintenance**: Modular command structure makes adding/updating commands easier
5. **Type Safety**: Consider migrating to TypeScript in future for better type safety

## Support

For issues during migration:
1. Check that Node.js 18+ is installed
2. Ensure all dependencies are installed: `npm install`
3. Verify `.env` file is properly configured
4. Check console for error messages
5. Refer to INSTALLATION.md for setup steps

const { Client, GatewayIntentBits, Collection, REST, Routes, ActivityType } = require('discord.js');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: './config/.env' });

// Initialize database functions
const { initDb, initModerationDb, initOtorolDb, initBirthdaysDb } = require('./src/database');

// Create a new Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildPresences,
        GatewayIntentBits.GuildVoiceStates
    ]
});

// Collections for commands
client.commands = new Collection();

// Loading animation
let animationRunning = true;
const loadingAnimation = () => {
    const anim = ['   ', '.  ', '.. ', '...'];
    let i = 0;
    const interval = setInterval(() => {
        if (!animationRunning) {
            process.stdout.write('\r\x1b[K');
            clearInterval(interval);
            return;
        }
        process.stdout.write(`\rBot başlatılıyor${anim[i % anim.length]}`);
        i++;
    }, 500);
};

// Start loading animation
loadingAnimation();

// Load command files
const commandsPath = path.join(__dirname, 'src', 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
    const filePath = path.join(commandsPath, file);
    const command = require(filePath);
    if ('data' in command && 'execute' in command) {
        client.commands.set(command.data.name, command);
    }
}

// Load event files
const eventsPath = path.join(__dirname, 'src', 'events');
const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

for (const file of eventFiles) {
    const filePath = path.join(eventsPath, file);
    const event = require(filePath);
    if (event.once) {
        client.once(event.name, (...args) => event.execute(...args, client));
    } else {
        client.on(event.name, (...args) => event.execute(...args, client));
    }
}

// Handle interactions (slash commands)
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    const command = client.commands.get(interaction.commandName);

    if (!command) return;

    try {
        await command.execute(interaction, client);
    } catch (error) {
        console.error(`Error executing ${interaction.commandName}:`, error);
        const reply = {
            content: '❌ Bu komutu çalıştırırken bir hata oluştu!',
            ephemeral: true
        };
        
        if (interaction.replied || interaction.deferred) {
            await interaction.followUp(reply);
        } else {
            await interaction.reply(reply);
        }
    }
});

// Bot ready event
client.once('ready', async () => {
    // Initialize databases
    initDb();
    initModerationDb();
    initOtorolDb();
    initBirthdaysDb();

    // Set bot presence
    client.user.setActivity('GAG | /help', { type: ActivityType.Playing });

    // Register slash commands
    const commands = [];
    for (const file of commandFiles) {
        const command = require(path.join(commandsPath, file));
        if ('data' in command) {
            commands.push(command.data.toJSON());
        }
    }

    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

    try {
        console.log(`Slash komutları kaydediliyor... (${commands.length} komut)`);
        await rest.put(
            Routes.applicationCommands(client.user.id),
            { body: commands }
        );
    } catch (error) {
        console.error('Komutlar kaydedilirken hata:', error);
    }

    // Stop loading animation
    animationRunning = false;
    
    console.log('\x1b[96mGAG BOT hazır ve komutlar senkronize edildi.\x1b[0m\n');
    console.log(`Logged in as ${client.user.tag}`);
});

// Login to Discord
const token = process.env.DISCORD_TOKEN;
if (!token) {
    console.error('❌ Discord token bulunamadı. Lütfen config/.env dosyasını kontrol edin.');
    process.exit(1);
}

client.login(token);

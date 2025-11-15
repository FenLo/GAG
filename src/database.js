const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

// Ensure database directory exists
const dbDir = path.join(__dirname, '..', 'config', 'database');
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

// Database paths
const PUBG_DB = path.join(dbDir, 'pubg_bot.db');
const MODERATION_DB = path.join(dbDir, 'moderation.db');
const OTOROL_DB = path.join(dbDir, 'otorol.db');
const BIRTHDAYS_DB = path.join(dbDir, 'birthdays.db');
const CRYPTO_DB = path.join(dbDir, 'crypto_channel.db');

// Initialize PUBG database
function initDb() {
    const db = new sqlite3.Database(PUBG_DB);
    db.run(`
        CREATE TABLE IF NOT EXISTS pubg_channels (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER
        )
    `);
    db.close();
}

// Save last match ID
function saveLastMatchId(matchId) {
    const filePath = path.join(__dirname, '..', 'config', 'last_match_id.json');
    fs.writeFileSync(filePath, JSON.stringify({ last_match_id: matchId }));
}

// Load last match ID
function loadLastMatchId() {
    const filePath = path.join(__dirname, '..', 'config', 'last_match_id.json');
    if (fs.existsSync(filePath)) {
        try {
            const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            return data.last_match_id || null;
        } catch (error) {
            return null;
        }
    }
    return null;
}

// Get PUBG channels
function getPubgChannels(callback) {
    const db = new sqlite3.Database(PUBG_DB);
    db.all('SELECT guild_id, channel_id FROM pubg_channels', [], (err, rows) => {
        if (err) {
            console.error('Error getting PUBG channels:', err);
            callback([]);
        } else {
            callback(rows);
        }
        db.close();
    });
}

// Set PUBG channel
function setPubgChannelDb(guildId, channelId) {
    const db = new sqlite3.Database(PUBG_DB);
    db.run('INSERT OR REPLACE INTO pubg_channels (guild_id, channel_id) VALUES (?, ?)', 
        [guildId, channelId]);
    db.close();
}

// Initialize moderation database
function initModerationDb() {
    const db = new sqlite3.Database(MODERATION_DB);
    db.run(`
        CREATE TABLE IF NOT EXISTS moderation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            guild_name TEXT,
            user_id INTEGER,
            user_name TEXT,
            moderator_id INTEGER,
            moderator_name TEXT,
            action TEXT,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
    db.close();
}

// Log moderation action
function logModerationAction(guildId, guildName, userId, userName, moderatorId, moderatorName, action, reason) {
    const db = new sqlite3.Database(MODERATION_DB);
    db.run(
        `INSERT INTO moderation_logs 
        (guild_id, guild_name, user_id, user_name, moderator_id, moderator_name, action, reason) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [guildId, guildName, userId, userName, moderatorId, moderatorName, action, reason]
    );
    db.close();
}

// Initialize otorol database
function initOtorolDb() {
    const db = new sqlite3.Database(OTOROL_DB);
    db.run(`
        CREATE TABLE IF NOT EXISTS autorole (
            guild_id INTEGER PRIMARY KEY,
            guild_name TEXT,
            user_role INTEGER,
            bot_role INTEGER
        )
    `);
    db.close();
}

// Set autorole
function setAutorole(guildId, guildName, userRole, botRole) {
    const db = new sqlite3.Database(OTOROL_DB);
    db.run(
        'INSERT OR REPLACE INTO autorole (guild_id, guild_name, user_role, bot_role) VALUES (?, ?, ?, ?)',
        [guildId, guildName, userRole, botRole]
    );
    db.close();
}

// Get autorole
function getAutorole(guildId, callback) {
    const db = new sqlite3.Database(OTOROL_DB);
    db.get('SELECT user_role, bot_role FROM autorole WHERE guild_id = ?', [guildId], (err, row) => {
        if (err) {
            console.error('Error getting autorole:', err);
            callback(null);
        } else {
            callback(row);
        }
        db.close();
    });
}

// Initialize birthdays database
function initBirthdaysDb() {
    const db = new sqlite3.Database(BIRTHDAYS_DB);
    db.run(`
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id INTEGER,
            user_name TEXT,
            guild_id INTEGER,
            month INTEGER,
            day INTEGER,
            PRIMARY KEY (user_id, guild_id)
        )
    `);
    db.run(`
        CREATE TABLE IF NOT EXISTS birthday_channels (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER
        )
    `);
    db.close();
}

// Set birthday
function setBirthday(userId, userName, guildId, month, day) {
    const db = new sqlite3.Database(BIRTHDAYS_DB);
    db.run(
        'INSERT OR REPLACE INTO birthdays (user_id, user_name, guild_id, month, day) VALUES (?, ?, ?, ?, ?)',
        [userId, userName, guildId, month, day]
    );
    db.close();
}

// Get birthdays for a guild
function getBirthdays(guildId, callback) {
    const db = new sqlite3.Database(BIRTHDAYS_DB);
    db.all('SELECT user_id, user_name, month, day FROM birthdays WHERE guild_id = ?', [guildId], (err, rows) => {
        if (err) {
            console.error('Error getting birthdays:', err);
            callback([]);
        } else {
            callback(rows);
        }
        db.close();
    });
}

// Get all birthdays
function getAllBirthdays(callback) {
    const db = new sqlite3.Database(BIRTHDAYS_DB);
    db.all('SELECT guild_id, user_id, user_name, month, day FROM birthdays', [], (err, rows) => {
        if (err) {
            console.error('Error getting all birthdays:', err);
            callback([]);
        } else {
            callback(rows);
        }
        db.close();
    });
}

// Set birthday channel
function setBirthdayChannel(guildId, channelId) {
    const db = new sqlite3.Database(BIRTHDAYS_DB);
    db.run('INSERT OR REPLACE INTO birthday_channels (guild_id, channel_id) VALUES (?, ?)', 
        [guildId, channelId]);
    db.close();
}

// Get birthday channel
function getBirthdayChannel(guildId, callback) {
    const db = new sqlite3.Database(BIRTHDAYS_DB);
    db.get('SELECT channel_id FROM birthday_channels WHERE guild_id = ?', [guildId], (err, row) => {
        if (err) {
            console.error('Error getting birthday channel:', err);
            callback(null);
        } else {
            callback(row ? row.channel_id : null);
        }
        db.close();
    });
}

module.exports = {
    initDb,
    saveLastMatchId,
    loadLastMatchId,
    getPubgChannels,
    setPubgChannelDb,
    initModerationDb,
    logModerationAction,
    initOtorolDb,
    setAutorole,
    getAutorole,
    initBirthdaysDb,
    setBirthday,
    getBirthdays,
    getAllBirthdays,
    setBirthdayChannel,
    getBirthdayChannel
};

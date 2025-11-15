import sqlite3
import json
import os

def init_db():
    conn = sqlite3.connect("config/database/pubg_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pubg_channels (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_last_match_id(match_id):
    with open("config/last_match_id.json", "w") as f:
        json.dump({"last_match_id": match_id}, f)

def load_last_match_id():
    if os.path.exists("config/last_match_id.json"):
        with open("config/last_match_id.json", "r") as f:
            try:
                data = json.load(f)
                return data.get("last_match_id")
            except json.JSONDecodeError:
                return None
    return None

def get_pubg_channels():
    conn = sqlite3.connect("config/database/pubg_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT guild_id, channel_id FROM pubg_channels")
    channels = cursor.fetchall()
    conn.close()
    return channels

def set_pubg_channel_db(guild_id, channel_id):
    conn = sqlite3.connect("config/database/pubg_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO pubg_channels (guild_id, channel_id)
        VALUES (?, ?)
    """, (guild_id, channel_id))
    conn.commit()
    conn.close()


def init_moderation_db():
    os.makedirs("config/database", exist_ok=True)
    conn = sqlite3.connect("config/database/moderation.db")
    cursor = conn.cursor()
    cursor.execute("""
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
    """)
    conn.commit()
    conn.close()

def log_moderation_action(guild_id, guild_name, user_id, user_name, moderator_id, moderator_name, action, reason):
    conn = sqlite3.connect("config/database/moderation.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO moderation_logs (
            guild_id, guild_name,
            user_id, user_name,
            moderator_id, moderator_name,
            action, reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        guild_id, guild_name,
        user_id, user_name,
        moderator_id, moderator_name,
        action, reason
    ))
    conn.commit()
    conn.close()

# Veritabanını başlat
def init_otorol_db():
    conn = sqlite3.connect("config/database/otorol.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autorole (
            guild_id INTEGER PRIMARY KEY,
            guild_name TEXT,
            user_role INTEGER,
            bot_role INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Rolleri kaydet
def set_autorole(guild_id, guild_name, user_role, bot_role):
    conn = sqlite3.connect("config/database/otorol.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO autorole (guild_id, guild_name, user_role, bot_role)
        VALUES (?, ?, ?, ?)
    """, (guild_id, guild_name, user_role, bot_role))
    conn.commit()
    conn.close()


# Kayıtlı rolleri al
def get_autorole(guild_id):
    conn = sqlite3.connect("config/database/otorol.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_role, bot_role FROM autorole WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()
    conn.close()
    return result


# Birthday Database Functions
def init_birthdays_db():
    os.makedirs("config/database", exist_ok=True)
    conn = sqlite3.connect("config/database/birthdays.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id INTEGER,
            user_name TEXT,
            guild_id INTEGER,
            month INTEGER,
            day INTEGER,
            PRIMARY KEY (user_id, guild_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthday_channels (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER
        )
    """)
    conn.commit()
    conn.close()


def set_birthday(user_id, user_name, guild_id, month, day):
    conn = sqlite3.connect("config/database/birthdays.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO birthdays (user_id, user_name, guild_id, month, day)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, user_name, guild_id, month, day))
    conn.commit()
    conn.close()


def get_birthdays(guild_id):
    conn = sqlite3.connect("config/database/birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, user_name, month, day FROM birthdays WHERE guild_id = ?", (guild_id,))
    birthdays = cursor.fetchall()
    conn.close()
    return birthdays


def get_all_birthdays():
    conn = sqlite3.connect("config/database/birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT guild_id, user_id, user_name, month, day FROM birthdays")
    birthdays = cursor.fetchall()
    conn.close()
    return birthdays


def set_birthday_channel(guild_id, channel_id):
    conn = sqlite3.connect("config/database/birthdays.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO birthday_channels (guild_id, channel_id)
        VALUES (?, ?)
    """, (guild_id, channel_id))
    conn.commit()
    conn.close()


def get_birthday_channel(guild_id):
    conn = sqlite3.connect("config/database/birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM birthday_channels WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
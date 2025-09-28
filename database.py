import sqlite3

def init_db():
    conn = sqlite3.connect('razlom_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_settings (
            guild_id TEXT PRIMARY KEY,
            channel_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_event_channel(guild_id):
    conn = sqlite3.connect('razlom_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT channel_id FROM event_settings WHERE guild_id = ?', (str(guild_id),))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None

def set_event_channel(guild_id, channel_id):
    conn = sqlite3.connect('razlom_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO event_settings 
        (guild_id, channel_id) 
        VALUES (?, ?)
    ''', (str(guild_id), str(channel_id)))
    
    conn.commit()
    conn.close()
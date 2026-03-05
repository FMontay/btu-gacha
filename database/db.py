import sqlite3


DB_PATH = "btu-gacha/btu_gacha.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS binder (
            user_id INTEGER,
            card_id TEXT,
            card_name TEXT,
            card_tier TEXT,
            card_description TEXT,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, card_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item_id TEXT,
            item_name TEXT,
            item_description TEXT,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, item_id)
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")
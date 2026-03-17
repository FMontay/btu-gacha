import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
DB_PATH = os.getenv("DB_PATH", "btu_gacha.db") 

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
        CREATE TABLE IF NOT EXISTS daily_pulls (
                   user_id INTEGER PRIMARY KEY,
                   pull_count INTEGER DEFAULT 0,
                   last_reset TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS converted_pulls (
                   user_id INTEGER,
                   pull_tier TEXT,
                   quantity INTEGER DEFAULT 1,
                   PRIMARY KEY (user_id, pull_tier)
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")
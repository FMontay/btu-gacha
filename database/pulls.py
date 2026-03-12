from database.db import get_connection
from datetime import datetime, timedelta
from gacha.pull import TIER_ORDER

def get_pull_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pull_count, last_reset FROM daily_pulls WHERE user_id = ?", (str(user_id),))

    row = cursor.fetchone()
    conn.close()
    return row #pull_count, last_reset, OR None


def update_pull_count(user_id, new_count, reset_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO daily_pulls (user_id, pull_count, last_reset)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id)
    DO UPDATE SET pull_count = ?, last_reset = ?               
""", (str(user_id), new_count, reset_time, new_count, reset_time))
    conn.commit()
    conn.close()


def add_converted_pull(user_id, tier, quantity=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO converted_pulls(user_id, pull_tier, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, pull_tier)
        DO UPDATE SET quantity = quantity + ?
    """, (str(user_id), tier, quantity, quantity))

    conn.commit()
    conn.close()


def check_free_pulls(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pull_tier, quantity FROM converted_pulls WHERE user_id = ?", (str(user_id),)) #order pulls by rarity in the python command itself with TIER ORDER

    rows = cursor.fetchall()
    conn.close()
    return rows


def use_free_pulls(user_id, tier, quantity=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM converted_pulls WHERE user_id = ? AND pull_tier = ?", (str(user_id), tier))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    if row[0] <= quantity:
        #Delete the row
        cursor.execute("DELETE FROM converted_pulls WHERE user_id = ? AND pull_tier = ?", (str(user_id), tier))
    
    else:
        cursor.execute("UPDATE converted_pulls SET quantity = quantity - ? WHERE user_id = ? AND pull_tier = ?", (quantity, str(user_id), tier))

    conn.commit()
    conn.close()
    return True

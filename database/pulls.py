from database.db import get_connection
from datetime import datetime, timedelta

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
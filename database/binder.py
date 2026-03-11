import sqlite3
from database.db import get_connection

# add card to database, either after pull or manual adding
def add_card(user_id, card_id, card_name, card_tier, card_description, amount=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO binder(user_id, card_id, card_name, card_tier, card_description, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, card_id)
        DO UPDATE SET quantity = quantity + ?
    """, (str(user_id), card_id, card_name, card_tier, card_description, amount, amount))

    conn.commit()
    conn.close()


# delete card from database
def remove_card(user_id, card_id, amount=1):
    conn = get_connection()
    cursor = conn.cursor()
    #check current quantity
    cursor.execute("SELECT quantity FROM binder WHERE user_id = ? AND card_id = ?", (str(user_id), card_id))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    if row[0] <= amount:
        #Delete the row
        cursor.execute("DELETE FROM binder WHERE user_id = ? AND card_id = ?", (str(user_id), card_id))
    
    else:
        cursor.execute("UPDATE binder SET quantity = quantity - ? WHERE user_id = ? AND card_id = ?", (amount, str(user_id), card_id))

    conn.commit()
    conn.close()
    return True


# select all the information in binder depending on user id, ordered by card tier
def get_user_binder(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT card_id, card_name, card_tier, quantity FROM binder WHERE user_id = ? ORDER BY card_tier", (str(user_id),))

    rows = cursor.fetchall()
    conn.close()
    return rows # list of (card_id, card_name, card_tier, quantity)


# entirely clear the binder
def clear_binder(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM binder WHERE user_id = ?", (str(user_id),))

    conn.commit()
    conn.close()


# select card info
def get_user_card(user_id, card_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT card_id, card_name, card_tier, card_description, quantity FROM binder WHERE user_id = ? AND card_id = ?", (str(user_id), card_id,))

    row = cursor.fetchone()
    conn.close()
    return row # list of (card_id, card_name, card_tier, description)
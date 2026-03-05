from database.db import get_connection

def get_user_binder(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item FROM inventory WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
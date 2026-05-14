# ==========================================
# database.py
# SQLite Database Management (Updated)
# ==========================================

import sqlite3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DATABASE_NAME = "messages.db"


# ==========================================
# Connection
# ==========================================

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# Init DB
# ==========================================

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT,
            sender_username TEXT,
            message_text TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# Save Message
# ==========================================

def save_message(sender_name, sender_username, message_text, timestamp):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (
            sender_name,
            sender_username,
            message_text,
            timestamp
        ) VALUES (?, ?, ?, ?)
    """, (sender_name, sender_username, message_text, timestamp))

    conn.commit()
    conn.close()


# ==========================================
# Get Recent Messages (by count)
# ==========================================

def get_recent_messages(limit=100):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ==========================================
# Get Messages by Hours (NEW)
# ==========================================

def get_messages_last_hours(hours: int):

    conn = get_connection()
    cursor = conn.cursor()

    cutoff = datetime.now() - timedelta(hours=hours)

    cursor.execute("""
        SELECT *
        FROM messages
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []

    for r in rows:
        try:
            msg_time = datetime.fromisoformat(r["timestamp"])

            if msg_time >= cutoff:
                result.append(dict(r))

        except Exception:
            continue

    return result


# ==========================================
# Cleanup Old Messages (optional)
# ==========================================

def delete_old_messages(limit=5000):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE id NOT IN (
            SELECT id FROM messages
            ORDER BY id DESC
            LIMIT ?
        )
    """, (limit,))

    conn.commit()
    conn.close()


# ==========================================
# Mentions
# ==========================================

def get_mentions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM messages
        WHERE message_text LIKE '%عبدالله%'
           OR message_text LIKE '%عبدالله الشرع%'
           OR message_text LIKE '%Abdullah%'
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

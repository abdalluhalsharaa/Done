# ==========================================
# database.py
# SQLite Database Management (Full Version)
# ==========================================

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DATABASE_NAME = "messages.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT,
            sender_username TEXT,
            message_text TEXT,
            timestamp TEXT
        )
    """)

    # Summaries table (for micro/daily summaries persistence)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized.")


def save_message(sender_name, sender_username, message_text, timestamp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (sender_name, sender_username, message_text, timestamp)
        VALUES (?, ?, ?, ?)
    """, (sender_name, sender_username, message_text, timestamp))
    conn.commit()
    conn.close()


def get_recent_messages(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]  # reverse order? keep as latest-first


def get_messages_since(cutoff_datetime: datetime):
    """
    Return all messages with timestamp >= cutoff_datetime (ISO compare works lexically if format consistent)
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Use direct string comparison because ISO format is lexicographically sortable
    cutoff_str = cutoff_datetime.isoformat()
    cursor.execute("""
        SELECT * FROM messages
        WHERE timestamp >= ?
        ORDER BY id ASC
    """, (cutoff_str,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_old_messages(keep_last=5000):
    """Delete messages beyond the most recent `keep_last`."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM messages
        WHERE id NOT IN (
            SELECT id FROM messages
            ORDER BY id DESC
            LIMIT ?
        )
    """, (keep_last,))
    conn.commit()
    conn.close()


def get_mentions(keywords):
    """Search for mentions of given keywords in message_text."""
    conn = get_connection()
    cursor = conn.cursor()
    # Build LIKE conditions
    conditions = " OR ".join(["message_text LIKE ?" for _ in keywords])
    params = [f"%{kw}%" for kw in keywords]
    cursor.execute(f"""
        SELECT * FROM messages
        WHERE {conditions}
        ORDER BY id DESC
        LIMIT 50
    """, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_summary(summary_text: str):
    """Store a generated summary for future reference (optional)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO summaries (summary_text) VALUES (?)
    """, (summary_text,))
    conn.commit()
    conn.close()


def get_recent_summaries(limit=20):
    """Retrieve most recent stored summaries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM summaries
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

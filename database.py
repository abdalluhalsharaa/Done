# ==========================================
# database.py
# SQLite Database Management
# ==========================================

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DATABASE_NAME = "messages.db"


# ==========================================
# Database Connection
# ==========================================

def get_connection():

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# Initialize Database
# ==========================================

def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # ======================================
    # Messages Table
    # ======================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_name TEXT,

            sender_username TEXT,

            message_text TEXT,

            timestamp TEXT
        )
        """
    )

    # ======================================
    # Micro Summaries Table
    # ======================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            summary_text TEXT,

            created_at TEXT
        )
        """
    )

    connection.commit()

    connection.close()

    logger.info("Database initialized successfully")


# ==========================================
# Save Message
# ==========================================

def save_message(
    sender_name,
    sender_username,
    message_text,
    timestamp
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages (
            sender_name,
            sender_username,
            message_text,
            timestamp
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            sender_name,
            sender_username,
            message_text,
            timestamp
        )
    )

    connection.commit()

    connection.close()


# ==========================================
# Save Summary
# ==========================================

def save_summary(summary_text):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO summaries (
            summary_text,
            created_at
        )
        VALUES (?, ?)
        """,
        (
            summary_text,
            str(datetime.now())
        )
    )

    connection.commit()

    connection.close()

    logger.info("Micro-summary saved")


# ==========================================
# Get Recent Messages
# ==========================================

def get_recent_messages(limit=100):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM messages
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==========================================
# Get Recent Summaries
# ==========================================

def get_recent_summaries(limit=20):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM summaries
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==========================================
# Get Mentions
# ==========================================

def get_mentions():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM messages
        WHERE
            message_text LIKE '%عبدالله%'
            OR message_text LIKE '%عبدالله الشرع%'
            OR message_text LIKE '%Abdullah%'
        ORDER BY id DESC
        LIMIT 50
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==========================================
# Search Messages
# ==========================================

def search_messages(keyword):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM messages
        WHERE message_text LIKE ?
        ORDER BY id DESC
        LIMIT 50
        """,
        (f"%{keyword}%",)
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==========================================
# Delete Old Messages
# ==========================================

def delete_old_messages(limit=5000):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM messages
        WHERE id NOT IN (
            SELECT id
            FROM messages
            ORDER BY id DESC
            LIMIT ?
        )
        """,
        (limit,)
    )

    connection.commit()

    connection.close()

    logger.info("Old messages cleaned")

"""
Database Layer
===============
Handles all SQLite access for the surveillance system: creating the
table, saving new motion events, and reading them back for the
dashboard and history page.

This is the same "detections" table the project already used - it has
just been extended with an event_type and alarm_status column so each
row can describe a full event, not just a timestamp and an image.

Functions here do not catch database errors themselves; if something
goes wrong (e.g. a locked or missing database file) the exception is
raised up to the caller (app.py or surveillance.py), which is
responsible for showing a useful error instead of crashing the app.
"""

import sqlite3
from datetime import datetime

import config


def get_db_connection():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create the detections table if it does not exist, and upgrade older databases."""
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TEXT NOT NULL,
            event_type TEXT DEFAULT 'Motion Detected',
            image TEXT,
            alarm_status TEXT DEFAULT 'Activated'
        )
    """)

    # Add columns for anyone upgrading from the older, simpler table.
    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(detections)").fetchall()
    ]

    if "event_type" not in columns:
        conn.execute(
            "ALTER TABLE detections ADD COLUMN event_type TEXT DEFAULT 'Motion Detected'"
        )

    if "alarm_status" not in columns:
        conn.execute(
            "ALTER TABLE detections ADD COLUMN alarm_status TEXT DEFAULT 'Activated'"
        )

    conn.commit()
    conn.close()


def save_event(image_filename, alarm_status="Activated", event_type="Motion Detected"):
    """
    Save a new surveillance event. The event ID is generated automatically
    by SQLite (AUTOINCREMENT) - it is never set manually.
    """
    detected_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    conn = get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO detections (detected_at, event_type, image, alarm_status)
        VALUES (?, ?, ?, ?)
        """,
        (detected_time, event_type, image_filename, alarm_status)
    )

    conn.commit()
    event_id = cursor.lastrowid
    conn.close()

    return {"id": event_id, "detected_at": detected_time}


def get_all_events():
    """Return every event, most recent first."""
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT id, detected_at, event_type, image, alarm_status
        FROM detections
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_latest_event():
    """Return the single most recent event, or None if there are no events yet."""
    conn = get_db_connection()

    row = conn.execute("""
        SELECT id, detected_at, event_type, image, alarm_status
        FROM detections
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    return dict(row) if row else None


def get_event_count():
    """Return the total number of recorded events."""
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
    conn.close()
    return count


def get_today_event_count():
    """Return how many events were recorded today."""
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM detections WHERE detected_at LIKE ?",
        (f"{today}%",)
    ).fetchone()[0]
    conn.close()

    return count

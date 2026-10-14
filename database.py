import sqlite3
from datetime import datetime

import config


def get_db_connection():
    connection = sqlite3.connect(config.DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create or upgrade the existing table without deleting records."""
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TEXT NOT NULL,
            event_type TEXT DEFAULT 'Motion Detected',
            image TEXT,
            alarm_status TEXT DEFAULT 'Activated'
        )
    """)

    columns = [
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(detections)"
        ).fetchall()
    ]

    if "event_type" not in columns:
        connection.execute(
            "ALTER TABLE detections "
            "ADD COLUMN event_type TEXT DEFAULT 'Motion Detected'"
        )

    if "alarm_status" not in columns:
        connection.execute(
            "ALTER TABLE detections "
            "ADD COLUMN alarm_status TEXT DEFAULT 'Activated'"
        )

    connection.commit()
    connection.close()


def save_event(
    image_filename,
    alarm_status="Activated",
    event_type="Motion Detected",
):
    detected_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO detections (
            detected_at,
            event_type,
            image,
            alarm_status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            detected_time,
            event_type,
            image_filename,
            alarm_status,
        ),
    )

    connection.commit()
    event_id = cursor.lastrowid
    connection.close()

    return {
        "id": event_id,
        "detected_at": detected_time,
    }


def get_all_events():
    connection = get_db_connection()

    rows = connection.execute("""
        SELECT id, detected_at, event_type, image, alarm_status
        FROM detections
        ORDER BY id DESC
    """).fetchall()

    connection.close()
    return [dict(row) for row in rows]


def get_latest_event():
    connection = get_db_connection()

    row = connection.execute("""
        SELECT id, detected_at, event_type, image, alarm_status
        FROM detections
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    connection.close()
    return dict(row) if row else None


def get_event_count():
    connection = get_db_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM detections"
    ).fetchone()[0]

    connection.close()
    return count


def get_today_event_count():
    today = datetime.now().strftime("%Y-%m-%d")
    connection = get_db_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM detections WHERE detected_at LIKE ?",
        (f"{today}%",),
    ).fetchone()[0]

    connection.close()
    return count
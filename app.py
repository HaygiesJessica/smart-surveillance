from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime
from PIL import Image, ImageDraw
import os


# =========================
# FLASK APPLICATION
# =========================

app = Flask(__name__)


# =========================
# CONFIGURATION
# =========================

DATABASE = "surveillance.db"
CAPTURE_FOLDER = "static/captures"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================
# INITIALIZE DATABASE
# =========================

def initialize_database():

    conn = get_db_connection()

    # Create the table if it does not exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TEXT NOT NULL,
            image TEXT
        )
    """)

    # Check existing columns
    columns = conn.execute(
        "PRAGMA table_info(detections)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    # Add image column if using an older database
    if "image" not in column_names:

        conn.execute(
            "ALTER TABLE detections ADD COLUMN image TEXT"
        )

    conn.commit()

    conn.close()


# =========================
# CREATE SIMULATED CAPTURE
# =========================

def create_simulated_capture():

    # Create captures folder if needed
    os.makedirs(
        CAPTURE_FOLDER,
        exist_ok=True
    )

    # Get current time
    now = datetime.now()

    # Create unique filename
    filename = now.strftime(
        "capture_%Y%m%d_%H%M%S.jpg"
    )

    filepath = os.path.join(
        CAPTURE_FOLDER,
        filename
    )

    # Create simulated surveillance image
    image = Image.new(
        "RGB",
        (800, 450),
        (20, 25, 30)
    )

    draw = ImageDraw.Draw(image)

    # Add text to the simulated image
    draw.text(
        (30, 30),
        "SMART SURVEILLANCE SYSTEM",
        fill="white"
    )

    draw.text(
        (30, 70),
        "MOTION DETECTED",
        fill=(255, 80, 80)
    )

    draw.text(
        (30, 110),
        now.strftime(
            "%Y-%m-%d %I:%M:%S %p"
        ),
        fill="white"
    )

    draw.text(
        (30, 400),
        "CAMERA 01 | SIMULATED CAPTURE",
        fill=(150, 160, 170)
    )

    # Save the image
    image.save(filepath)

    return filename


# =========================
# PAGES
# =========================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )


@app.route("/history")
def history():

    return render_template(
        "history.html"
    )


# =========================
# API - SYSTEM STATUS
# =========================

@app.route("/api/status")
def get_status():

    conn = get_db_connection()

    # Count detections
    count = conn.execute(
        "SELECT COUNT(*) FROM detections"
    ).fetchone()[0]

    # Get latest detection
    latest = conn.execute(
        """
        SELECT detected_at, image
        FROM detections
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    last_detection = None
    latest_image = None

    if latest:

        last_detection = latest[
            "detected_at"
        ]

        latest_image = latest[
            "image"
        ]

    return jsonify({

        "system_status": "Monitoring",

        "motion_count": count,

        "last_detection": last_detection,

        "latest_image": latest_image,

        "alarm": "Inactive"

    })


# =========================
# API - SIMULATE DETECTION
# =========================

@app.route(
    "/api/detection",
    methods=["POST"]
)
def simulate_detection():

    # Get current detection time
    detected_time = datetime.now().strftime(
        "%Y-%m-%d %I:%M:%S %p"
    )

    # Create simulated camera image
    image_filename = (
        create_simulated_capture()
    )

    # Save detection in database
    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO detections
        (detected_at, image)

        VALUES (?, ?)
        """,
        (
            detected_time,
            image_filename
        )
    )

    conn.commit()

    conn.close()

    return jsonify({

        "success": True,

        "message": "Motion detected!",

        "detected_at": detected_time,

        "image": image_filename

    })


# =========================
# API - GET ALL DETECTIONS
# =========================

@app.route("/api/detections")
def get_detections():

    conn = get_db_connection()

    # Get all detections
    detections = conn.execute(
        """
        SELECT
            id,
            detected_at,
            image

        FROM detections

        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    detection_list = []

    for detection in detections:

        detection_list.append({

            "id": detection["id"],

            "detected_at":
                detection["detected_at"],

            "image":
                detection["image"]

        })

    return jsonify(
        detection_list
    )


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    # Initialize database
    initialize_database()

    # Start Flask
    app.run(
        debug=True
    )
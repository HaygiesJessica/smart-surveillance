"""
Flask Application
===================
This file only handles web routes: the two pages (dashboard, history)
and the JSON API endpoints the dashboard/history pages poll with
JavaScript. All of the actual surveillance logic lives in:

    config.py       - settings (simulation mode, timing, file paths)
    database.py     - saving/reading events from SQLite
    hardware.py     - simulated LED + buzzer (future: real GPIO)
    simulation.py   - simulated PIR sensor + camera
    surveillance.py - the MOTION -> CAPTURE -> ALARM -> SAVE state machine
"""

from flask import Flask, render_template, jsonify

import config
import database
from surveillance import surveillance_system

app = Flask(__name__)


# =========================
# PAGES
# =========================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/history")
def history():
    return render_template("history.html")


# =========================
# API - CURRENT SYSTEM STATE
# =========================

@app.route("/api/status")
def get_status():
    """Used by the dashboard to poll the live state of the simulation."""
    return jsonify(surveillance_system.get_status())


# =========================
# API - SIMULATE MOTION (the "PIR sensor" button)
# =========================

@app.route("/api/simulate-motion", methods=["POST"])
def simulate_motion_route():
    try:
        result = surveillance_system.trigger_motion()
        status_code = 200 if result["success"] else 409  # 409 = busy, ignored
        return jsonify(result), status_code

    except Exception as error:
        return jsonify({
            "success": False,
            "message": f"Could not start simulation: {error}",
        }), 500


# =========================
# API - EVENT HISTORY
# =========================

@app.route("/api/detections")
def get_detections():
    try:
        return jsonify(database.get_all_events())

    except Exception as error:
        return jsonify({"error": f"Could not load detection history: {error}"}), 500


@app.route("/api/stats")
def get_stats():
    """Summary numbers used at the top of the History page."""
    try:
        return jsonify({
            "total_events": database.get_event_count(),
            "today_events": database.get_today_event_count(),
            "latest_event": database.get_latest_event(),
        })

    except Exception as error:
        return jsonify({"error": f"Could not load statistics: {error}"}), 500


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":
    try:
        database.initialize_database()
    except Exception as error:
        # If the database can't even be created, fail loudly and clearly
        # instead of letting Flask start in a broken state.
        raise SystemExit(f"Could not initialize the database: {error}")

    print(f"Starting Smart Home Surveillance System (SIMULATION_MODE={config.SIMULATION_MODE})")
    app.run(debug=True)

from flask import Flask, render_template, jsonify
import threading
import time
from datetime import date
from pathlib import Path

import config
import database
import hardware
import simulation
from surveillance import surveillance_system

app = Flask(__name__)


@app.context_processor
def frontend_context():
    """Read-only presentation settings and versioned static assets."""
    def asset_version(filename):
        return (Path(app.static_folder) / filename).stat().st_mtime_ns

    return {
        "asset_version": asset_version,
        "runtime_settings": {
            "alarm_duration": config.ALARM_DURATION,
            "pir_pin": config.PIR_PIN,
            "led_pin": config.LED_PIN,
            "buzzer_pin": config.BUZZER_PIN,
        },
    }


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/api/status")
def get_status():
    return jsonify(surveillance_system.get_status())


@app.route("/api/simulate-motion", methods=["POST"])
def simulate_motion_route():
    if not config.SIMULATION_MODE:
        return jsonify({
            "success": False,
            "message": (
                "Manual simulation is unavailable in hardware mode. "
                "Motion is triggered by the PIR sensor."
            ),
        }), 403

    print("\n" + "=" * 60, flush=True)
    print("[APP] POST REQUEST RECEIVED AT /api/simulate-motion !!!", flush=True)
    print("=" * 60 + "\n", flush=True)

    try:
        print(
            "[APP] Calling surveillance_system.trigger_motion()...",
            flush=True,
        )
        result = surveillance_system.trigger_motion()
        print(f"[APP] Result from trigger_motion: {result}", flush=True)
        status_code = 200 if result["success"] else 409
        return jsonify(result), status_code
    except Exception as error:
        print(f"[APP] EXCEPTION CAUGHT: {error}", flush=True)
        return jsonify({
            "success": False,
            "message": f"Could not start simulation: {error}",
        }), 500


@app.route("/api/detections")
def get_detections():
    try:
        return jsonify(database.get_all_events())
    except Exception as error:
        return jsonify({
            "error": f"Could not load detection history: {error}",
        }), 500


@app.route("/api/stats")
def get_stats():
    try:
        return jsonify({
            "server_date": date.today().isoformat(),
            "total_events": database.get_event_count(),
            "today_events": database.get_today_event_count(),
            "latest_event": database.get_latest_event(),
        })
    except Exception as error:
        return jsonify({
            "error": f"Could not load statistics: {error}",
        }), 500


def hardware_monitor_thread():
    """Monitor the physical PIR sensor and trigger the detection sequence."""
    if config.SIMULATION_MODE:
        return

    print("Hardware Monitor: System Ready. Waiting for motion...")

    try:
        while True:
            if simulation.check_pir_sensor():
                print("Hardware Monitor: MOTION DETECTED!")
                surveillance_system.trigger_motion()

                total_sequence_time = (
                    config.MOTION_DELAY
                    + config.CAPTURE_DELAY
                    + config.ALARM_DURATION
                    + config.SAVED_DISPLAY_TIME
                )
                time.sleep(total_sequence_time + 0.5)

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Hardware Monitor: Stopping...")
    finally:
        hardware.cleanup_hardware()


if __name__ == "__main__":
    if not config.SIMULATION_MODE and not (
        hardware.HARDWARE_AVAILABLE and simulation.HARDWARE_AVAILABLE
    ):
        raise SystemExit(
            "GPIO is unavailable. Start this application on the Raspberry Pi "
            "with RPi.GPIO installed and GPIO access enabled."
        )

    try:
        database.initialize_database()
    except Exception as error:
        raise SystemExit(f"Could not initialize the database: {error}")

    if not config.SIMULATION_MODE:
        monitor_thread = threading.Thread(
            target=hardware_monitor_thread,
            daemon=True,
        )
        monitor_thread.start()

    print(
        "Starting Smart Home Surveillance System "
        f"(SIMULATION_MODE={config.SIMULATION_MODE})"
    )

    try:
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False,
        )
    finally:
        hardware.cleanup_hardware()
from flask import Flask, render_template, jsonify
import threading
import time

import config
import database
import simulation
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
# API ENDPOINTS
# =========================

@app.route("/api/status")
def get_status():
    return jsonify(surveillance_system.get_status())


@app.route("/api/simulate-motion", methods=["POST"])
def simulate_motion_route():
    print("\n" + "="*60, flush=True)
    print("[APP] POST REQUEST RECEIVED AT /api/simulate-motion !!!", flush=True)
    print("="*60 + "\n", flush=True)
    try:
        print("[APP] Calling surveillance_system.trigger_motion()...", flush=True)
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
        return jsonify({"error": f"Could not load detection history: {error}"}), 500


@app.route("/api/stats")
def get_stats():
    try:
        return jsonify({
            "total_events": database.get_event_count(),
            "today_events": database.get_today_event_count(),
            "latest_event": database.get_latest_event(),
        })
    except Exception as error:
        return jsonify({"error": f"Could not load statistics: {error}"}), 500


# =========================
# HARDWARE MONITOR THREAD
# =========================

def hardware_monitor_thread():
    """
    Background thread that monitors the PIR sensor when running on real hardware.
    This replaces the `while True` loop from your original script.py, integrating
    it seamlessly with the Flask app's state machine and database.
    """
    if config.SIMULATION_MODE:
        return
    
    print("Hardware Monitor: System Ready. Waiting for motion...")
    try:
        while True:
            if simulation.check_pir_sensor():
                print("Hardware Monitor: MOTION DETECTED!")
                # Trigger the full surveillance sequence (capture, alarm, save)
                surveillance_system.trigger_motion()
                
                # Wait for the sequence to finish before checking again to prevent 
                # overlapping triggers. Matches the timing in surveillance.py.
                total_sequence_time = (config.MOTION_DELAY + config.CAPTURE_DELAY + 
                                       config.ALARM_DURATION + config.SAVED_DISPLAY_TIME)
                time.sleep(total_sequence_time + 0.5) 
            
            time.sleep(0.1) # Prevent CPU overload, matching your original script
    except KeyboardInterrupt:
        print("Hardware Monitor: Stopping...")
    finally:
        import hardware
        hardware.cleanup_hardware()


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":
    try:
        database.initialize_database()
    except Exception as error:
        raise SystemExit(f"Could not initialize the database: {error}")

    if not config.SIMULATION_MODE:
        monitor_thread = threading.Thread(target=hardware_monitor_thread, daemon=True)
        monitor_thread.start()

    print(f"Starting Smart Home Surveillance System (SIMULATION_MODE={config.SIMULATION_MODE})")
    
    # DAGDAGAN NG use_reloader=False
    app.run(debug=True, use_reloader=False) 
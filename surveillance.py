"""
Surveillance Process
=====================
This is the heart of the system. It manages the state machine described
in the project plan:

    MONITORING -> MOTION DETECTED -> CAPTURING -> ALARM ACTIVE
    -> EVENT SAVED -> back to MONITORING

The alarm needs to stay on for a few seconds, and the sequence should
not freeze the rest of the Flask app while that happens. To keep that
simple, the whole sequence runs on a background thread (Python's
built-in `threading` module) instead of blocking the web request. A
lock/flag (`_busy`) makes sure a second "Simulate Motion" click cannot
start a new event while one is already running.
"""

import threading
import time

import config
import database
import hardware
import simulation

STATE_MONITORING = "MONITORING"
STATE_MOTION_DETECTED = "MOTION DETECTED"
STATE_CAPTURING = "CAPTURING"
STATE_ALARM_ACTIVE = "ALARM ACTIVE"
STATE_EVENT_SAVED = "EVENT SAVED"


class SurveillanceSystem:
    """Holds the current state of the (simulated) surveillance system."""

    def __init__(self):
        self.state = STATE_MONITORING
        self.motion_sensor = "No Motion"
        self.camera_status = "Ready"
        self.last_detection = None
        self.latest_image = None
        self.last_error = None

        # True while a detection sequence is running. Used to ignore
        # extra "Simulate Motion" clicks until the current one finishes.
        self._busy = False

    def get_status(self):
        """A snapshot of the current system state, used by the dashboard."""
        return {
            "state": self.state,
            "motion_sensor": self.motion_sensor,
            "camera_status": self.camera_status,
            "led": hardware.led_is_on(),
            "buzzer": hardware.buzzer_is_on(),
            "last_detection": self.last_detection,
            "latest_image": self.latest_image,
            "busy": self._busy,
            "error": self.last_error,
            "simulation_mode": config.SIMULATION_MODE,
        }

    def trigger_motion(self):
        """
        Called when the user presses "Simulate Motion" (this stands in
        for the PIR sensor firing). Starts the detection sequence on a
        background thread so the Flask server keeps responding to other
        requests (like the dashboard polling /api/status) while it runs.
        """
        if self._busy:
            return {
                "success": False,
                "message": "System is already processing an event. Please wait.",
            }

        self._busy = True
        self.last_error = None

        thread = threading.Thread(target=self._run_detection_sequence, daemon=True)
        thread.start()

        return {"success": True, "message": "Motion detected! Processing event..."}

    def _run_detection_sequence(self):
        """Runs the full MOTION -> CAPTURE -> ALARM -> SAVE -> MONITORING flow."""
        try:
            # --- 1. MOTION DETECTED ---
            simulation.simulate_motion()
            self.state = STATE_MOTION_DETECTED
            self.motion_sensor = "Motion Detected"
            time.sleep(config.MOTION_DELAY)

            # --- 2. CAPTURING ---
            self.state = STATE_CAPTURING
            self.camera_status = "Capturing..."
            time.sleep(config.CAPTURE_DELAY)

            image_filename = simulation.simulate_camera_capture()
            self.latest_image = image_filename
            self.camera_status = "Ready"

            # --- 3. ALARM ACTIVE (LED + buzzer on for a few seconds) ---
            self.state = STATE_ALARM_ACTIVE
            hardware.activate_alarm()
            time.sleep(config.ALARM_DURATION)

            hardware.deactivate_alarm()

            # --- 4. EVENT SAVED (written to the database) ---
            self.state = STATE_EVENT_SAVED
            saved = database.save_event(
                image_filename=image_filename,
                alarm_status="Activated",
                event_type="Motion Detected",
            )
            self.last_detection = saved["detected_at"]
            time.sleep(config.SAVED_DISPLAY_TIME)

        except Exception as error:
            # Camera, database, or file-system problem. Do not crash the
            # app - record the error, make sure the alarm is off, and
            # fall back to Monitoring.
            self.last_error = f"Simulation error: {error}"
            hardware.deactivate_alarm()

        finally:
            # --- 5. BACK TO MONITORING ---
            self.state = STATE_MONITORING
            self.motion_sensor = "No Motion"
            self.camera_status = "Ready"
            self._busy = False


# A single shared instance used by the whole Flask app.
surveillance_system = SurveillanceSystem()

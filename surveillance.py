import threading
import time
import sys

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
    def __init__(self):
        self.state = STATE_MONITORING
        self.motion_sensor = "No Motion"
        self.camera_status = "Ready"
        self.last_detection = None
        self.latest_image = None
        self.last_error = None
        self._busy = False

    def get_status(self):
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
        print("[SURVEILLANCE] Button clicked! Starting sequence...", flush=True)
        if self._busy:
            print("[SURVEILLANCE] Already busy!", flush=True)
            return {"success": False, "message": "System is busy."}

        self._busy = True
        self.last_error = None
        thread = threading.Thread(target=self._run_detection_sequence, daemon=True)
        thread.start()
        return {"success": True, "message": "Processing..."}

    def _run_detection_sequence(self):
        print("[SURVEILLANCE] === SEQUENCE STARTED ===", flush=True)
        try:
            # Step 1
            print("[SURVEILLANCE] Step 1: Motion", flush=True)
            simulation.simulate_motion()
            self.state = STATE_MOTION_DETECTED
            self.motion_sensor = "Motion Detected"
            time.sleep(config.MOTION_DELAY)

            # Step 2
            print("[SURVEILLANCE] Step 2: Capturing...", flush=True)
            self.state = STATE_CAPTURING
            self.camera_status = "Capturing..."
            time.sleep(config.CAPTURE_DELAY)

           # Step 3 - CAMERA
            print("[SURVEILLANCE] Step 3: Calling camera NOW", flush=True)
            image_filename = simulation.simulate_camera_capture()
            print(f"[SURVEILLANCE] Camera saved: {image_filename}", flush=True)

            # DAPAT NANDITO ITO:
            self.latest_image = image_filename  # <--- Siguraduhing nandito ito!
            self.camera_status = "Ready"

            # Step 4
            print("[SURVEILLANCE] Step 4: Alarm", flush=True)
            self.state = STATE_ALARM_ACTIVE
            hardware.activate_alarm()
            time.sleep(config.ALARM_DURATION)
            hardware.deactivate_alarm()

            # Step 5
            print("[SURVEILLANCE] Step 5: Saving to DB", flush=True)
            self.state = STATE_EVENT_SAVED
            database.save_event(
                image_filename=image_filename,
                alarm_status="Activated",
                event_type="Motion Detected",
            )
            time.sleep(config.SAVED_DISPLAY_TIME)
            
            print("[SURVEILLANCE] === SEQUENCE COMPLETE ===", flush=True)

        except Exception as error:
            print(f"[SURVEILLANCE] ERROR: {error}", flush=True)
            self.last_error = str(error)
            hardware.deactivate_alarm()

        finally:
            self.state = STATE_MONITORING
            self.motion_sensor = "No Motion"
            self.camera_status = "Ready"
            self._busy = False

surveillance_system = SurveillanceSystem()
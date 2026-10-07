# Set to False when running on a Raspberry Pi with real hardware connected
SIMULATION_MODE = False 

DATABASE = "surveillance.db"
CAPTURE_FOLDER = "static/captures"

# GPIO Pin Configuration (BCM numbering, matching your script.py)
PIR_PIN = 4
LED_PIN = 17
BUZZER_PIN = 27

# Timing for the detection sequence (in seconds)
MOTION_DELAY = 1.0        # PIR sensor "sees" motion
CAPTURE_DELAY = 1.0       # Camera pretends to take a photo
ALARM_DURATION = 3.0      # LED + buzzer stay on
SAVED_DISPLAY_TIME = 1.0  # "Event Saved" is shown before returning to Monitoring
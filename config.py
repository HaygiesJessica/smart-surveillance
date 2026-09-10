"""
Configuration
=============
Central place for settings that are likely to change later, especially
the switch from software simulation to real Raspberry Pi hardware.

SIMULATION_MODE = True   -> the PIR sensor, camera, LED and buzzer are
                            all simulated in software (current mode).
                            This is what lets the project run on a
                            normal Windows computer with no hardware.

SIMULATION_MODE = False  -> reserved for later, once the Raspberry Pi 3,
                            PIR sensor, camera, LED and buzzer are wired
                            up. hardware.py and simulation.py would then
                            need real GPIO / camera code added to them.
"""

SIMULATION_MODE = True

# Database file and folder for simulated camera captures
DATABASE = "surveillance.db"
CAPTURE_FOLDER = "static/captures"

# Timing for the simulated detection sequence (in seconds).
# These control how long each state is visible on the dashboard.
MOTION_DELAY = 1.0        # PIR sensor "sees" motion
CAPTURE_DELAY = 1.0       # Camera pretends to take a photo
ALARM_DURATION = 3.0      # LED + buzzer stay on (requirement: ~3 seconds)
SAVED_DISPLAY_TIME = 1.0  # "Event Saved" is shown before returning to Monitoring

"""
Simulated Sensors
==================
This module represents the physical INPUT devices of the surveillance
system: the PIR motion sensor and the camera.

There is no Raspberry Pi connected yet, so these functions simulate what
the real sensors will eventually do:

    simulate_motion()          will later become   read_pir_sensor()
    simulate_camera_capture()  will later become   capture_real_image()

Keeping these functions separate (instead of mixed into app.py) means
that swapping in real hardware later is just a matter of rewriting the
inside of these two functions.
"""

import os
from datetime import datetime

from PIL import Image, ImageDraw

import config


def simulate_motion():
    """
    Pretend the PIR sensor detected movement.

    FUTURE (Raspberry Pi):

        def read_pir_sensor():
            return GPIO.input(PIR_PIN) == GPIO.HIGH

    In simulation mode this always returns True, because it is only
    called after the user presses the "Simulate Motion" button - that
    button press IS the simulated motion event.
    """
    return True


def _next_capture_number():
    """
    Look inside the captures folder and work out the next sequential
    number to use, so files are named capture_001.jpg, capture_002.jpg,
    and so on without ever overwriting an existing capture.
    """
    os.makedirs(config.CAPTURE_FOLDER, exist_ok=True)

    existing_numbers = []

    for name in os.listdir(config.CAPTURE_FOLDER):
        if name.startswith("capture_") and name.endswith(".jpg"):
            digits = name[len("capture_"):-len(".jpg")]

            if digits.isdigit():
                existing_numbers.append(int(digits))

    return max(existing_numbers, default=0) + 1


def simulate_camera_capture():
    """
    Simulate the camera taking a photo when motion is detected.

    Creates a placeholder image (with a timestamp printed on it) and
    saves it with a sequential filename, e.g. capture_001.jpg.

    FUTURE (Raspberry Pi):

        def capture_real_image():
            camera = PiCamera()
            camera.capture(filepath)
            return filename

    Raises an exception on failure so the caller (surveillance.py) can
    catch it and show a useful error instead of crashing the app.
    """
    os.makedirs(config.CAPTURE_FOLDER, exist_ok=True)

    number = _next_capture_number()
    filename = f"capture_{number:03d}.jpg"
    filepath = os.path.join(config.CAPTURE_FOLDER, filename)

    now = datetime.now()

    # Build a simple placeholder "photo" so the dashboard has something
    # realistic to display in place of a real camera frame.
    image = Image.new("RGB", (800, 450), (20, 25, 30))
    draw = ImageDraw.Draw(image)

    draw.text((30, 30), "SMART SURVEILLANCE SYSTEM", fill="white")
    draw.text((30, 70), "MOTION DETECTED", fill=(255, 80, 80))
    draw.text((30, 110), now.strftime("%Y-%m-%d %I:%M:%S %p"), fill="white")
    draw.text((30, 400), "CAMERA 01 | SIMULATED CAPTURE", fill=(150, 160, 170))

    image.save(filepath)

    return filename

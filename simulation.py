"""
Simulated Sensors - DEBUG VERSION WITH FLUSH
"""

import os
import sys
from datetime import datetime

from PIL import Image, ImageDraw
import cv2

import config

print(f"[DEBUG] simulation.py loaded. SIMULATION_MODE = {config.SIMULATION_MODE}", flush=True)

# Try to import RPi.GPIO for real hardware PIR reading
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIR_PIN, GPIO.IN)
    HARDWARE_AVAILABLE = True
    print("[DEBUG] RPi.GPIO loaded successfully", flush=True)
except (ImportError, RuntimeError) as e:
    HARDWARE_AVAILABLE = False
    print(f"[DEBUG] RPi.GPIO not available: {e}", flush=True)


def check_pir_sensor():
    if not config.SIMULATION_MODE and HARDWARE_AVAILABLE:
        result = GPIO.input(config.PIR_PIN) == GPIO.HIGH
        print(f"[DEBUG] PIR sensor reading: {result}", flush=True)
        return result
    return False


def simulate_motion():
    return True


def _next_capture_number():
    os.makedirs(config.CAPTURE_FOLDER, exist_ok=True)
    existing_numbers = []
    for name in os.listdir(config.CAPTURE_FOLDER):
        if name.startswith("capture_") and name.endswith(".jpg"):
            digits = name[len("capture_"):-len(".jpg")]
            if digits.isdigit():
                existing_numbers.append(int(digits))
    next_num = max(existing_numbers, default=0) + 1
    print(f"[DEBUG] Next capture number: {next_num}", flush=True)
    return next_num


def _save_placeholder_image(filepath, now):
    print(f"[DEBUG] _save_placeholder_image() called for {filepath}", flush=True)
    image = Image.new("RGB", (800, 450), (20, 25, 30))
    draw = ImageDraw.Draw(image)
    draw.text((30, 30), "SMART SURVEILLANCE SYSTEM", fill="white")
    draw.text((30, 70), "MOTION DETECTED", fill=(255, 80, 80))
    draw.text((30, 110), now.strftime("%Y-%m-%d %I:%M:%S %p"), fill="white")
    draw.text((30, 400), "CAMERA 01 | SIMULATED CAPTURE", fill=(150, 160, 170))
    image.save(filepath)
    print(f"[DEBUG] Placeholder image saved", flush=True)


def simulate_camera_capture():
    print("[DEBUG] ============================================", flush=True)
    print("[DEBUG] simulate_camera_capture() STARTED", flush=True)
    print(f"[DEBUG] SIMULATION_MODE = {config.SIMULATION_MODE}", flush=True)
    print("[DEBUG] ============================================", flush=True)
    
    os.makedirs(config.CAPTURE_FOLDER, exist_ok=True)
    number = _next_capture_number()
    filename = f"capture_{number:03d}.jpg"
    filepath = os.path.join(config.CAPTURE_FOLDER, filename)
    now = datetime.now()
    
    print(f"[DEBUG] Will save to: {filepath}", flush=True)

    if not config.SIMULATION_MODE:
        print("[DEBUG] REAL WEBCAM MODE - attempting to open camera", flush=True)
        try:
            print("[DEBUG] Creating VideoCapture(0)...", flush=True)
            camera = cv2.VideoCapture(0)
            print(f"[DEBUG] VideoCapture created. isOpened = {camera.isOpened()}", flush=True)

            if not camera.isOpened():
                raise RuntimeError("Could not open webcam")

            print("[DEBUG] Warming up camera (5 frames)...", flush=True)
            for i in range(5):
                success, frame = camera.read()
                print(f"[DEBUG] Warmup frame {i+1}: success={success}", flush=True)

            print("[DEBUG] Capturing actual photo...", flush=True)
            success, frame = camera.read()
            print(f"[DEBUG] Capture result: success={success}, frame is None: {frame is None}", flush=True)
            
            camera.release()
            print("[DEBUG] Camera released", flush=True)

            if not success or frame is None:
                raise RuntimeError("Webcam returned an empty frame")

            print(f"[DEBUG] Saving image to {filepath}...", flush=True)
            cv2.imwrite(filepath, frame)
            print(f"[SUCCESS] Webcam capture saved: {filename}", flush=True)

        except Exception as e:
            print(f"[ERROR] Webcam error: {e}", flush=True)
            print("[DEBUG] Falling back to placeholder image", flush=True)
            _save_placeholder_image(filepath, now)
    else:
        print("[DEBUG] SIMULATION MODE - using placeholder image", flush=True)
        _save_placeholder_image(filepath, now)

    print(f"[DEBUG] Returning filename: {filename}", flush=True)
    return filename
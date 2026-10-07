# Smart Home Surveillance System

An automated, web-based surveillance system that detects motion, captures real-time images, triggers visual/audio alarms, and logs security events. 

The system is designed with a dual-mode architecture: it can run in Simulation Mode on a standard Windows PC for development and testing, and seamlessly switch to Hardware Mode when deployed on a Raspberry Pi with physical sensors.

## Features

- **Automated Motion Detection:** Continuously monitors a PIR sensor in the background.
- **Real-Time Image Capture:** Uses OpenCV to snap a photo from a USB/Built-in Webcam the moment motion is detected.
- **Hardware Alarms:** Triggers a physical LED and Buzzer for 3 seconds upon intrusion.
- **Live Web Dashboard:** A sleek, dark-themed UI that polls the backend every 500ms to show real-time system states (Monitoring, Capturing, Alarm Active, etc.).
- **Event History & Logging:** Saves every detection event (timestamp, image, alarm status) to a local SQLite database.
- **Responsive Design:** Fully responsive CSS layout that works on desktops, tablets, and mobile devices.

## Tech Stack

- **Backend:** Python 3, Flask
- **Computer Vision:** OpenCV (cv2)
- **Database:** SQLite3
- **Hardware Control:** RPi.GPIO (for Raspberry Pi)
- **Frontend:** HTML5, CSS3 (Custom Dark Theme), Vanilla JavaScript

## Hardware Requirements (For Raspberry Pi Deployment)

To run this system on a Raspberry Pi, you will need:
- Raspberry Pi (3, 4, or 5)
- HC-SR501 PIR Motion Sensor
- USB Webcam (or Pi Camera Module with code adjustments)
- Active Buzzer
- LED (any color)
- 220 Ohm Resistor (for the LED)
- Breadboard and Jumper Wires

### GPIO Pinout Configuration

| Component | GPIO Pin (BCM) | Physical Pin |
| :--- | :---: | :---: |
| **PIR Sensor (OUT)** | GPIO 4 | Pin 7 |
| **LED (Anode)** | GPIO 17 | Pin 11 |
| **Buzzer (+)** | GPIO 27 | Pin 13 |
| **GND** | Ground | Pin 6, 9, 14, etc. |

## Installation & Setup

### 1. Project Directory
Ensure you are in the root folder of the project.
```bash
cd D:\EmbeddedLab\SmartSurveillance\smart-surveillance
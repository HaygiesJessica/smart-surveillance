import config

# Simulated hardware state
_led_on = False
_buzzer_on = False

# Real hardware setup
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.LED_PIN, GPIO.OUT)
    GPIO.setup(config.BUZZER_PIN, GPIO.OUT)
    GPIO.output(config.LED_PIN, GPIO.LOW)
    GPIO.output(config.BUZZER_PIN, GPIO.LOW)
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    # ImportError happens on Windows; RuntimeError happens if GPIO is already in use
    HARDWARE_AVAILABLE = False


def activate_led():
    global _led_on
    _led_on = True
    if not config.SIMULATION_MODE and HARDWARE_AVAILABLE:
        GPIO.output(config.LED_PIN, GPIO.HIGH)


def deactivate_led():
    global _led_on
    _led_on = False
    if not config.SIMULATION_MODE and HARDWARE_AVAILABLE:
        GPIO.output(config.LED_PIN, GPIO.LOW)


def activate_buzzer():
    global _buzzer_on
    _buzzer_on = True
    if not config.SIMULATION_MODE and HARDWARE_AVAILABLE:
        GPIO.output(config.BUZZER_PIN, GPIO.HIGH)


def deactivate_buzzer():
    global _buzzer_on
    _buzzer_on = False
    if not config.SIMULATION_MODE and HARDWARE_AVAILABLE:
        GPIO.output(config.BUZZER_PIN, GPIO.LOW)


def activate_alarm():
    activate_led()
    activate_buzzer()


def deactivate_alarm():
    deactivate_led()
    deactivate_buzzer()


def led_is_on():
    return _led_on


def buzzer_is_on():
    return _buzzer_on


def cleanup_hardware():
    if not config.SIMULATION_MODE and HARDWARE_AVAILABLE:
        GPIO.cleanup()
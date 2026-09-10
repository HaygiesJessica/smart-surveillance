"""
Hardware Abstraction Layer
===========================
This module represents the physical OUTPUT devices of the surveillance
system: the warning LED and the buzzer.

There is no Raspberry Pi connected yet, so these functions only simulate
the hardware by flipping simple True/False flags. When the real
Raspberry Pi, LED and buzzer are wired up, only the bodies of the
functions below need to change (to real RPi.GPIO calls) - nothing else
in the project has to know the difference.
"""

import config

# Simulated hardware state. On a real Raspberry Pi these would not exist
# as variables - the actual GPIO pins would hold the state instead.
_led_on = False
_buzzer_on = False


def activate_led():
    """Turn the warning LED on (simulated)."""
    global _led_on
    _led_on = True

    if not config.SIMULATION_MODE:
        # FUTURE (Raspberry Pi): GPIO.output(LED_PIN, GPIO.HIGH)
        pass


def deactivate_led():
    """Turn the warning LED off (simulated)."""
    global _led_on
    _led_on = False

    if not config.SIMULATION_MODE:
        # FUTURE (Raspberry Pi): GPIO.output(LED_PIN, GPIO.LOW)
        pass


def activate_buzzer():
    """Turn the buzzer on (simulated)."""
    global _buzzer_on
    _buzzer_on = True

    if not config.SIMULATION_MODE:
        # FUTURE (Raspberry Pi): GPIO.output(BUZZER_PIN, GPIO.HIGH)
        pass


def deactivate_buzzer():
    """Turn the buzzer off (simulated)."""
    global _buzzer_on
    _buzzer_on = False

    if not config.SIMULATION_MODE:
        # FUTURE (Raspberry Pi): GPIO.output(BUZZER_PIN, GPIO.LOW)
        pass


def activate_alarm():
    """Turn on both the LED and the buzzer together."""
    activate_led()
    activate_buzzer()


def deactivate_alarm():
    """Turn off both the LED and the buzzer together."""
    deactivate_led()
    deactivate_buzzer()


def led_is_on():
    return _led_on


def buzzer_is_on():
    return _buzzer_on

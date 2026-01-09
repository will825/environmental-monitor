
""" Reads GPIO17 as a light/dark detector from a photoresister divider"""

import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

light_pin = 17

GPIO.setup(light_pin, GPIO.IN)


try:
    while True:
        value = GPIO.input(light_pin)

        if value == 1:
            print("LIGHT")
        else:
            print("DARK")

        time.sleep(0.5)
 
finally:
    GPIO.cleanup()

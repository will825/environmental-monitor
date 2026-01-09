"""
All Sensors Test
- DHT11 (temperature/humidity) on GPIO4
- Photoresistor divider (light/dark) on GPIO17

Prints a status line every 2 seconds.
"""

import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

# --- Pins (BCM numbering) ---
DHT_PIN = board.D4     # GPIO4
LIGHT_PIN = 17         # GPIO17


def c_to_f(celsius: float):
    return (celsius * 9 / 5) + 32


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT_PIN, GPIO.IN)

def read_light_state():
    return "LIGHT" if GPIO.input(LIGHT_PIN) == 1 else "DARK"

def main() -> None:

    setup_gpio()
    dht = adafruit_dht.DHT11(DHT_PIN)

    try:
        while True:
            light_state = read_light_state()

            try:
                temp_c = dht.temperature
                humidity = dht.humidity

                if temp_c is None or humidity is None:
                    raise RuntimeError("DHT returned None")

                temp_f = c_to_f(temp_c)
                print(f"Temp: {temp_f:.1f} F | Humidity: {humidity:.0f}% | {light_state}")

            except RuntimeError as err:
                # DHT sensors commonly fail reads; keep running.
                print(f"DHT read error: {err} | {light_state}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping test...")

    finally:
        dht.exit()
        GPIO.cleanup()


if __name__ == "__main__":
    main()    

"""
Environmental Monitoring Application

- DHT11 (temperature/humidity) on GPIO4
- Photoresistor divider (light/dark) on GPIO17

Reads Temp/Humidity and light state and prints status lines .
"""

import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
from datetime import datetime
import csv
import os

# --- Pins (BCM numbering) ---
DHT_PIN = board.D4     # GPIO4
LIGHT_PIN = 17         # GPIO17

# --- CSV File Path ---
DATA_DIR = "data"

#--- Celsius to Farenheight ---
def c_to_f(celsius: float):
    return (celsius * 9 / 5) + 32


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT_PIN, GPIO.IN)

def read_light_state():
    return "LIGHT" if GPIO.input(LIGHT_PIN) == 1 else "DARK"

def daily_log_path() -> str:
    """Return today's CSV path, e.g. data/readings_2026-01-07.csv"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"readings_{date_str}.csv")


def ensure_csv_header(path: str) -> None:
    """Create CSV file and header if it doesn't exist yet."""
    if not os.path.exists(path):
        with open(path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "temp_f", "humidity", "light"])


def main() -> None:


    setup_gpio()
    os.makedirs(DATA_DIR, exist_ok=True)


    dht = adafruit_dht.DHT11(DHT_PIN)

    try:
        while True:
            light_state = read_light_state()
            timestamp =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_path = daily_log_path()
            ensure_csv_header(log_path)

            try:
                temp_c = dht.temperature
                humidity = dht.humidity

                if temp_c is None or humidity is None:
                    raise RuntimeError("DHT returned None")

                temp_f = c_to_f(temp_c)
                print(f"{timestamp} Temp: {temp_f:.1f} F | Humidity: {humidity:.0f}% | {light_state}")

                with open(log_path, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, f"{temp_f:.1f}", humidity, light_state])

            except RuntimeError as err:
                # DHT sensors commonly fail reads; keep running.
                print(f"{timestamp} DHT read error: {err} | {light_state}")

            time.sleep(300)

    except KeyboardInterrupt:
        print("\nStopping Environmental Monitor...")

    finally:
        dht.exit()
        GPIO.cleanup()


if __name__ == "__main__":
    main()    

"""
Environmental Monitor (5-minute sampling) + I2C 1602 LCD

- Reads DHT11 (temp/humidity) + photoresistor (LIGHT/DARK)
- Logs to CSV
- Displays latest values on an I2C 1602 LCD
"""

import csv
import time
from datetime import datetime

import board
import adafruit_dht
import RPi.GPIO as GPIO

from RPLCD.i2c import CharLCD


# --- Config ---
SAMPLE_SECONDS = 300  # 5 minutes
CSV_PATH = "data/readings.csv"

DHT_PIN = board.D4     # GPIO4
LIGHT_PIN = 17         # GPIO17

# LCD config (most common: 0x27, sometimes 0x3f)
LCD_ADDRESS = 0x27
LCD_COLS = 16
LCD_ROWS = 2


def c_to_f(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def setup_gpio() -> None:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT_PIN, GPIO.IN)


def read_light_state() -> str:
    return "LIGHT" if GPIO.input(LIGHT_PIN) == 1 else "DARK"


def ensure_csv_header(path: str) -> None:
    # Create file + header once
    import os
    if not os.path.exists(path):
        with open(path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temp_f", "humidity", "light"])


def lcd_write(lcd: CharLCD, line1: str, line2: str) -> None:
    # Force exactly 16 chars per line for a clean display
    line1 = (line1[:LCD_COLS]).ljust(LCD_COLS)
    line2 = (line2[:LCD_COLS]).ljust(LCD_COLS)
    lcd.home()
    lcd.write_string(line1)
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2)


def main() -> None:
    ensure_csv_header(CSV_PATH)
    setup_gpio()

    dht = adafruit_dht.DHT11(DHT_PIN)

    # Init LCD
    lcd = CharLCD("PCF8574", LCD_ADDRESS, port=1, cols=LCD_COLS, rows=LCD_ROWS)
    lcd.clear()
    lcd_write(lcd, "Env Monitor", "Starting...")

    next_run = time.monotonic()

    try:
        while True:
            # Sleep until next scheduled sample time (prevents drift)
            now = time.monotonic()
            sleep_for = next_run - now
            if sleep_for > 0:
                time.sleep(sleep_for)
            next_run += SAMPLE_SECONDS

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            light_state = read_light_state()

            try:
                temp_c = dht.temperature
                humidity = dht.humidity
                if temp_c is None or humidity is None:
                    raise RuntimeError("DHT returned None")

                temp_f = c_to_f(temp_c)

                # Console
                print(f"{timestamp} Temp: {temp_f:.1f} F | Humidity: {humidity:.0f}% | {light_state}")

                # CSV
                with open(CSV_PATH, mode="a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, f"{temp_f:.1f}", f"{humidity:.0f}", light_state])

                # LCD (2 lines, compact)
                lcd_line1 = f"T:{temp_f:>4.1f}F H:{humidity:>2.0f}%"
                lcd_line2 = f"{light_state} {timestamp[-8:]}"  # HH:MM:SS
                lcd_write(lcd, lcd_line1, lcd_line2)

            except RuntimeError as err:
                print(f"{timestamp} DHT read error: {err} | {light_state}")
                lcd_write(lcd, "DHT READ ERROR", light_state)

    except KeyboardInterrupt:
        print("\nStopping Environmental Monitor...")

    finally:
        try:
            lcd.clear()
            lcd_write(lcd, "Monitor Stopped", "Goodbye")
            time.sleep(1)
            lcd.clear()
        except Exception:
            pass

        dht.exit()
        GPIO.cleanup()


if __name__ == "__main__":
    main()

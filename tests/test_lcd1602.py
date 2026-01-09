"""
LCD1602 (I2C) smoke test using RPLCD.

What it does:
- Initializes the LCD at the configured I2C address
- Writes a few test screens
- Exits cleanly (Ctrl+C safe)

Run:
  source .venv/bin/activate
  python tests/test_lcd1602.py
"""

import time
from RPLCD.i2c import CharLCD

# Match your main_lcd.py defaults
LCD_ADDRESS = 0x27  # sometimes 0x3F
LCD_COLS = 16
LCD_ROWS = 2


def lcd_write(lcd: CharLCD, line1: str, line2: str) -> None:
    """Write exactly 16 chars per line for a clean LCD."""
    line1 = (line1[:LCD_COLS]).ljust(LCD_COLS)
    line2 = (line2[:LCD_COLS]).ljust(LCD_COLS)
    lcd.home()
    lcd.write_string(line1)
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2)


def main() -> None:
    # Typical Raspberry Pi I2C port is 1
    lcd = CharLCD("PCF8574", address=LCD_ADDRESS, port=1, cols=LCD_COLS, rows=LCD_ROWS)

    try:
        lcd.clear()
        lcd_write(lcd, "LCD TEST: OK", "RPLCD + I2C")
        time.sleep(2)

        lcd.clear()
        lcd_write(lcd, "Line1: Hello", "Line2: World")
        time.sleep(2)

        lcd.clear()
        lcd_write(lcd, "Addr: 0x%02X" % LCD_ADDRESS, "Done.")
        time.sleep(2)

    except KeyboardInterrupt:
        pass
    finally:
        try:
            lcd.clear()
        except Exception:
            pass


if __name__ == "__main__":
    main()

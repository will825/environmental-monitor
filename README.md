# Environmental Monitor (Raspberry Pi) — Sensors + Logging + API + Dashboard

A production-style environmental monitoring system built on a Raspberry Pi.

**Features**
-  DHT11 temperature/humidity sensor + photoresistor light/dark sensor
-  5-minute sampling cadence (configurable)
-  Daily CSV rotation: `data/readings_YYYY-MM-DD.csv`
-  Plot generator: `plot_YYYY-MM-DD.png` (red temp, blue humidity)
-  FastAPI dashboard + API (live readings, logs, downloads)
-  systemd services: runs on boot, auto-restarts, logs to journal

---

## Hardware

### Sensors
- **DHT11** (Temp/Humidity) → GPIO4
- **Photoresistor + resistor voltage divider** (Light/Dark) → GPIO17
- **Optional:** I2C LCD 1602 screen

### Wiring
See: `docs/wiring.md`

---

## Software Overview

### 1) Data Logger
- `software/main.py` (no LCD)
- `software/main_lcd.py` (LCD build)

Writes daily rotated CSV:
- `data/readings_YYYY-MM-DD.csv`

CSV columns:
- `timestamp,temp_f,humidity,light`

### 2) Plot Generator
Generate a plot for today:

python software/plot_readings.py

Generate a plot for a specific date:
python software/plot_readings.py year-month-date

Outputs:
data/plot_YYYY-MM-DD.png
3) Dashboard + API
Runs a local web dashboard on:
http://bread.local:8000 (example)
Dashboard includes:
Latest reading
Recent system logs
On-demand plot generation button
Download links for today’s CSV + plot
API endpoints:
GET /api/latest
GET /api/today
GET /api/logs?lines=80
POST /api/plot/today
GET /plot/today.png

# Architecture

## Components

### 1) Data Logger (systemd: `environmental-monitor`)
- Reads sensors every 5 minutes:
  - DHT11 (Temp/Humidity) on GPIO4
  - Photoresistor divider (Light/Dark) on GPIO17
- Writes daily rotated CSV:
  - `data/readings_YYYY-MM-DD.csv`
- Displays live values on I2C LCD1602 (optional build)

### 2) Plot Generator
- `software/plot_readings.py [YYYY-MM-DD]`
- Reads: `data/readings_YYYY-MM-DD.csv`
- Outputs: `data/plot_YYYY-MM-DD.png`
- Style: red temperature, blue humidity, clean time axis

### 3) Dashboard + API (systemd: `envdash`)
- FastAPI server (`web/app.py`)
- Dashboard at `/`
- API endpoints:
  - `/api/latest`
  - `/api/today`
  - `/api/logs`
  - `/api/plot/today`
  - `/plot/today.png`

"""
Daily Plot (Today)

Reads today's rotated CSV:
- data/readings_YYYY-MM-DD.csv

Outputs a clean plot image:
- data/plot_YYYY-MM-DD.png

Style:
- Temperature line = red
- Humidity line = blue
- Title shows Month + Year
- X-axis shows only HH:MM:SS
"""

import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


DATA_DIR = "data"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def csv_path_for(date_str: str) -> str:
    return os.path.join(DATA_DIR, f"readings_{date_str}.csv")


def output_path_for(date_str: str) -> str:
    return os.path.join(DATA_DIR, f"plot_{date_str}.png")


def main() -> None:
    date_str = today_str()
    csv_path = csv_path_for(date_str)
    output_path = output_path_for(date_str)

    if not os.path.exists(csv_path):
        print(f"Today's CSV not found: {csv_path}")
        print("Run your monitor first to generate today's readings.")
        return

    timestamps: list[datetime] = []
    temperatures: list[float] = []
    humidities: list[float] = []

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if not row.get("timestamp") or not row.get("temp_f") or not row.get("humidity"):
                continue

            ts = datetime.strptime(row["timestamp"], TIME_FORMAT)
            temp_f = float(row["temp_f"])
            hum = float(row["humidity"])

            timestamps.append(ts)
            temperatures.append(temp_f)
            humidities.append(hum)

    if not timestamps:
        print(f"No data rows found in: {csv_path}")
        return

    month_year = timestamps[0].strftime("%B %Y")

    # --- Plot ---
    fig, ax_temp = plt.subplots(figsize=(10, 5))

    # Temperature (left axis) - RED
    ax_temp.plot(timestamps, temperatures, color="red", linewidth=2, label="Temperature (°F)")
    ax_temp.set_ylabel("Temperature (°F)", color="red")
    ax_temp.tick_params(axis="y", labelcolor="red")

    # Humidity (right axis) - BLUE
    ax_hum = ax_temp.twinx()
    ax_hum.plot(timestamps, humidities, color="blue", linewidth=2, label="Humidity (%)")
    ax_hum.set_ylabel("Humidity (%)", color="blue")
    ax_hum.tick_params(axis="y", labelcolor="blue")

    # X-axis formatting: HH:MM:SS only
    ax_temp.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax_temp.set_xlabel("Time (HH:MM:SS)")

    # Title includes Month + Year
    plt.title(f"Environmental Monitor — Temperature & Humidity ({month_year})")

    # Legends
    ax_temp.legend(loc="upper left")
    ax_hum.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f"Saved plot to: {output_path}")


if __name__ == "__main__":
    main()

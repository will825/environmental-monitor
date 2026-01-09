"""
Plot temperature and humidity readings over time from data/readings.csv.

Output:
- Saves a clean PNG plot to: data/plot_temp_humidity_graph.png
"""

import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CSV_PATH = "data/readings.csv"
OUTPUT_PATH = "data/plot_temp_humidity_graph.png"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def main() -> None:
    timestamps: list[datetime] = []
    temperatures: list[float] = []
    humidities: list[float] = []

    # --- Read CSV ---
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if not row.get("timestamp") or not row.get("temp_f") or not row.get("humidity"):
                continue

            ts = datetime.strptime(row["timestamp"], TIME_FORMAT)
            temp_f = float(row["temp_f"])
            humidity = float(row["humidity"])

            timestamps.append(ts)
            temperatures.append(temp_f)
            humidities.append(humidity)

    if not timestamps:
        print(f"No data found in {CSV_PATH}.")
        return

    # Extract month + year for title
    month_year = timestamps[0].strftime("%B %Y")

    # --- Plot ---
    fig, ax_temp = plt.subplots(figsize=(10, 5))

    # Temperature (left axis)
    ax_temp.plot(
        timestamps,
        temperatures,
        color="red",
        linewidth=2,
        label="Temperature (°F)",
    )
    ax_temp.set_ylabel("Temperature (°F)", color="red")
    ax_temp.tick_params(axis="y", labelcolor="red")

    # Humidity (right axis)
    ax_hum = ax_temp.twinx()
    ax_hum.plot(
        timestamps,
        humidities,
        color="blue",
        linewidth=2,
        label="Humidity (%)",
    )
    ax_hum.set_ylabel("Humidity (%)", color="blue")
    ax_hum.tick_params(axis="y", labelcolor="blue")

    # X-axis formatting (HH:MM:SS only)
    ax_temp.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax_temp.set_xlabel("Time")

    # Title
    plt.title(f"Environmental Monitor — Temperature & Humidity ({month_year})")

    # Legends (explicit placement)
    ax_temp.legend(loc="upper left")
    ax_hum.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved plot to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

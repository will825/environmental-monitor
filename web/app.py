"""
Environmental Monitor API + Dashboard

Run (dev):
  uvicorn web.app:app --host 0.0.0.0 --port 8000

Endpoints:
- GET /api/latest         -> latest reading (JSON)
- GET /api/today          -> today's readings (JSON list)
- GET /api/logs?lines=50  -> last N log lines from systemd journal
- GET /download/csv       -> download today's CSV file
- GET /download/plot      -> download today's plot PNG if it exists
- GET /                  -> simple dashboard page
"""

import csv
import os
import subprocess
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi import Response

DATA_DIR = "data"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MONITOR_SERVICE = "environmental-monitor"  # your systemd service name

app = FastAPI(title="Environmental Monitor")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def today_csv_path() -> str:
    return os.path.join(DATA_DIR, f"readings_{today_str()}.csv")


def today_plot_path() -> str:
    return os.path.join(DATA_DIR, f"plot_{today_str()}.png")


def read_csv_rows(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not os.path.exists(path):
        return rows

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not r.get("timestamp"):
                continue
            rows.append(r)
    return rows


@app.get("/api/latest")
def api_latest():
    path = today_csv_path()
    rows = read_csv_rows(path)
    if not rows:
        return JSONResponse(
            {"ok": False, "error": "No data yet for today.", "csv": path},
            status_code=404,
        )

    last = rows[-1]
    # Convert numeric fields to numbers when possible
    try:
        last["temp_f"] = float(last["temp_f"])
    except Exception:
        pass
    try:
        last["humidity"] = float(last["humidity"])
    except Exception:
        pass

    return {"ok": True, "data": last}
@app.post("/api/plot/today")
def api_plot_today():
    """
    Generate today's plot PNG on demand by calling your plot script.
    """
    date_str = today_str()

    # Call your existing plotter (preferred because it uses your styling)
    cmd = [
        "/home/willy/environmental-monitor/.venv/bin/python",
        "software/plot_readings.py",
        date_str,
    ]

    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            {"ok": False, "error": "Plot generation failed", "details": e.output},
            status_code=500,
        )

    plot_path = today_plot_path()
    if not os.path.exists(plot_path):
        return JSONResponse(
            {"ok": False, "error": "Plot script ran but PNG not found", "path": plot_path, "output": out},
            status_code=500,
        )

    return {"ok": True, "date": date_str, "plot": plot_path, "output": out}


@app.get("/plot/today.png")
def plot_today_png():
    """
    Serve today's plot PNG for <img> embedding.
    """
    path = today_plot_path()
    if not os.path.exists(path):
        return JSONResponse({"ok": False, "error": "Today's plot not found", "path": path}, status_code=404)

    # Prevent aggressive browser caching by returning the file normally but allowing cache-busting query params
    return FileResponse(path, media_type="image/png", filename=os.path.basename(path))



@app.get("/api/today")
def api_today(limit: int = Query(5000, ge=1, le=20000)):
    path = today_csv_path()
    rows = read_csv_rows(path)
    return {"ok": True, "csv": path, "count": min(len(rows), limit), "data": rows[-limit:]}


@app.get("/api/logs")
def api_logs(lines: int = Query(50, ge=10, le=500)):
    # Pull last N lines from journalctl for your monitor service
    cmd = ["journalctl", "-u", MONITOR_SERVICE, "-n", str(lines), "--no-pager"]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return {"ok": True, "service": MONITOR_SERVICE, "lines": lines, "text": out}
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            {"ok": False, "error": "Failed to read logs", "details": e.output},
            status_code=500,
        )


@app.get("/download/csv")
def download_csv():
    path = today_csv_path()
    if not os.path.exists(path):
        return JSONResponse({"ok": False, "error": "Today's CSV not found", "path": path}, status_code=404)
    return FileResponse(path, media_type="text/csv", filename=os.path.basename(path))


@app.get("/download/plot")
def download_plot():
    path = today_plot_path()
    if not os.path.exists(path):
        return JSONResponse({"ok": False, "error": "Today's plot not found", "path": path}, status_code=404)
    return FileResponse(path, media_type="image/png", filename=os.path.basename(path))


@app.get("/", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Environmental Monitor Dashboard</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; }
    .row { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-start; }
    .card { border: 1px solid #ddd; border-radius: 10px; padding: 16px; min-width: 280px; }
    .big { font-size: 28px; font-weight: 700; }
    .muted { color: #666; }
    pre { background: #111; color: #eee; padding: 12px; border-radius: 10px; overflow: auto; max-height: 420px; }
    a { text-decoration: none; }
    button { padding: 10px 12px; border-radius: 10px; border: 1px solid #ccc; cursor: pointer; }
    img { display: block; margin-top: 12px; max-width: 100%; border: 1px solid #ddd; border-radius: 10px; }
  </style>
</head>
<body>
  <h1>Environmental Monitor</h1>
  <p class="muted">Live readings + system logs + on-demand plots.</p>

  <div class="row">
    <div class="card">
      <div class="muted">Latest reading</div>
      <div id="latest" class="big">Loading...</div>
      <div id="latest_meta" class="muted"></div>

      <p style="margin-top: 12px;">
        <a href="/download/csv">Download today’s CSV</a><br/>
        <a href="/download/plot">Download today’s plot</a>
      </p>

      <hr style="border: none; border-top: 1px solid #eee; margin: 14px 0;" />

      <div class="muted">On-demand plot</div>
      <p style="margin: 8px 0;">
        <button id="btnPlot">Generate Today’s Plot</button>
        <span id="plotStatus" class="muted" style="margin-left: 10px;"></span>
      </p>
      <img id="plotImg" src="/plot/today.png" alt="Today's plot (generate to update)" />
    </div>

    <div class="card" style="flex: 1; min-width: 360px;">
      <div class="muted">Monitor logs (last 80 lines)</div>
      <pre id="logs">Loading logs...</pre>
    </div>
  </div>

<script>
async function refreshLatest() {
  const el = document.getElementById("latest");
  const meta = document.getElementById("latest_meta");

  try {
    const r = await fetch("/api/latest");
    const j = await r.json();

    if (!j.ok) {
      el.textContent = "No data yet";
      meta.textContent = j.error || "";
      return;
    }

    const d = j.data;
    el.textContent = `${d.temp_f} °F | ${d.humidity}% | ${d.light}`;
    meta.textContent = `Timestamp: ${d.timestamp}`;
  } catch (e) {
    el.textContent = "Error fetching latest";
    meta.textContent = String(e);
  }
}

async function refreshLogs() {
  const el = document.getElementById("logs");
  try {
    const r = await fetch("/api/logs?lines=80");
    const j = await r.json();
    el.textContent = j.ok ? j.text : (j.error || "Failed to load logs");
  } catch (e) {
    el.textContent = "Error fetching logs: " + String(e);
  }
}

async function generatePlot() {
  const status = document.getElementById("plotStatus");
  const img = document.getElementById("plotImg");

  status.textContent = "Generating...";

  try {
    const r = await fetch("/api/plot/today", { method: "POST" });
    const j = await r.json();

    if (!j.ok) {
      status.textContent = "Failed: " + (j.error || "unknown");
      return;
    }

    status.textContent = "Updated.";
    img.src = "/plot/today.png?v=" + Date.now(); // cache-bust
  } catch (e) {
    status.textContent = "Error: " + String(e);
  }
}

document.getElementById("btnPlot").addEventListener("click", generatePlot);

refreshLatest();
refreshLogs();
setInterval(refreshLatest, 5000);
setInterval(refreshLogs, 15000);
</script>
</body>
</html>
"""

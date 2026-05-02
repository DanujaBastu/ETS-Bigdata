"""
# Dashboard WeatherPulse - Big Data ETS Kelompok 8
# Monitor Cuaca 6 Kota Besar Indonesia
# Flask app yang membaca hasil Spark + data live dari consumer
"""

from flask import Flask, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

# =====================
# Path ke file data
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

SPARK_RESULTS_FILE = os.path.join(DATA_DIR, "spark_results.json")
LIVE_API_FILE      = os.path.join(DATA_DIR, "live_api.json")
LIVE_RSS_FILE      = os.path.join(DATA_DIR, "live_rss.json")

# =====================
# Helper: baca JSON file
# =====================
def read_json(filepath, default=None):
    """Baca file JSON, return default jika file tidak ada atau error."""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[WARNING] Gagal baca {filepath}: {e}")
    return default

# =====================
# Mapping weather_code ke deskripsi
# =====================
WEATHER_DESC = {
    0: "Cerah", 1: "Sebagian Cerah", 2: "Berawan Sebagian", 3: "Mendung",
    45: "Berkabut", 48: "Kabut Beku",
    51: "Gerimis Ringan", 53: "Gerimis Sedang", 55: "Gerimis Lebat",
    61: "Hujan Ringan", 63: "Hujan Sedang", 65: "Hujan Lebat",
    71: "Salju Ringan", 73: "Salju Sedang", 75: "Salju Lebat",
    80: "Hujan Lokal Ringan", 81: "Hujan Lokal Sedang", 82: "Hujan Lokal Lebat",
    95: "Badai Petir", 96: "Badai dengan Hujan Es", 99: "Badai Hebat",
}

WEATHER_ICON = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦️", 81: "🌦️", 82: "⛈️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

def get_weather_desc(code):
    return WEATHER_DESC.get(code, f"Kode {code}")

def get_weather_icon(code):
    return WEATHER_ICON.get(code, "🌡️")

# =====================
# Routes
# =====================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    """
    Endpoint utama — mengembalikan semua data yang dibutuhkan dashboard:
    - spark_results: hasil analisis Spark
    - live_api: data cuaca terbaru per kota
    - live_rss: berita/feed terbaru
    """
    spark_data = read_json(SPARK_RESULTS_FILE, default={})
    live_api   = read_json(LIVE_API_FILE, default=[])
    live_rss   = read_json(LIVE_RSS_FILE, default=[])

    # --- Proses live_api: ambil data terbaru per kota ---
    latest_per_city = {}
    for event in (live_api if isinstance(live_api, list) else []):
        kode = event.get("kode_kota", "")
        if kode not in latest_per_city:
            latest_per_city[kode] = event
        else:
            # Simpan yang timestamp-nya lebih baru
            existing_ts = latest_per_city[kode].get("timestamp", "")
            current_ts  = event.get("timestamp", "")
            if current_ts > existing_ts:
                latest_per_city[kode] = event

    # Enrich data kota dengan deskripsi cuaca
    cities_list = []
    for kode, data in latest_per_city.items():
        code = data.get("weather_code", 0)
        data["weather_desc"] = get_weather_desc(code)
        data["weather_icon"] = get_weather_icon(code)

        # Tentukan status ekstrem
        temp  = data.get("temperature", 0)
        wind  = data.get("wind_speed", 0)
        humid = data.get("humidity", 0)
        if wind > 40 or humid > 90 or temp > 35:
            data["status"] = "ekstrem"
        elif wind > 25 or temp > 32:
            data["status"] = "waspada"
        else:
            data["status"] = "normal"

        cities_list.append(data)

    # Urutkan berdasarkan suhu tertinggi
    cities_list.sort(key=lambda x: x.get("temperature", 0), reverse=True)

    # --- Proses live_rss: ambil 8 berita terbaru ---
    rss_list = live_rss if isinstance(live_rss, list) else []
    rss_list = rss_list[-8:]  # ambil 8 terbaru
    rss_list.reverse()        # terbaru di atas

    return jsonify({
        "status": "ok",
        "last_updated": datetime.now().isoformat(),
        "spark": spark_data,
        "live_weather": cities_list,
        "live_rss": rss_list,
        "data_available": {
            "spark": bool(spark_data),
            "live_api": bool(cities_list),
            "live_rss": bool(rss_list),
        }
    })


@app.route("/api/spark")
def api_spark():
    """Endpoint khusus untuk hasil analisis Spark."""
    data = read_json(SPARK_RESULTS_FILE, default={})
    return jsonify(data)


@app.route("/api/live")
def api_live():
    """Endpoint khusus untuk data cuaca live terbaru."""
    live_api = read_json(LIVE_API_FILE, default=[])
    return jsonify(live_api[-20:] if isinstance(live_api, list) else [])


@app.route("/api/news")
def api_news():
    """Endpoint khusus untuk berita RSS terbaru."""
    live_rss = read_json(LIVE_RSS_FILE, default=[])
    rss_list = live_rss if isinstance(live_rss, list) else []
    return jsonify(rss_list[-10:])


if __name__ == "__main__":
    print("=" * 50)
    print("  WeatherPulse Dashboard — Kelompok 8 ETS Big Data")
    print("  http://localhost:5000")
    print("=" * 50)
    print(f"  Data dir : {DATA_DIR}")
    print(f"  Spark    : {'✓' if os.path.exists(SPARK_RESULTS_FILE) else '✗ (belum ada)'}")
    print(f"  Live API : {'✓' if os.path.exists(LIVE_API_FILE) else '✗ (belum ada)'}")
    print(f"  Live RSS : {'✓' if os.path.exists(LIVE_RSS_FILE) else '✗ (belum ada)'}")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)

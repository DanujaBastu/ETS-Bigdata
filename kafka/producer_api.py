# [Nama Anda] Producer API - WeatherPulse
# Mengambil data cuaca 6 kota dari Open-Meteo dan mengirim ke Kafka topic weather-api

import json
import time
import requests
from datetime import datetime
from kafka import KafkaProducer

# =========================
# Konfigurasi Kota
# =========================
CITIES = [
    {"kode_kota": "JKT", "nama_kota": "Jakarta",   "latitude": -6.21, "longitude": 106.85},
    {"kode_kota": "SBY", "nama_kota": "Surabaya",  "latitude": -7.25, "longitude": 112.75},
    {"kode_kota": "SMG", "nama_kota": "Semarang",  "latitude": -6.99, "longitude": 110.42},
    {"kode_kota": "MDN", "nama_kota": "Medan",     "latitude":  3.59, "longitude":  98.67},
    {"kode_kota": "MKS", "nama_kota": "Makassar",  "latitude": -5.14, "longitude": 119.41},
    {"kode_kota": "DPS", "nama_kota": "Denpasar",  "latitude": -8.67, "longitude": 115.21},
]

TOPIC_NAME = "weather-api"
BOOTSTRAP_SERVER = "localhost:9092"
INTERVAL_SECONDS = 600   # 10 menit

# =========================
# Kafka Producer
# =========================
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
    acks="all",
    enable_idempotence=True,
)

# =========================
# Ambil Data Cuaca
# =========================
def get_weather(city):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "Asia/Jakarta"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()["current"]

    event = {
        "kode_kota": city["kode_kota"],
        "nama_kota": city["nama_kota"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "temperature": data["temperature_2m"],
        "humidity": data["relative_humidity_2m"],
        "wind_speed": data["wind_speed_10m"],
        "weather_code": data["weather_code"],
        "timestamp": datetime.now().isoformat()
    }

    return event

# =========================
# Kirim ke Kafka
# =========================
def send_weather():
    for city in CITIES:
        try:
            event = get_weather(city)

            producer.send(
                topic=TOPIC_NAME,
                key=city["kode_kota"],
                value=event
            )

            print(f"[SUKSES] {city['nama_kota']} -> {event}")

        except Exception as e:
            print(f"[ERROR] {city['nama_kota']} -> {e}")

    producer.flush()

# =========================
# Main Loop
# =========================
if __name__ == "__main__":
    print("Producer Weather API berjalan... Tekan CTRL+C untuk berhenti.")

    while True:
        print("\nMengambil data cuaca terbaru...")
        send_weather()
        print(f"Menunggu {INTERVAL_SECONDS} detik...\n")
        time.sleep(INTERVAL_SECONDS)

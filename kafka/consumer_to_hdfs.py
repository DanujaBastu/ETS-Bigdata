"""
# Clarissa Aydin - 014: Consumer to HDFS — WeatherPulse ETS Big Data
Membaca dari topic weather-api dan weather-rss, buffer event,
simpan ke HDFS setiap 3 menit menggunakan Docker Command.
Juga menyimpan salinan lokal untuk dashboard Flask.
"""

import json
import os
import subprocess
import threading
import time
import logging
from datetime import datetime
from kafka import KafkaConsumer

# =========================
# Konfigurasi
# =========================
BOOTSTRAP_SERVER = "localhost:9092"
TOPIC_API = "weather-api"
TOPIC_RSS = "weather-rss"
GROUP_ID  = "weather-hdfs-consumer"

FLUSH_INTERVAL   = 180   # 3 menit
MAX_BUFFER_SIZE  = 100   

# Konfigurasi Docker & HDFS
DOCKER_CONTAINER = "namenode"
HDFS_PATH_API = "/data/weather/api"
HDFS_PATH_RSS = "/data/weather/rss"

LOCAL_TMP_DIR      = "tmp_buffer"  # Folder lokal sementara
DASHBOARD_DATA_DIR = "dashboard/data"
DASHBOARD_LIVE_API = os.path.join(DASHBOARD_DATA_DIR, "live_api.json")
DASHBOARD_LIVE_RSS = os.path.join(DASHBOARD_DATA_DIR, "live_rss.json")
MAX_DASHBOARD_EVENTS = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Consumer] %(message)s"
)
log = logging.getLogger(__name__)

# Buffer (thread-safe)
api_buffer = []
rss_buffer = []
buffer_lock = threading.Lock()

# =========================
# Setup direktori
# =========================
def ensure_local_dirs():
    os.makedirs(LOCAL_TMP_DIR, exist_ok=True)
    os.makedirs(DASHBOARD_DATA_DIR, exist_ok=True)

def hdfs_mkdir(path):
    """Buat direktori HDFS via Docker exec."""
    try:
        subprocess.run(
            ["docker", "exec", DOCKER_CONTAINER, "hdfs", "dfs", "-mkdir", "-p", path],
            check=True, capture_output=True
        )
        log.info(f"HDFS dir siap: {path}")
    except subprocess.CalledProcessError as e:
        log.error(f"Gagal buat HDFS dir {path}: {e.stderr.decode()}")

def setup_hdfs():
    hdfs_mkdir(HDFS_PATH_API)
    hdfs_mkdir(HDFS_PATH_RSS)
    hdfs_mkdir("/data/weather/hasil")

# =========================
# Simpan ke HDFS via Docker exec
# =========================
def save_to_hdfs(events, hdfs_dir, label):
    if not events:
        return

    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename      = f"{timestamp_str}.json"
    local_path    = os.path.abspath(os.path.join(LOCAL_TMP_DIR, f"{label}_{filename}"))
    container_tmp_path = f"/tmp/{label}_{filename}"
    hdfs_path     = f"{hdfs_dir}/{filename}"

    try:
        # 1. Tulis ke file lokal laptop
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

        # 2. Copy file dari laptop ke dalam kontainer namenode
        subprocess.run(["docker", "cp", local_path, f"{DOCKER_CONTAINER}:{container_tmp_path}"], check=True)

        # 3. Masukkan dari filesystem kontainer ke HDFS
        subprocess.run(
            ["docker", "exec", DOCKER_CONTAINER, "hdfs", "dfs", "-put", container_tmp_path, hdfs_path],
            check=True, capture_output=True
        )

        # 4. Hapus file sementara di dalam kontainer
        subprocess.run(["docker", "exec", DOCKER_CONTAINER, "rm", container_tmp_path], check=True)

        log.info(f"[HDFS] {label}: {len(events)} events berhasil disimpan ke {hdfs_path}")

    except subprocess.CalledProcessError as e:
        log.error(f"Gagal proses HDFS {label}: {e}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

# =========================
# Update Dashboard & Flush Logic (Sama seperti sebelumnya)
# =========================
def update_dashboard_file(events, filepath):
    try:
        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        combined = (existing + events)[-MAX_DASHBOARD_EVENTS:]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Gagal update dashboard file: {e}")

def flush_buffers():
    with buffer_lock:
        api_snap, rss_snap = api_buffer.copy(), rss_buffer.copy()
        api_buffer.clear(); rss_buffer.clear()

    if api_snap:
        save_to_hdfs(api_snap, HDFS_PATH_API, "api")
        update_dashboard_file(api_snap, DASHBOARD_LIVE_API)
    if rss_snap:
        save_to_hdfs(rss_snap, HDFS_PATH_RSS, "rss")
        update_dashboard_file(rss_snap, DASHBOARD_LIVE_RSS)

def flush_thread_fn():
    while True:
        time.sleep(FLUSH_INTERVAL)
        log.info("--- Periodical Flush ke HDFS ---")
        flush_buffers()

def consume_api():
    consumer = KafkaConsumer(TOPIC_API, bootstrap_servers=BOOTSTRAP_SERVER, group_id=GROUP_ID,
                             value_deserializer=lambda v: json.loads(v.decode("utf-8")))
    for message in consumer:
        with buffer_lock:
            api_buffer.append(message.value)
            if len(api_buffer) >= MAX_BUFFER_SIZE: flush_buffers()

def consume_rss():
    consumer = KafkaConsumer(TOPIC_RSS, bootstrap_servers=BOOTSTRAP_SERVER, group_id=GROUP_ID,
                             value_deserializer=lambda v: json.loads(v.decode("utf-8")))
    for message in consumer:
        with buffer_lock:
            rss_buffer.append(message.value)
            if len(rss_buffer) >= MAX_BUFFER_SIZE: flush_buffers()

if __name__ == "__main__":
    ensure_local_dirs()
    setup_hdfs()
    
    threading.Thread(target=consume_api, daemon=True).start()
    threading.Thread(target=consume_rss, daemon=True).start()
    threading.Thread(target=flush_thread_fn, daemon=True).start()

    log.info("Consumer Running... (Docker Exec Mode)")
    try:
        while True:
            time.sleep(10)
            log.info(f"[Status] Buffer API: {len(api_buffer)} | RSS: {len(rss_buffer)}")
    except KeyboardInterrupt:
        flush_buffers()
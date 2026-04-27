## ⚙️ Cara Menjalankan Project
Danuja - 037

### 1️⃣ Nyalakan Hadoop
```bash
docker-compose -f docker-compose-hadoop.yml up -d
```

### 2️⃣ Nyalakan Kafka
```bash
docker-compose -f docker-compose-kafka.yml up -d
```

### 3️⃣ Inisialisasi Kafka Topic
```bash
docker exec -it kafka-broker kafka-topics.sh --create --topic weather-api --bootstrap-server localhost:9092
docker exec -it kafka-broker kafka-topics.sh --create --topic weather-rss --bootstrap-server localhost:9092
```

### 4️⃣ Inisialisasi Folder HDFS
```bash
docker exec -it namenode hdfs dfs -mkdir -p /data/weather/api/
docker exec -it namenode hdfs dfs -mkdir -p /data/weather/rss/
docker exec -it namenode hdfs dfs -mkdir -p /data/weather/hasil/
```

### 5️⃣ Buat Virtual Environment
```bash
python -m venv env
```

### 6️⃣ Aktifkan Virtual Environment

#### Windows PowerShell
```powershell
.\env\Scripts\Activate.ps1
```

#### CMD
```cmd
env\Scripts\activate.bat
```

### 7️⃣ Install Dependencies
```bash
pip install kafka-python requests feedparser hdfs pyspark pandas flask
```

---

## 👨‍💻 Bagian Anggota 2 — Producer API (Open-Meteo → Kafka)

### 📌 Tugas
Mengambil data cuaca real-time dari **Open-Meteo API** lalu mengirimkannya ke Kafka topic:

```text
weather-api
```

### 📂 File
```text
kafka/producer_api.py
```

### ▶️ Cara Menjalankan
```bash
python kafka/producer_api.py
```

---

## 🌍 Data yang Diambil

### Field JSON yang dikirim:
```json
{
  "kode_kota": "SBY",
  "nama_kota": "Surabaya",
  "latitude": -7.25,
  "longitude": 112.75,
  "temperature": 28.2,
  "humidity": 85,
  "wind_speed": 3.6,
  "weather_code": 3,
  "timestamp": "2026-04-27T18:30:24"
}
```

---

## 📡 Verifikasi Data Masuk Kafka

```bash
docker exec -it kafka-broker kafka-console-consumer.sh --topic weather-api --from-beginning --bootstrap-server localhost:9092
```

Jika berhasil, data JSON cuaca akan muncul di terminal.

## Bagian Anggota 3: Producer RSS & Consumer HDFS (RSS → Kafka → HDFS)
Clarissa Aydin - 5027241014

### Tugas:
1. Producer RSS: Mengambil berita cuaca terbaru dari RSS Feed (Tempo & Kompas) dan mengirimkannya ke Kafka topic: weather-rss.

2. Consumer to HDFS: Membaca data dari topic weather-api dan weather-rss, melakukan buffering, lalu menyimpannya ke HDFS secara periodik. Script ini juga memperbarui file JSON lokal untuk kebutuhan dashboard.

### File
- `kafka/producer_rss.py`
- `kafka/consumer_to_hdfs.py`

### Cara Menjalankan

#### 1. Persiapan Infrastruktur (Docker)
Jalankan Hadoop & Kafka
```bash
docker compose -f docker-compose-kafka.yml up -d
docker compose -f docker-compose-hadoop.yml up -d
```
Cek apakah semua kontainer sudah status (Up)
```bash
docker ps
```

#### 2. Persiapan Environment Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install kafka-python feedparser requests hdfs # Pastikan library pendukung sudah terinstall
```

#### 3. Menjalankan Data Pipeline
- Terminal 1: Producer API (Data Cuaca Kota)
```bash
python3 kafka/producer_api.py
```
- Terminal 2: Producer RSS (Data Berita Cuaca)
```bash
python3 kafka/producer_rss.py
```
- Terminal 3: Consumer to HDFS (Pusat Data)
```bash
python3 kafka/consumer_to_hdfs.py
```

docker exec -it namenode hdfs dfs -ls -R /data/weather

<img width="1158" height="133" alt="image" src="https://github.com/user-attachments/assets/e33d6d72-be72-4b1c-ab7f-ea53e99bee3e" />


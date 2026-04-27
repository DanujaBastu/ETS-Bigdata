## ⚙️ Cara Menjalankan Project

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
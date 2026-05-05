# ETS AI
## Kelompok 8 
Anggota dan Kontribusi :
- Danuja Prasasta Bastu - 5027241037 -> Setup Docker (Hadoop & Kafka), buat topic, troubleshooting infrastruktur
- Raihan Fahri Ghazali - 5027241061 -> producer_api.py — integrasi API eksternal
- Clarissa Aydin Rahmazea - 5027241014 -> producer_rss.py + consumer_to_hdfs.py
- Dimas Muhammad Putra - 5027241075 -> spark/analysis.ipynb — 3 analisis wajib
- Mochkamad Maulana Syafaat - 5027241021 -> spark/analysis.ipynb — 3 analisis wajib

## Kenapa WeatherPulse?
Menurut kami, topik ini sangat relevan karena menawarkan representasi nyata dari penerapan Big Data untuk memecahkan masalah industri. Topik ini secara langsung menjawab tantangan geografis dan iklim Indonesia yang dinamis serta sulit diprediksi. Oleh karena itu, kehadiran sistem ini diharapkan dapat memfasilitasi pengambilan keputusan yang lebih akurat terkait keamanan rute pengiriman logistik darat, berdasarkan pantauan kondisi cuaca di kota-kota yang dilalui.

## Diagram Arsitektur
<img width="1440" height="1240" alt="image" src="https://github.com/user-attachments/assets/d4da666e-5f91-4c48-900d-bb70fcaeecc6" />

1. Sumber Data — Proyek ini menarik data dari dua sumber berbeda: Open-Meteo API untuk data cuaca kota-kota Indonesia (suhu, kelembaban, kecepatan angin, dll.) dan RSS Feed dari Tempo & Kompas untuk berita bertema cuaca.
2. Kafka Producers — Masing-masing sumber punya producer tersendiri. producer_api.py mengambil data JSON dari Open-Meteo lalu mempublikasikannya ke Kafka topic weather-api, sementara producer_rss.py mem-parsing berita RSS dan mengirimnya ke topic weather-rss.
3. Apache Kafka — Bertindak sebagai message broker di tengah pipeline. Kafka memisahkan produsen dan konsumen data, sehingga kecepatan produksi dan konsumsi tidak saling bergantung.
4. Consumer & Storage — consumer_to_hdfs.py membaca dari kedua Kafka topic, melakukan buffering, lalu menyimpan data ke dua tempat sekaligus: HDFS untuk penyimpanan terdistribusi, dan file JSON lokal untuk kebutuhan dashboard.
5. Output Akhir — Data di HDFS dianalisis menggunakan Spark (notebook analysis.ipynb) yang menghasilkan grafik dan statistik. Data JSON lokal langsung dibaca oleh Flask Dashboard (app.py) yang menyajikan visualisasi ke pengguna via web browser.

## ⚙️ Setup Project
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
Raihan - 061
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
## Dokumentasi Kafka

### Producer API (Data Cuaca Kota)

<img width="1105" height="479" alt="image" src="https://github.com/user-attachments/assets/d04497d7-c728-45e4-9a0f-97950dad9a3e" />

Data dari API disimpan ke HDFS

<img width="1113" height="354" alt="image" src="https://github.com/user-attachments/assets/5e0c4206-22d3-4035-9f42-4042f195a709" />

### Producer RSS (Data Berita Cuaca)

Berhasil mengambil data dari RSS yang akan disimpan ke Kafka
<img width="1117" height="668" alt="image" src="https://github.com/user-attachments/assets/53dfcfd3-53a7-41cd-910c-d15878056d47" />

### Consumer to HDFS (Pusat Data)

Mengirim data (20 data) ke HDFS

<img width="1028" height="551" alt="image" src="https://github.com/user-attachments/assets/6c848b21-aa66-41d7-b515-283402ffd733" />

RSS mengirimkan data setiap 300 detik (dokumentasi di bawah terlihat penambahan data dari artikel sebanyak 89)

<img width="1041" height="98" alt="image" src="https://github.com/user-attachments/assets/faa7afea-efd8-4da6-a2c8-e4110cf150e1" />

Data dari rss sebelumnya sudah tersimpan di hdfs dalam bentuk `.json` sehingga kembali 0, namun karena ditambahkannya data dari artikel lain, `consumer_to_hdfs` bertambah, dan dikirimkan (flush) ke HDFS.

<img width="1268" height="674" alt="image" src="https://github.com/user-attachments/assets/87dd23fc-8c04-4383-aa88-9bcbd81f9ada" />


### Hasil penyimpanan di HDFS (setelah program dijalankan kurang lebih 24 menit)

`docker exec -it namenode hdfs dfs -ls -R /data/weather/rss`

<img width="1168" height="113" alt="image" src="https://github.com/user-attachments/assets/83e071f8-84ac-4422-933c-4bcd3e031a95" />


`docker exec -it namenode hdfs dfs -ls -R /data/weather`

<img width="1193" height="297" alt="image" src="https://github.com/user-attachments/assets/72c82102-a617-471a-905a-27db9a3262b8" />

## Kendala
Dalam pengembangan pipeline Big Data WeatherPulse, terdapat beberapa kendala teknis yang saya hadapi, di antaranya:

- Ketersediaan Data pada RSS Feed (Zero-Data Fetch):
Pada beberapa sesi pengoperasian, ditemukan bahwa sumber RSS tidak menyediakan artikel baru (Fetched 0 artikel). Hal ini terjadi dikarenakan tidak adanya pembaruan data dari sisi penyedia (source) atau sistem deduplikasi pada Producer yang mencegah pengiriman data yang sama secara berulang ke Kafka. Solusi yang diterapkan adalah dengan menambahkan variasi sumber RSS untuk memastikan aliran data tetap terjaga.
<img width="1244" height="294" alt="image" src="https://github.com/user-attachments/assets/3eda88bd-2e27-41c6-80e0-68a9e0d28622" />

- Manajemen Status Buffer & Offset:
Munculnya jeda waktu (latency) saat proses Consumer Group Rebalancing mengakibatkan beberapa data awal yang dikirim oleh Producer tidak tertangkap oleh Consumer. Kendala ini diselesaikan dengan memastikan urutan eksekusi yang tepat—menjalankan Consumer hingga status `Ready` sebelum mengaktifkan Producer, serta memantau proses Periodical Flush agar data dalam buffer tidak hilang saat terjadi interupsi sistem.




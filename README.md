# ETS-Bigdata

## Nyalakan Hadoop
docker-compose -f docker-compose-hadoop.yml up -d

## lalu nyalakan Kafka
docker-compose -f docker-compose-kafka.yml up -d

## inisialisasi Topic Kafka & Folder HDFS
## Buat Topic Kafka
docker exec -it kafka-broker kafka-topics.sh --create --topic weather-api --bootstrap-server localhost:9092
docker exec -it kafka-broker kafka-topics.sh --create --topic weather-rss --bootstrap-server localhost:9092

## Buat Direktori HDFS
docker exec -it namenode hdfs dfs -mkdir -p /data/weather/api/
docker exec -it namenode hdfs dfs -mkdir -p /data/weather/rss/
docker exec -it namenode hdfs dfs -mkdir -p /data/weather/hasil/

## Buat virtual environment
python -m venv env

## Aktifkan env (Windows)
env\Scripts\activate

## Install library yang dibutuhkan
pip install kafka-python requests feedparser hdfs pyspark pandas flask

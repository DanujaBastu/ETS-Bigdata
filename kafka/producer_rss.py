"""
Clarissa Aydin - 014: Producer RSS
producer_rss.py — WeatherPulse ETS Big Data
Mengambil berita cuaca dari RSS feed dan mengirim ke Kafka topic weather-rss
Polling interval: setiap 5 menit
"""
 
import json
import hashlib
import time
import logging
from datetime import datetime
 
import feedparser
from kafka import KafkaProducer
 
# =========================
# Konfigurasi
# =========================
BOOTSTRAP_SERVER = "localhost:9092"   # sama dengan producer_api.py 
TOPIC_NAME = "weather-rss"
INTERVAL_SECONDS = 300                # 5 menit
 
RSS_FEEDS = [
    "https://www.antaranews.com/rss/warta-bumi.xml",       # Berita lingkungan & cuaca Antara
    "https://www.republika.co.id/rss/leisure/info-sehat", # Alternatif (sering update lingkungan)
    "https://lapi.okezone.com/news/rss/622/rss.xml"       # Fokus ke news (cuaca sering masuk sini)
]
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RSS-Producer] %(message)s"
)
log = logging.getLogger(__name__)
 
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
# Tracking duplikat
# =========================
sent_ids: set[str] = set()
 
 
def make_key(url: str) -> str:
    """Hash 8 karakter dari URL — dipakai sebagai key Kafka (sesuai spesifikasi ETS)."""
    return hashlib.md5(url.encode()).hexdigest()[:8]
 
 
def parse_feed(feed_url: str) -> list[dict]:
    """Parse satu RSS feed, return list artikel."""
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        source = feed.feed.get("title", feed_url)
 
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url:
                continue
 
            article = {
                "article_id": make_key(url),
                "title":      entry.get("title", ""),
                "link":       url,
                "summary":    entry.get("summary", ""),
                "published":  entry.get("published", entry.get("updated", "")),
                "source":     source,
                "timestamp":  datetime.now().isoformat(),  # format sama dengan producer_api.py
            }
            articles.append(article)
 
        log.info(f"Fetched {len(articles)} artikel dari: {source}")
    except Exception as e:
        log.error(f"Gagal fetch {feed_url}: {e}")
 
    return articles
 
 
def send_articles():
    """Ambil semua feed lalu kirim artikel baru ke Kafka."""
    new_count = 0
 
    for feed_url in RSS_FEEDS:
        articles = parse_feed(feed_url)
 
        for article in articles:
            key = article["article_id"]
 
            if key in sent_ids:
                continue  # skip duplikat
 
            producer.send(
                topic=TOPIC_NAME,
                key=key,
                value=article,
            )
            sent_ids.add(key)
            new_count += 1
            log.info(f"[SUKSES] [{key}] {article['title'][:70]}")
 
    producer.flush()
    log.info(f"Total baru dikirim: {new_count} | Total unique: {len(sent_ids)}")
 
 
# =========================
# Main Loop
# =========================
if __name__ == "__main__":
    log.info("Producer RSS WeatherPulse berjalan... Tekan CTRL+C untuk berhenti.")
 
    while True:
        log.info("\nPolling RSS feeds...")
        send_articles()
        log.info(f"Menunggu {INTERVAL_SECONDS} detik...\n")
        time.sleep(INTERVAL_SECONDS)
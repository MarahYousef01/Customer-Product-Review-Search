"""Download a small sample of Amazon Electronics reviews."""

import csv
import gzip
import json
import re
import ssl
import certifi
from urllib.request import Request, urlopen

DATA_URL = (
    "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/"
    "raw/review_categories/Electronics.jsonl.gz"
)
OUTPUT_FILE = "amazon_reviews_raw.csv"
MAX_RECORDS = 20000


def normalize_for_duplicate_check(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


columns = [
    "doc_id", "title", "review_text", "rating",
    "product_id", "timestamp", "verified_purchase"
]

print("Connecting to the official Amazon Reviews 2023 data source...")
print("Reading Electronics reviews as a compressed stream...")

saved = 0
scanned = 0
seen_reviews = set()

request = Request(DATA_URL, headers={"User-Agent": "Mozilla/5.0"})

ssl_context = ssl.create_default_context(cafile=certifi.where())

with urlopen(request, timeout=60, context=ssl_context) as response:
    with gzip.GzipFile(fileobj=response) as compressed_file:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as output:
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()

            for line in compressed_file:
                scanned += 1

                try:
                    review = json.loads(line.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                title = str(review.get("title") or "").strip()
                body = str(review.get("text") or "").strip()

                if not body:
                    continue

                full_text = (title + " " + body).strip()
                duplicate_key = normalize_for_duplicate_check(full_text)

                if not duplicate_key or duplicate_key in seen_reviews:
                    continue

                seen_reviews.add(duplicate_key)
                saved += 1

                writer.writerow({
                    "doc_id": f"R{saved:05d}",
                    "title": title,
                    "review_text": body,
                    "rating": review.get("rating", ""),
                    "product_id": review.get("parent_asin") or review.get("asin") or "",
                    "timestamp": review.get("timestamp", ""),
                    "verified_purchase": review.get("verified_purchase", "")
                })

                if saved % 200 == 0:
                    print(f"Collected {saved} unique reviews...")

                if saved >= MAX_RECORDS:
                    break

print("\nDownload completed.")
print(f"Reviews scanned: {scanned}")
print(f"Unique reviews saved: {saved}")
print(f"Output file: {OUTPUT_FILE}")

if saved < 100:
    print("WARNING: Fewer than 100 reviews were collected.")

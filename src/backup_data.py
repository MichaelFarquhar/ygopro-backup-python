import json
from pathlib import Path

import requests

from src import BACKUP_DIR

API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
DATA_DIR = BACKUP_DIR / "data"
OUTPUT_PATH = DATA_DIR / "data.json"


def run() -> None:
    print(f"Fetching {API_URL} ...")
    response = requests.get(API_URL, timeout=120)
    response.raise_for_status()

    payload = response.json()
    data = payload["data"]

    DATA_DIR.mkdir(exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    count = len(data) if isinstance(data, list) else "unknown"
    print(f"Saved {count} records to {OUTPUT_PATH}")

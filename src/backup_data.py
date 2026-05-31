import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from src import BACKUP_DIR

DATA_DIR = BACKUP_DIR / "data"
DELAY_SECONDS = 2


@dataclass(frozen=True)
class Endpoint:
    tag: str
    url: str
    output: Path
    extract: Callable[[Any], Any] = lambda payload: payload


ENDPOINTS = (
    Endpoint(
        tag="Card Data",
        url="https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes",
        output=DATA_DIR / "data.json",
        extract=lambda payload: payload["data"],
    ),
    Endpoint(
        tag="Archetypes",
        url="https://db.ygoprodeck.com/api/v7/archetypes.php",
        output=DATA_DIR / "archetypes.json",
    ),
    Endpoint(
        tag="Card Sets",
        url="https://db.ygoprodeck.com/api/v7/cardsets.php",
        output=DATA_DIR / "cardsets.json",
    ),
)


def _log(tag: str, message: str) -> None:
    print(f"[{tag}] {message}")


def _record_count(data: Any) -> str:
    if isinstance(data, list):
        return f"{len(data):,}"
    return "unknown"


def _backup_endpoint(endpoint: Endpoint) -> None:
    _log(endpoint.tag, f"Fetching {endpoint.url}")
    response = requests.get(endpoint.url, timeout=120)
    response.raise_for_status()

    data = endpoint.extract(response.json())

    with endpoint.output.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    _log(endpoint.tag, f"Saved {_record_count(data)} records → {endpoint.output}")


def run() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    for index, endpoint in enumerate(ENDPOINTS):
        _backup_endpoint(endpoint)
        if index < len(ENDPOINTS) - 1:
            _log(endpoint.tag, f"⏳ Waiting {DELAY_SECONDS}s (rate limit) …")
            time.sleep(DELAY_SECONDS)

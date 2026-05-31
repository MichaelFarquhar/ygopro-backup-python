import json
import sys
import time
from pathlib import Path
from typing import Any

import requests
from PIL import Image
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn

from src import BACKUP_DIR, ensure_backup_dirs
from src.console import console

IMAGES_DIR = BACKUP_DIR / "images"
DATA_FILE = BACKUP_DIR / "data" / "data.json"
SAVED_FILE = IMAGES_DIR / "_saved.json"
DELAY_FULL_TO_CROPPED = 2
DELAY_BETWEEN_CARDS = 4


def load_saved_ids() -> set[int]:
    if not SAVED_FILE.exists():
        SAVED_FILE.write_text("[]", encoding="utf-8")
        return set()

    try:
        data = json.loads(SAVED_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON in {SAVED_FILE}:[/] {exc}")
        sys.exit(1)

    if not isinstance(data, list):
        console.print(f"[red]{SAVED_FILE} must contain a JSON array of card ids.[/]")
        sys.exit(1)

    return {int(card_id) for card_id in data}


def append_saved_id(card_id: int) -> None:
    ids = sorted(load_saved_ids() | {card_id})
    with SAVED_FILE.open("w", encoding="utf-8") as f:
        json.dump(ids, f, indent=2)


def download_and_convert(url: str, output_path: Path) -> None:
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    suffix = Path(url.split("?")[0]).suffix or ".img"
    tmp_path = output_path.parent / f"_tmp{suffix}"

    try:
        tmp_path.write_bytes(response.content)
        with Image.open(tmp_path) as img:
            img.convert("RGB").save(output_path, format="WEBP", quality=75, method=6)
    finally:
        tmp_path.unlink(missing_ok=True)


def _has_pending_downloads(cards: list[dict[str, Any]], saved_ids: set[int]) -> bool:
    for card in cards:
        card_id = int(card["id"])
        if card_id not in saved_ids and _card_image_urls(card) is not None:
            return True
    return False


def _card_image_urls(card: dict[str, Any]) -> tuple[str, str] | None:
    card_images = card.get("card_images")
    if not card_images:
        return None

    first = card_images[0]
    image_url = first.get("image_url")
    image_url_cropped = first.get("image_url_cropped")
    if not image_url or not image_url_cropped:
        return None

    return image_url, image_url_cropped


def _download_card_images(card_id: int, image_url: str, image_url_cropped: str) -> None:
    card_dir = IMAGES_DIR / str(card_id)
    card_dir.mkdir(parents=True, exist_ok=True)

    full_path = card_dir / f"{card_id}_full.webp"
    cropped_path = card_dir / f"{card_id}_cropped.webp"

    download_and_convert(image_url, full_path)
    time.sleep(DELAY_FULL_TO_CROPPED)
    download_and_convert(image_url_cropped, cropped_path)


def run() -> None:
    ensure_backup_dirs()
    IMAGES_DIR.mkdir(exist_ok=True)

    if not DATA_FILE.exists():
        console.print(f"[red]Missing {DATA_FILE}.[/] Run [bold]backup-data[/] first.")
        sys.exit(1)

    with DATA_FILE.open(encoding="utf-8") as f:
        cards = json.load(f)

    saved_ids = load_saved_ids()
    skipped = 0
    downloaded = 0
    warnings = 0

    with Progress(
        TextColumn("[bold blue]backup-images[/]"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("skipped: {task.fields[skipped]}"),
        TextColumn("downloaded: {task.fields[downloaded]}"),
        TextColumn("warnings: {task.fields[warnings]}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Processing cards",
            total=len(cards),
            skipped=0,
            downloaded=0,
            warnings=0,
        )

        for index, card in enumerate(cards):
            card_id = int(card["id"])

            if card_id in saved_ids:
                skipped += 1
                progress.update(task, advance=1, skipped=skipped)
                continue

            urls = _card_image_urls(card)
            if urls is None:
                warnings += 1
                card_name = card.get("name", "unknown")
                console.print(
                    f"[yellow]⚠[/] Skipping [bold]{card_id}[/] ({card_name}): "
                    "missing or invalid [bold]card_images[/]."
                )
                progress.update(task, advance=1, warnings=warnings)
                continue

            image_url, image_url_cropped = urls
            try:
                _download_card_images(card_id, image_url, image_url_cropped)
            except (OSError, requests.RequestException, Image.UnidentifiedImageError) as exc:
                console.print(f"[red]Failed to download card {card_id}:[/] {exc}")
                sys.exit(1)

            append_saved_id(card_id)
            saved_ids.add(card_id)
            downloaded += 1
            progress.update(task, advance=1, downloaded=downloaded)

            if _has_pending_downloads(cards[index + 1 :], saved_ids):
                time.sleep(DELAY_BETWEEN_CARDS)

    summary = (
        f"[bold]Total[/]     {len(cards):,}\n"
        f"[bold]Skipped[/]   {skipped:,}\n"
        f"[bold]Downloaded[/] {downloaded:,}\n"
        f"[bold]Warnings[/]  {warnings:,}"
    )
    console.print(Panel(summary, title="[green]Done[/]", border_style="green"))

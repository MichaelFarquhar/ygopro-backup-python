import urllib.request
from pathlib import Path

from PIL import Image
from rich.table import Table

from src import BACKUP_DIR, ensure_backup_dirs
from src.console import console

IMAGES_DIR = BACKUP_DIR / "images"


def download_image(url: str) -> tuple[Path, str]:
    clean_url = url.split("?")[0]
    suffix = Path(clean_url).suffix or ".img"
    stem = Path(clean_url).stem or "image"
    tmp_path = IMAGES_DIR / f"_tmp{suffix}"
    console.print(f"[bold]Downloading[/] [link={url}]{url}[/link] …")
    urllib.request.urlretrieve(url, tmp_path)
    return tmp_path, stem


def convert_to_webp(source: Path, stem: str) -> Path:
    output_path = IMAGES_DIR / f"{stem}.webp"

    with Image.open(source) as img:
        if img.mode in ("RGBA", "LA", "PA"):
            img.save(output_path, format="WEBP", lossless=True, quality=100, method=6)
        else:
            img = img.convert("RGB")
            img.save(output_path, format="WEBP", lossless=True, quality=100, method=6)

    return output_path


def run(url: str) -> None:
    ensure_backup_dirs()
    IMAGES_DIR.mkdir(exist_ok=True)

    tmp_path, stem = download_image(url)

    try:
        original_size = tmp_path.stat().st_size
        output_path = convert_to_webp(tmp_path, stem)
        output_size = output_path.stat().st_size

        savings = original_size - output_size
        savings_pct = (savings / original_size) * 100

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="dim")
        table.add_column(justify="right")
        table.add_row("Original", f"{original_size:,} bytes")
        table.add_row("Output", f"{output_size:,} bytes")
        table.add_row("File", f"[bold]{output_path.name}[/]")
        console.print(table)

        if savings < 0:
            console.print(
                f"[yellow]⚠[/] Output is [bold]{-savings:,}[/] bytes larger than the original "
                f"([bold]{-savings_pct:.1f}%[/] increase)."
            )
        else:
            console.print(
                f"[green]✓[/] Saved [bold]{savings:,}[/] bytes "
                f"([bold green]{savings_pct:.1f}%[/] reduction)."
            )

    finally:
        tmp_path.unlink(missing_ok=True)

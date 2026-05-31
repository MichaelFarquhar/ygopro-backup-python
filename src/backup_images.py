import urllib.request
from pathlib import Path

from PIL import Image

from src import BACKUP_DIR, ensure_backup_dirs

IMAGES_DIR = BACKUP_DIR / "images"


def download_image(url: str) -> tuple[Path, str]:
    clean_url = url.split("?")[0]
    suffix = Path(clean_url).suffix or ".img"
    stem = Path(clean_url).stem or "image"
    tmp_path = IMAGES_DIR / f"_tmp{suffix}"
    print(f"Downloading {url} ...")
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

        print(f"Original:  {original_size:,} bytes")
        print(f"Output:    {output_size:,} bytes  →  {output_path.name}")

        if savings < 0:
            print(f"⚠ Output is {-savings:,} bytes larger than the original ({-savings_pct:.1f}% increase).")
        else:
            print(f"✓ Saved {savings:,} bytes ({savings_pct:.1f}% reduction).")

    finally:
        tmp_path.unlink(missing_ok=True)

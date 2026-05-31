from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = PROJECT_ROOT / "backup"


def ensure_backup_dirs() -> None:
    BACKUP_DIR.mkdir(exist_ok=True)
    (BACKUP_DIR / "data").mkdir(exist_ok=True)
    (BACKUP_DIR / "images").mkdir(exist_ok=True)

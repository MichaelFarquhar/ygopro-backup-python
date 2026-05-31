import sys

from rich.table import Table

from src import ensure_backup_dirs
from src.backup_images import IMAGES_DIR, load_saved_ids
from src.console import console


def _image_dir_ids() -> tuple[set[int], list[str]]:
    numeric_ids: set[int] = set()
    invalid_names: list[str] = []

    for path in IMAGES_DIR.iterdir():
        if not path.is_dir():
            continue
        try:
            numeric_ids.add(int(path.name))
        except ValueError:
            invalid_names.append(path.name)

    return numeric_ids, invalid_names


def run() -> None:
    ensure_backup_dirs()
    IMAGES_DIR.mkdir(exist_ok=True)

    saved_ids = load_saved_ids()
    dir_ids, invalid_names = _image_dir_ids()

    dirs_without_saved = sorted(dir_ids - saved_ids)
    saved_without_dirs = sorted(saved_ids - dir_ids)

    if invalid_names:
        console.print("[yellow]Non-numeric image directories:[/]")
        for name in sorted(invalid_names):
            console.print(f"  [yellow]•[/] {name}")

    if not dirs_without_saved and not saved_without_dirs:
        console.print(
            f"[green]✓[/] All {len(saved_ids):,} saved ids match image directories."
        )
        return

    table = Table(title="Image verification mismatches", show_lines=True)
    table.add_column("Issue", style="bold")
    table.add_column("Ids")

    if dirs_without_saved:
        table.add_row(
            "Directories missing from _saved.json",
            ", ".join(str(card_id) for card_id in dirs_without_saved),
        )

    if saved_without_dirs:
        table.add_row(
            "Saved ids missing image directories",
            ", ".join(str(card_id) for card_id in saved_without_dirs),
        )

    console.print(table)
    sys.exit(1)

import argparse
import sys

from src import backup_data, backup_images, verify_images


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and backup YGOPro card data and images.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("backup-data", help="Fetch card data from the YGOPRODeck API")

    subparsers.add_parser(
        "backup-images",
        help="Download card images from data.json",
    )

    subparsers.add_parser(
        "verify-images",
        help="Verify image folders match _saved.json",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "backup-data":
        backup_data.run()
    elif args.command == "backup-images":
        backup_images.run()
    elif args.command == "verify-images":
        verify_images.run()
    else:
        parser.print_help()
        sys.exit(1)

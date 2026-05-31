import argparse
import sys

from src import backup_data, backup_images


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and backup YGOPro card data and images.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("backup-data", help="Fetch card data from the YGOPRODeck API")

    backup_images_parser = subparsers.add_parser(
        "backup-images",
        help="Download an image from a URL and convert it to lossless WEBP",
    )
    backup_images_parser.add_argument("url", help="URL of the image to download and convert")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "backup-data":
        backup_data.run()
    elif args.command == "backup-images":
        backup_images.run(args.url)
    else:
        parser.print_help()
        sys.exit(1)

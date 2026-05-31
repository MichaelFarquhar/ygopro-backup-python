# YGOPro Backup CLI

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![UV](https://img.shields.io/badge/uv-30173d?style=for-the-badge&logo=uv&logoColor=DE5FE9)

A Python CLI for archiving YGOPro content from [YGOPRODeck](https://ygoprodeck.com/). It fetches card metadata, archetypes, and set data; downloads full and cropped card images from that data; converts images to WEBP; and verifies that saved progress matches the image folders on disk.

| Command | Purpose |
| --- | --- |
| `backup-data` | Fetch card info, archetypes, and card sets from the YGOPRODeck API into `backup/data/` |
| `backup-images` | Download and convert card images from `data.json` into `backup/images/{id}/` (resumable via `_saved.json`) |
| `verify-images` | Confirm image subdirectories match the ids recorded in `_saved.json` |

## 📦 Installation

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
uv sync
```

## 🚀 Usage

Commands create `backup/` with `data/` and `images/` subfolders automatically if missing.

### Api Data

Fetch card data from the YGOPRODeck API:

```bash
uv run main.py backup-data
```

Output is saved under `backup/data/`:

- `data.json` — card info
- `archetypes.json` — archetype names
- `cardsets.json` — TCG set metadata

### Card Images

Download full and cropped card images from `data.json`:

```bash
uv run main.py backup-images
```

Requires `backup/data/data.json` (run `backup-data` first). Progress is tracked in `backup/images/_saved.json` so interrupted runs can resume.

Output layout:

```
backup/images/
  _saved.json
  80181649/
    80181649_full.webp
    80181649_cropped.webp
```

### Verify Images

Check that image subdirectories match the ids listed in `_saved.json`:

```bash
uv run main.py verify-images
```

Exits with code 1 if any directory is missing from `_saved.json` or any saved id has no matching directory.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

## ⚠️ Disclaimer

These scripts are intended for backup and archival use only — not for scraping, spamming, or any other malicious or abusive activity. They are designed to download YGOPro card data and images in a responsible way, in line with the YGOPRODeck API guidelines. Please run them sparingly, respect rate limits, and avoid hammering endpoints with repeated or automated requests beyond what the API allows. I am not responsible for any IP bans or other restrictions that result from you running this tool.

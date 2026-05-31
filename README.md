# YGOPro Data Backup Python Script

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![UV](https://img.shields.io/badge/uv-30173d?style=for-the-badge&logo=uv&logoColor=DE5FE9)

A small CLI script that downloads an image from a URL, converts it to WEBP, and applies lossless compression — reducing file size without any quality loss.

## 📦 Installation

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
uv sync
```

## 🚀 Usage

Fetch card data from the YGOPRODeck API:

```bash
uv run main.py backup-data
```

Output is saved to `backup/data/data.json`.

Convert an image from a URL:

```bash
uv run main.py backup-images "https://example.com/photo.png"
```

Output is saved to the `backup/images/` folder, named after the original file:

```
backup/images/photo.webp
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

## ⚠️ Disclaimer

These scripts are intended for backup and archival use only — not for scraping, spamming, or any other malicious or abusive activity. They are designed to download YGOPro card data and images in a responsible way, in line with the YGOPRODeck API guidelines. Please run them sparingly, respect rate limits, and avoid hammering endpoints with repeated or automated requests beyond what the API allows. I am not responsible for any IP bans or other restrictions that result from you running this tool.

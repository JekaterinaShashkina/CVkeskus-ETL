from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

RSS_DIR = RAW_DATA_DIR / "rss"
HTML_DIR = RAW_DATA_DIR / "html"
IMAGES_DIR = RAW_DATA_DIR / "images"

PROCESSED_DIR = DATA_DIR / "processed"
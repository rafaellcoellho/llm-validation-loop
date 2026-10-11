import json
from pathlib import Path

SOURCE_COMMIT = "abb8e438d1a0db29646998e1348ab7de9d924a8b"
SOURCE_REPO = "https://raw.githubusercontent.com/Strvm/vnzla-libre"
SOURCE_BASE = f"{SOURCE_REPO}/{SOURCE_COMMIT}"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"
SAMPLE_PATH = DATA_DIR / "sample.json"


def image_url(image_name):
    return f"{SOURCE_BASE}/images/{image_name}"


def image_path(image_name):
    return IMAGES_DIR / image_name


def load_sample():
    return json.loads(SAMPLE_PATH.read_text())

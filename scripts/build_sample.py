import json
import random
import urllib.error
import urllib.request
from collections import defaultdict

from dataset import IMAGES_DIR, SAMPLE_PATH, SOURCE_BASE, image_path, image_url

SEED = 2024
PER_FAMILY = 100


def main():
    records = _download_json(f"{SOURCE_BASE}/outputs/qr_data.json")
    candidates = _one_record_per_acta(records)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    sample = []

    for family in ("high_res", "low_res"):
        sample += _pick_family(candidates, family)

    SAMPLE_PATH.write_text(json.dumps(sample, indent=2) + "\n")
    print(f"✅ {len(sample)} tally sheets written to {SAMPLE_PATH.name}")


def _download_json(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.load(response)


def _one_record_per_acta(records):
    by_acta = defaultdict(list)

    for record in records:
        by_acta[record["acta_id"]].append(record)

    return [group[0] for group in by_acta.values() if _is_consistent(group)]


def _is_consistent(group):
    return len({record["data"] for record in group}) == 1


def _family_of(record):
    return "high_res" if record["image_path"].startswith("AG8A") else "low_res"


def _pick_family(candidates, family):
    pool = [
        r for r in candidates if _family_of(r) == family and " " not in r["image_path"]
    ]
    random.Random(SEED).shuffle(pool)
    picked = []

    for record in pool:
        if len(picked) == PER_FAMILY:
            break
        if _download_image(record["image_path"]):
            picked.append(_sample_entry(record, family))

    return picked


def _sample_entry(record, family):
    return {
        "acta_id": record["acta_id"],
        "family": family,
        "image": record["image_path"],
        "qr": record["data"],
    }


def _download_image(image_name):
    target = image_path(image_name)
    if target.exists():
        return True

    try:
        urllib.request.urlretrieve(image_url(image_name), target)
    except urllib.error.HTTPError:
        return False

    return True


if __name__ == "__main__":
    main()

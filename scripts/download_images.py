import urllib.request

from dataset import IMAGES_DIR, image_path, image_url, load_sample


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    missing = [e["image"] for e in load_sample() if not image_path(e["image"]).exists()]

    for image_name in missing:
        urllib.request.urlretrieve(image_url(image_name), image_path(image_name))

    print(f"✅ {len(missing)} images downloaded to {IMAGES_DIR}")


if __name__ == "__main__":
    main()

from io import BytesIO

from PIL import Image

CONTENT_HEIGHT_RATIO = 0.68
SEGMENT_COUNT = 3
SEGMENT_OVERLAP = 80


def load_content(path):
    image = Image.open(path).convert("L")
    bottom = int(image.height * CONTENT_HEIGHT_RATIO)

    return image.crop((0, 0, image.width, bottom))


def split_vertically(image, count=SEGMENT_COUNT, overlap=SEGMENT_OVERLAP):
    step = image.height // count
    segments = []

    for index in range(count):
        top = max(0, index * step - overlap)
        bottom = min(image.height, (index + 1) * step + overlap)
        segments.append(image.crop((0, top, image.width, bottom)))

    return segments


def to_jpeg_bytes(image):
    buffer = BytesIO()
    image.save(buffer, "JPEG", quality=90)

    return buffer.getvalue()

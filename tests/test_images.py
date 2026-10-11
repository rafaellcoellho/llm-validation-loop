from PIL import Image

from tally_sheet.images import load_content, split_vertically, to_jpeg_bytes


def test_keeps_only_the_top_of_the_sheet(tmp_path):
    path = tmp_path / "sheet.jpg"
    Image.new("RGB", (600, 10000), "white").save(path)

    content = load_content(path)

    assert content.size == (600, 6800)
    assert content.mode == "L"


def test_splits_into_overlapping_segments():
    image = Image.new("L", (600, 3000))

    segments = split_vertically(image, count=3, overlap=80)

    assert [segment.size for segment in segments] == [
        (600, 1080),
        (600, 1160),
        (600, 1080),
    ]


def test_encodes_as_jpeg():
    assert to_jpeg_bytes(Image.new("L", (10, 10))).startswith(b"\xff\xd8")

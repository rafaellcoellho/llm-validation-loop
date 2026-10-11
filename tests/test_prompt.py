from tally_sheet.ballot import PARTIES
from tally_sheet.prompt import build_prompt


def test_lists_every_expected_party():
    prompt = build_prompt("vision")

    assert all(party in prompt for party in PARTIES)


def test_vision_asks_to_copy_as_printed():
    assert "Copy both exactly as printed." in build_prompt("vision")


def test_ocr_asks_to_recover_from_recognition_errors():
    prompt = build_prompt("ocr")

    assert "recognition errors" in prompt
    assert "Copy both exactly as printed." not in prompt

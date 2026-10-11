from tally_sheet.scoring import score_tally_sheet
from tests.factories import SAMPLE_TRUTH, number, sheet_output, with_party_votes


def test_exact_when_every_field_matches():
    score = score_tally_sheet(sheet_output(), SAMPLE_TRUTH)

    assert score.exact
    assert score.wrong_fields == []


def test_lists_each_wrong_field():
    output = with_party_votes(sheet_output(), 35, 263)
    output["summary"]["null"] = number(1)

    score = score_tally_sheet(output, SAMPLE_TRUTH)

    assert not score.exact
    assert score.wrong_fields == ["MUD", "null"]


def test_missing_rows_count_as_wrong():
    output = sheet_output()
    output["parties"] = output["parties"][:36]

    assert score_tally_sheet(output, SAMPLE_TRUTH).wrong_fields == [
        "CENTRADOS",
        "CONDE",
    ]


def test_everything_is_wrong_when_output_breaks_the_schema():
    score = score_tally_sheet({"unparsable_response": "?"}, SAMPLE_TRUTH)

    assert len(score.wrong_fields) == 42

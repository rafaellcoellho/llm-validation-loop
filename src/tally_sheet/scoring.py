from dataclasses import dataclass

from pydantic import ValidationError

from tally_sheet.ballot import PARTIES
from tally_sheet.schema import TallySheet


@dataclass(frozen=True)
class Score:
    wrong_fields: list[str]

    @property
    def exact(self):
        return not self.wrong_fields


def score_tally_sheet(output, truth):
    expected = _expected_values(truth)

    try:
        sheet = TallySheet.model_validate(output)
    except ValidationError:
        return Score(list(expected))

    found = _found_values(sheet)

    return Score(
        [field for field, value in expected.items() if found.get(field) != value]
    )


def _expected_values(truth):
    summary = {
        "total": truth.total,
        "valid": truth.valid,
        "null": truth.null,
        "blank": truth.blank,
    }

    return {**dict(zip(PARTIES, truth.party_votes)), **summary}


def _found_values(sheet):
    summary = sheet.summary
    parties = [row.votes.digits for row in sheet.parties]
    totals = {
        "total": summary.total.digits,
        "valid": summary.valid.digits,
        "null": summary.null.digits,
        "blank": summary.blank.digits,
    }

    return {**dict(zip(PARTIES, parties)), **totals}

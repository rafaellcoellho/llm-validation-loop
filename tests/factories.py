import copy

from tally_sheet.ballot import PARTIES
from tally_sheet.ground_truth import GroundTruth

SPANISH_DIGITS = ("Cero", "Uno", "Dos", "Tres", "Cuatro")
SPANISH_DIGITS += ("Cinco", "Seis", "Siete", "Ocho", "Nueve")

SAMPLE_VOTES = (108, 5, 9, 0, 0, 1, 0, 0, 11, 2, 1, 0, 4) + (0, 1, 0, 0, 0, 0)
SAMPLE_VOTES += (0,) * 11 + (1, 0, 0, 25, 14, 253, 0, 0)

SAMPLE_TRUTH = GroundTruth("210203002.03.1.0001", SAMPLE_VOTES, null=0, blank=0)


def spell(value):
    return ", ".join(SPANISH_DIGITS[int(char)] for char in f"{value:04d}")


def number(value):
    return {"digits": value, "words": spell(value)}


def sheet_output(truth=SAMPLE_TRUTH, registered_voters=978):
    parties = [
        {"party": party, "votes": number(votes)}
        for party, votes in zip(PARTIES, truth.party_votes)
    ]
    summary = {
        "total": number(truth.total),
        "valid": number(truth.valid),
        "null": number(truth.null),
        "blank": number(truth.blank),
    }

    return {
        "registered_voters": registered_voters,
        "voters_on_machine": number(truth.total),
        "parties": parties,
        "summary": summary,
    }


def with_party_votes(output, party_index, value, words=None):
    changed = copy.deepcopy(output)
    changed["parties"][party_index]["votes"] = {
        "digits": value,
        "words": words or spell(value),
    }

    return changed

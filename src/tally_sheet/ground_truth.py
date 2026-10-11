from dataclasses import dataclass

from tally_sheet.ballot import PARTIES


@dataclass(frozen=True)
class GroundTruth:
    acta_id: str
    party_votes: tuple[int, ...]
    null: int
    blank: int

    @property
    def valid(self):
        return sum(self.party_votes)

    @property
    def total(self):
        return self.valid + self.null + self.blank


def parse_qr(data):
    acta_id, votes, null, blank = data.split("!")
    party_votes = tuple(int(value) for value in votes.split(","))
    if len(party_votes) != len(PARTIES):
        raise ValueError(f"expected {len(PARTIES)} party votes, got {len(party_votes)}")

    return GroundTruth(acta_id, party_votes, int(null), int(blank))

import pytest

from tally_sheet.ground_truth import parse_qr

QR = (
    "090501002.02.1.0001!77,4,6,3,2,1,0,1,5,0,0,3,10,0,0,0,0,2,0,1,0,0,0,0,"
    "0,0,0,0,1,1,0,0,1,19,15,252,1,1!1!0"
)


def test_parses_acta_id_votes_null_and_blank():
    truth = parse_qr(QR)

    assert truth.acta_id == "090501002.02.1.0001"
    assert truth.party_votes[:3] == (77, 4, 6)
    assert (truth.null, truth.blank) == (1, 0)


def test_valid_is_the_sum_of_party_votes():
    assert parse_qr(QR).valid == 406


def test_total_adds_null_and_blank():
    assert parse_qr(QR).total == 407


def test_rejects_wrong_number_of_parties():
    with pytest.raises(ValueError, match="expected 38 party votes, got 2"):
        parse_qr("id!1,2!0!0")

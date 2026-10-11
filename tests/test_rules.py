import copy

from tally_sheet.rules import validate_tally_sheet
from tests.factories import number, sheet_output, with_party_votes

MUD = 35


def rules_of(violations):
    return [violation.rule for violation in violations]


def test_consistent_sheet_has_no_violations():
    assert validate_tally_sheet(sheet_output()) == []


def test_schema_violation_when_fields_are_missing():
    violations = validate_tally_sheet({"parties": []})

    assert rules_of(violations) == ["schema"]
    assert "registered_voters" in violations[0].message


def test_schema_violation_for_unparsable_response():
    violations = validate_tally_sheet({"unparsable_response": "oops"})

    assert rules_of(violations) == ["schema"]


def test_party_order_violation_when_a_row_is_missing():
    output = sheet_output()
    output["parties"].pop(3)
    output["summary"]["valid"] = number(435)

    assert "party_order" in rules_of(validate_tally_sheet(output))


def test_party_order_accepts_case_and_spacing_differences():
    output = sheet_output()
    output["parties"][0]["party"] = " psuv "

    assert validate_tally_sheet(output) == []


def test_digits_that_disagree_with_words():
    output = with_party_votes(sheet_output(), MUD, 263, words="Cero, Dos, Cinco, Tres")

    violations = validate_tally_sheet(output)

    assert rules_of(violations) == ["digits_match_words", "party_sum"]
    assert "MUD: digits say 263, but the words" in violations[0].message
    assert "say 253" in violations[0].message


def test_words_that_are_not_digit_words():
    output = with_party_votes(sheet_output(), MUD, 253, words="Dos Cinco Tres")

    violations = validate_tally_sheet(output)

    assert rules_of(violations) == ["digits_match_words"]
    assert "is not a list of Spanish digit words" in violations[0].message


def test_party_sum_that_differs_from_valid_votes():
    output = with_party_votes(sheet_output(), MUD, 263)

    violations = validate_tally_sheet(output)

    assert rules_of(violations) == ["party_sum"]
    assert violations[0].message == (
        "The party votes add up to 445, but 'Votos validos' is 435 (difference +10)."
    )


def test_summary_total_that_differs_from_its_parts():
    output = sheet_output()
    output["summary"]["null"] = number(2)

    violations = validate_tally_sheet(output)

    assert rules_of(violations) == ["summary_total"]
    assert "valid + null + blank = 435 + 2 + 0 = 437" in violations[0].message


def test_machine_voters_that_differ_from_total_votes():
    output = sheet_output()
    output["voters_on_machine"] = number(436)

    violations = validate_tally_sheet(output)

    assert rules_of(violations) == ["machine_voters"]
    assert violations[0].message == (
        "'En la maquina de votacion' is 436, but 'Votos' is 435."
    )


def test_total_votes_above_registered_voters():
    output = copy.deepcopy(sheet_output(registered_voters=400))

    violations = validate_tally_sheet(output)

    assert rules_of(violations) == ["registered_voters"]
    assert violations[0].message == "'Votos' (435) is greater than 'Electores' (400)."

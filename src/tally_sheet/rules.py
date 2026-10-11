from pydantic import ValidationError

from llm_validation_loop import Violation
from tally_sheet.ballot import PARTIES
from tally_sheet.schema import TallySheet
from tally_sheet.spanish_numbers import parse_digit_words


def validate_tally_sheet(output):
    try:
        sheet = TallySheet.model_validate(output)
    except ValidationError as error:
        return [Violation("schema", _describe_schema_error(error))]

    return [violation for rule in RULES for violation in rule(sheet)]


def check_party_order(sheet):
    found = tuple(row.party.strip().upper() for row in sheet.parties)
    if found == PARTIES:
        return []

    message = (
        f"Expected the {len(PARTIES)} party rows in ballot order "
        f"({', '.join(PARTIES)}), got {len(found)} rows: {', '.join(found)}."
    )

    return [Violation("party_order", message)]


def check_digits_match_words(sheet):
    violations = []

    for label, number in _numbers_of(sheet):
        violation = _compare_digits_and_words(label, number)
        if violation:
            violations.append(violation)

    return violations


def check_party_sum(sheet):
    party_sum = sum(row.votes.digits for row in sheet.parties)
    valid = sheet.summary.valid.digits
    if party_sum == valid:
        return []

    message = (
        f"The party votes add up to {party_sum}, but 'Votos validos' is {valid} "
        f"(difference {party_sum - valid:+d})."
    )

    return [Violation("party_sum", message)]


def check_summary_total(sheet):
    summary = sheet.summary
    parts = summary.valid.digits + summary.null.digits + summary.blank.digits
    if parts == summary.total.digits:
        return []

    message = (
        f"'Votos' is {summary.total.digits}, but valid + null + blank = "
        f"{summary.valid.digits} + {summary.null.digits} + {summary.blank.digits}"
        f" = {parts}."
    )

    return [Violation("summary_total", message)]


def check_machine_voters(sheet):
    voters = sheet.voters_on_machine.digits
    total = sheet.summary.total.digits
    if voters == total:
        return []

    message = f"'En la maquina de votacion' is {voters}, but 'Votos' is {total}."

    return [Violation("machine_voters", message)]


def check_registered_voters(sheet):
    total = sheet.summary.total.digits
    registered = sheet.registered_voters
    if total <= registered:
        return []

    message = f"'Votos' ({total}) is greater than 'Electores' ({registered})."

    return [Violation("registered_voters", message)]


RULES = (
    check_party_order,
    check_digits_match_words,
    check_party_sum,
    check_summary_total,
    check_machine_voters,
    check_registered_voters,
)


def _numbers_of(sheet):
    summary = sheet.summary
    parties = [(row.party, row.votes) for row in sheet.parties]
    totals = [
        ("Votos", summary.total),
        ("Votos validos", summary.valid),
        ("Votos nulos", summary.null),
        ("Votos vacios", summary.blank),
    ]

    return [("En la maquina de votacion", sheet.voters_on_machine), *parties, *totals]


def _compare_digits_and_words(label, number):
    try:
        spelled = parse_digit_words(number.words)
    except ValueError:
        message = f"{label}: '{number.words}' is not a list of Spanish digit words."
        return Violation("digits_match_words", message)

    if spelled == number.digits:
        return None

    message = (
        f"{label}: digits say {number.digits}, "
        f"but the words '{number.words}' say {spelled}."
    )

    return Violation("digits_match_words", message)


def _describe_schema_error(error):
    problems = [
        f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
        for item in error.errors()[:5]
    ]

    return "The JSON does not match the schema. " + "; ".join(problems)

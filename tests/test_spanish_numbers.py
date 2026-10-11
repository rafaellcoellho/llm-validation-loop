import pytest

from tally_sheet.spanish_numbers import parse_digit_words


def test_parses_four_spelled_digits():
    assert parse_digit_words("Cero, Dos, Cinco, Tres") == 253


def test_parses_all_zeros():
    assert parse_digit_words("Cero, Cero, Cero, Cero") == 0


def test_ignores_case_accents_and_spacing():
    assert parse_digit_words("  cero,SÉIS ,  Nueve,uno ") == 691


def test_ignores_trailing_comma():
    assert parse_digit_words("Cero, Uno,") == 1


def test_rejects_unknown_word():
    with pytest.raises(ValueError, match="unknown digit word 'once'"):
        parse_digit_words("Cero, Once")


def test_rejects_empty_text():
    with pytest.raises(ValueError, match="no digit words"):
        parse_digit_words(" , ")

from llm_validation_loop import Attempt, Violation, build_feedback


def test_lists_each_failed_check_of_the_round():
    attempt = Attempt(
        round=2,
        output={},
        violations=[
            Violation("party_sum", "The party votes add up to 445"),
            Violation("digits_match_words", "MUD: digits say 263"),
        ],
    )

    feedback = build_feedback(attempt)

    assert feedback.startswith("Your answer in round 2 failed these checks:")
    assert "- [party_sum] The party votes add up to 445" in feedback
    assert "- [digits_match_words] MUD: digits say 263" in feedback


def test_asks_to_reread_instead_of_forcing_the_check():
    attempt = Attempt(round=1, output={}, violations=[Violation("x", "y")])

    assert "Do not change a value just to make a check pass" in build_feedback(attempt)


def test_caps_messages_per_rule():
    violations = [Violation("digits_match_words", f"row {i}") for i in range(14)]
    violations.append(Violation("party_sum", "off by 10"))
    attempt = Attempt(round=1, output={}, violations=violations)

    lines = build_feedback(attempt).splitlines()

    assert "- [digits_match_words] row 9" in lines
    assert "- [digits_match_words] row 10" not in lines
    assert "- [digits_match_words] ... and 4 more like these." in lines
    assert "- [party_sum] off by 10" in lines

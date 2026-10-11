from llm_validation_loop import Extraction, Violation, run_validation_loop


def validate_answer(output):
    if output["answer"] == 42:
        return []

    return [Violation("answer", f"expected 42, got {output['answer']}")]


class ScriptedExtractor:
    def __init__(self, answers):
        self.answers = list(answers)
        self.histories = []

    def __call__(self, history):
        self.histories.append(history)

        return Extraction({"answer": self.answers.pop(0)}, {"output_tokens": 10})


def test_stops_at_the_first_round_that_passes():
    result = run_validation_loop(ScriptedExtractor([42]), validate_answer)

    assert result.passed
    assert len(result.attempts) == 1


def test_corrects_itself_with_the_previous_attempts():
    extractor = ScriptedExtractor([41, 42])

    result = run_validation_loop(extractor, validate_answer)

    assert result.passed
    assert [a.output["answer"] for a in result.attempts] == [41, 42]
    assert extractor.histories[1][0].violations[0].message == "expected 42, got 41"


def test_gives_up_after_max_rounds():
    extractor = ScriptedExtractor([1, 2, 3, 4])

    result = run_validation_loop(extractor, validate_answer, max_rounds=3)

    assert not result.passed
    assert len(result.attempts) == 3
    assert extractor.answers == [4]


def test_each_round_sees_only_earlier_attempts():
    extractor = ScriptedExtractor([1, 2, 42])

    run_validation_loop(extractor, validate_answer)

    assert [len(history) for history in extractor.histories] == [0, 1, 2]


def test_result_serializes_attempts_with_usage():
    result = run_validation_loop(ScriptedExtractor([41, 42]), validate_answer)

    serialized = result.to_dict()

    assert serialized["passed"] is True
    assert serialized["attempts"][0]["violations"][0]["rule"] == "answer"
    assert serialized["attempts"][1]["usage"] == {"output_tokens": 10}

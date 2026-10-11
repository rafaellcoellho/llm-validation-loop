from llm_validation_loop.attempt import Attempt, LoopResult


def run_validation_loop(extract, validate, max_rounds=3):
    attempts = []

    for round_number in range(1, max_rounds + 1):
        attempt = _run_round(extract, validate, attempts, round_number)
        attempts.append(attempt)
        if attempt.passed:
            break

    return LoopResult(attempts)


def _run_round(extract, validate, history, round_number):
    extraction = extract(list(history))
    violations = validate(extraction.output)

    return Attempt(round_number, extraction.output, violations, extraction.usage)

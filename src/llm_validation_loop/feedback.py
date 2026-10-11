from itertools import groupby

MAX_MESSAGES_PER_RULE = 10

INSTRUCTION = (
    "Look at the source again, only at the fields involved, and fix what was "
    "misread. Do not change a value just to make a check pass: if a value "
    "really reads that way, keep it. Return the complete JSON again."
)


def build_feedback(attempt):
    header = f"Your answer in round {attempt.round} failed these checks:"
    by_rule = groupby(attempt.violations, key=lambda violation: violation.rule)
    checks = [line for rule, group in by_rule for line in _rule_lines(rule, group)]

    return "\n".join([header, *checks, "", INSTRUCTION])


def _rule_lines(rule, violations):
    violations = list(violations)
    shown = violations[:MAX_MESSAGES_PER_RULE]
    lines = [f"- [{rule}] {violation.message}" for violation in shown]
    hidden = len(violations) - len(shown)
    if hidden:
        lines.append(f"- [{rule}] ... and {hidden} more like these.")

    return lines

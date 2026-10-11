from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Violation:
    rule: str
    message: str


@dataclass(frozen=True)
class Extraction:
    output: dict
    usage: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Attempt:
    round: int
    output: dict
    violations: list[Violation]
    usage: dict = field(default_factory=dict)

    @property
    def passed(self):
        return not self.violations


@dataclass(frozen=True)
class LoopResult:
    attempts: list[Attempt]

    @property
    def final(self):
        return self.attempts[-1]

    @property
    def passed(self):
        return self.final.passed

    def to_dict(self):
        return {"passed": self.passed, "attempts": [asdict(a) for a in self.attempts]}

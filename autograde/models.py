from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    passed: bool
    points: int
    feedback: str | None = None


@dataclass
class GradeResult:
    score: int
    max_score: int
    tests: list[TestResult]
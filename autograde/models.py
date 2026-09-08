from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    passed: bool
    points: int
    feedback: str | None = None
    runtime_ms: float | None = None


@dataclass
class GradeResult:
    score: int
    max_score: int
    tests: list[TestResult]
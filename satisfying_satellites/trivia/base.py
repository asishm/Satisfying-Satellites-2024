from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    """A question."""

    category: str
    question: str
    answers: list[str]

"""The one hard-coded truth: positives and negatives exist.

That is all this module asserts. There is no name for what is positive or
negative, no scale that means anything in itself, no list of causes, and no
instruction to seek one or avoid the other. Everything about valence beyond
its sign is left for the system to grow from living.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Valence:
    value: float

    @property
    def sign(self) -> int:
        if self.value > 0:
            return 1
        if self.value < 0:
            return -1
        return 0

    @property
    def magnitude(self) -> float:
        return abs(self.value)

    def __repr__(self) -> str:
        return f"{self.value:+.3f}"


class TruthViolation(Exception):
    """Raised when a shell cannot produce both signs."""


def assert_truth(possible_values) -> None:
    """A shell is admissible only if both signs can actually be lived in it.

    This is the single invariant the core enforces on any space it is placed
    in. A world of only positives, or only negatives, is not a world the core
    can grow meaning in, because the one truth would be unobservable.
    """
    signs = {Valence(v).sign for v in possible_values}
    if 1 not in signs or -1 not in signs:
        raise TruthViolation(
            f"shell cannot produce both signs (saw {sorted(signs)})"
        )

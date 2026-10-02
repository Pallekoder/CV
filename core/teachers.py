"""Peer teachers.

Teachers look at the channel and offer a perspective. They cannot change
anything: they receive a read-only view and return a Perspective object. A
perspective may carry a proposal (a rule the teacher sees in the lived
material) or a doubt (a category the teacher thinks no longer holds), and a
remark.

The remark is in human language for the transcript, so the distant figure
can follow along. The mind never reads remarks; it reads only proposals and
doubts, and treats them as candidates to test against consequence, never as
decrees. Many teachers, each partial, is the point.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .channel import ChannelView, Rule, purity


@dataclass(frozen=True)
class Perspective:
    source: str
    tick: int
    remark: str
    proposal: Optional[Rule] = None
    doubt: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "tick": self.tick,
            "remark": self.remark,
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "doubt": self.doubt,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Perspective":
        p = d.get("proposal")
        return cls(
            source=d["source"],
            tick=d["tick"],
            remark=d["remark"],
            proposal=Rule.from_dict(p) if p else None,
            doubt=d.get("doubt"),
        )


class Teacher(Protocol):
    id: str

    def regard(self, view: ChannelView, tick: int) -> Perspective: ...


def _dist(a: tuple, b: tuple) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


class AxisTeacher:
    """Sees the world along one axis only.

    If the open bucket holds both signs, it looks for the line on its axis
    that best sorts them, and proposes it. It has no idea whether its axis
    is the one that matters. That is for consequence to say.
    """

    def __init__(self, axis: int) -> None:
        self.axis = axis
        self.id = f"axis-{axis}"

    def regard(self, view: ChannelView, tick: int) -> Perspective:
        lived = view.valenced(view.open)
        if {e.sign for e in lived} != {1, -1}:
            return Perspective(self.id, tick, "I see only one sign here, or none; nothing to divide.")
        points = sorted((e.features[self.axis], e.sign) for e in lived)
        n = len(points)
        total_pos = sum(1 for _, s in points if s > 0)
        best = None
        pos_lo = 0
        for i in range(1, n):
            if points[i - 1][1] > 0:
                pos_lo += 1
            if points[i][0] == points[i - 1][0]:
                continue
            lo_n, hi_n = i, n - i
            pos_hi = total_pos - pos_lo
            sorted_right = max(pos_lo, lo_n - pos_lo) + max(pos_hi, hi_n - pos_hi)
            if best is None or sorted_right > best[0]:
                best = (sorted_right, (points[i - 1][0] + points[i][0]) / 2)
        if best is None:
            return Perspective(
                self.id, tick,
                "Along my axis everything sits in the same place; I cannot tell the signs apart.",
            )
        sorted_right, thr = best
        return Perspective(
            self.id, tick,
            f"Along axis {self.axis} a line at {thr:.3f} sorts {sorted_right} of {n}.",
            proposal=Rule(axis=self.axis, threshold=thr),
        )


class NearnessTeacher:
    """Looks at pairs, not axes, and only at recent ones.

    Finds the two closest lived experiences with opposite consequences. If they
    are far apart it proposes the axis along which they differ most. If they
    are the same on the surface, it says so and proposes nothing: this is the
    paradox, and no surface rule will resolve it.
    """

    id = "nearness"
    WINDOW = 80  # it only remembers the most recent consequences

    def regard(self, view: ChannelView, tick: int) -> Perspective:
        lived = view.valenced(view.experiences)[-self.WINDOW:]
        best = None
        for i, a in enumerate(lived):
            for b in lived[i + 1:]:
                if a.sign * b.sign < 0:
                    d = _dist(a.features, b.features)
                    if best is None or d < best[0]:
                        best = (d, a, b)
        if best is None:
            return Perspective(self.id, tick, "No two things of opposite consequence to compare yet.")
        d, a, b = best
        if d < 1e-9:
            return Perspective(
                self.id, tick,
                f"#{a.index} and #{b.index} are the same on every surface and opposite in consequence. "
                "Nothing you can see tells them apart.",
            )
        axis = max(range(len(a.features)), key=lambda k: abs(a.features[k] - b.features[k]))
        threshold = (a.features[axis] + b.features[axis]) / 2
        return Perspective(
            self.id, tick,
            f"The nearest opposites (#{a.index}, #{b.index}) differ most along axis {axis}.",
            proposal=Rule(axis=axis, threshold=threshold),
        )


class DoubtTeacher:
    """Looks only at what has already been carved, and asks whether it still holds."""

    id = "doubt"

    def __init__(self, tolerance: float = 0.75) -> None:
        self.tolerance = tolerance

    def regard(self, view: ChannelView, tick: int) -> Perspective:
        worst = None
        for cat in view.categories:
            members = [view.by_index(i) for i in cat.members]
            p = purity(m for m in members if m is not None)
            if worst is None or p < worst[0]:
                worst = (p, cat)
        if worst is None:
            return Perspective(self.id, tick, "Nothing has been carved; nothing to doubt.")
        p, cat = worst
        if p < self.tolerance:
            return Perspective(
                self.id, tick,
                f"'{cat.name}' no longer holds together ({p:.2f} agreement). I doubt it.",
                doubt=cat.name,
            )
        return Perspective(self.id, tick, f"What has been carved still holds ({p:.2f} at worst).")


DOUBT_DEFAULT = 0.75


def default_teachers(dims: int) -> list:
    """One axis teacher per dimension, one who looks at pairs, one who doubts."""
    return [AxisTeacher(k) for k in range(dims)] + [NearnessTeacher(), DoubtTeacher(DOUBT_DEFAULT)]

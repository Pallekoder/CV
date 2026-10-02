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
        signs = {e.sign for e in lived}
        if signs != {1, -1}:
            return Perspective(self.id, tick, "I see only one sign here, or none; nothing to divide.")
        values = sorted({e.features[self.axis] for e in lived})
        if len(values) < 2:
            return Perspective(
                self.id, tick,
                "Along my axis everything sits in the same place; I cannot tell the signs apart.",
            )
        best = None
        for lo_v, hi_v in zip(values, values[1:]):
            thr = (lo_v + hi_v) / 2
            hi = [e for e in lived if e.features[self.axis] >= thr]
            lo = [e for e in lived if e.features[self.axis] < thr]
            sorted_right = _majority(hi) + _majority(lo)
            if best is None or sorted_right > best[0]:
                best = (sorted_right, thr)
        sorted_right, thr = best
        return Perspective(
            self.id, tick,
            f"Along axis {self.axis} a line at {thr:.3f} sorts {sorted_right} of {len(lived)}.",
            proposal=Rule(axis=self.axis, threshold=thr),
        )


def _majority(exps) -> int:
    pos = sum(1 for e in exps if e.sign > 0)
    return max(pos, len(exps) - pos)


class NearnessTeacher:
    """Looks at pairs, not axes.

    Finds the two closest lived experiences with opposite consequences. If they
    are far apart it proposes the axis along which they differ most. If they
    are the same on the surface, it says so and proposes nothing: this is the
    paradox, and no surface rule will resolve it.
    """

    id = "nearness"

    def regard(self, view: ChannelView, tick: int) -> Perspective:
        lived = view.valenced(view.experiences)
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

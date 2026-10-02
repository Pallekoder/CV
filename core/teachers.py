"""Teachers.

The brief: many peer sources give perspectives, never decrees. "This is
how I see it, you decide." This file is the mechanism; what the teachers
actually are is the distant one's to specify, and nothing here is on until
it is switched on. See TEACHERS.md.

What a teacher is here: a visitor. It comes rarely and irregularly, looks
at the open bucket through a read-only view, and leaves one perspective:
a remark for the transcript and, at most, one proposed cut. The mind
keeps the perspective and weighs the cut as one candidate among its own,
by lived consequence. It never has to wait for a visitor, never carves
because of one, and never hears from the same one on a schedule it could
lean on.

What a teacher is not: the mind's eyes. The mind finds its own cuts along
every axis it perceives and doubts its own categories; see `core/mind.py`.
Earlier units had the mind consult six teachers on every tick and carve
only on their proposals. That was a crutch, and it is gone.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .channel import ChannelView, Rule


@dataclass(frozen=True)
class Perspective:
    source: str
    tick: int
    remark: str
    proposal: Optional[Rule] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "tick": self.tick,
            "remark": self.remark,
            "proposal": self.proposal.to_dict() if self.proposal else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Perspective":
        p = d.get("proposal")
        return cls(source=d["source"], tick=d["tick"], remark=d["remark"],
                   proposal=Rule.from_dict(p) if p else None)


class Teacher(Protocol):
    id: str

    def regard(self, view: ChannelView, tick: int) -> Perspective: ...


def _dist(a: tuple, b: tuple) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


class NearnessTeacher:
    """Looks at pairs, not axes, which is not how the mind looks on its own.

    Finds the two closest lived experiences with opposite consequences. If
    they are far apart it proposes the axis along which they differ most.
    If they are the same on the surface, it says so and proposes nothing:
    this is the paradox, and no surface rule will resolve it.
    """

    id = "nearness"
    WINDOW = 80  # it only looks at the most recent consequences

    def regard(self, view: ChannelView, tick: int) -> Perspective:
        lived = view.valenced(view.open)[-self.WINDOW:]
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


def default_teachers(dims: int = 0) -> list:
    """The teachers that may visit, when visits are switched on. One, for now."""
    return [NearnessTeacher()]

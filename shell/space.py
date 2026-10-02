"""An abstract space of forms.

A form has a surface (a tuple of unnamed numbers the core can perceive) and
a hidden consequence (what consuming it does). The core can touch a form,
which yields a fraction of the consequence and leaves the form in place, or
consume it, which yields the whole consequence and removes the form forever.
Removal is final: the space keeps only the id of what was lost.
"""
from __future__ import annotations

from dataclasses import dataclass

from core.valence import assert_truth

TOUCH_FRACTION = 0.25


@dataclass(frozen=True)
class Form:
    id: str
    surface: tuple
    hidden: float


class Gone(KeyError):
    """The form is no longer in the space."""


class Space:
    def __init__(self, forms, dims: int, label: str) -> None:
        self.dims = dims
        self.label = label
        self.forms: dict[str, Form] = {f.id: f for f in forms}
        self.tombstones: list[str] = []
        assert_truth(self.possible_values())

    def possible_values(self):
        return [f.hidden for f in self.forms.values()]

    def perceive(self) -> list:
        """Everything with a surface, in a stable order. Hidden values are not exposed."""
        return [(f.id, f.surface) for f in sorted(self.forms.values(), key=lambda f: f.id)]

    def touch(self, fid: str) -> float:
        form = self.forms.get(fid)
        if form is None:
            raise Gone(fid)
        return form.hidden * TOUCH_FRACTION

    def consume(self, fid: str) -> float:
        form = self.forms.pop(fid, None)
        if form is None:
            raise Gone(fid)
        self.tombstones.append(fid)
        return form.hidden

    @property
    def empty(self) -> bool:
        return not self.forms

    def describe(self) -> str:
        lines = [f"space {self.label}: {len(self.forms)} forms, {self.dims} dims"]
        for fid, surface in self.perceive():
            lines.append("  " + fid + "  " + " ".join(f"{x:+.2f}" for x in surface))
        if self.tombstones:
            lines.append("  gone: " + ", ".join(self.tombstones))
        return "\n".join(lines)

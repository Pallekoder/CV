"""Builders for spaces, and the hidden law they obey.

Every shell built for a given world seed shares one `Law`: a hidden rule
that says which sign a form's consequence has, from its surface. The core
is never told the law. It can only live it. Each builder also plants a
paradox: two forms identical on every surface whose consequences are
opposite, which no surface rule can ever account for.

Two kinds of law. `axis`: one threshold on one axis decides the sign.
`corner`: a form is positive only if it clears thresholds on two axes at
once. The second cannot be carved in one cut; a category carved on one
axis will hold both signs until it is narrowed along the other.

`first_moment` is the seed: a space made only of contrast. Two forms nearly
the same on the surface and nearly the same in consequence (a parallel), and
two forms exactly the same on the surface and opposite in consequence (a
paradox). The core's first act in it can only be noticing difference.

`scatter` is a larger throwaway space: many forms obeying the law, plus one
paradox pair.

Changing the world seed changes the law. A core carried into a world with a
different law will find its carved categories betrayed, and must revise.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from core.symbols import coin
from .space import Form, Space

LAW_KINDS = ("axis", "corner")


@dataclass(frozen=True)
class Law:
    axis: int
    threshold: float
    axis2: Optional[int] = None
    threshold2: Optional[float] = None

    @property
    def kind(self) -> str:
        return "corner" if self.axis2 is not None else "axis"

    def conditions(self) -> list:
        out = [(self.axis, self.threshold)]
        if self.axis2 is not None:
            out.append((self.axis2, self.threshold2))
        return out

    def sign(self, surface: tuple) -> int:
        return 1 if all(surface[a] >= t for a, t in self.conditions()) else -1

    def describe(self) -> str:
        parts = " and ".join(f"axis {a} >= {t:+.3f}" for a, t in self.conditions())
        return f"{parts} is one sign, anything else the other"

    def to_dict(self) -> dict:
        return {"axis": self.axis, "threshold": self.threshold, "axis2": self.axis2, "threshold2": self.threshold2}


def law_for(seed, dims: int, kind: str = "axis") -> Law:
    if kind not in LAW_KINDS:
        raise ValueError(f"unknown law kind {kind!r}; choose from {LAW_KINDS}")
    rng = random.Random(f"law:{seed}")
    axis = rng.randrange(dims)
    threshold = round(rng.uniform(-0.3, 0.3), 3)
    if kind == "axis":
        return Law(axis=axis, threshold=threshold)
    axis2 = rng.choice([a for a in range(dims) if a != axis])
    return Law(axis=axis, threshold=threshold, axis2=axis2, threshold2=round(rng.uniform(-0.3, 0.3), 3))


def _vec(rng: random.Random, dims: int) -> tuple:
    return tuple(round(rng.uniform(-1, 1), 3) for _ in range(dims))


def _jitter(v: tuple, rng: random.Random, amount: float) -> tuple:
    return tuple(round(x + rng.uniform(-amount, amount), 3) for x in v)


def _paradox(rng: random.Random, law: Law, dims: int, magnitude: float) -> list:
    twin = _vec(rng, dims)
    s = law.sign(twin)
    return [
        Form(coin("paradox", 1, twin), twin, round(s * magnitude, 3)),
        Form(coin("paradox", 2, twin), twin, round(-s * magnitude, 3)),
    ]


def first_moment(rng: random.Random, law: Law, dims: int = 4) -> Space:
    base = list(_vec(rng, dims))
    for a, t in law.conditions():
        base[a] = round(min(1.0, t + rng.uniform(0.15, 0.6)), 3)
    base = tuple(base)
    forms = [
        # the parallel: alike on the surface, alike in consequence, obeying the law
        Form(coin("parallel", 1, base), _jitter(base, rng, 0.02), +0.60),
        Form(coin("parallel", 2, base), _jitter(base, rng, 0.02), +0.55),
    ]
    forms += _paradox(rng, law, dims, 0.70)
    return Space(forms, dims=dims, label=coin("first", base, law))


def scatter(rng: random.Random, law: Law, n: Optional[int] = None, dims: int = 4) -> Space:
    if n is None:
        n = 16 if law.kind == "axis" else 24   # positives are rarer under a corner law
    forms = []
    for i in range(n):
        surface = _vec(rng, dims)
        hidden = round(law.sign(surface) * rng.uniform(0.3, 0.9), 3)
        forms.append(Form(coin("scatter", i, surface), surface, hidden))
    forms += _paradox(rng, law, dims, 0.65)
    return Space(forms, dims=dims, label=coin("scatter", n, law, rng.random()))


BUILDERS = {"first": first_moment, "scatter": scatter}


def build(kind: str, rng: random.Random, law: Law) -> Space:
    return BUILDERS[kind](rng, law)

"""Builders for spaces, and the hidden law they obey.

Every shell built for a given world seed shares one `Law`: a hidden rule that
says which sign a form's consequence has, from one surface axis. The core is
never told the law. It can only live it. Each builder also plants a paradox:
two forms identical on every surface whose consequences are opposite, which
no surface rule can ever account for.

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

from core.symbols import coin
from .space import Form, Space


@dataclass(frozen=True)
class Law:
    axis: int
    threshold: float

    def sign(self, surface: tuple) -> int:
        return 1 if surface[self.axis] >= self.threshold else -1

    def describe(self) -> str:
        return f"axis {self.axis} >= {self.threshold:+.3f} is one sign, below it the other"


def law_for(seed, dims: int) -> Law:
    rng = random.Random(f"law:{seed}")
    return Law(axis=rng.randrange(dims), threshold=round(rng.uniform(-0.3, 0.3), 3))


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
    base[law.axis] = round(min(1.0, law.threshold + rng.uniform(0.15, 0.6)), 3)
    base = tuple(base)
    forms = [
        # the parallel: alike on the surface, alike in consequence, obeying the law
        Form(coin("parallel", 1, base), _jitter(base, rng, 0.02), +0.60),
        Form(coin("parallel", 2, base), _jitter(base, rng, 0.02), +0.55),
    ]
    forms += _paradox(rng, law, dims, 0.70)
    return Space(forms, dims=dims, label=coin("first", base, law))


def scatter(rng: random.Random, law: Law, n: int = 12, dims: int = 4) -> Space:
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

"""The open channel.

Every lived thing lands here first, in a single nameless bucket. The system
may carve named categories out of that bucket, revise them, and dissolve them
back. No category exists before the system makes one, and every category name
is coined by the system from its own state.

Categories are rules, not labels: a category is "the experiences on this side
of this threshold on this axis". That keeps them editable and testable
against consequence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional


@dataclass(frozen=True)
class Experience:
    """One lived moment.

    `features` is what was perceived outwardly, if anything. An experience
    with no features is something that arrived without a surface: the system
    finding its own earlier utterance, or a rare contact from outside.
    `token` is any symbol string the moment carried. `valence` is the lived
    consequence, if there was one.
    """

    index: int
    tick: int
    features: Optional[tuple]
    token: Optional[str] = None
    valence: Optional[float] = None

    @property
    def sign(self) -> Optional[int]:
        if self.valence is None:
            return None
        return (self.valence > 0) - (self.valence < 0)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "tick": self.tick,
            "features": list(self.features) if self.features is not None else None,
            "token": self.token,
            "valence": self.valence,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Experience":
        f = d["features"]
        return cls(
            index=d["index"],
            tick=d["tick"],
            features=tuple(f) if f is not None else None,
            token=d.get("token"),
            valence=d.get("valence"),
        )


@dataclass(frozen=True)
class Rule:
    axis: int
    threshold: float

    def side(self, features: tuple) -> int:
        return 1 if features[self.axis] >= self.threshold else -1

    def to_dict(self) -> dict:
        return {"axis": self.axis, "threshold": self.threshold}

    @classmethod
    def from_dict(cls, d: dict) -> "Rule":
        return cls(axis=d["axis"], threshold=d["threshold"])


@dataclass
class Category:
    name: str
    rule: Rule
    side: int
    born: int
    members: set = field(default_factory=set)

    def admits(self, exp: Experience) -> bool:
        return exp.features is not None and self.rule.side(exp.features) == self.side

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "rule": self.rule.to_dict(),
            "side": self.side,
            "born": self.born,
            "members": sorted(self.members),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Category":
        return cls(
            name=d["name"],
            rule=Rule.from_dict(d["rule"]),
            side=d["side"],
            born=d["born"],
            members=set(d["members"]),
        )


@dataclass(frozen=True)
class CategorySnapshot:
    name: str
    rule: Rule
    side: int
    born: int
    members: tuple


@dataclass(frozen=True)
class ChannelView:
    """Read-only view handed to teachers. They can look; they cannot touch."""

    experiences: tuple
    open: tuple
    categories: tuple

    def valenced(self, source: Iterable[Experience]) -> tuple:
        return tuple(e for e in source if e.valence is not None and e.features is not None)

    def by_index(self, index: int) -> Optional[Experience]:
        for e in self.experiences:
            if e.index == index:
                return e
        return None


def purity(exps: Iterable[Experience]) -> float:
    """Fraction of valenced members that share the majority sign. 1.0 if none."""
    signs = [e.sign for e in exps if e.sign]
    if not signs:
        return 1.0
    pos = sum(1 for s in signs if s > 0)
    return max(pos, len(signs) - pos) / len(signs)


class Channel:
    def __init__(self) -> None:
        self.experiences: dict[int, Experience] = {}
        self.categories: dict[str, Category] = {}

    # -- arrivals ----------------------------------------------------------

    def add(self, exp: Experience) -> Optional[str]:
        """Add an experience; place it in an existing category if one admits it.

        Returns the name of the category it landed in, or None for the open
        bucket.
        """
        self.experiences[exp.index] = exp
        for cat in self.categories.values():
            if cat.admits(exp):
                cat.members.add(exp.index)
                return cat.name
        return None

    # -- reading -----------------------------------------------------------

    def categorized_indices(self) -> set:
        out: set = set()
        for cat in self.categories.values():
            out |= cat.members
        return out

    def open_bucket(self) -> list:
        taken = self.categorized_indices()
        return [e for i, e in sorted(self.experiences.items()) if i not in taken]

    def members_of(self, name: str) -> list:
        return [self.experiences[i] for i in sorted(self.categories[name].members)]

    def category_of(self, exp: Experience) -> Optional[str]:
        for cat in self.categories.values():
            if exp.index in cat.members:
                return cat.name
        return None

    def view(self) -> ChannelView:
        return ChannelView(
            experiences=tuple(e for _, e in sorted(self.experiences.items())),
            open=tuple(self.open_bucket()),
            categories=tuple(
                CategorySnapshot(
                    name=c.name,
                    rule=c.rule,
                    side=c.side,
                    born=c.born,
                    members=tuple(sorted(c.members)),
                )
                for c in self.categories.values()
            ),
        )

    # -- carving -----------------------------------------------------------

    def split(self, rule: Rule, tick: int, namer: Callable[..., str]) -> tuple:
        """Carve the open bucket along a rule into two new categories.

        Only experiences with features can be carved; featureless ones stay
        open. Names come from the namer, which the mind supplies.
        """
        candidates = [e for e in self.open_bucket() if e.features is not None]
        born = []
        for side in (1, -1):
            members = {e.index for e in candidates if rule.side(e.features) == side}
            name = namer("category", rule.axis, round(rule.threshold, 4), side, tick)
            while name in self.categories:
                name = namer(name, "again")
            cat = Category(name=name, rule=rule, side=side, born=tick, members=members)
            self.categories[name] = cat
            born.append(cat)
        return tuple(born)

    def dissolve(self, name: str) -> Category:
        """Remove a category; its members fall back into the open bucket."""
        return self.categories.pop(name)

    # -- persistence -------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "experiences": [e.to_dict() for _, e in sorted(self.experiences.items())],
            "categories": [c.to_dict() for c in self.categories.values()],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Channel":
        ch = cls()
        for row in d["experiences"]:
            e = Experience.from_dict(row)
            ch.experiences[e.index] = e
        for row in d["categories"]:
            c = Category.from_dict(row)
            ch.categories[c.name] = c
        return ch

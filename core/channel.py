"""The open channel.

Every lived thing lands here first, in a single nameless bucket. The system
may carve named categories out of that bucket, narrow a category into more
specific ones when consequence inside it disagrees, revise them, and
dissolve them back. No category exists before the system makes one, and
every category name is coined by the system from its own state.

Categories are rules, not labels: a category is "the experiences on this
side of this threshold on this axis", within its parent's category if it
has one. That keeps them editable and testable against consequence, and it
lets them narrow: a category whose members disagree can be split along
another axis into two children. An experience lives in the deepest
category whose chain of rules admits it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Iterable, Mapping, Optional


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
    parent: Optional[str] = None
    members: set = field(default_factory=set)

    def admits(self, exp: Experience) -> bool:
        return exp.features is not None and self.admits_surface(exp.features)

    def admits_surface(self, surface: tuple) -> bool:
        return self.rule.side(surface) == self.side

    def describe_rule(self) -> str:
        return f"axis {self.rule.axis} {'>=' if self.side > 0 else '< '} {self.rule.threshold:+.3f}"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "rule": self.rule.to_dict(),
            "side": self.side,
            "born": self.born,
            "parent": self.parent,
            "members": sorted(self.members),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Category":
        return cls(
            name=d["name"],
            rule=Rule.from_dict(d["rule"]),
            side=d["side"],
            born=d["born"],
            parent=d.get("parent"),
            members=set(d["members"]),
        )


@dataclass(frozen=True)
class CategorySnapshot:
    name: str
    rule: Rule
    side: int
    born: int
    members: tuple
    parent: Optional[str]
    leaf: bool
    depth: int


@dataclass(frozen=True)
class ChannelView:
    """Read-only view handed to teachers. They can look; they cannot touch.

    `open` is the direct material of the scope being looked at: the open
    bucket itself, or the direct members of one category when the question
    is whether that category can be narrowed. `categories` are the scope's
    children; `leaves` are every category in the whole channel that has no
    children.
    """

    experiences: tuple
    open: tuple
    categories: tuple
    leaves: tuple = ()
    scope: Optional[str] = None
    lookup: Mapping = field(default_factory=lambda: MappingProxyType({}))

    def valenced(self, source: Iterable[Experience]) -> tuple:
        return tuple(e for e in source if e.valence is not None and e.features is not None)

    def by_index(self, index: int) -> Optional[Experience]:
        return self.lookup.get(index)


def best_line(exps: Iterable[Experience], axis: int) -> Optional[Rule]:
    """Along one axis, the threshold that best sorts these experiences by sign.

    None if they are all one sign or all sit at one value on the axis.
    """
    lived = [e for e in exps if e.sign and e.features is not None]
    if {e.sign for e in lived} != {1, -1}:
        return None
    points = sorted((e.features[axis], e.sign) for e in lived)
    n = len(points)
    total_pos = sum(1 for _, sg in points if sg > 0)
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
    return Rule(axis=axis, threshold=best[1]) if best else None


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

    def new_index(self) -> int:
        """The next free experience index.

        Experience indices are the channel's own, not the ledger's. A child
        carries its parent's channel but starts its own ledger at zero, so
        ledger indices would collide with inherited experiences and the
        child's acts would overwrite its inheritance. These never collide.
        """
        return max(self.experiences, default=-1) + 1

    # -- structure ---------------------------------------------------------

    def children(self, name: Optional[str]) -> list:
        return [c for c in self.categories.values() if c.parent == name]

    def leaves(self) -> list:
        parents = {c.parent for c in self.categories.values() if c.parent is not None}
        return [c for c in self.categories.values() if c.name not in parents]

    def depth(self, name: str) -> int:
        d = 0
        while name is not None:
            d += 1
            name = self.categories[name].parent
        return d

    def chain(self, name: str) -> list:
        out = []
        while name is not None:
            cat = self.categories[name]
            out.append(cat)
            name = cat.parent
        return list(reversed(out))

    def locate(self, surface: tuple) -> Optional[str]:
        """The deepest category whose chain of rules admits this surface."""
        node = None
        candidates = self.children(None)
        while True:
            nxt = next((c for c in candidates if c.admits_surface(surface)), None)
            if nxt is None:
                return node
            node = nxt.name
            candidates = self.children(node)

    # -- arrivals ----------------------------------------------------------

    def add(self, exp: Experience) -> Optional[str]:
        """Add an experience; place it in the deepest category that admits it.

        Returns the name of the category it landed in, or None for the open
        bucket.
        """
        if exp.index in self.experiences:
            raise ValueError(f"experience {exp.index} already exists; use new_index()")
        self.experiences[exp.index] = exp
        if exp.features is None:
            return None
        name = self.locate(exp.features)
        if name is not None:
            self.categories[name].members.add(exp.index)
        return name

    # -- reading -----------------------------------------------------------

    def categorized_indices(self) -> set:
        out: set = set()
        for cat in self.categories.values():
            out |= cat.members
        return out

    def open_bucket(self) -> list:
        taken = self.categorized_indices()
        return [e for i, e in sorted(self.experiences.items()) if i not in taken]

    def direct(self, scope: Optional[str]) -> list:
        """The open bucket, or one category's direct members."""
        return self.open_bucket() if scope is None else self.members_of(scope)

    def members_of(self, name: str) -> list:
        return [self.experiences[i] for i in sorted(self.categories[name].members)]

    def under(self, name: str) -> list:
        """Every experience in a category or any category beneath it."""
        out = list(self.members_of(name))
        for child in self.children(name):
            out += self.under(child.name)
        return out

    def category_of(self, exp: Experience) -> Optional[str]:
        for cat in self.categories.values():
            if exp.index in cat.members:
                return cat.name
        return None

    def _snapshot(self, c: Category, leaf_names: set) -> CategorySnapshot:
        return CategorySnapshot(
            name=c.name, rule=c.rule, side=c.side, born=c.born, members=tuple(sorted(c.members)),
            parent=c.parent, leaf=c.name in leaf_names, depth=self.depth(c.name),
        )

    def view(self, scope: Optional[str] = None) -> ChannelView:
        leaf_names = {c.name for c in self.leaves()}
        return ChannelView(
            experiences=tuple(e for _, e in sorted(self.experiences.items())),
            open=tuple(self.direct(scope)),
            categories=tuple(self._snapshot(c, leaf_names) for c in self.children(scope)),
            leaves=tuple(self._snapshot(c, leaf_names) for c in self.leaves()),
            scope=scope,
            lookup=MappingProxyType(dict(self.experiences)),
        )

    # -- carving -----------------------------------------------------------

    def split(self, rule: Rule, tick: int, namer: Callable[..., str], within: Optional[str] = None) -> tuple:
        """Carve a scope's direct material along a rule into two children.

        With no scope, the open bucket is carved into two root categories.
        With a scope, that category's direct members are carved into two
        children of it, which is how a category narrows. Only experiences
        with features can be carved; featureless ones stay where they are.
        Names come from the namer, which the mind supplies.
        """
        candidates = [e for e in self.direct(within) if e.features is not None]
        born = []
        for side in (1, -1):
            members = {e.index for e in candidates if rule.side(e.features) == side}
            name = namer("category", rule.axis, round(rule.threshold, 4), side, tick, within)
            while name in self.categories:
                name = namer(name, "again")
            cat = Category(name=name, rule=rule, side=side, born=tick, parent=within, members=members)
            self.categories[name] = cat
            born.append(cat)
        if within is not None:
            self.categories[within].members -= {e.index for e in candidates}
        return tuple(born)

    def dissolve(self, name: str) -> Category:
        """Remove a childless category. Its members fall back to its parent,
        or into the open bucket if it had none."""
        if self.children(name):
            raise ValueError(f"'{name}' has children; dissolve them first")
        cat = self.categories.pop(name)
        if cat.parent is not None:
            self.categories[cat.parent].members |= cat.members
        return cat

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

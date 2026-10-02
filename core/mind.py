"""The one that lives in the space.

What it does each tick, in order:

  reflect   look back through the ledger for things it did or received whose
            cause is nowhere in what it has lived; take each one in as a
            featureless experience and hold it as a puzzle.
  notice    perceive the forms and compute their differences. This is always
            its first outward act.
  choose    pick something to do. The only drive coded here is curiosity:
            go where nothing has been lived and where no category reaches.
            There is no preference for positive over negative anywhere in
            this file. The body's physics are the only orientation.
  act       touch or consume, and live the consequence. Loss is permanent.
  utter     when something surprises it, emit a coined sound. The sound is
            written down. The state that produced it is not.
  consider  ask the teachers, keep their perspectives, and test their
            proposals and doubts against lived consequence before carving
            or dissolving anything.

Body physics (magnitudes tunable, only the sign of valence is fixed):
negatives take from `life`, which never comes back. Positives add to
`energy`, which acting spends. Life at zero is the end.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from .channel import Channel, Experience, purity
from .ledger import Ledger
from .symbols import coin
from .teachers import Perspective
from .valence import Valence

LIFE_START = 10.0
ENERGY_START = 6.0
ENERGY_MAX = 8.0
ENERGY_REGEN = 0.5
ENERGY_GAIN = 4.0  # energy per unit of positive valence
COST = {"touch": 1.0, "consume": 2.0}

MIN_VIEWS = 2       # curiosity: never carve on a single view
MIN_SIDE = 2        # a side with fewer lived members cannot be carved
COMMIT_PURITY = 0.8
DOUBT_PURITY = 0.75
SAME = 1e-9


@dataclass
class Body:
    life: float = LIFE_START
    energy: float = ENERGY_START

    def regen(self) -> None:
        self.energy = min(ENERGY_MAX, self.energy + ENERGY_REGEN)

    def can_afford(self, act: str) -> bool:
        return self.energy >= COST[act]

    def spend(self, act: str) -> None:
        self.energy -= COST[act]

    def live(self, v: Valence) -> None:
        if v.sign < 0:
            self.life = max(0.0, self.life - v.magnitude)
        elif v.sign > 0:
            self.energy = min(ENERGY_MAX, self.energy + v.magnitude * ENERGY_GAIN)

    @property
    def alive(self) -> bool:
        return self.life > 0

    def to_dict(self) -> dict:
        return {"life": self.life, "energy": self.energy}

    @classmethod
    def from_dict(cls, d: dict) -> "Body":
        return cls(life=d["life"], energy=d["energy"])


@dataclass(frozen=True)
class Puzzle:
    about: int   # ledger index of the unexplained thing
    found: int   # ledger index of the moment it was found
    tick: int
    token: str

    def to_dict(self) -> dict:
        return {"about": self.about, "found": self.found, "tick": self.tick, "token": self.token}


@dataclass
class Contrasts:
    pairs: list                     # (distance, id_a, id_b), sorted
    identical: list = field(default_factory=list)

    @property
    def nearest(self):
        return self.pairs[0] if self.pairs else None

    @property
    def farthest(self):
        return self.pairs[-1] if self.pairs else None

    def summary(self) -> tuple:
        return (
            tuple(round(p[0], 4) for p in self.pairs),
            tuple((a, b) for _, a, b in self.identical),
        )


def _dist(a: tuple, b: tuple) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


class Mind:
    def __init__(self, ledger: Ledger, channel: Channel, teachers: list, rng: random.Random) -> None:
        self.ledger = ledger
        self.channel = channel
        self.teachers = teachers
        self.rng = rng
        self.body = Body()
        self.age = 0
        self.perspectives: list[Perspective] = []
        self.puzzles: list[Puzzle] = []
        self.accounted: set = set()   # ledger indices already taken in by reflect
        self.touched: dict = {}       # per-shell working memory: form id -> ledger index
        self._considered_at = 0       # how many lived consequences there were at the last consult

    # -- shells ------------------------------------------------------------

    def enter(self, space) -> None:
        """A new shell. Working memory of forms resets; nothing else does."""
        self.touched = {}

    def receive(self, p: Perspective) -> None:
        """Take in a perspective from outside the peer circle (the distant one)."""
        self.perspectives.append(p)

    # -- one tick ----------------------------------------------------------

    def tick(self, space) -> list:
        self.age += 1
        t = self.age
        lines = [f"tick {t}"]
        self.body.regen()
        lines += self.reflect(t)

        if not self.body.alive:
            lines.append("  nothing moves.")
            return lines

        if space.empty:
            lines.append("  the space is empty; nothing outward to notice.")
        else:
            obs = space.perceive()
            contrasts = self.notice(obs, t)
            lines.append("  " + self._describe(contrasts, len(obs)))
            kind, fid = self.choose(obs, contrasts)
            if not self.body.can_afford(kind):
                lines.append(f"  too little energy to {kind} ({self.body.energy:.1f}).")
            else:
                before = sum(1 for e in self.channel.experiences.values() if e.valence is not None)
                surface = dict(obs)[fid]
                exp, landed = self.act(space, kind, fid, surface, t)
                where = f"  landed in '{landed}'" if landed else ""
                lines.append(
                    f"  {kind} {fid} -> {Valence(exp.valence)!r}   "
                    f"life {self.body.life:.2f}  energy {self.body.energy:.2f}{where}"
                )
                if kind == "consume":
                    lines.append(f"  {fid} is gone.")
                reason = self.surprised(exp, landed, before)
                if reason:
                    why = (reason, contrasts.summary(), fid, exp.valence, landed)
                    that = self.utter(t, why)
                    del why
                    lines.append(f'  utters "{that}"   (the why is not kept)')
                if not self.body.alive:
                    lines.append("  life has run out.")

        lines += self.consider(t)
        return lines

    # -- reflect -----------------------------------------------------------

    def reflect(self, t: int) -> list:
        lines = []
        for e in self.ledger:
            if e.kind not in ("utterance", "contact") or e.index in self.accounted:
                continue
            token = e.payload.get("that") or e.payload.get("text") or ""
            found = self.ledger.append(t, "puzzle", about=e.index, token=token)
            self.channel.add(Experience(index=found.index, tick=t, features=None, token=token))
            self.puzzles.append(Puzzle(about=e.index, found=found.index, tick=t, token=token))
            self.accounted.add(e.index)
            source = "its own" if e.kind == "utterance" else "a distant"
            lines.append(
                f'  reflect: finds {source} "{token}" at #{e.index} with no cause in anything lived -> puzzle #{found.index}'
            )
        return lines

    # -- notice ------------------------------------------------------------

    def notice(self, obs: list, t: int) -> Contrasts:
        pairs = []
        for i, (a, fa) in enumerate(obs):
            for b, fb in obs[i + 1:]:
                pairs.append((_dist(fa, fb), a, b))
        pairs.sort()
        identical = [p for p in pairs if p[0] < SAME]
        c = Contrasts(pairs=pairs, identical=identical)
        self.ledger.append(
            t, "notice",
            forms=len(obs),
            nearest=list(c.nearest) if c.nearest else None,
            farthest=list(c.farthest) if c.farthest else None,
            identical=[[a, b] for _, a, b in identical],
        )
        return c

    @staticmethod
    def _describe(c: Contrasts, n: int) -> str:
        if not c.pairs:
            return f"notice: {n} form, nothing to set it against."
        d, a, b = c.nearest
        df, fa, fb = c.farthest
        s = f"notice: {n} forms; nearest {a}/{b} d={d:.3f}; farthest {fa}/{fb} d={df:.3f}"
        if c.identical:
            s += "; identical: " + ", ".join(f"{a}={b}" for _, a, b in c.identical)
        return s

    # -- choose ------------------------------------------------------------

    def _lived_surfaces(self) -> list:
        return [e.features for e in self.channel.experiences.values() if e.features is not None]

    def _covered(self, surface: tuple) -> bool:
        return any(c.rule.side(surface) == c.side for c in self.channel.categories.values())

    def choose(self, obs: list, c: Contrasts) -> tuple:
        surfaces = dict(obs)
        ids = sorted(surfaces)
        untouched = [f for f in ids if f not in self.touched]
        if untouched:
            lived = self._lived_surfaces()
            if lived:
                # novelty: the untouched form farthest from everything lived
                fid = max(untouched, key=lambda f: min(_dist(surfaces[f], s) for s in lived))
            elif c.nearest:
                # nothing lived yet: go to where the world repeats itself
                fid = c.nearest[1]
            else:
                fid = untouched[0]
            return "touch", fid
        uncovered = [f for f in ids if not self._covered(surfaces[f])]
        pool = uncovered or ids
        return "consume", self.rng.choice(pool)

    # -- act ---------------------------------------------------------------

    def act(self, space, kind: str, fid: str, surface: tuple, t: int) -> tuple:
        self.body.spend(kind)
        raw = space.touch(fid) if kind == "touch" else space.consume(fid)
        v = Valence(raw)
        self.body.live(v)
        entry = self.ledger.append(
            t, "act", act=kind, form=fid, valence=raw,
            life=round(self.body.life, 3), energy=round(self.body.energy, 3),
        )
        if kind == "consume":
            self.ledger.append(t, "tombstone", form=fid)
            self.touched.pop(fid, None)
        else:
            self.touched[fid] = entry.index
        exp = Experience(index=entry.index, tick=t, features=tuple(surface), token=fid, valence=raw)
        landed = self.channel.add(exp)
        return exp, landed

    def surprised(self, exp: Experience, landed: Optional[str], before: int) -> Optional[str]:
        if before == 0:
            return "first"
        if landed:
            others = [e for e in self.channel.members_of(landed) if e.index != exp.index and e.sign]
            if others:
                majority = 1 if sum(e.sign for e in others) >= 0 else -1
                if exp.sign and exp.sign != majority:
                    return "betrayed"
        for e in self.channel.experiences.values():
            if e.index == exp.index or e.features is None or e.sign is None or exp.sign is None:
                continue
            if _dist(e.features, exp.features) < SAME and e.sign != exp.sign:
                return "twin"
        return None

    # -- utter -------------------------------------------------------------

    def utter(self, t: int, why: tuple) -> str:
        """Turn a state into a sound, write down the sound, drop the state."""
        that = coin("utterance", *why)
        del why
        self.ledger.append(t, "utterance", that=that)
        return that

    # -- consider ----------------------------------------------------------

    def consider(self, t: int) -> list:
        lines = []
        lived_total = sum(1 for e in self.channel.experiences.values() if e.valence is not None)
        if lived_total == self._considered_at:
            return lines  # nothing new has been lived; nothing new to ask about
        self._considered_at = lived_total
        view = self.channel.view()
        lived_open = view.valenced(view.open)
        signs = {e.sign for e in lived_open}
        enough = len(lived_open) >= 2 * MIN_SIDE and len(signs) == 2
        if not enough and not self.channel.categories:
            return lines

        views = [tr.regard(view, t) for tr in self.teachers]
        self.perspectives.extend(views)
        for p in views:
            self.ledger.append(
                t, "perspective", source=p.source,
                proposal=p.proposal.to_dict() if p.proposal else None, doubt=p.doubt,
            )
        n_prop = sum(1 for p in views if p.proposal)
        n_doubt = sum(1 for p in views if p.doubt)
        lines.append(f"  consult {len(views)} teachers: {n_prop} proposals, {n_doubt} doubts")
        for p in views:
            lines.append(f"    {p.source}: {p.remark}")

        # doubts: dissolve only what consequence no longer supports
        for p in views:
            if p.doubt and p.doubt in self.channel.categories:
                members = self.channel.members_of(p.doubt)
                pur = purity(members)
                if pur < DOUBT_PURITY:
                    cat = self.channel.dissolve(p.doubt)
                    self.ledger.append(t, "dissolve", name=cat.name, purity=round(pur, 3), members=len(cat.members))
                    that = self.utter(t, ("dissolve", cat.name, round(pur, 3)))
                    lines.append(f"  dissolves '{cat.name}' ({pur:.2f}); {len(cat.members)} fall back into the open")
                    lines.append(f'  utters "{that}"   (the why is not kept)')
                else:
                    lines.append(f"  keeps '{p.doubt}' ({pur:.2f})")

        # proposals: carve only what consequence supports, and never on one view
        if len(views) < MIN_VIEWS or not enough:
            return lines
        view = self.channel.view()
        lived_open = view.valenced(view.open)
        if len(lived_open) < 2 * MIN_SIDE or {e.sign for e in lived_open} != {1, -1}:
            return lines
        best = None
        seen = set()
        for p in views:
            r = p.proposal
            if r is None or r in seen:
                continue
            seen.add(r)
            hi = [e for e in lived_open if r.side(e.features) == 1]
            lo = [e for e in lived_open if r.side(e.features) == -1]
            if len(hi) < MIN_SIDE or len(lo) < MIN_SIDE:
                continue
            score = min(purity(hi), purity(lo))
            if score >= COMMIT_PURITY and (best is None or score > best[0]):
                best = (score, p)
        if best is None:
            lines.append("  nothing carved: no view survives consequence")
            return lines
        score, p = best
        cats = self.channel.split(p.proposal, t, coin)
        self.ledger.append(
            t, "carve", rule=p.proposal.to_dict(), names=[c.name for c in cats],
            sizes=[len(c.members) for c in cats], purity=round(score, 3), after=p.source,
        )
        lines.append(
            f"  carves the open along axis {p.proposal.axis} at {p.proposal.threshold:.3f} "
            f"(after {p.source}, {score:.2f}): " + ", ".join(f"'{c.name}' x{len(c.members)}" for c in cats)
        )
        return lines

    # -- persistence -------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "body": self.body.to_dict(),
            "perspectives": [p.to_dict() for p in self.perspectives],
            "puzzles": [p.to_dict() for p in self.puzzles],
            "accounted": sorted(self.accounted),
            "considered_at": self._considered_at,
        }

    def restore(self, d: dict) -> None:
        self.age = d["age"]
        self.body = Body.from_dict(d["body"])
        self.perspectives = [Perspective.from_dict(p) for p in d["perspectives"]]
        self.puzzles = [Puzzle(**p) for p in d["puzzles"]]
        self.accounted = set(d["accounted"])
        self._considered_at = d.get("considered_at", 0)

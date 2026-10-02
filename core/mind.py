"""The one that lives in the space.

What it does each tick, in order:

  upkeep    existing costs energy. With no energy it starves, and starving
            takes life, which never comes back.
  reflect   look back through its own ledger for things it did or received
            whose cause is nowhere in what it has lived; take each one in
            as a featureless experience and hold it as a puzzle.
  notice    perceive the forms and compute their differences. This is
            always its first outward act.
  choose    weigh every possible act by its tendencies and draw one. The
            tendencies are heritable, and every one of them may be negative
            at birth: a mind can be born drawn toward what hurt it. Nothing
            here says which way is right. The body's physics, and whether
            the mind is still around later, are the only judges.
  act       touch or consume, and live the consequence. Loss is permanent.
  utter     when something surprises it, emit a coined sound. The sound is
            written down. The state that produced it is not.
  consider  ask the teachers, keep their perspectives, and test their
            proposals and doubts against lived consequence before carving
            or dissolving anything.

Body physics (magnitudes tunable; only the sign of valence is fixed):
negatives take from `life`, which nothing restores. Positives add to
`energy`. Existing costs energy every tick, acting costs more, and a body
with no energy loses life until it finds some. Life at zero is the end.
"""
from __future__ import annotations

import math
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
ENERGY_MAX = 20.0
UPKEEP = 0.08        # what merely existing costs, per tick
STARVE = 0.3         # life lost per tick spent with no energy
ENERGY_GAIN = 4.0    # energy per unit of positive valence
COST = {"touch": 0.5, "consume": 1.0, "rest": 0.0}

ECHO_SCALE = 0.3     # how far away a lived consequence is still felt
VARIATION = 0.15     # how far a child's tendencies drift from its parent's

MIN_VIEWS = 2        # never carve on a single view
MIN_SIDE = 2         # a side with fewer lived members cannot be carved
COMMIT_PURITY = 0.8
DOUBT_PURITY = 0.75
SAME = 1e-9


@dataclass
class Body:
    life: float = LIFE_START
    energy: float = ENERGY_START

    def upkeep(self) -> bool:
        """Existing costs. Returns True if the body is starving."""
        self.energy = max(0.0, self.energy - UPKEEP)
        if self.energy > 0.0:
            return False
        self.life = max(0.0, self.life - STARVE)
        return True

    def can_afford(self, act: str) -> bool:
        return self.energy >= COST[act]

    def spend(self, act: str) -> None:
        self.energy = max(0.0, self.energy - COST[act])

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
class Disposition:
    """Heritable tendencies. No sign is given for any of them.

    novelty  pull toward (or away from) what has not been lived
    echo     pull toward (or away from) what nearby consequences felt like
    kin      pull toward (or away from) what the admitting category felt like
    bold     pull toward consuming rather than touching
    heat     how much chance is left in the draw
    """

    novelty: float
    echo: float
    kin: float
    bold: float
    heat: float

    @classmethod
    def random(cls, rng: random.Random) -> "Disposition":
        return cls(
            novelty=rng.uniform(-1, 1),
            echo=rng.uniform(-1, 1),
            kin=rng.uniform(-1, 1),
            bold=rng.uniform(-1, 1),
            heat=rng.uniform(0.05, 0.5),
        )

    def vary(self, rng: random.Random) -> "Disposition":
        return Disposition(
            novelty=self.novelty + rng.gauss(0, VARIATION),
            echo=self.echo + rng.gauss(0, VARIATION),
            kin=self.kin + rng.gauss(0, VARIATION),
            bold=self.bold + rng.gauss(0, VARIATION),
            heat=max(0.02, self.heat + rng.gauss(0, VARIATION / 2)),
        )

    def to_dict(self) -> dict:
        return {"novelty": self.novelty, "echo": self.echo, "kin": self.kin, "bold": self.bold, "heat": self.heat}

    @classmethod
    def from_dict(cls, d: dict) -> "Disposition":
        return cls(**d)

    def __str__(self) -> str:
        return (f"nov {self.novelty:+.2f}  echo {self.echo:+.2f}  kin {self.kin:+.2f}  "
                f"bold {self.bold:+.2f}  heat {self.heat:.2f}")


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
    def __init__(self, ledger: Ledger, channel: Channel, teachers: list, rng: random.Random,
                 disposition: Optional[Disposition] = None) -> None:
        self.ledger = ledger
        self.channel = channel
        self.teachers = teachers
        self.rng = rng
        self.disposition = disposition if disposition is not None else Disposition.random(rng)
        self.body = Body()
        self.age = 0
        self.perspectives: list[Perspective] = []
        self.puzzles: list[Puzzle] = []
        self.accounted: set = set()   # ledger indices already taken in by reflect
        self.touched: dict = {}       # per-shell working memory: form id -> ledger index
        self._considered_at = 0       # how many lived consequences there were at the last consult
        self._scanned = 0             # how far reflect has read its own ledger

    # -- shells and contacts -------------------------------------------------

    def enter(self, space) -> None:
        """A new shell. Working memory of forms resets; nothing else does."""
        self.touched = {}
        self.ledger.append(self.age, "enter", shell=getattr(space, "label", None),
                           forms=len(getattr(space, "forms", {})))

    def receive(self, p: Perspective) -> None:
        """Take in words from outside the peer circle. They land in the ledger
        like any other thing that happened, for reflect to find."""
        self.ledger.append(self.age, "contact", text=p.remark, source=p.source)
        self.perspectives.append(p)

    # -- one tick --------------------------------------------------------------

    def tick(self, space) -> list:
        self.age += 1
        t = self.age
        lines = [f"tick {t}"]
        if self.body.upkeep():
            lines.append(f"  starving: life {self.body.life:.2f}")
        lines += self.reflect(t)

        if not self.body.alive:
            lines.append("  life has run out.")
            return lines

        if space.empty:
            lines.append("  the space is empty; nothing outward to notice.")
        else:
            obs = space.perceive()
            contrasts = self.notice(obs, t)
            lines.append("  " + self._describe(contrasts, len(obs)))
            kind, fid = self.choose(obs, contrasts)
            if kind == "rest":
                lines.append(f"  rests.   life {self.body.life:.2f}  energy {self.body.energy:.2f}")
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
        entries = self.ledger.since(self._scanned)
        self._scanned = len(self.ledger)
        for e in entries:
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
        self._scanned = len(self.ledger)
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

    def _felt(self, surface: tuple, lived: list) -> tuple:
        """How new this surface is, and what consequences near it felt like.

        The echo is a distance-weighted mean of lived consequence, shrunk
        toward nothing when nothing lived is anywhere near.
        """
        if not lived:
            return 1.0, 0.0
        nearest = math.inf
        num = den = 0.0
        for features, valence in lived:
            d = _dist(surface, features)
            nearest = min(nearest, d)
            w = math.exp(-d / ECHO_SCALE)
            num += w * valence
            den += w
        return min(nearest, 1.0), num / (den + 1.0)

    def _kin(self, surface: tuple) -> float:
        """What the category that admits this surface has felt like, if any."""
        for cat in self.channel.categories.values():
            if cat.rule.side(surface) == cat.side:
                lived = [self.channel.experiences[i].valence for i in cat.members
                         if self.channel.experiences[i].valence is not None]
                return sum(lived) / len(lived) if lived else 0.0
        return 0.0

    def choose(self, obs: list, c: Contrasts) -> tuple:
        """Weigh every affordable act by the tendencies and draw one.

        Resting always scores nothing, so a mind whose tendencies make every
        act look worse than nothing will rest. Nothing here prefers one sign
        of consequence over the other; the tendencies decide, and they were
        drawn at random or inherited.
        """
        d = self.disposition
        lived = [(e.features, e.valence) for e in self.channel.experiences.values()
                 if e.features is not None and e.valence is not None]
        options = [("rest", None, 0.0)]
        for fid, surface in obs:
            novelty, echo = self._felt(surface, lived)
            kin = self._kin(surface)
            for act in ("touch", "consume"):
                if act == "touch" and fid in self.touched:
                    continue
                if not self.body.can_afford(act):
                    continue
                score = d.novelty * novelty + d.echo * echo + d.kin * kin + (d.bold if act == "consume" else 0.0)
                options.append((act, fid, score))
        heat = max(d.heat, 1e-3)
        top = max(o[2] for o in options)
        weights = [math.exp((o[2] - top) / heat) for o in options]
        act, fid, _ = self.rng.choices(options, weights=weights, k=1)[0]
        return act, fid

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
        if len(views) < MIN_VIEWS:
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
            "disposition": self.disposition.to_dict(),
            "perspectives": [p.to_dict() for p in self.perspectives],
            "puzzles": [p.to_dict() for p in self.puzzles],
            "accounted": sorted(self.accounted),
            "considered_at": self._considered_at,
            "scanned": self._scanned,
        }

    def restore(self, d: dict) -> None:
        self.age = d["age"]
        self.body = Body.from_dict(d["body"])
        self.disposition = Disposition.from_dict(d["disposition"])
        self.perspectives = [Perspective.from_dict(p) for p in d["perspectives"]]
        self.puzzles = [Puzzle(**p) for p in d["puzzles"]]
        self.accounted = set(d["accounted"])
        self._considered_at = d.get("considered_at", 0)
        self._scanned = d.get("scanned", 0)

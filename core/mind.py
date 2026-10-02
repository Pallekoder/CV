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
            at birth: a mind can be born drawn toward what hurt it. Two of
            them read the body: how hungry it is and how hurt. Nothing
            here says which way is right. The body's physics, and whether
            the mind is still around later, are the only judges.
  act       touch or consume, and live the consequence. Loss is permanent.
  bend      let what was just lived bend the tendencies that chose it, by
            an inherited amount whose sign is random at birth. The ledger
            never holds the why; the body is bent by it anyway.
  utter     when something surprises it, emit a coined sound. The sound is
            written down. The state that produced it is not.
  consider  look at what it has lived, along every axis it perceives, for
            the cut that consequence supports best; carve the open bucket,
            narrow a category whose members disagree, doubt and dissolve
            what no longer holds, undo a cut that parts nothing. All of it
            its own. If a visitor left a perspective, that is one more
            candidate cut, weighed the same way.
  visit     rarely, and only if visits are switched on, a teacher looks at
            the open bucket and leaves a perspective. The mind never waits
            for one.

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

from .channel import Channel, Experience, best_line, purity
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

ECHO_SCALE = 0.3     # how far away a lived consequence still echoes
VARIATION = 0.15     # how far a child's tendencies drift from its parent's
BOUND = 3.0          # how far a tendency can be bent within a life
KEEP_PUZZLES = 500   # puzzles held at most; the oldest go first
KEEP_PERSPECTIVES = 500

FROZEN: frozenset = frozenset()   # tendencies held at zero, for experiments asking what a knob does

CONSULT_MIN = 4      # lived consequences of both signs before it looks for a cut
MIN_SIDE = 4         # a side with fewer lived members cannot be carved
COMMIT_PURITY = 0.8  # both sides this pure, and purer together than what they were cut from: carve
TWO_SIDED_IMPROVEMENT = 0.05
ONE_SIDED_MIN = 6    # or one side this big ...
ONE_SIDED_PURITY = 0.9   # ... and this pure ...
IMPROVEMENT = 0.15       # ... and this much purer than the scope it is carved from
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


def freeze(names) -> None:
    """Hold the named tendencies at zero in every mind drawn or begotten from now on.

    The random draws still happen, so a frozen world and a free world with
    the same seed share every other tendency of every being: only the
    frozen knobs differ. That is what makes the two comparable.
    """
    global FROZEN
    unknown = set(names) - set(Disposition.__dataclass_fields__)
    if unknown:
        raise ValueError(f"no such tendencies: {sorted(unknown)}")
    FROZEN = frozenset(names)


@dataclass(frozen=True)
class Disposition:
    """Heritable tendencies. No sign is given for any of them.

    novelty     pull toward (or away from) what has not been lived
    echo        pull toward (or away from) what consequences near it were
    kin         pull toward (or away from) what the admitting category's consequences were
    bold        pull toward consuming rather than touching
    hungry      when energy is low: pull toward acting at all (or toward resting)
    hurt        when life is low: pull toward consuming (or away from it)
    heat        how much chance is left in the draw
    plasticity  how much, and which way, a lived consequence bends the first four
    """

    novelty: float
    echo: float
    kin: float
    bold: float
    hungry: float
    hurt: float
    heat: float
    plasticity: float

    BENDABLE = ("novelty", "echo", "kin", "bold")

    @classmethod
    def random(cls, rng: random.Random) -> "Disposition":
        d = dict(
            novelty=rng.uniform(-1, 1),
            echo=rng.uniform(-1, 1),
            kin=rng.uniform(-1, 1),
            bold=rng.uniform(-1, 1),
            hungry=rng.uniform(-1, 1),
            hurt=rng.uniform(-1, 1),
            heat=rng.uniform(0.05, 0.5),
            plasticity=rng.uniform(-0.5, 0.5),
        )
        return cls(**{k: (0.0 if k in FROZEN else v) for k, v in d.items()})

    def vary(self, rng: random.Random) -> "Disposition":
        d = {k: v + rng.gauss(0, VARIATION) for k, v in self.to_dict().items()}
        d["heat"] = max(0.02, self.heat + rng.gauss(0, VARIATION / 2))
        d["plasticity"] = self.plasticity + rng.gauss(0, VARIATION / 2)
        return Disposition(**{k: (0.0 if k in FROZEN else v) for k, v in d.items()})

    def bend(self, components: dict, valence: float) -> "Disposition":
        """What was just lived pulls on the tendencies that chose it.

        With plasticity above zero, a tendency that pointed at something
        that turned out positive grows, and one that pointed at something
        that turned out negative shrinks. Below zero, the opposite. Which
        of those is worth having is not decided here.
        """
        d = self.to_dict()
        for name in self.BENDABLE:
            c = components.get(name, 0.0)
            if c:
                d[name] = max(-BOUND, min(BOUND, d[name] + self.plasticity * valence * c))
        return Disposition(**d)

    def to_dict(self) -> dict:
        return {"novelty": self.novelty, "echo": self.echo, "kin": self.kin, "bold": self.bold,
                "hungry": self.hungry, "hurt": self.hurt, "heat": self.heat, "plasticity": self.plasticity}

    @classmethod
    def from_dict(cls, d: dict) -> "Disposition":
        return cls(**d)

    def __str__(self) -> str:
        return (f"nov {self.novelty:+.2f} echo {self.echo:+.2f} kin {self.kin:+.2f} bold {self.bold:+.2f} "
                f"hungry {self.hungry:+.2f} hurt {self.hurt:+.2f} heat {self.heat:.2f} plast {self.plasticity:+.2f}")


@dataclass(frozen=True)
class Puzzle:
    about: int       # ledger index of the unexplained thing
    found: int       # ledger index of the moment it was found
    tick: int
    token: str
    exp: int = -1    # the featureless experience it became, in the channel

    def to_dict(self) -> dict:
        return {"about": self.about, "found": self.found, "tick": self.tick, "token": self.token, "exp": self.exp}


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
                 disposition: Optional[Disposition] = None, visit_rate: int = 0,
                 visit_rng: Optional[random.Random] = None) -> None:
        self.ledger = ledger
        self.channel = channel
        self.teachers = teachers          # who may visit; nobody does unless visit_rate > 0
        self.visit_rate = visit_rate      # a visit about every this many ticks, never two closer than half that
        self.visit_rng = visit_rng or random.Random(0)   # its own stream, so visits change nothing else
        self.rng = rng
        self.nature = disposition if disposition is not None else Disposition.random(rng)
        self.disposition = self.nature   # what it is now; life bends this, never the nature
        self.body = Body()
        self.age = 0
        self.perspectives: list[Perspective] = []
        self.puzzles: list[Puzzle] = []
        self.accounted: set = set()   # ledger indices already taken in by reflect
        self.touched: dict = {}       # per-shell working memory: form id -> ledger index
        self._considered_at = 0       # how many lived consequences there were at the last consult
        self._scanned = 0             # how far reflect has read its own ledger
        self._chosen: dict = {}       # the components behind the last choice, for bend
        self._offered: list = []      # visitors' proposals not yet weighed
        self._last_visit = -10 ** 9

    # -- shells and contacts -------------------------------------------------

    def enter(self, space) -> None:
        """A new shell. Working memory of forms resets; nothing else does."""
        self.touched = {}
        self.ledger.append(self.age, "enter", shell=getattr(space, "label", None),
                           forms=len(getattr(space, "forms", {})))

    def receive(self, p: Perspective) -> None:
        """Take in words from the distant one. They land in the ledger like
        any other thing that happened, for reflect to find."""
        self.ledger.append(self.age, "contact", text=p.remark, source=p.source)
        self.perspectives.append(p)

    # -- visits ------------------------------------------------------------

    def visit(self, t: int) -> list:
        """Rarely, a teacher looks at the open bucket and leaves a perspective."""
        if not self.teachers or self.visit_rate <= 0:
            return []
        if t - self._last_visit < self.visit_rate // 2 or self.visit_rng.random() >= 1.0 / self.visit_rate:
            return []
        self._last_visit = t
        teacher = self.visit_rng.choice(self.teachers)
        p = teacher.regard(self.channel.view(None), t)
        self.ledger.append(t, "visit", source=p.source, remark=p.remark,
                           proposal=p.proposal.to_dict() if p.proposal else None)
        self.perspectives.append(p)
        del self.perspectives[:-KEEP_PERSPECTIVES]
        if p.proposal is not None:
            self._offered.append(p)
        return [f"  a visitor, {p.source}: {p.remark}"]

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
                bent = self.bend(exp.valence)
                if bent:
                    lines.append("  bends: " + bent)
                reason = self.surprised(exp, landed, before)
                if reason:
                    why = (reason, contrasts.summary(), fid, exp.valence, landed)
                    that = self.utter(t, why)
                    del why
                    lines.append(f'  utters "{that}"   (the why is not kept)')
                if not self.body.alive:
                    lines.append("  life has run out.")

        lines += self.visit(t)
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
            index = self.channel.new_index()
            found = self.ledger.append(t, "puzzle", about=e.index, token=token, exp=index)
            self.channel.add(Experience(index=index, tick=t, features=None, token=token))
            self.puzzles.append(Puzzle(about=e.index, found=found.index, tick=t, token=token, exp=index))
            del self.puzzles[:-KEEP_PUZZLES]
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

    def _near(self, surface: tuple, lived: list) -> tuple:
        """How new this surface is, and what consequences near it were.

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
        """What the consequences were in the most specific category that admits this surface."""
        name = self.channel.locate(surface)
        if name is None:
            return 0.0
        lived = [e.valence for e in self.channel.members_of(name) if e.valence is not None]
        return sum(lived) / len(lived) if lived else 0.0

    def choose(self, obs: list, c: Contrasts) -> tuple:
        """Weigh every affordable act by the tendencies and draw one.

        Resting always scores nothing, so a mind whose tendencies make every
        act look worse than nothing will rest. Hunger and hurt are read from
        the body and weighed like everything else. Nothing here prefers one
        sign of consequence over the other; the tendencies decide, and they
        were drawn at random, inherited, or bent by what was lived.
        """
        d = self.disposition
        hunger = 1.0 - self.body.energy / ENERGY_MAX
        hurt = 1.0 - self.body.life / LIFE_START
        lived = [(e.features, e.valence) for e in self.channel.experiences.values()
                 if e.features is not None and e.valence is not None]
        options = [("rest", None, 0.0, {})]
        for fid, surface in obs:
            novelty, echo = self._near(surface, lived)
            kin = self._kin(surface)
            for act in ("touch", "consume"):
                if act == "touch" and fid in self.touched:
                    continue
                if not self.body.can_afford(act):
                    continue
                consume = 1.0 if act == "consume" else 0.0
                components = {"novelty": novelty, "echo": echo, "kin": kin, "bold": consume}
                score = (d.novelty * novelty + d.echo * echo + d.kin * kin + d.bold * consume
                         + d.hungry * hunger + d.hurt * hurt * consume)
                options.append((act, fid, score, components))
        heat = max(d.heat, 1e-3)
        top = max(o[2] for o in options)
        weights = [math.exp((o[2] - top) / heat) for o in options]
        act, fid, _, components = self.rng.choices(options, weights=weights, k=1)[0]
        self._chosen = components
        return act, fid

    # -- bend --------------------------------------------------------------

    def bend(self, valence: float) -> str:
        """Let the consequence just lived bend the tendencies that chose it.

        Returns a short account of the largest change, or an empty string.
        """
        before = self.disposition
        self.disposition = before.bend(self._chosen, valence)
        self._chosen = {}
        changes = {k: getattr(self.disposition, k) - getattr(before, k) for k in Disposition.BENDABLE}
        name, delta = max(changes.items(), key=lambda kv: abs(kv[1]))
        return f"{name} {delta:+.3f}" if abs(delta) >= 0.005 else ""

    # -- act ---------------------------------------------------------------

    def act(self, space, kind: str, fid: str, surface: tuple, t: int) -> tuple:
        self.body.spend(kind)
        raw = space.touch(fid) if kind == "touch" else space.consume(fid)
        v = Valence(raw)
        self.body.live(v)
        index = self.channel.new_index()
        entry = self.ledger.append(
            t, "act", act=kind, form=fid, valence=raw, exp=index,
            life=round(self.body.life, 3), energy=round(self.body.energy, 3),
        )
        if kind == "consume":
            self.ledger.append(t, "tombstone", form=fid)
            self.touched.pop(fid, None)
        else:
            self.touched[fid] = entry.index
        exp = Experience(index=index, tick=t, features=tuple(surface), token=fid, valence=raw)
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
            return lines  # nothing new has been lived; nothing new to look at
        self._considered_at = lived_total

        stood = [c.name for c in self.channel.leaves()]

        # a category whose members disagree gets a chance to narrow first
        for name in stood:
            lived = [e for e in self.channel.members_of(name) if e.valence is not None]
            if purity(lived) >= COMMIT_PURITY or len(lived) < 2 * MIN_SIDE or {e.sign for e in lived} != {1, -1}:
                continue
            lines += self._look(t, name)

        # then the open bucket
        lines += self._look(t, None)

        # doubt falls only on what already stood and still stands unnarrowed
        lines += self._doubt(t, stood)

        # a cut whose two sides no longer part consequence is undone
        lines += self._undo_idle_cuts(t, stood)
        return lines

    def _own_cuts(self, lived: list) -> list:
        """Along every axis it perceives, the line that best sorts what it has lived."""
        dims = len(lived[0].features)
        cuts = []
        for axis in range(dims):
            rule = best_line(lived, axis)
            if rule is not None:
                cuts.append((rule, f"own axis {axis}"))
        return cuts

    def _look(self, t: int, within: Optional[str]) -> list:
        """Weigh every candidate cut for one scope and carve if consequence allows."""
        lines = []
        lived = [e for e in self.channel.direct(within) if e.valence is not None and e.features is not None]
        if len(lived) < CONSULT_MIN or {e.sign for e in lived} != {1, -1}:
            return lines
        candidates = self._own_cuts(lived)
        if within is None and self._offered:
            candidates += [(p.proposal, f"visitor {p.source}") for p in self._offered]
            self._offered = []
        where = f"within '{within}'" if within else "in the open"

        scope_purity = purity(lived)
        best = None
        seen = set()
        for rule, source in candidates:
            if rule in seen:
                continue
            seen.add(rule)
            hi = [e for e in lived if rule.side(e.features) == 1]
            lo = [e for e in lived if rule.side(e.features) == -1]
            if min(len(hi), len(lo)) < MIN_SIDE:
                continue
            ph, pl = purity(hi), purity(lo)
            together = (len(hi) * ph + len(lo) * pl) / (len(hi) + len(lo))
            if min(ph, pl) >= COMMIT_PURITY and together - scope_purity >= TWO_SIDED_IMPROVEMENT:
                score = (2, min(ph, pl), max(ph, pl))
            else:
                pure_side, pp = (hi, ph) if ph >= pl else (lo, pl)
                if len(pure_side) >= ONE_SIDED_MIN and pp >= ONE_SIDED_PURITY and pp - scope_purity >= IMPROVEMENT:
                    score = (1, pp, min(ph, pl))
                else:
                    continue
            if best is None or score > best[0]:
                best = (score, rule, source, ph, pl)
        if best is None:
            lines.append(f"  looks {where}: {len(candidates)} cuts weighed; none holds")
            return lines
        score, rule, source, ph, pl = best
        cats = self.channel.split(rule, t, coin, within)
        kind = "refine" if within else "carve"
        self.ledger.append(
            t, kind, within=within, rule=rule.to_dict(), names=[c.name for c in cats],
            sizes=[len(c.members) for c in cats], purities=[round(ph, 3), round(pl, 3)],
            depth=self.channel.depth(cats[0].name), after=source,
        )
        verb = f"narrows '{within}'" if within else "carves the open"
        lines.append(
            f"  {verb} along axis {rule.axis} at {rule.threshold:.3f} ({source}, {len(candidates)} cuts weighed): "
            + ", ".join(f"'{c.name}' x{len(c.members)} ({pu:.2f})" for c, pu in zip(cats, (ph, pl)))
        )
        return lines

    def _doubt(self, t: int, stood: list) -> list:
        """Its own doubt: a category that no longer agrees with itself dissolves."""
        lines = []
        for name in stood:
            if name not in self.channel.categories or self.channel.children(name):
                continue
            members = self.channel.members_of(name)
            lived = [e for e in members if e.valence is not None]
            if len(lived) < MIN_SIDE:
                continue
            pur = purity(members)
            if pur >= DOUBT_PURITY:
                continue
            cat = self.channel.dissolve(name)
            self.ledger.append(t, "dissolve", name=cat.name, parent=cat.parent,
                               purity=round(pur, 3), members=len(cat.members))
            that = self.utter(t, ("dissolve", cat.name, round(pur, 3)))
            where = f"into '{cat.parent}'" if cat.parent else "into the open"
            lines.append(f"  dissolves '{cat.name}' ({pur:.2f}); {len(cat.members)} fall back {where}")
            lines.append(f'  utters "{that}"   (the why is not kept)')
        return lines

    def _undo_idle_cuts(self, t: int, stood: list) -> list:
        """Where both children of a scope lean the same way and agree together,
        the cut separates nothing; the children fall back into the scope."""
        lines = []
        scopes = [None] + [c.name for c in self.channel.categories.values()]
        for scope in scopes:
            kids = self.channel.children(scope)
            if len(kids) != 2 or any(k.name not in stood for k in kids):
                continue
            leanings = []
            for k in kids:
                lived = [e for e in self.channel.members_of(k.name) if e.sign]
                if not lived:
                    break
                leanings.append(1 if sum(e.sign for e in lived) >= 0 else -1)
            if len(leanings) != 2 or leanings[0] != leanings[1]:
                continue
            together = self.channel.members_of(kids[0].name) + self.channel.members_of(kids[1].name)
            pur = purity(together)
            if pur < COMMIT_PURITY:
                continue
            for k in kids:
                self.channel.dissolve(k.name)
            self.ledger.append(t, "merge", within=scope, names=[k.name for k in kids],
                               members=len(together), purity=round(pur, 3))
            where = f"into '{scope}'" if scope else "into the open"
            lines.append(f"  undoes a cut that parted nothing: '{kids[0].name}' and '{kids[1].name}' "
                         f"({pur:.2f} together); {len(together)} fall back {where}")
        return lines

    # -- persistence -------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "body": self.body.to_dict(),
            "nature": self.nature.to_dict(),
            "disposition": self.disposition.to_dict(),
            "perspectives": [p.to_dict() for p in self.perspectives],
            "puzzles": [p.to_dict() for p in self.puzzles],
            "accounted": sorted(self.accounted),
            "considered_at": self._considered_at,
            "scanned": self._scanned,
            "last_visit": self._last_visit,
            "offered": [p.to_dict() for p in self._offered],
        }

    def restore(self, d: dict) -> None:
        self.age = d["age"]
        self.body = Body.from_dict(d["body"])
        self.nature = Disposition.from_dict(d.get("nature", d["disposition"]))
        self.disposition = Disposition.from_dict(d["disposition"])
        self.perspectives = [Perspective.from_dict(p) for p in d["perspectives"]]
        self.puzzles = [Puzzle(**p) for p in d["puzzles"]]
        self.accounted = set(d["accounted"])
        self._considered_at = d.get("considered_at", 0)
        self._scanned = d.get("scanned", 0)
        self._last_visit = d.get("last_visit", -10 ** 9)
        self._offered = [Perspective.from_dict(p) for p in d.get("offered", [])]

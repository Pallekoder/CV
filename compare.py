#!/usr/bin/env python3
"""Did being around change anything?

Runs the many for some generations, then puts children of the survivors
and an equal number of strangers (tendencies drawn at random, nothing
lived) into identical fresh shells for one generation each, and compares
what happened to them. Nothing in the world prefers one sign of
consequence over the other, so any difference between the two groups is
what consequence did on its own.

    python compare.py --seed 0 --beings 24 --generations 20
"""
from __future__ import annotations

import argparse
import random
import time

from core import mind as mind_module
from core.being import Being
from core.many import World
from core.teachers import default_teachers
from shell.seed import LAW_KINDS, build, law_for

DIMS = 4


def acts_since(beings, before) -> tuple:
    consumes = negative = touches = negative_touches = 0
    for b in beings:
        for e in b.ledger.since(before.get(b.id, 0)):
            if e.kind != "act":
                continue
            v = e.payload["valence"]
            if e.payload["act"] == "consume":
                consumes += 1
                negative += v < 0
            else:
                touches += 1
                negative_touches += v < 0
    return consumes, negative, touches, negative_touches


def drift(beings) -> float:
    """How far life has bent the living from what they were born as."""
    if not beings:
        return 0.0
    total = 0.0
    for b in beings:
        total += sum(abs(getattr(b.mind.disposition, k) - getattr(b.mind.nature, k))
                     for k in b.mind.disposition.BENDABLE) / len(b.mind.disposition.BENDABLE)
    return total / len(beings)


def trial(group, seed, law, ticks, energy=None) -> dict:
    lost = gathered = 0.0
    alive = consumes = negative = acts = ticks_lived = 0
    for i, b in enumerate(group):
        space = build("scatter", random.Random(f"trial:{seed}:{i}"), law)
        b.mind.enter(space)
        if energy is not None:
            b.mind.body.energy = energy
        start = len(b.ledger)
        for _ in range(ticks):
            b.mind.tick(space)
            if not b.alive:
                break
        for e in b.ledger.since(start):
            if e.kind == "notice":
                ticks_lived += 1
            if e.kind != "act":
                continue
            acts += 1
            v = e.payload["valence"]
            lost += -v if v < 0 else 0.0
            gathered += v if v > 0 else 0.0
            if e.payload["act"] == "consume":
                consumes += 1
                negative += v < 0
        alive += b.alive
    n = len(group)
    return {"n": n, "alive": alive, "lost": lost / n, "gathered": gathered / n,
            "consumes": consumes, "negative": negative, "acts": acts / n,
            "rests": (ticks_lived - acts) / n, "drift": drift(group)}


def describe(name: str, r: dict) -> str:
    share = 100 * r["negative"] / max(1, r["consumes"])
    return (f"  {name:<28} alive {r['alive']:2d}/{r['n']}   life lost {r['lost']:.2f}   gathered {r['gathered']:.2f}   "
            f"negative consumes {r['negative']}/{r['consumes']} ({share:.0f}%)   "
            f"acts {r['acts']:.1f}  rests {r['rests']:.1f}   bent {r['drift']:.2f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--beings", type=int, default=24)
    ap.add_argument("--generations", type=int, default=20)
    ap.add_argument("--ticks", type=int, default=60)
    ap.add_argument("--first-ticks", type=int, default=12)
    ap.add_argument("--frozen", default="", help="tendencies held at zero, comma-separated, e.g. hungry,hurt,plasticity")
    ap.add_argument("--law", choices=LAW_KINDS, default="axis")
    args = ap.parse_args(argv)
    frozen = [n for n in args.frozen.split(",") if n]
    mind_module.freeze(frozen)

    t0 = time.time()
    teachers = default_teachers(DIMS)
    world = World(args.seed, DIMS, teachers)
    world.found(args.beings)
    law = law_for(args.seed, DIMS, args.law)
    print(f"seed {args.seed}: {args.beings} beings, {args.generations} generations; "
          f"law, hidden from them: {law.describe()}" + (f"; frozen at zero: {', '.join(frozen)}" if frozen else ""))
    print("  gen  survived  died   consumes  negative   touches  negative")
    for _ in range(args.generations):
        g = world.generation
        kind = "first" if g == 0 else "scatter"
        ticks = args.first_ticks if g == 0 else args.ticks
        before = {b.id: len(b.ledger) for b in world.beings}

        def builder(b, kind=kind, g=g):
            return build(kind, random.Random(f"{args.seed}:{g}:{b.id}"), law)

        world.live(builder, ticks)
        consumes, negative, touches, negative_touches = acts_since(world.beings, before)
        report = world.select(refound=True)
        print(f"  {g:3d}  {len(report['living']):8d}  {len(report['died']):4d}   {consumes:8d}  "
              f"{100 * negative / max(1, consumes):7.0f}%  {touches:8d}  {100 * negative_touches / max(1, touches):7.0f}%")

    living = world.living
    if not living:
        print("no one is left to compare.")
        return 1
    print()
    print("  among the living, signs of what they were born with:")
    for name in ("echo", "kin", "bold", "novelty", "hungry", "hurt", "plasticity"):
        values = [getattr(b.mind.nature, name) for b in living]
        print(f"    {name:<10} +{sum(1 for v in values if v > 0):2d} / -{sum(1 for v in values if v < 0):2d}"
              f"   mean {sum(values) / len(values):+.2f}")
    print(f"  bent by life so far, mean over the living: {drift(living):.2f}")

    n = len(living)
    children = [b.beget(args.seed, 99, i, teachers) for i, b in enumerate(living)]
    hungry_children = [b.beget(args.seed, 99, 1000 + i, teachers) for i, b in enumerate(living)]
    strangers = [Being.found(f"strangers{args.seed}", 99, i, teachers) for i in range(n)]
    hungry_strangers = [Being.found(f"hungry-strangers{args.seed}", 99, i, teachers) for i in range(n)]
    print()
    print(f"one generation in identical fresh shells, {n} of each (hungry: born with a quarter of the energy):")
    print(describe("children of survivors", trial(children, args.seed, law, args.ticks)))
    print(describe("strangers", trial(strangers, args.seed, law, args.ticks)))
    print(describe("children of survivors, hungry", trial(hungry_children, args.seed, law, args.ticks, energy=1.5)))
    print(describe("strangers, hungry", trial(hungry_strangers, args.seed, law, args.ticks, energy=1.5)))
    print(f"({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

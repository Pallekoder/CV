#!/usr/bin/env python3
"""Run the world.

    python run.py                                 # one mind, the seed space, the first moment
    python run.py --generations 3                 # carry it on through fresh shells
    python run.py --beings 12 --generations 20    # the many: selection by still being around
    python run.py --watch 3                       # follow one being tick by tick
    python run.py --god "..."                     # say something to them (rarely answered)
    python run.py --fresh                         # throw the saved world away

The transcript is written for you, the distant one. The minds never see
these words; they see numbers, coined syllables, and consequence.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from core.many import World
from core.persist import load, save
from core.teachers import default_teachers
from shell.seed import LAW_KINDS, build, law_for
from view import describe_being

DIMS = 4
STATE = Path("state") / "world.json"
GONE = Path("state") / "gone"


def table(world: World) -> list:
    lines = ["  being        age   life  energy  lived  neg  cats  puzzles  tendencies"]
    for b in world.beings:
        lived, neg = b.lived()
        m = b.mind
        state = f"{m.body.life:5.2f}  {m.body.energy:6.2f}" if b.alive else " gone        "
        lines.append(
            f"  {b.id:<11} {m.age:4d}  {state}  {lived:5d}  {neg:3d}  {len(m.channel.categories):4d}  "
            f"{len(m.puzzles):7d}  {m.disposition}"
        )
    return lines


def signs(beings, name: str) -> str:
    values = [getattr(b.mind.disposition, name) for b in beings]
    return f"{name} +{sum(1 for v in values if v > 0)}/-{sum(1 for v in values if v < 0)}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--beings", type=int, default=1, help="how many to found in a new world")
    ap.add_argument("--generations", type=int, default=1, help="how many shells to live through")
    ap.add_argument("--ticks", type=int, default=60, help="ticks per generation")
    ap.add_argument("--first-ticks", type=int, default=12, help="ticks in the seed space")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--law", choices=LAW_KINDS, default=None,
                    help="the hidden law of a new world: 'axis' (one cut) or 'corner' (two cuts at once); default axis")
    ap.add_argument("--god", default=None, help="something to say to them")
    ap.add_argument("--watch", type=int, default=None, help="print one being's ticks (default: the only one)")
    ap.add_argument("--fresh", action="store_true", help="discard any saved world")
    ap.add_argument("--state", default=str(STATE))
    args = ap.parse_args(argv)

    state = Path(args.state)
    gone_dir = state.parent / "gone"

    if state.exists() and not args.fresh:
        world = load(state, default_teachers)
        print(f"the world continues: generation {world.generation}, "
              f"{len(world.living)} of {len(world.beings)} living, {len(world.ledger)} entries in its record")
    else:
        world = World(args.seed, DIMS, default_teachers(DIMS))
        world.options["law"] = args.law or "axis"
        world.found(args.beings)
        print(f"a new world. nothing has happened yet. {len(world.beings)} being(s), tendencies drawn at random:")
        for b in world.beings:
            print(f"  {b.id:<11} {b.mind.disposition}")

    many = len(world.beings) > 1
    watch = args.watch if args.watch is not None else (None if many else 0)
    law_kind = world.options.get("law", "axis")
    if args.law and args.law != law_kind:
        print(f"(this world's law is '{law_kind}' and stays so; --law applies to a new world)")
    law = law_for(world.seed, world.dims, law_kind)

    if not world.living:
        print("no one is left. the record remains. use --fresh to begin another world.")
        return 1

    if args.god:
        p = world.god.speak(world.generation, args.god)
        if p is None:
            print(f"(too soon; the distant one stays silent. last contact in generation {world.god.last_contact})")
        else:
            for b in world.living:
                b.mind.receive(p)
            print(f'(the distant one speaks to all who live: "{args.god}")')

    history = []
    for _ in range(args.generations):
        g = world.generation
        kind = "first" if g == 0 else "scatter"
        ticks = args.first_ticks if g == 0 else args.ticks
        print()
        print(f"generation {g}: shell '{kind}', {ticks} ticks; law, hidden from them: {law.describe()}")

        def builder(b, kind=kind, g=g):
            return build(kind, random.Random(f"{world.seed}:{g}:{b.id}"), law)

        for line in world.live(builder, ticks, watch):
            print(line)
        for line in table(world):
            print(line)
        report = world.select(refound=many, gone_dir=gone_dir)
        for b in report["died"]:
            print(f"  gone: {b.id} (age {b.mind.age}, born in {b.born}, {len(b.ledger)} entries sealed)")
        for b in report["born"]:
            print(f"  born: {b.id} of {b.parent}   {b.mind.disposition}")
        if report["extinct"]:
            print("  no one was left." + (" the world begins again from strangers." if many else ""))
        living = world.living
        if many and living:
            print("  among the living: " + ", ".join(
                signs(living, n) for n in ("echo", "kin", "bold", "novelty", "hungry", "hurt", "plasticity")))
        history.append((g, len(report["living"]), len(report["died"]),
                        sum(1 for b in living if b.mind.disposition.echo > 0),
                        sum(1 for b in living if b.mind.disposition.echo < 0),
                        sum(b.mind.body.life for b in living) / len(living) if living else 0.0))
        if not living and not many:
            print("the mind is gone. the ledger remains.")
            break

    print()
    if many and len(history) > 1:
        print("  gen  survived  died  echo+  echo-  mean life")
        for g, lived_n, died_n, ep, en, ml in history:
            print(f"  {g:3d}  {lived_n:8d}  {died_n:4d}  {ep:5d}  {en:5d}  {ml:9.2f}")
        print()
    if not many:
        print("\n".join(describe_being(world.beings[0])))
    chains = all(b.ledger.verify() for b in world.beings)
    print(f"world record: {len(world.ledger)} entries, chain {'intact' if world.ledger.verify() else 'BROKEN'}; "
          f"beings' chains {'intact' if chains else 'BROKEN'}")
    save(state, world)
    print(f"world saved to {state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

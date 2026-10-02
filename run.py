#!/usr/bin/env python3
"""Run the first unit.

    python run.py                      # first run: the seed space, the first moment
    python run.py --ticks 20           # continue the saved core in a fresh shell
    python run.py --god "..."          # speak, if enough time has passed
    python run.py --fresh              # throw the saved core away and begin again

The transcript is written for the distant one to read. The mind never sees
these words.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from core.channel import Channel, purity
from core.god import God
from core.ledger import Ledger
from core.mind import Mind
from core.persist import load, save
from core.teachers import default_teachers
from shell.seed import BUILDERS, build, law_for

DIMS = 4
STATE = Path("state") / "core.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticks", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shell", choices=sorted(BUILDERS), default=None,
                    help="which space to build (default: 'first' for a new core, 'scatter' after)")
    ap.add_argument("--god", default=None, help="something to say to it")
    ap.add_argument("--fresh", action="store_true", help="discard any saved core")
    ap.add_argument("--state", default=str(STATE))
    args = ap.parse_args(argv)

    state = Path(args.state)
    rng = random.Random(args.seed)

    if state.exists() and not args.fresh:
        ledger, channel, mind, god, dims = load(state, default_teachers, rng)
        kind = args.shell or "scatter"
        print(f"core continues: age {mind.age}, {len(ledger)} ledger entries, "
              f"{len(channel.experiences)} experiences, {len(channel.categories)} categories, "
              f"{len(mind.puzzles)} puzzles")
    else:
        dims = DIMS
        ledger, channel = Ledger(), Channel()
        god = God(ledger)
        mind = Mind(ledger, channel, default_teachers(dims), rng)
        kind = args.shell or "first"
        print("a new core. nothing has happened yet.")

    if not mind.body.alive:
        print("the mind is gone. the ledger remains. use --fresh to begin another.")
        return 1

    law = law_for(args.seed, dims)
    shell_rng = random.Random(f"{args.seed}:{god.shells_built}")
    space = god.remake(mind.age, lambda: build(kind, shell_rng, law))
    mind.enter(space)
    print(f"shell {god.shells_built} ({kind}); law, hidden from the mind: {law.describe()}")
    print(space.describe())
    print()

    if args.god:
        p = god.speak(mind.age, args.god)
        if p is None:
            print(f"(too soon; the distant one stays silent. last contact at {god.last_contact})")
        else:
            mind.receive(p)
            print(f'(the distant one speaks: "{args.god}")')
        print()

    for _ in range(args.ticks):
        for line in mind.tick(space):
            print(line)
        if not mind.body.alive:
            break

    print()
    print(space.describe())
    print()
    print(f"body: life {mind.body.life:.2f}  energy {mind.body.energy:.2f}  age {mind.age}")
    open_n = len(channel.open_bucket())
    print(f"channel: {len(channel.experiences)} experiences, {open_n} open, {len(channel.categories)} categories")
    for name, cat in channel.categories.items():
        members = channel.members_of(name)
        lived = [e for e in members if e.valence is not None]
        mean = sum(e.valence for e in lived) / len(lived) if lived else 0.0
        print(f"  '{name}': axis {cat.rule.axis} {'>=' if cat.side > 0 else '< '} {cat.rule.threshold:.3f}, "
              f"{len(members)} members, agreement {purity(members):.2f}, mean {mean:+.3f}")
    print(f"puzzles: {len(mind.puzzles)}")
    for p in mind.puzzles:
        print(f'  "{p.token}" (about #{p.about}, found at tick {p.tick})')
    print(f"ledger: {len(ledger)} entries, chain {'intact' if ledger.verify() else 'BROKEN'}")

    save(state, ledger=ledger, channel=channel, mind=mind, god=god, dims=dims)
    print(f"core saved to {state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

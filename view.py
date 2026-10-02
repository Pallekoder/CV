#!/usr/bin/env python3
"""Look into the channels.

    python view.py                       # every living being, one row each, then growth by generation
    python view.py --being 3             # one being: its open bucket, its categories as a tree, its history
    python view.py --all                 # every living being's tree
    python view.py --gone ne-ti-so       # a sealed being, from state/gone/

Growth shows here. The open bucket is the box they fill. A category is a
region carved out of it along one axis. A narrowing is a category split
into two more specific children because the consequences inside it
disagreed. A dissolution is a category that failed and fell back.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from core.being import Being
from core.channel import purity
from core.persist import load
from core.teachers import default_teachers

STATE = Path("state") / "world.json"


# -- one being ---------------------------------------------------------------

def open_summary(channel) -> str:
    open_ = channel.open_bucket()
    featured = [e for e in open_ if e.features is not None]
    bare = [e for e in open_ if e.features is None]
    pos = sum(1 for e in featured if e.sign and e.sign > 0)
    neg = sum(1 for e in featured if e.sign and e.sign < 0)
    return f"open: {len(featured)} with a surface ({pos} +, {neg} -), {len(bare)} without one"


def tree_lines(channel, inherited: set, scope=None, indent: str = "  ") -> list:
    lines = []
    for cat in sorted(channel.children(scope), key=lambda c: (c.born, c.name)):
        members = channel.members_of(cat.name)
        lived = [e for e in members if e.valence is not None]
        mean = sum(e.valence for e in lived) / len(lived) if lived else 0.0
        kids = channel.children(cat.name)
        tag = "   (inherited)" if cat.name in inherited else ""
        if kids and not members:
            lines.append(f"{indent}'{cat.name}'  {cat.describe_rule()}   narrowed into {len(kids)}   born {cat.born}{tag}")
        else:
            lines.append(
                f"{indent}'{cat.name}'  {cat.describe_rule()}   {len(members)} members  "
                f"agreement {purity(members):.2f}  mean {mean:+.3f}   born {cat.born}{tag}"
            )
        lines += tree_lines(channel, inherited, cat.name, indent + "    ")
    return lines


def history_lines(ledger) -> list:
    lines = []
    for e in ledger:
        p = e.payload
        if e.kind == "born" and p.get("categories"):
            lines.append(f"  born carrying {len(p['categories'])} categories from {p.get('parent')}")
        elif e.kind == "carve":
            lines.append(
                f"  tick {e.tick:4d}  carve     axis {p['rule']['axis']} at {p['rule']['threshold']:+.3f}  -> "
                + ", ".join(f"'{n}' x{s} ({pu:.2f})" for n, s, pu in zip(p["names"], p["sizes"], p["purities"]))
                + f"   after {p['after']}"
            )
        elif e.kind == "refine":
            lines.append(
                f"  tick {e.tick:4d}  narrow    '{p['within']}' along axis {p['rule']['axis']} at {p['rule']['threshold']:+.3f}  -> "
                + ", ".join(f"'{n}' x{s} ({pu:.2f})" for n, s, pu in zip(p["names"], p["sizes"], p["purities"]))
                + f"   depth {p['depth']}"
            )
        elif e.kind == "dissolve":
            where = f"into '{p['parent']}'" if p.get("parent") else "into the open"
            lines.append(f"  tick {e.tick:4d}  dissolve  '{p['name']}' ({p['purity']:.2f}); {p['members']} fall back {where}")
        elif e.kind == "merge":
            where = f"into '{p['within']}'" if p.get("within") else "into the open"
            lines.append(f"  tick {e.tick:4d}  undo      '{p['names'][0]}' and '{p['names'][1]}' parted nothing "
                         f"({p['purity']:.2f} together); {p['members']} fall back {where}")
    return lines


def describe_being(being: Being) -> list:
    born = being.ledger[0]
    inherited = set(born.payload.get("categories", [])) if born.kind == "born" else set()
    m = being.mind
    state = f"life {m.body.life:.2f}, energy {m.body.energy:.2f}" if being.alive else "gone"
    lines = [
        f"{being.id}: age {m.age}, born in generation {being.born} of {being.parent or 'no one'}; "
        f"{state}; {len(m.puzzles)} puzzles held",
        "  " + open_summary(being.channel),
    ]
    tree = tree_lines(being.channel, inherited)
    lines += tree if tree else ["  no categories yet"]
    history = history_lines(being.ledger)
    if history:
        lines.append("  history:")
        lines += history
    return lines


# -- the world ---------------------------------------------------------------

def row(being: Being) -> str:
    ch = being.channel
    m = being.mind
    open_ = ch.open_bucket()
    featured = sum(1 for e in open_ if e.features is not None)
    bare = len(open_) - featured
    depth = max((ch.depth(c.name) for c in ch.categories.values()), default=0)
    events = {k: len(being.ledger.of_kind(k)) for k in ("carve", "refine", "dissolve", "merge")}
    state = "alive" if being.alive else "gone "
    return (f"  {being.id:<11} {state}  born {being.born:3d}  age {m.age:4d}   categories {len(ch.categories):3d}  "
            f"deepest {depth}  leaves {len(ch.leaves()):3d}   open {featured:3d}+{bare:<3d}  "
            f"carved {events['carve']:2d}  narrowed {events['refine']:2d}  dissolved {events['dissolve']:2d}  "
            f"undone {events['merge']:2d}")


def growth(beings: list) -> list:
    """Per world generation: how much structure the beings alive then held.

    Replays each being's ledger. A being's generations begin at each
    `enter`; what it carried at birth comes from its `born` entry.
    """
    per = defaultdict(lambda: {"beings": 0, "categories": 0, "deepest": 0, "carve": 0, "refine": 0, "dissolve": 0, "merge": 0})
    for b in beings:
        count = len(b.ledger[0].payload.get("categories", [])) if b.ledger[0].kind == "born" else 0
        inherited = b.ledger[0].payload.get("categories", []) if b.ledger[0].kind == "born" else []
        depth = max((b.channel.depth(n) for n in inherited if n in b.channel.categories), default=1 if inherited else 0)
        k = -1
        pending = None
        for e in b.ledger:
            if e.kind == "enter":
                if pending is not None:
                    per[pending]["beings"] += 1
                    per[pending]["categories"] += count
                    per[pending]["deepest"] = max(per[pending]["deepest"], depth)
                k += 1
                pending = b.born + k
            elif e.kind == "carve":
                count += 2
                depth = max(depth, 1)
                if pending is not None:
                    per[pending]["carve"] += 1
            elif e.kind == "refine":
                count += 2
                depth = max(depth, e.payload.get("depth", 2))
                if pending is not None:
                    per[pending]["refine"] += 1
            elif e.kind == "dissolve":
                count -= 1
                if pending is not None:
                    per[pending]["dissolve"] += 1
            elif e.kind == "merge":
                count -= 2
                if pending is not None:
                    per[pending]["merge"] += 1
        if pending is not None:
            per[pending]["beings"] += 1
            per[pending]["categories"] += count
            per[pending]["deepest"] = max(per[pending]["deepest"], depth)
    lines = ["  gen  beings  categories each  deepest  carved  narrowed  dissolved  undone"]
    for g in sorted(per):
        r = per[g]
        mean = r["categories"] / r["beings"] if r["beings"] else 0.0
        lines.append(f"  {g:3d}  {r['beings']:6d}  {mean:15.2f}  {r['deepest']:7d}  {r['carve']:6d}  {r['refine']:8d}  "
                     f"{r['dissolve']:9d}  {r['merge']:6d}")
    return lines


def load_gone(gone_dir: Path, teachers_for_dims) -> list:
    out = []
    if gone_dir.is_dir():
        for path in sorted(gone_dir.glob("*.json")):
            d = json.loads(path.read_text())
            dims = len(next((e["features"] for e in d["channel"]["experiences"] if e["features"]), [0, 0, 0, 0]))
            out.append(Being.from_dict(d, teachers_for_dims(dims)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default=str(STATE))
    ap.add_argument("--being", type=int, default=None, help="index of one living being")
    ap.add_argument("--gone", default=None, help="id of a sealed being")
    ap.add_argument("--all", action="store_true", help="every living being's tree")
    args = ap.parse_args(argv)

    state = Path(args.state)
    if not state.exists():
        print(f"no world at {state}")
        return 1
    world = load(state, default_teachers)
    gone_dir = state.parent / "gone"

    if args.gone:
        path = gone_dir / f"{args.gone}.json"
        if not path.exists():
            print(f"no sealed being {args.gone} in {gone_dir}")
            return 1
        being = Being.from_dict(json.loads(path.read_text()), default_teachers(world.dims))
        print("\n".join(describe_being(being)))
        return 0
    if args.being is not None:
        print("\n".join(describe_being(world.beings[args.being])))
        return 0
    if args.all:
        for b in world.beings:
            print("\n".join(describe_being(b)))
            print()
        return 0

    print(f"generation {world.generation}; {len(world.living)} of {len(world.beings)} living; "
          f"law: {world.options.get('law', 'axis')}")
    for b in world.beings:
        print(row(b))
    everyone = world.beings + load_gone(gone_dir, default_teachers)
    print()
    print(f"growth, over every being that has lived here ({len(everyone)}):")
    print("\n".join(growth(everyone)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

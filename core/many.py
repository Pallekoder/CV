"""The many.

Selection, not instruction. A population of beings, each in its own shell
under the same hidden law. When a being's life runs out it is gone: its
ledger is sealed into the world's record and kept. The empty place is taken
by a child of whoever is still around, with varied tendencies and the
parent's lived material carried over.

Nothing in here ranks the living. Nothing scores them. Being alive at the
end of a generation is the whole of what it takes to beget, and every
survivor is as likely a parent as any other. Whatever tendencies the
population ends up with, nobody put them there.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Callable, Optional

from .being import Being
from .god import God
from .ledger import Ledger

FORMAT = 2


class World:
    def __init__(self, seed, dims: int, teachers: list) -> None:
        self.seed = seed
        self.dims = dims
        self.teachers = teachers
        self.ledger = Ledger()          # the world's own record
        self.god = God(self.ledger)
        self.rng = random.Random(f"world:{seed}")
        self.generation = 0
        self.births = 0
        self.sealed: set = set()        # ids of the dead already recorded
        self.beings: list = []

    @property
    def living(self) -> list:
        return [b for b in self.beings if b.alive]

    # -- beginnings --------------------------------------------------------

    def _found_one(self, generation: int) -> Being:
        b = Being.found(self.seed, generation, self.births, self.teachers)
        self.births += 1
        self.ledger.append(generation, "born", being=b.id, parent=None,
                           disposition=b.mind.disposition.to_dict())
        return b

    def found(self, n: int) -> None:
        for _ in range(n):
            self.beings.append(self._found_one(self.generation))

    # -- a generation ------------------------------------------------------

    def live(self, builder: Callable[[Being], object], ticks: int, watch: Optional[int] = None) -> list:
        """Every living being gets its own shell and lives `ticks` ticks in it."""
        g = self.generation
        lines = []
        for i, b in enumerate(self.beings):
            if not b.alive:
                continue
            space = self.god.remake(g, lambda: builder(b))
            b.mind.enter(space)
            for _ in range(ticks):
                out = b.mind.tick(space)
                if watch == i:
                    lines += ["  " + line for line in out]
                if not b.alive:
                    break
        self.ledger.append(g, "lived", ticks=ticks, living=len(self.living), beings=len(self.beings))
        return lines

    def select(self, refound: bool, gone_dir=None) -> dict:
        """Seal the dead. Fill their places with children of the living.

        With no one left, the world either begins again from strangers
        (`refound`) or stays as it fell. Either way the record says so.
        """
        g = self.generation
        dead = [b for b in self.beings if not b.alive and b.id not in self.sealed]
        living = self.living
        for b in dead:
            self.ledger.append(g, "died", being=b.id, born=b.born, parent=b.parent, age=b.mind.age,
                               entries=len(b.ledger), chain=b.ledger[-1].hash,
                               nature=b.mind.nature.to_dict(), bent=b.mind.disposition.to_dict())
            self.sealed.add(b.id)
            if gone_dir is not None:
                Path(gone_dir).mkdir(parents=True, exist_ok=True)
                (Path(gone_dir) / f"{b.id}.json").write_text(json.dumps(b.to_dict()))
        extinct = not living
        if extinct and dead:
            self.ledger.append(g, "extinction", were=len(self.beings))
        born = []
        kept = []
        for b in self.beings:
            if b.alive:
                kept.append(b)
                continue
            if extinct:
                if not refound:
                    kept.append(b)   # the dead stay where they fell
                    continue
                child = self._found_one(g + 1)
            else:
                parent = self.rng.choice(living)
                child = parent.beget(self.seed, g + 1, self.births, self.teachers)
                self.births += 1
                self.ledger.append(g, "born", being=child.id, parent=parent.id,
                                   disposition=child.mind.disposition.to_dict())
            kept.append(child)
            born.append(child)
        self.beings = kept
        self.generation += 1
        return {"died": dead, "born": born, "living": living, "extinct": extinct}

    # -- persistence -------------------------------------------------------

    def to_dict(self) -> dict:
        version, internal, gauss = self.rng.getstate()
        return {
            "format": FORMAT,
            "seed": self.seed,
            "dims": self.dims,
            "generation": self.generation,
            "births": self.births,
            "sealed": sorted(self.sealed),
            "ledger": self.ledger.to_list(),
            "god": self.god.to_dict(),
            "rng": [version, list(internal), gauss],
            "beings": [b.to_dict() for b in self.beings],
        }

    @classmethod
    def from_dict(cls, d: dict, teachers_for_dims: Callable[[int], list]) -> "World":
        if d.get("format") != FORMAT:
            raise ValueError(f"unknown state format {d.get('format')}")
        teachers = teachers_for_dims(d["dims"])
        world = cls(d["seed"], d["dims"], teachers)
        world.generation = d["generation"]
        world.births = d["births"]
        world.sealed = set(d["sealed"])
        world.ledger = Ledger.from_list(d["ledger"])
        world.god = God(world.ledger)
        world.god.restore(d["god"])
        v, internal, gauss = d["rng"]
        world.rng.setstate((v, tuple(internal), gauss))
        world.beings = [Being.from_dict(b, teachers) for b in d["beings"]]
        return world

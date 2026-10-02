"""One being: a ledger, a channel, a mind, and where it came from.

A being is founded with tendencies drawn at random, or begotten by a living
parent with the parent's tendencies varied and the parent's lived material
carried over. Its ledger is its own chain from birth. A child's first entry
names its parent's chain, so the generations link by hash.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from .channel import Channel
from .ledger import Ledger
from .mind import Disposition, Mind
from .symbols import coin


def _state_out(state) -> list:
    version, internal, gauss = state
    return [version, list(internal), gauss]


def _state_in(data) -> tuple:
    return (data[0], tuple(data[1]), data[2])


@dataclass
class Being:
    id: str
    born: int                 # generation
    parent: Optional[str]
    ledger: Ledger
    channel: Channel
    mind: Mind

    @property
    def alive(self) -> bool:
        return self.mind.body.alive

    @classmethod
    def found(cls, world_seed, generation: int, number: int, teachers: list) -> "Being":
        """A stranger: tendencies drawn at random, nothing lived."""
        bid = coin("being", world_seed, generation, number)
        rng = random.Random(f"being:{world_seed}:{bid}")
        ledger, channel = Ledger(), Channel()
        mind = Mind(ledger, channel, teachers, rng, Disposition.random(rng))
        ledger.append(0, "born", being=bid, parent=None, generation=generation,
                      disposition=mind.disposition.to_dict())
        return cls(bid, generation, None, ledger, channel, mind)

    def beget(self, world_seed, generation: int, number: int, teachers: list) -> "Being":
        """A child: this being's tendencies varied, its lived material carried."""
        bid = coin("being", world_seed, generation, number, self.id)
        rng = random.Random(f"being:{world_seed}:{bid}")
        ledger = Ledger()
        channel = Channel.from_dict(self.channel.to_dict())
        mind = Mind(ledger, channel, teachers, rng, self.mind.disposition.vary(rng))
        mind.perspectives = list(self.mind.perspectives)
        mind.puzzles = list(self.mind.puzzles)
        mind._considered_at = self.mind._considered_at
        ledger.append(0, "born", being=bid, parent=self.id, generation=generation,
                      parent_chain=self.ledger[-1].hash, parent_age=self.mind.age,
                      carried=len(channel.experiences), disposition=mind.disposition.to_dict())
        return Being(bid, generation, self.id, ledger, channel, mind)

    def lived(self) -> tuple:
        """(consequences lived, how many were negative)"""
        signs = [e.sign for e in self.channel.experiences.values() if e.sign]
        return len(signs), sum(1 for s in signs if s < 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "born": self.born,
            "parent": self.parent,
            "ledger": self.ledger.to_list(),
            "channel": self.channel.to_dict(),
            "mind": self.mind.to_dict(),
            "rng": _state_out(self.mind.rng.getstate()),
        }

    @classmethod
    def from_dict(cls, d: dict, teachers: list) -> "Being":
        ledger = Ledger.from_list(d["ledger"])
        channel = Channel.from_dict(d["channel"])
        rng = random.Random()
        rng.setstate(_state_in(d["rng"]))
        mind = Mind(ledger, channel, teachers, rng, Disposition.from_dict(d["mind"]["disposition"]))
        mind.restore(d["mind"])
        return cls(d["id"], d["born"], d["parent"], ledger, channel, mind)

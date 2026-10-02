"""Carrying the core across shells.

Everything that is the core (ledger, channel, mind, the distant one's
record) is written to one JSON file. The shell is never saved: it is meant
to be thrown away.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from .channel import Channel
from .god import God
from .ledger import Ledger
from .mind import Mind

FORMAT = 1


def save(path, *, ledger: Ledger, channel: Channel, mind: Mind, god: God, dims: int) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "format": FORMAT,
        "dims": dims,
        "ledger": ledger.to_list(),
        "channel": channel.to_dict(),
        "mind": mind.to_dict(),
        "god": god.to_dict(),
    }
    path.write_text(json.dumps(data, indent=1))


def load(path, teachers_for_dims, rng: random.Random) -> tuple:
    data = json.loads(Path(path).read_text())
    if data.get("format") != FORMAT:
        raise ValueError(f"unknown state format {data.get('format')}")
    dims = data["dims"]
    ledger = Ledger.from_list(data["ledger"])
    channel = Channel.from_dict(data["channel"])
    god = God(ledger)
    god.restore(data["god"])
    mind = Mind(ledger, channel, teachers_for_dims(dims), rng)
    mind.restore(data["mind"])
    return ledger, channel, mind, god, dims

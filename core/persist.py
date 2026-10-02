"""Carrying the world between runs.

The world's record, the distant one's record, and every living being
(ledger, channel, mind) go into one JSON file. The dead are sealed into
their own files as they go. Shells are never saved: they are meant to be
thrown away.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .many import World


def save(path, world: World) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(world.to_dict()))


def load(path, teachers_for_dims: Callable[[int], list]) -> World:
    return World.from_dict(json.loads(Path(path).read_text()), teachers_for_dims)

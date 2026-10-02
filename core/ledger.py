"""Irreversibility.

The ledger is append-only. Nothing in it can be edited or removed, and every
entry is chained to the one before it, so any tampering is visible. The
ledger is what makes consequence real: what happened, happened.

Note what the ledger does not do: it does not store the reasons for things.
A reason that is not written down here is gone.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass(frozen=True)
class Entry:
    index: int
    tick: int
    kind: str
    payload: dict = field(default_factory=dict)
    prev_hash: str = ""
    hash: str = ""

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "tick": self.tick,
            "kind": self.kind,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }


def _digest(index: int, tick: int, kind: str, payload: dict, prev_hash: str) -> str:
    body = json.dumps(
        [index, tick, kind, payload, prev_hash], sort_keys=True, default=str
    ).encode()
    return hashlib.blake2b(body, digest_size=16).hexdigest()


class Ledger:
    def __init__(self) -> None:
        self._entries: list[Entry] = []

    def append(self, tick: int, kind: str, **payload: Any) -> Entry:
        index = len(self._entries)
        prev_hash = self._entries[-1].hash if self._entries else ""
        entry = Entry(
            index=index,
            tick=tick,
            kind=kind,
            payload=payload,
            prev_hash=prev_hash,
            hash=_digest(index, tick, kind, payload, prev_hash),
        )
        self._entries.append(entry)
        return entry

    def verify(self) -> bool:
        prev = ""
        for i, e in enumerate(self._entries):
            if e.index != i or e.prev_hash != prev:
                return False
            if e.hash != _digest(e.index, e.tick, e.kind, e.payload, e.prev_hash):
                return False
            prev = e.hash
        return True

    def of_kind(self, kind: str) -> list[Entry]:
        return [e for e in self._entries if e.kind == kind]

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[Entry]:
        return iter(tuple(self._entries))

    def __getitem__(self, index: int) -> Entry:
        return self._entries[index]

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self._entries]

    @classmethod
    def from_list(cls, rows: list[dict]) -> "Ledger":
        ledger = cls()
        for row in rows:
            ledger._entries.append(Entry(**row))
        if not ledger.verify():
            raise ValueError("ledger failed verification on load")
        return ledger

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
    """Append-only. Older entries may be moved to an archive file; the chain
    in memory then starts mid-way, and still verifies against what was
    archived because every entry carries the hash of the one before."""

    def __init__(self) -> None:
        self._entries: list[Entry] = []
        self.archived = 0   # how many entries were moved to an archive file

    @property
    def base(self) -> int:
        return self._entries[0].index if self._entries else self.archived

    def append(self, tick: int, kind: str, **payload: Any) -> Entry:
        index = len(self)
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
        prev = None
        base = self.base
        for i, e in enumerate(self._entries):
            if e.index != base + i or (prev is not None and e.prev_hash != prev):
                return False
            if i == 0 and base == 0 and e.prev_hash != "":
                return False
            if e.hash != _digest(e.index, e.tick, e.kind, e.payload, e.prev_hash):
                return False
            prev = e.hash
        return True

    def archive(self, path, keep: int) -> int:
        """Move all but the newest `keep` entries to an append-only file.

        Nothing is lost: the file holds them in order, as JSON lines, and the
        first entry left in memory still names the hash of the last one
        written out.
        """
        extra = len(self._entries) - keep
        if extra <= 0:
            return 0
        with open(path, "a") as f:
            for e in self._entries[:extra]:
                f.write(json.dumps(e.to_dict(), sort_keys=True) + "\n")
        self._entries = self._entries[extra:]
        self.archived += extra
        return extra

    def of_kind(self, kind: str) -> list[Entry]:
        return [e for e in self._entries if e.kind == kind]

    def since(self, index: int) -> list[Entry]:
        """Entries from `index` on, among those still in memory."""
        return list(self._entries[max(0, index - self.base):])

    def __len__(self) -> int:
        """Entries ever appended, archived ones included."""
        return self.base + len(self._entries)

    def __iter__(self) -> Iterator[Entry]:
        return iter(tuple(self._entries))

    def __getitem__(self, index: int) -> Entry:
        if index < 0:
            return self._entries[index]
        at = index - self.base
        if at < 0:
            raise IndexError(f"entry {index} is in the archive")
        return self._entries[at]

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self._entries]

    @classmethod
    def from_list(cls, rows: list[dict]) -> "Ledger":
        ledger = cls()
        for row in rows:
            ledger._entries.append(Entry(**row))
        if rows:
            ledger.archived = rows[0]["index"]
        if not ledger.verify():
            raise ValueError("ledger failed verification on load")
        return ledger

"""The distant figure.

Reached only rarely. Its words enter the channel like any other featureless
arrival, in a different alphabet from the system's own, and are kept as a
perspective, not a decree. Its other power is over the shell: it can throw
the space away and build another, leaving the core untouched.
"""
from __future__ import annotations

from typing import Callable, Optional

from .ledger import Ledger
from .teachers import Perspective


class God:
    ID = "distant"

    def __init__(self, ledger: Ledger, min_gap: int = 40) -> None:
        self.ledger = ledger
        self.min_gap = min_gap
        self.last_contact: Optional[int] = None
        self.shells_built = 0

    def can_speak(self, tick: int) -> bool:
        return self.last_contact is None or tick - self.last_contact >= self.min_gap

    def speak(self, tick: int, text: str) -> Optional[Perspective]:
        """Say something. Refused, and recorded as silence, if too soon."""
        if not self.can_speak(tick):
            self.ledger.append(tick, "silence", wanted=text, since=self.last_contact)
            return None
        self.last_contact = tick
        self.ledger.append(tick, "contact", text=text)
        return Perspective(source=self.ID, tick=tick, remark=text)

    def remake(self, tick: int, builder: Callable[[], object]):
        """Throw the shell away and build another. The core is not touched."""
        self.shells_built += 1
        space = builder()
        self.ledger.append(
            tick, "shell", number=self.shells_built, label=getattr(space, "label", None),
            forms=len(getattr(space, "forms", {})),
        )
        return space

    def to_dict(self) -> dict:
        return {
            "min_gap": self.min_gap,
            "last_contact": self.last_contact,
            "shells_built": self.shells_built,
        }

    def restore(self, d: dict) -> None:
        self.min_gap = d.get("min_gap", self.min_gap)
        self.last_contact = d.get("last_contact")
        self.shells_built = d.get("shells_built", 0)

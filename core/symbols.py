"""Names the system coins for itself.

No human word is ever handed to the system as a label. Forms, categories and
utterances are named by hashing the state that produced them into short
syllable strings. The syllables mean nothing; they are only distinct.
"""
from __future__ import annotations

import hashlib
from typing import Any

SYLLABLES = (
    "ka", "ro", "ti", "mu", "ne", "so", "va", "li",
    "de", "xu", "po", "ri", "ga", "lo", "shi", "en",
)


def coin(*parts: Any, length: int = 3) -> str:
    """Deterministically turn any state into a short coined name."""
    raw = "|".join(repr(p) for p in parts).encode()
    digest = hashlib.blake2b(raw, digest_size=8).digest()
    return "-".join(SYLLABLES[b % len(SYLLABLES)] for b in digest[:length])

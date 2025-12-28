from __future__ import annotations

import math
from typing import Dict, Tuple


CHAR_CLASSES = {
    "lower": str.islower,
    "upper": str.isupper,
    "digit": str.isdigit,
    "space": str.isspace,
}


def shannon_entropy_total(password: str) -> float:
    """Return the Shannon entropy (bits) of the provided candidate."""
    if not password:
        return 0.0

    length = len(password)
    counts: Dict[str, int] = {}
    for char in password:
        counts[char] = counts.get(char, 0) + 1

    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy * length


def length_and_classes(password: str) -> Tuple[int, int, Dict[str, bool]]:
    """Return the length, number of active character classes, and flags."""
    length = len(password or "")
    flags = {name: False for name in CHAR_CLASSES}
    flags["symbol"] = False

    for char in password or "":
        matched_class = False
        for name, checker in CHAR_CLASSES.items():
            if checker(char):
                flags[name] = True
                matched_class = True
                break
        if not matched_class:
            flags["symbol"] = True

    class_count = sum(1 for value in flags.values() if value)
    return length, class_count, flags

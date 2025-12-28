from __future__ import annotations

import hashlib
import math
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import requests


HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/"
MAX_CACHE_SIZE = 256
_PREFIX_CACHE: "OrderedDict[str, Dict[str, int]]" = OrderedDict()


@dataclass(frozen=True)
class HIBPPrevalence:
    count: int
    log_count: float


def _hash_candidate(candidate: str) -> Tuple[str, str]:
    digest = hashlib.sha1(candidate.encode("utf-8")).hexdigest().upper()
    return digest[:5], digest[5:]


def _update_cache(prefix: str, mapping: Dict[str, int]) -> None:
    if prefix in _PREFIX_CACHE:
        _PREFIX_CACHE.move_to_end(prefix)
    _PREFIX_CACHE[prefix] = mapping
    while len(_PREFIX_CACHE) > MAX_CACHE_SIZE:
        _PREFIX_CACHE.popitem(last=False)


def clear_cache() -> None:
    _PREFIX_CACHE.clear()


def _fetch_range(prefix: str, session: Optional[requests.Session], timeout: float) -> Dict[str, int]:
    session = session or requests.Session()
    url = f"{HIBP_RANGE_URL}{prefix}"
    headers = {
        "Add-Padding": "true",
        "User-Agent": "pwstrength/0.1",
    }

    backoff = 0.5
    for attempt in range(4):
        response = session.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            result: Dict[str, int] = {}
            for line in response.text.splitlines():
                if ":" not in line:
                    continue
                suffix, count = line.split(":", 1)
                suffix = suffix.strip().upper()
                try:
                    result[suffix] = int(count.strip())
                except ValueError:
                    continue
            _update_cache(prefix, result)
            return result
        time.sleep(backoff)
        backoff *= 2

    response.raise_for_status()
    raise RuntimeError("HIBP query failed")  # failsafe


def _range_lookup(prefix: str, session: Optional[requests.Session], timeout: float) -> Dict[str, int]:
    if prefix in _PREFIX_CACHE:
        _PREFIX_CACHE.move_to_end(prefix)
        return _PREFIX_CACHE[prefix]
    return _fetch_range(prefix, session, timeout)


def get_count(candidate: str, session: Optional[requests.Session] = None, timeout: float = 10.0) -> int:
    """Return the breach count for the candidate using the k-anonymity API."""
    if not candidate:
        return 0
    prefix, suffix = _hash_candidate(candidate)
    response = _range_lookup(prefix, session, timeout)
    return response.get(suffix.upper(), 0)


def get_prevalence(candidate: str, session: Optional[requests.Session] = None, timeout: float = 10.0) -> HIBPPrevalence:
    count = get_count(candidate, session=session, timeout=timeout)
    return HIBPPrevalence(count=count, log_count=math.log1p(count))

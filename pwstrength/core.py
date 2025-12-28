from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pandas as pd

from .adapters import aadi_adapters
from .features.entropy import length_and_classes, shannon_entropy_total
from .features.hibp_client import HIBPPrevalence, get_prevalence
from .features.zxcvbn_adapter import zxcvbn_features
from .models.hybrid import hybrid_score_v0


@dataclass
class ScoreResult:
    """Typed response for the pwscore helper."""

    candidate: str
    features: pd.DataFrame
    crack_times_display: Dict[str, str]

    def to_dict(self) -> Dict[str, object]:
        row = self.features.iloc[0].to_dict()
        row["crack_times_display"] = self.crack_times_display
        row["pw"] = self.candidate
        return row

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=2)


def _safe_log_count(prevalence: HIBPPrevalence | None) -> float:
    if not prevalence:
        return 0.0
    return prevalence.log_count


def build_features(
    strings: Iterable[str],
    online: bool = False,
    tau: int = 10,
    session=None,
) -> pd.DataFrame:
    """Assemble a tidy feature frame for downstream modeling."""
    rows: List[Dict[str, object]] = []
    for candidate in strings:
        password = candidate or ""
        matches = aadi_adapters.match_patterns(password)
        guess_info = aadi_adapters.estimate_guesses(password, matches)
        crack_info = aadi_adapters.crack_times(guess_info["guesses"])
        feedback = aadi_adapters.human_feedback(password, matches, score=guess_info["score"])

        entropy_bits = shannon_entropy_total(password)
        length, class_count, class_flags = length_and_classes(password)
        z_features = zxcvbn_features(password)

        prevalence_mode = "online" if online else "offline"
        hibp_count = 0
        prevalence: Optional[HIBPPrevalence] = None
        if online:
            try:
                prevalence = get_prevalence(password, session=session)
                hibp_count = prevalence.count
            except Exception:
                prevalence_mode = "error"
        log_count = _safe_log_count(prevalence)

        row: Dict[str, object] = {
            "pw": password,
            "length": length,
            "classes": class_count,
            "class_flags": class_flags,
            "H_bits": entropy_bits,
            "zxcvbn_score": z_features["zxcvbn_score"],
            "zxcvbn_guesses": z_features["zxcvbn_guesses"],
            "zxcvbn_feedback": z_features["zxcvbn_feedback"],
            "hibp_count": hibp_count,
            "log_count": log_count,
            "prevalence_mode": prevalence_mode,
            "aadi_guesses": guess_info["guesses"],
            "aadi_score": guess_info["score"],
            "aadi_feedback": feedback,
            "aadi_sequence": guess_info["sequence"],
            "HybridScore_v0": 0.0,
            "label_breached": 0,
            "tau": tau,
            "crack_times_display": crack_info["crack_times_display"],
        }
        row["HybridScore_v0"] = hybrid_score_v0(row)
        row["label_breached"] = int((hibp_count or 0) >= tau)
        rows.append(row)

    return pd.DataFrame(rows)


def score(candidate: str, online: bool = False, tau: int = 10, session=None) -> ScoreResult:
    """Convenience wrapper used by the CLI and external callers."""
    features = build_features([candidate], online=online, tau=tau, session=session)
    crack_times = features.iloc[0]["crack_times_display"] or {}
    return ScoreResult(candidate=candidate, features=features, crack_times_display=crack_times)

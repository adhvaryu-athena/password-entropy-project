from __future__ import annotations

from typing import Dict

try:
    from zxcvbn import zxcvbn as _zxcvbn_impl
except ImportError as exc:  # pragma: no cover
    _ZXCVBN_ERROR = exc
    _zxcvbn_impl = None
else:
    _ZXCVBN_ERROR = None


def zxcvbn_features(password: str) -> Dict[str, object]:
    """Return select zxcvbn metrics for the candidate."""
    if _zxcvbn_impl is None:  # pragma: no cover
        raise RuntimeError("The 'zxcvbn' package is required for zxcvbn_features.") from _ZXCVBN_ERROR

    result = _zxcvbn_impl(password or "")
    feedback = result.get("feedback", {}) or {}
    warning = feedback.get("warning") or ""
    suggestions = " ".join(feedback.get("suggestions", []) or [])
    feedback_text = warning.strip()
    if suggestions:
        feedback_text = f"{feedback_text} {suggestions}".strip()

    return {
        "zxcvbn_score": int(result.get("score", 0)),
        "zxcvbn_guesses": float(result.get("guesses", 0) or 0.0),
        "zxcvbn_feedback": feedback_text,
    }

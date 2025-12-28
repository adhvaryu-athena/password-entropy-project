from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import ModuleType
from typing import Any, Dict, List, Optional


BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
STUDENT_DIR = BASE_DIR / "password-py"
PACKAGE_NAME = "_aadi_pw"

if PACKAGE_NAME not in sys.modules:
    pseudo_pkg = ModuleType(PACKAGE_NAME)
    pseudo_pkg.__path__ = [str(STUDENT_DIR)]
    sys.modules[PACKAGE_NAME] = pseudo_pkg


def _import_from_student(module_suffix: str, filename: str) -> ModuleType:
    qualified_name = f"{PACKAGE_NAME}.{module_suffix}"
    if qualified_name in sys.modules:
        return sys.modules[qualified_name]

    source_path = STUDENT_DIR / filename
    if not source_path.exists():
        raise FileNotFoundError(f"Missing student file: {source_path}")

    spec = importlib.util.spec_from_file_location(qualified_name, source_path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load spec for {qualified_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)
    return module


def _student_modules() -> Dict[str, ModuleType]:
    adjacency = _import_from_student("adjacency_graphs", "Adjacency Graphs.py")
    matching = _import_from_student("matching_script", "Matching Script.py")
    scoring = _import_from_student("scoring_script", "Scoring Script.py")
    time_estimates = _import_from_student("time_estimates", "Time Estimates.py")
    feedback = _import_from_student("feedback", "Feedback.py")
    return {
        "adjacency": adjacency,
        "matching": matching,
        "scoring": scoring,
        "time": time_estimates,
        "feedback": feedback,
    }


MODULES = _student_modules()


def match_patterns(password: str) -> List[Dict[str, Any]]:
    """Return the list of pattern matches from Aadi's matching script."""
    return MODULES["matching"].omnimatch(password)


def estimate_guesses(password: str, matches: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Estimate guesses using the original scorer."""
    matches = matches or match_patterns(password)
    result = MODULES["scoring"].most_guessable_match_sequence(password, matches)
    guesses = result["guesses"]
    score = MODULES["time"].guesses_to_score(float(guesses))
    return {
        "password": password,
        "sequence": result["sequence"],
        "guesses": float(guesses),
        "guesses_log10": result["guesses_log10"],
        "score": score,
    }


def crack_times(guesses: float) -> Dict[str, Any]:
    """Return crack time estimates for the provided guess count."""
    return MODULES["time"].estimate_attack_times(guesses)


def human_feedback(
    password: str,
    matches: Optional[List[Dict[str, Any]]] = None,
    score: Optional[int] = None,
) -> str:
    """Return a human-facing feedback string."""
    matches = matches or match_patterns(password)
    if score is None:
        score = estimate_guesses(password, matches)["score"]
    feedback = MODULES["feedback"].get_feedback(score, matches)
    warning = feedback.get("warning", "")
    suggestions = feedback.get("suggestions", []) or []
    segments = [warning] if warning else []
    segments.extend(suggestions)
    return " ".join(s for s in segments if s)

"""pwstrength package exports."""

from importlib import import_module
from typing import Any

__all__ = ["ScoreResult", "build_features", "score"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(".core", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name!r}")

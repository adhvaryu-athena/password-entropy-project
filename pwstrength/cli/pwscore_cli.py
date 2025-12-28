from __future__ import annotations

import argparse
import json
from typing import Iterable, Tuple

from ..core import ScoreResult, score as score_password


def _format_rows(row: dict) -> Iterable[Tuple[str, str]]:
    class_flags = ", ".join([flag for flag, enabled in row.get("class_flags", {}).items() if enabled]) or "none"
    hibp_mode = row.get("prevalence_mode", "offline")
    hibp_count = row.get("hibp_count", 0)
    log_count = row.get("log_count", 0.0)
    label = row.get("label_breached", 0)
    tau = row.get("tau", 10)
    return [
        ("Entropy (bits)", f"{row.get('H_bits', 0.0):.2f}"),
        ("Length / Classes", f"{row.get('length', 0)} / {row.get('classes', 0)}"),
        ("Class flags", class_flags),
        ("zxcvbn score", str(row.get("zxcvbn_score", 0))),
        ("zxcvbn guesses", f"{row.get('zxcvbn_guesses', 0.0):.2f}"),
        ("zxcvbn feedback", row.get("zxcvbn_feedback") or "-"),
        ("Aadi guesses", f"{row.get('aadi_guesses', 0.0):.2f}"),
        ("Aadi score", str(row.get("aadi_score", 0))),
        ("Aadi feedback", row.get("aadi_feedback") or "-"),
        ("HIBP mode", hibp_mode),
        ("HIBP count", f"{hibp_count} (log1p={log_count:.2f})"),
        ("HybridScore v0", f"{row.get('HybridScore_v0', 0.0):.4f}"),
        (f"Label τ={tau}", "breached" if label else "unknown"),
    ]


def _print_table(result: ScoreResult) -> None:
    row = result.features.iloc[0].to_dict()
    print("Don't paste real passwords.")
    print("-" * 40)
    for name, value in _format_rows(row):
        print(f"{name:<20} {value}")
    crack_times = row.get("crack_times_display") or {}
    if crack_times:
        print("\nEstimated crack times:")
        for scenario, display in crack_times.items():
            print(f"  - {scenario}: {display}")


def score(candidate: str, online: bool = False, tau: int = 10) -> dict:
    """Module-level helper returning the computed metrics."""
    return score_password(candidate, online=online, tau=tau).to_dict()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Password scoring CLI")
    parser.add_argument("candidate", help="Password candidate string (avoid real secrets!)")
    parser.add_argument("--online", action="store_true", help="Enable HIBP online queries")
    parser.add_argument("--tau", type=int, default=10, help="Label threshold for breached counts")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human output")
    args = parser.parse_args(argv)

    result = score_password(args.candidate, online=args.online, tau=args.tau)
    row = result.to_dict()

    if args.json:
        print(json.dumps(row, indent=2, default=str))
    else:
        _print_table(result)
        if row.get("prevalence_mode") == "offline":
            print("\nHIBP: offline mode (no network query).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

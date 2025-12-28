from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import (
    PrecisionRecallDisplay,
    RocCurveDisplay,
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)


def label_from_count(count: int, tau: int = 10) -> int:
    return int((count or 0) >= tau)


def compute_metrics(df: pd.DataFrame, score_col: str = "HybridScore_v0", label_col: str = "label_breached") -> dict:
    scores = df[score_col].astype(float).to_numpy()
    labels = df[label_col].astype(int).to_numpy()
    return {
        "roc_auc": roc_auc_score(labels, scores),
        "ap": average_precision_score(labels, scores),
        "brier": brier_score_loss(labels, scores),
    }


def metrics_over_thresholds(
    df: pd.DataFrame,
    taus: Sequence[int] = (1, 10, 100),
    count_col: str = "hibp_count",
    score_col: str = "HybridScore_v0",
) -> pd.DataFrame:
    records = []
    for tau in taus:
        labels = df[count_col].apply(lambda c: label_from_count(c, tau))
        working = df.copy()
        working["label_tmp"] = labels
        metrics = compute_metrics(working, score_col=score_col, label_col="label_tmp")
        records.append({"tau": tau, **metrics})
    return pd.DataFrame(records)


def plot_roc(y_true: Iterable[int], y_score: Iterable[float], ax=None):
    """Plot ROC curve for a given set of scores."""
    ax = ax or plt.gca()
    RocCurveDisplay.from_predictions(y_true, y_score, ax=ax)
    ax.set_title("ROC Curve")
    return ax


def plot_pr(y_true: Iterable[int], y_score: Iterable[float], ax=None):
    ax = ax or plt.gca()
    PrecisionRecallDisplay.from_predictions(y_true, y_score, ax=ax)
    ax.set_title("Precision-Recall Curve")
    return ax


def plot_calibration(y_true: Iterable[int], y_prob: Iterable[float], ax=None, n_bins: int = 10):
    ax = ax or plt.gca()
    CalibrationDisplay.from_predictions(y_true, y_prob, n_bins=n_bins, strategy="quantile", ax=ax)
    ax.set_title("Calibration")
    return ax

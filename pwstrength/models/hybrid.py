from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

FEATURE_COLUMNS = ["H_bits", "log_count", "log10_zxcvbn_guesses"]


def _coerce_numeric(series: Iterable) -> np.ndarray:
    values = []
    for value in series:
        if value is None:
            values.append(0.0)
            continue
        try:
            values.append(float(value))
        except Exception:
            values.append(0.0)
    arr = np.array(values, dtype=float)
    return np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)


def _log10_safe(values: Iterable) -> np.ndarray:
    arr = _coerce_numeric(values)
    arr[arr <= 0] = 1.0
    return np.log10(arr)


def hybrid_score_v0(row: pd.Series | dict) -> float:
    """Hybrid baseline that combines entropy, zxcvbn, and prevalence."""
    h_bits = float(row.get("H_bits", 0.0) or 0.0)
    log10_guesses = 0.0
    guesses = row.get("zxcvbn_guesses", 0.0) or 0.0
    if guesses and guesses > 0:
        log10_guesses = math.log10(float(guesses))
    log_count = float(row.get("log_count", 0.0) or 0.0)
    return h_bits - log10_guesses - log_count


def _build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    h_bits = _coerce_numeric(df.get("H_bits", 0.0))
    log_count = _coerce_numeric(df.get("log_count", 0.0))
    log10_guesses = _log10_safe(df.get("zxcvbn_guesses", 0.0))
    return np.vstack([h_bits, log_count, log10_guesses]).T


def fit_logistic(df: pd.DataFrame, labels: Iterable[int]) -> LogisticRegression:
    """Fit an interpretable logistic baseline using selected features."""
    X = _build_feature_matrix(df)
    y = np.array([int(v) for v in labels], dtype=int)
    model = LogisticRegression(max_iter=1000, solver="liblinear")
    model.fit(X, y)
    return model


def predict_proba(model: LogisticRegression, df: pd.DataFrame) -> np.ndarray:
    """Predict breach probabilities using the fitted logistic model."""
    X = _build_feature_matrix(df)
    probabilities = model.predict_proba(X)[:, 1]
    return np.nan_to_num(probabilities, nan=0.0)

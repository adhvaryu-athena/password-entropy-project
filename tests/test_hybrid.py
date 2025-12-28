import numpy as np
import pandas as pd

from pwstrength.models.hybrid import fit_logistic, hybrid_score_v0, predict_proba


def test_hybrid_score_orders_passwords():
    df = pd.DataFrame(
        [
            {"H_bits": 12.0, "log_count": 0.0, "zxcvbn_guesses": 1e2},
            {"H_bits": 4.0, "log_count": 2.0, "zxcvbn_guesses": 1e5},
        ]
    )
    df["HybridScore_v0"] = df.apply(hybrid_score_v0, axis=1)
    assert df.loc[0, "HybridScore_v0"] > df.loc[1, "HybridScore_v0"]


def test_logistic_fit_and_predict():
    df = pd.DataFrame(
        [
            {"H_bits": 10.0, "log_count": 0.0, "zxcvbn_guesses": 1e3},
            {"H_bits": 5.0, "log_count": 3.0, "zxcvbn_guesses": 1e6},
            {"H_bits": 12.0, "log_count": 1.5, "zxcvbn_guesses": 1e5},
            {"H_bits": 2.0, "log_count": 4.0, "zxcvbn_guesses": 10},
        ]
    )
    labels = [0, 1, 0, 1]
    model = fit_logistic(df, labels)
    probs = predict_proba(model, df)
    assert len(probs) == len(df)
    assert np.all((probs >= 0.0) & (probs <= 1.0))

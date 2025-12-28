# pwstrength tooling

This repository composes Aadi’s password-pattern scripts with additional
features, models, and a user-friendly CLI. The original student files inside
`password-py/` remain untouched and are imported through thin adapters.

## Repository layout

```
password-entropy-project/
├── password-py/          # Aadi’s original scripts (do not edit)
├── pwstrength/           # Package code (adapters, features, models, CLI)
├── tests/                # Regression tests
├── README.md             # This guide
└── pyproject.toml        # Packaging + pwscore entry point
```

## Installation

1. Create/activate a Python 3.10+ environment (e.g., `conda activate password`).
2. From the project root install dependencies in editable mode:

   ```bash
   pip install -e .
   ```

   This pulls in `zxcvbn`, pandas, scikit-learn, requests, matplotlib, and
   registers the `pwscore` console script.

## CLI usage

```bash
pwscore 'CorrectHorseBatteryStaple' --tau 10        # offline mode (no HIBP)
pwscore 'Tr1vial\!' --online --tau 100 --json       # query HIBP and emit JSON
```

Key flags:

- `--online`: Enables Have I Been Pwned prefix-range queries (only the SHA-1
  prefix is sent). Without this flag the prevalence fields are zeroed and the
  CLI annotates “offline mode”.
- `--tau`: Breach-label threshold for the HybridScore summary.
- `--json`: Print the full feature dictionary as JSON instead of a table.

Each invocation prints an ethics reminder, entropy/length/class stats, zxcvbn
scores, Aadi’s guess estimates and feedback, optional HIBP counts/log-counts,
HybridScore v0, τ-based label, and crack-time scenarios from
`Time Estimates.py`.

## Module usage

```python
from pwstrength import build_features, score

# Single password (same data the CLI uses)
result = score("Tr1vial!", online=True, tau=10)
print(result["HybridScore_v0"])

# Batch feature engineering for modeling/evaluation
frame = build_features(["passw0rd", "CorrectHorseBatteryStaple"], online=False)
print(frame[["pw", "H_bits", "HybridScore_v0"]])
```

Outputs include entropy bits, character class coverage, zxcvbn score/guesses,
HIBP counts/log-counts (if online), Aadi’s guesses/score/feedback, HybridScore
v0, τ-based breach labels, and cached crack-time displays.

## Evaluation helpers

`pwstrength.models.hybrid` exposes:

- `hybrid_score_v0(row)` for the transparent baseline,
- `fit_logistic(df, labels)` and `predict_proba(...)` for a lightweight
  logistic baseline using entropy/log-count/log-guesses features.

`pwstrength.models.evaluate` provides ROC/PR/Calibration plotting helpers and
`metrics_over_thresholds(df, taus=(1,10,100))` to summarize ROC AUC, average
precision, and Brier score across τ values.

## Student workflow & deliverables

We hand this repo (or the `password-entropy-project/` folder) to students so
they can generate consistent artifacts:

1. **Environment + smoke test**  
   `pip install -e .` followed by `pwscore 'Example123!'` to confirm the CLI.

2. **Feature dataset**  
   Use `build_features(password_list, online=True)` to turn a supplied corpus
   of candidates into a DataFrame, then save it (e.g. `df.to_parquet("data/features.parquet")`).
   Columns include entropy bits, char-class coverage, zxcvbn metrics, HIBP
   prevalence, Aadi guesses/scores/feedback, HybridScore v0, and τ-based labels.

3. **Evaluation table**  
   Feed the same frame into `metrics_over_thresholds(df)` (and optionally the
   logistic baseline) to produce ROC AUC / Average Precision / Brier metrics for
   τ ∈ {1, 10, 100}. Export to CSV for review.

4. **Plots (optional but encouraged)**  
   Use `plot_roc`, `plot_pr`, and `plot_calibration` to save figures in `figs/`
   showing how HybridScore/logistic probabilities behave.

These deliverables (features.parquet/CSV, metrics table, and plots) become the
“results/data” package we expect back from the student.

## Tests

Run the regression tests with:

```bash
python -m pytest -q
```

The suite currently covers entropy calculations, HIBP prefix caching/parsing,
and the hybrid scoring/logistic baseline. Ensure the `password-py/` student
files remain adjacent to the package so the adapters can import them.

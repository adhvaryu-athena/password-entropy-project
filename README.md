# pwstrength tooling

**Aim of the paper:** Show that **Shannon entropy alone** mis-ranks real-world password risk, and that a **hybrid score**—combining entropy, human-pattern signals, and breach prevalence—tracks risk better with reproducible code and figures.

---

## What to understand (before you run anything)

* **Entropy is a baseline, not attacker effort.** We compute total Shannon entropy for context; it’s necessary but insufficient for estimating how hard a password is to guess. ([NIST Computer Security Resource Center][1])
* **Human patterns matter.** The zxcvbn estimator detects dictionary words, keyboard paths, dates, repeats, and related patterns and outputs an estimated **guess count**—a stronger proxy than entropy alone. ([GitHub][2])
* **Prevalence matters (privately).** We use **Have I Been Pwned** (HIBP) **k-anonymity** to learn how often a hash appears in breaches—only a 5-char SHA-1 prefix is sent (never plaintext or a full hash); responses can be padded. ([Have I Been Pwned][3])

---

## How this repo generates the data for the paper

1. **Feature engineering (batch).** For each candidate string, compute
   `entropy bits`, `length/classes`, `zxcvbn score/guesses/feedback`, `HIBP count + log_count`, and a **HybridScore v0**.
2. **Labeling (proxy).** Define `breached = 1` if `HIBP_count ≥ τ` (use τ in {1, 10, 100}).
3. **Evaluation.** Produce ROC/PR/Calibration plots comparing **entropy-only**, **zxcvbn-only**, and **hybrid**, plus a metrics table across τ.
4. **Artifacts.** Save `features.parquet`/CSV, `metrics.csv`, and plots in `figs/`—these become the results package cited in the paper.

---

## Repository layout

```
password-entropy-project/
├── password-py/          # Original pattern/guessing scripts (keep as-is)
├── pwstrength/           # Adapters, features (entropy/zxcvbn/HIBP), models, CLI
├── tests/                # Minimal regression tests
├── README.md             # This guide
└── pyproject.toml        # Packaging + 'pwscore' entry point
```

---

## Install

```bash
# Python 3.10+ recommended
pip install -e .
```

Registers the `pwscore` CLI and installs dependencies (zxcvbn, pandas, scikit-learn, requests, matplotlib, etc.). ([GitHub][4])

---

## Quick start (CLI)

```bash
pwscore 'CorrectHorseBatteryStaple' --tau 10            # offline (no HIBP)
pwscore 'Tr1vial\!' --online --tau 100 --json           # HIBP prefix-range + JSON
```

* `--online` uses HIBP **range** API (5-char prefix only) for prevalence; offline mode zeroes prevalence and notes it. ([Have I Been Pwned][3])
* `--tau` sets the breach-label threshold used in summaries.
* `--json` emits the full feature dictionary.

Each run prints an ethics reminder, entropy/length/class stats, zxcvbn score/guesses, pattern-script guesses/feedback, optional HIBP counts/log-counts, **HybridScore v0**, τ-based label, and crack-time scenarios.

---

## Programmatic use

```python
from pwstrength import build_features, score

# Single candidate (same fields as CLI)
res = score("Tr1vial!", online=True, tau=10)
print(res["HybridScore_v0"], res["hibp_count"])

# Batch feature set for modeling/eval
df = build_features(["passw0rd", "CorrectHorseBatteryStaple"], online=False)
df.to_parquet("data/features.parquet")
```

---

## Modeling & evaluation

* `pwstrength.models.hybrid`

  * `hybrid_score_v0(row)` (transparent baseline)
  * `fit_logistic(...)` / `predict_proba(...)` (lightweight, interpretable baseline)

* `pwstrength.models.evaluate`

  * `metrics_over_thresholds(df, taus=(1,10,100))` → ROC AUC / AP / Brier
  * `plot_roc`, `plot_pr`, `plot_calibration` → figures in `figs/`

**Workflow (run in order):**

1. **Smoke test:** `pip install -e .` → `pwscore 'Example123!'`
2. **Generate features:** `build_features([...], online=True)` → save Parquet/CSV
3. **Compute metrics & plots:** run evaluation helpers (ROC/PR/Calibration; τ grid)
4. **Bundle artifacts:** push `features.parquet`, `metrics.csv`, and `figs/*.png`

---

## Notes

* Keep `password-py/` as-is; the package imports through thin adapters.
* Use synthetic/obviously fake examples; never paste real passwords.
* HIBP **range** endpoint requires a user-agent; only the SHA-1 **prefix** leaves your machine; enable padding where possible. ([Have I Been Pwned][3])

---

## References

* **NIST SP 800-63B (Rev. 4): Digital Identity Guidelines — Authentication & Authenticator Management.** (official) ([NIST Computer Security Resource Center][5])
* **Have I Been Pwned — API v3 (Pwned Passwords / range).** (official) ([Have I Been Pwned][3])
* **Cloudflare Blog — “Validating Leaked Passwords with k-Anonymity.”** (explainer) ([The Cloudflare Blog][6])
* **Dropbox zxcvbn (GitHub).** (pattern-aware estimator) ([GitHub][4])

[1]: https://csrc.nist.gov/pubs/sp/800/63/b/upd2/final?utm_source=chatgpt.com "SP 800-63B, Digital Identity Guidelines: Authentication and Lifecycle ..."
[2]: https://github.com/dropbox/zxcvbn/blob/master/README.md?utm_source=chatgpt.com "zxcvbn/README.md at master · dropbox/zxcvbn · GitHub"
[3]: https://haveibeenpwned.com/API/v3?utm_source=chatgpt.com "API Documentation - Have I Been Pwned"
[4]: https://github.com/dropbox/zxcvbn?utm_source=chatgpt.com "GitHub - dropbox/zxcvbn: Low-Budget Password Strength Estimation"
[5]: https://csrc.nist.gov/pubs/sp/800/63/b/4/final?utm_source=chatgpt.com "SP 800-63B-4, Digital Identity Guidelines: Authentication and ..."
[6]: https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/?utm_source=chatgpt.com "Validating Leaked Passwords with k-Anonymity - The Cloudflare Blog"

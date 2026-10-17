# Verification: code vs. manuscript

Checked against the **revised** *SSW_Paper_EMS_SPMK.docx* (October 2026), which corrected every discrepancy found in the first audit (listed below). There are three independent checks:

1. **Numbers:** every numeric claim in the paper, recomputed from the archived outputs (`scripts/verify_paper_numbers.py`, full table in `VERIFICATION_numbers.md`).
2. **Methods:** every method parameter stated in Sections 2.2–2.6, compared with the notebook code.
3. **Re-execution:** the notebook's own cells re-run from the archived raw POWER download, with models retrained from scratch and compared fold by fold (`scripts/rerun_check.py`).

There is also an automated test suite (`tests/`, 16 tests) that runs on every push via GitHub Actions.

## 1. Numbers: 160 claims, 160 match

The first audit, against the submitted draft, found 16 numbers in the manuscript text that did not match the code and data. In each case the code and results were internally consistent; the text quoted a number computed on a different input set, or misstated what was computed. All 16 were corrected in the revised manuscript:

| Section | Draft said | Revised (= code / data) | Cause in draft |
|---|---|---|---|
| 3.1 | 116 southern cells | 115 | 134 + 116 = 250; the dropped cell (7.5S) was southern |
| 1.2, 2.7, 3.1 | r(AI, mean SSW) 0.709 / 0.799; humid mean 0.687 | 0.802; 0.681 | 0.709 was the India-60 value; 0.799 / 0.687 were computed on 250 cells, before the constant cell was dropped |
| 2.2 | minimum of four cells per stratum | ...or all candidates where fewer exist (one stratum has a single candidate) | the code takes min(4, available) |
| 3.2 | the MI bound is the higher where the bounds diverge | MI above linear in 121 cells, below in 128 | MI uses 3 lags against 12 |
| 3.3 | AR12 win rates .868 / .593 / .558; RF semi-arid wins 15; MI split 59.5 % / 74.2 % | .849 / .574 / .462; 13; 56.2 % / 71.9 % | draft values came from the 9-model table (before ESN); Table 2 is 10-model |
| 3.4, 4.3 | drivers-only 0.664 vs lag-only 0.643; drivers-only 0.859 | 0.695 vs 0.693 ("matches"); 0.887 | draft mixed averaging bases; now all on Table 3's best-per-cell basis |
| 3.5, 4.5 | 36 of 49 over-ceiling cells won by nonlinear models | 34 (OLS 13, climatology 2) | 36 counted climatology as nonlinear |
| 3.5 | climatology exceeds the ceiling in two cells | five cells, two of which it wins | wording |

## 2. Methods: text vs. code

Every method statement in the revised manuscript matches the code. Four statements in the draft did not, and were rewritten:

| Draft statement | Code | Revised text |
|---|---|---|
| "tuned tree tier"; "per-site hyperparameter optimisation is worth 0.002 NSE" (Abstract, 3.3, 4.2, 5) | no hyperparameter search anywhere; one fixed configuration per model; only the ESN ridge penalty is data-selected | fixed settings listed in 2.5; tree ensembles vs ESN "differ by less than 0.003 NSE"; 4.2 states that per-site tuning was not tested |
| "reported alongside Kling–Gupta efficiency" | KGE stored but never reported | mention removed |
| "skill is referenced to the climatology floor rather than the series mean" | NSE uses the test-block mean | every model is read against the climatology floor reported alongside it |
| Stage D "holding folds, models, seeds and metrics fixed" | Stage D uses 3 models; Δ uses the best per cell | stated explicitly in 2.6 |

Statements verified unchanged:
- T2M ≥ 5 °C and PET > 200 mm filters
- stratification, farthest-point sampling, 55 km separation
- daily → monthly aggregation, 504 months
- constant-cell drop (s.d. < 0.01)
- 2-harmonic deseasonalisation, ACF/PACF lags, SampEn (m = 2, r = 0.2)
- Yule–Walker p = 12
- KSG settings (k = 4, Chebyshev, lags 1, 2, 12, jitter 1e-8, 5-nat cap, n = 492)
- AR(2) validation errors 0.0003–0.0024
- the floors
- ESN settings
- 5 rolling folds × 60 months × 5 seeds

The settings the paper does not state are visible in the notebook: `land_frac > 0.2`, `P_ann > 0`, aridity class breaks 0.05 / 0.20 / 0.50 / 0.65, ESN sparsity 0.1 and input scale 0.5.

## 3. Re-execution

`scripts/rerun_check.py` runs the notebook's own cell code, starting from the archived daily POWER download. Models are **retrained from scratch** on six cells: the three Punjab sites plus one hyper-arid, one arid and one humid cell. Each fit is compared with the archived checkpoint for the same (cell, fold, model, seed).

| Stage | Scope | Fits compared | Max abs. difference |
|---|---|---|---|
| Cell 3: daily to monthly aggregation | all 249 cells, 12 variables | 125,496 rows | 0 |
| Cell 3: Stage A diagnostics | all 249 cells, 8 statistics | 249 | 4e-16 |
| Cell 4: linear ceilings | all 249 cells | 249 | 9e-16 |
| Cell 4: KSG MI bounds (full sequential run) | all 249 cells | 249 | 0 |
| Cell 5: Stage C ladder (9 models × 5 seeds × 5 folds) | 6 cells | 870 | 1e-15 NSE |
| Cell 6: ESN (5 seeds × 5 folds) | 6 cells | 150 | 6e-13 NSE |
| Cell 7: Stage D, lags 1–3 | 6 cells | 990 | 2e-14 NSE |
| Cell 7b: Stage D, lags 0–2 | 6 cells | 990 | 6e-15 NSE |

**The pipeline reproduces the archived results to floating-point precision.**

**Library version matters.** With scikit-learn 1.9.1, CART fits differ by up to 0.02 NSE per fold, AdaBoost-CART by up to 0.12, and RF by up to 5e-4, because tree internals changed between releases. With **scikit-learn 1.6.1** all three reproduce exactly, so the version is pinned in `requirements.txt` and in the notebook's install line.

Tested with Python 3.13, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.6.1, xgboost 3.4.1 and lightgbm 4.7.0. The original run used Colab with Python 3.11.

**Not re-run:**
- Cell 2 (the NASA POWER download) needs network access to `power.larc.nasa.gov`, so the archived download was used as input.
- The Earth Engine export was not re-run because its script was not kept; its output is archived in `data/gpc_*.csv`.
- Stage C and Stage D were retrained on 6 of 249 cells. The full run takes several hours on 2 CPUs; run `scripts/rerun_check.py --cells 5` for more cells.

## 4. Automated tests

`pytest -q tests` runs 16 tests, all passing:

- the AR(2) closed-form recovery (paper Sec 1.2), white-noise and bounds checks;
- deseasonalisation;
- KSG against the Gaussian analytic value and on floor-tied series;
- sample entropy;
- NSE reference points;
- lag-matrix alignment;
- ESN stability;
- a smoke test of the figure script;
- regression tests that pin Table 2, the ceiling, and the Stage D headline numbers to the archived tables.

GitHub Actions runs the 13 data-free tests on every push.

# Verification: code vs. manuscript

Checked against *SSW_Paper_EMS_SPMK.docx* (the version submitted to EMS). There are three independent checks:

1. **Numbers:** every numeric claim in the paper, recomputed from the archived outputs (`scripts/verify_paper_numbers.py`, full table in `VERIFICATION_numbers.md`).
2. **Methods:** every method parameter stated in Sections 2.2–2.6, compared with the notebook code.
3. **Re-execution:** the notebook's own cells re-run from the archived raw POWER download, with models retrained from scratch and compared fold by fold (`scripts/rerun_check.py`).

There is also an automated test suite (`tests/`, 16 tests) that runs on every push via GitHub Actions.

## 1. Numbers: 157 claims, 141 match, 16 do not

All 16 mismatches are errors in the **manuscript text**. In each case the code and results are internally consistent, and the paper quotes a number computed on a different input set, or misstates what was computed.

| # | Section | Paper says | Code / data give | Cause |
|---|---|---|---|---|
| 1 | 3.1 | 116 southern cells | **115** | 134 + 116 = 250; the dropped cell (7.5S) was southern |
| 2 | 3.1, 2.7 | r(AI, mean SSW) = 0.799; humid mean 0.687 | **0.802; 0.681** | quoted values were computed on 250 cells, before the constant cell was dropped |
| 3 | 1.2 | r = 0.709 | **0.802** | 0.709 is the preliminary India-60 value |
| 4 | 2.2 | "minimum of four cells per non-empty stratum" | one stratum (hyperarid / med / S) has **1** cell | only one candidate exists in the whole export; the code takes min(4, available) |
| 5 | 3.2 | "where the two diverge, the information bound is the higher" | MI bound is **below** the linear bound in **128 / 249** cells | MI uses 3 lags against 12 for the linear bound |
| 6–11 | 3.3 | AR12 win rates humid .868, dry-subhumid .593, arid .558; RF semiarid wins 15; MI split 59.5 % / 74.2 % | **.849, .574, .462; 13; 56.2 % / 71.9 %** | quoted values come from the 9-model table (before ESN, AR12 wins 167); Table 2 is 10-model (AR12 wins 160). The U-shape survives, with arid now lowest |
| 12–13 | 3.4, 4.3 | drivers-only 0.664 vs lag-only 0.643; drivers-only 0.859 | on the Table 3 basis: **0.695 vs 0.693**, and **0.887** | 0.664 / 0.643 / 0.859 are means over all models and seeds, while Table 3 uses the best model per cell. On the Table 3 basis "outperforms" becomes a tie |
| 14 | 3.5 | "nonlinear models account for 36 of the 49" | **34** | 36 counts every non-AR12 winner, which includes 2 climatology wins |
| 15 | 3.5 | "climatology exceeds the ceiling in two cells" | true for the 2 cells it **wins**; it exceeds in **5** cells overall | wording |

## 2. Methods: text vs. code

| Paper statement | Code | Verdict |
|---|---|---|
| T2M ≥ 5 °C, PET > 200 mm filters | `T2M_ann>=5`, `PET_ann>200`, plus `land_frac>0.2`, `P_ann>0` | match; the land-fraction and P>0 filters are not stated |
| aridity × irrigation tercile × hemisphere strata, min 4 per stratum, round-robin, farthest-point sampling, 55 km separation, Punjab exempt | as stated | match (see #4 above). The aridity class breaks (0.05 / 0.20 / 0.50 / 0.65) and the rule that uncropped cells go to the low irrigation class are not stated |
| snapped to containing cell centre, deduplicated | coordinates come from the GEE export lattice; all 250 extracted series are distinct | dedup claim verified |
| daily 1981–2025 → monthly, precip summed, others averaged, first 3 yr discarded, 504 months | as stated | match |
| constant cell removed | `std < 0.01` drop | match |
| 2-harmonic deseasonalisation; ACF to lag 24; PACF to 12; SampEn m = 2, r = 0.2 sd | as stated | match |
| Yule–Walker ceiling, p = 12 | as stated | match |
| KSG k = 4, Chebyshev, standardised, lags 1, 2, 12, jitter 1e-8, cap 5 nats, n = 492 | as stated | match |
| AR(2) validation: 3 settings, R² 0.09–0.58, error < 0.003 | errors 0.0003–0.0024 | match |
| floors: persistence, seasonal-naive, climatology (train only), AR12 | as stated | match |
| ESN: 300 units, ρ = 0.9, leak 0.3, ridge on inner holdout, standardised | as stated (sparsity 0.1 and input scale 0.5 not stated) | match |
| 5 expanding folds, 60-month blocks, 5 seeds | as stated | match |
| **"tuned tree tier", "per-site hyperparameter optimisation is worth 0.002 NSE"** (Abstract, 3.3, 4.2, 5) | **no hyperparameter search anywhere.** RF, XGBoost, LightGBM and AdaBoost use one fixed setting at every cell; only the ESN ridge is selected | **NOT SUPPORTED.** What was measured is fixed-setting tree ensembles vs. a fixed reservoir; the claim about tuning must be removed or the tuning actually run |
| "reported alongside Kling–Gupta efficiency" | KGE is computed and stored but never reported | text claims a result that is not shown |
| "skill is referenced to the climatology floor rather than the series mean" | NSE uses the test-block mean; no climatology-referenced skill score is computed | **NOT IMPLEMENTED** as worded |
| Stage D "holding folds, models, seeds and metrics fixed" | Stage D uses 3 models (OLS, RF, LightGBM), not the 10-model ladder | **models are not held fixed**; also not stated that Δ uses the best model per cell |

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

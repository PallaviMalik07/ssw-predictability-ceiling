# notebooks/

- **`ssw_global_pipeline.ipynb`** is the clean, runnable pipeline. Run it from the repository root (Colab or local Jupyter).
- **`archive/ssw_global_pipeline_as_run.ipynb`** is the Colab notebook exactly as it was executed for the paper, outputs included. It has diagnostic cells, Colab restore and download cells, and the fix cells added during the run. Keep it as the provenance record; don't rerun it top to bottom.

| Cell | Stage | Output in `data/` |
|---|---|---|
| 0 | setup; loads the 24 GEE chunks `gpc_0..23.csv` | — |
| Z | checkpoint: zip `data/` and download it; restore after a Colab recycle | — |
| 1 | panel selection: filters, aridity × irrigation × hemisphere strata, farthest-point sampling, 55 km separation, Punjab cells forced in | `panel_global.parquet` |
| 2 | NASA POWER daily pull, 1981–2025 (checkpointed per cell) | `raw_daily/`, `power_daily_panel.parquet` |
| 3 | monthly aggregation (1984+), drop of the degenerate cell, Stage A diagnostics | `power_monthly_panel.parquet`, `stageA_diagnostics.parquet` |
| 4 / 4v | Stage B linear (Yule–Walker) and KSG ceilings / AR(2) validation | `stageB_ceilings.parquet` |
| 5 | Stage C ladder: floors, AR12, CART, RF, AdaBoost, XGBoost, LightGBM | `stageC_ck/`, `stageC_legacy_results.parquet` |
| 6 | tuning-free tier: ESN (optional Chronos zero-shot) | `stageE_ck/`, `stageC_all_results.parquet` |
| 7 | Stage D, drivers at lags 1–3 (forecast) | `stageD_summary_lag1.parquet` |
| 7b | Stage D, drivers at lags 0–2 (diagnostic) | `stageD_summary_lag0.parquet` |
| 8 | ceiling-exceedance diagnostic | `exceedance_diagnostic.parquet` |
| 9 | figures, via `scripts/make_figures.py` | `figures/` |
| 10 | headline numbers | — |

**Two steps were added during the original run** and are carried into the clean notebook verbatim from the archived copy:

- **Cell 3:** drop cells with GWETTOP s.d. below 0.01. This removes one cell, 7.5S 34.7W, which is saturated at 1.0 in all 504 months.
- **Cell 4:** KSG mutual information with 1e-8 s.d. tie-breaking jitter and a 5-nat cap. It uses one generator seeded 0, drawn for each cell in turn (raw series, then deseasonalised).

**Verified reproduction** against the archived result tables:

| Step | Result |
|---|---|
| Panel (Cells 1 + 3, from `data/gpc_*.csv`) | the 249 published cells, exactly |
| Stage B linear ceilings, all 249 cells | max abs. difference 9e-16 |
| Stage B KSG MI, all 249 cells | max abs. difference 0 |
| Stage C, Stage D, exceedance | every number in the paper recomputed exactly from the archived tables |

**Two averaging bases in Stage D.** Cell 10 reports `lag_only` and `lag+drivers` two ways:

- the best of {OLS, RF, LightGBM} in each cell, averaged over cells (the `stageD_summary_*` tables);
- the mean over all models, seeds and folds.

Do not quote numbers from the two bases side by side.

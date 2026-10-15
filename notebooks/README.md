# notebooks/

`ssw_global_pipeline.ipynb` is the full analysis. Run it from the repository root (Colab or local Jupyter).

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

Cells marked `PATCH` in the code (Cell 3 degenerate-cell drop, Cell 4 KSG jitter and 5-nat cap) carry out the procedures described in paper Sections 2.2 and 2.4.

**Two averaging bases in Stage D.** Cell 10 reports `lag_only` and `lag+drivers` two ways:

- the best of {OLS, RF, LightGBM} in each cell, averaged over cells (the `stageD_summary_*` tables);
- the mean over all models, seeds and folds.

Do not quote numbers from the two bases side by side.

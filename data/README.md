# data/

The pipeline writes its outputs here. Git ignores this folder; the archived release will be deposited with a DOI.

Files and the columns that `scripts/make_figures.py` reads:

| File | Contents | Columns used by figures |
|---|---|---|
| `panel_global.parquet` | 249-cell panel definition | `cell_id, lat, lon` |
| `power_monthly_panel.parquet` | monthly POWER series, 504 months × 249 cells | — |
| `stageB_ceilings.parquet` | per-cell Stage A statistics and Stage B ceilings | `cell_id, AI, irrig_index, aridity_class, ceil_lin_raw` |
| `stageC_all_results.parquet` | one row per cell × fold × model × seed | `cell_id, fold, model, nse` |
| `stageD_summary_lag1.parquet` | Stage D, drivers at lags 1–3 (forecast) | `cell_id, irrig_class, acf1_des, driver_gain, above_ceiling` |
| `stageD_summary_lag0.parquet` | Stage D, drivers at lags 0–2 (diagnostic) | same as above |

Model labels in `stageC_all_results.model` that `make_figures.py` treats as classical floors: `Climatology, Persistence, SeasonalNaive, AR12`.

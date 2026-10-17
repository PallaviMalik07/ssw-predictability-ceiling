# data/

## Committed: Earth Engine covariate export (`gpc_0.csv` … `gpc_23.csv`)

These are the 24 chunks exported from Google Earth Engine: 6 longitude sectors × 4 latitude bands, 60°S–80°N, reduced at 10 km. There are 50,860 rows in total, and `gpc_0.csv` holds only a header.

The Earth Engine script that produced them was not kept, so the exported chunks are archived in its place. Notebook Cell 1 starts from these files and rebuilds the published panel exactly: it selects 250 cells, the 249 analysed cells plus `-07p500_-034p688`, which Cell 3 drops because its GWETTOP s.d. is below 0.01 (it is saturated at 1.0 in every month).

| Column | Source |
|---|---|
| `lat, lon` | NASA POWER grid-cell centre |
| `land_frac` | land fraction of the cell |
| `crop_frac` | cropland fraction: IGBP classes 12 and 14, modal MCD12Q1 2005–2020 |
| `AI` | aridity index P/PET, TerraClimate 1991–2020 |
| `P_ann, PET_ann` | TerraClimate annual precipitation and Penman–Monteith PET (mm/yr), 1991–2020 |
| `T2M_ann` | mean annual temperature (°C) |
| `ndvi_dry_crop` | mean dry-season MOD13Q1 NDVI over cropland, 2008–2022. Dry season is Dec–Mar in the north and Jun–Nov in the south. |

## Not committed: pipeline outputs

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

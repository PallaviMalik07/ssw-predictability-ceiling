# Predictability ceilings for lag-based emulation of soil surface wetness

Code and figures for:

> Malik, P., Chauhan, S. *Predictability ceilings for lag-based emulation of modelled soil surface wetness: a linear baseline outperforms six machine-learning families across 249 global grid cells.* Submitted to *Environmental Modelling & Software*.

## What the study does

ML emulators of modelled soil moisture are usually ranked against each other, with no reference for how much skill the series allows in the first place. This study derives that reference and scores a ladder of models against it.

| Stage | What it does |
|---|---|
| **A** Series characterisation | 2-harmonic seasonal fit, seasonal variance share, raw and deseasonalised ACF/PACF, sample entropy |
| **B** Predictability ceilings | Linear ceiling R²<sub>max</sub> from the Yule–Walker system on lags 1–12 (no model fitted). Independent check: a KSG mutual-information bound |
| **C** Benchmark ladder | Persistence, seasonal-naive, climatology, AR12 (12-lag OLS), CART, RF, AdaBoost-CART, XGBoost, LightGBM, echo state network. 5-fold rolling origin, 60-month test blocks, 5 seeds |
| **D** Exogenous drivers | Lag-only vs drivers-only vs lag+drivers. Drivers at lags 1–3 (forecast) and lags 0–2 (diagnostic only) |

**Data.** NASA POWER (GEOS/MERRA-2) monthly `GWETTOP`, 1984–2025 (504 months) for 249 grid cells on six continents. Cells are stratified by TerraClimate aridity (P/PET) × MODIS dry-season cropped greenness × hemisphere.

## Main results (249 cells)

| Model | Mean NSE | SD | Cells won |
|---|---|---|---|
| **AR12 (12-lag OLS)** | **0.687** | **0.210** | **160** |
| Random forest | 0.662 | 0.227 | 51 |
| AdaBoost-CART | 0.650 | 0.244 | 16 |
| Echo state network | 0.634 | 0.267 | 9 |
| XGBoost | 0.633 | 0.269 | 6 |
| LightGBM | 0.616 | 0.293 | 4 |
| Persistence | 0.490 | 0.213 | 1 |
| Climatology | 0.354 | 0.787 | 2 |
| CART | 0.348 | 0.500 | 0 |
| Seasonal-naive | 0.125 | 0.596 | 0 |

- Mean panel ceiling is 0.751 (range 0.27–0.95). Achieved skill tracks the ceiling at r = 0.936. The linear and MI bounds agree at r = 0.937.
- Seed noise is about 12× smaller than the between-model spread, so the rankings are real. The simplest model comes first.
- With drivers at lags 1–3, NSE gains +0.047 (Wilcoxon p = 1.3 × 10⁻³⁹) and 137 of 249 cells go above the lag-only ceiling.
- Adding the concurrent month makes the gain five times larger (+0.238) and puts 246 of 249 cells above the ceiling. This is information leakage, so it is reported only as a diagnostic.

## Repository layout

```
figures/               Figures 1-6 as submitted (300 dpi PNG)
scripts/
  make_figures.py      re-renders Figures 1-6 from the result tables in data/
  colab_io.py          backs up and restores data/ (with checkpoints) on Colab
  check_references.py  resolves every cited DOI against Crossref / DataCite
notebooks/
  ssw_global_pipeline.ipynb  full pipeline: GEE panel -> POWER pull -> Stages A-D (see notebooks/README.md)
data/                  pipeline outputs, not version-controlled (see data/README.md)
```

## Reproducing

```bash
pip install -r requirements.txt
# 1. GEE covariate export -> data/gpc_0.csv ... gpc_23.csv
# 2. run notebooks/ssw_global_pipeline.ipynb from the repo root -> data/*.parquet
#    (Cell 9 renders the figures; or run step 3 on its own)
# 3. render the figures
python scripts/make_figures.py --data data --out figures
```

You need a Google Earth Engine account for the covariate export. You need network access to `power.larc.nasa.gov` for the POWER pull. No GPU is needed and 8 GB RAM is enough. Every heavy stage saves a checkpoint per grid cell and picks up where it left off after a restart.

The pipeline was run twice from raw inputs on separate compute environments and gave the same reported numbers both times.

## Data sources

All inputs are public and need no special permission.

- NASA POWER: https://power.larc.nasa.gov
- TerraClimate (Abatzoglou et al., 2018), via Google Earth Engine
- MODIS MCD12Q1 v006 and MOD13Q1, via Google Earth Engine

## Citation

See `CITATION.cff`. A DOI for the archived release will be added here.

## License

The code is under MIT (see `LICENSE`). The figures are under CC BY 4.0.

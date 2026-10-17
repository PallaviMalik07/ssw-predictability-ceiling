# Manuscript number audit

157 numeric claims recomputed from the archived outputs: **141 match, 16 do not.**

| Section | Claim | Paper | Recomputed | | Note |
|---|---|---|---|---|---|
| 2.2 | raw GEE records | 50860.0 | 50860 | OK |  |
| 2.2 | unique cells after chunk dedup | 50412.0 | 50412 | OK |  |
| 2.2 | cells after T/PET filters | 29951.0 | 29951 | OK |  |
| 2.2 | final panel size | 249.0 | 249 | OK |  |
| 2.2 | southern-most latitude (deg S) | 55.2 | 55.2 | OK |  |
| 2.2 | northern-most latitude (deg N) | 64.0 | 64.0 | OK |  |
| 2.2 | min aridity index | 0.001 | 0.001 | OK |  |
| 2.2 | max aridity index | 2.83 | 2.83 | OK |  |
| 2.2 | min annual precip (mm) | 1.0 | 1 | OK |  |
| 2.2 | max annual precip (mm) | 4021.0 | 4021 | OK |  |
| 2.2 | closest Punjab pair (km) | 59.6 | 59.6 | OK |  |
| 3.1 | non-empty strata | 29.0 | 29 | OK |  |
| 3.1 | northern-hemisphere cells | 134.0 | 134 | OK |  |
| 3.1 | southern-hemisphere cells | 116.0 | 115 | **MISMATCH** |  |
| 3.1 | corr(AI, irrig_index) | -0.073 | -0.073 | OK |  |
| 3.1 | min separation, non-replication cells (km) | 55.1 | 55.1 | OK |  |
| 2.2 | every extracted cell returns a distinct series (250 incl. dropped cell) | 250.0 | 250 | OK |  |
| 3.1 | mean GWETTOP hyperarid | 0.186 | 0.186 | OK |  |
| 3.1 | mean GWETTOP humid | 0.687 | 0.681 | **MISMATCH** | 0.687 / 0.799 reproduce only on 250 cells, i.e. before the constant cell was dropped |
| 3.1 / 2.7 | corr(AI, mean GWETTOP) | 0.799 | 0.802 | **MISMATCH** |  |
| 1.2 | corr(AI, mean GWETTOP) as stated in 1.2 | 0.709 | 0.802 | **MISMATCH** | 0.709 is the India-60 value |
| 2.2 | strata with fewer than 4 cells ('minimum of four per stratum') | 0.0 | 1 | **MISMATCH** | hyperarid|med|S has only 1 candidate cell in the whole export; code takes min(4, available) |
| 3.1 | seas_share min | 0.057 | 0.057 | OK |  |
| 3.1 | seas_share max | 0.944 | 0.944 | OK |  |
| 3.1 | seas_share mean | 0.532 | 0.532 | OK |  |
| 3.1 | Punjab seas_share min | 0.443 | 0.443 | OK |  |
| 3.1 | Punjab seas_share max | 0.531 | 0.531 | OK |  |
| 3.1 | acf1_des min | 0.373 | 0.373 | OK |  |
| 3.1 | acf1_des max | 0.952 | 0.952 | OK |  |
| 3.1 | sample entropy semiarid | 1.597 | 1.597 | OK |  |
| 3.1 | sample entropy dry-subhumid | 1.621 | 1.621 | OK |  |
| 3.1 | sample entropy hyperarid | 1.261 | 1.261 | OK |  |
| 3.1 | sample entropy humid | 1.404 | 1.404 | OK |  |
| 3.2 / Abs | panel-mean linear ceiling | 0.751 | 0.751 | OK |  |
| 3.2 | ceiling min | 0.272 | 0.272 | OK |  |
| 3.2 | ceiling max | 0.951 | 0.951 | OK |  |
| 3.2 | mean ceiling hyperarid | 0.637 | 0.637 | OK |  |
| 3.2 | mean ceiling arid | 0.742 | 0.742 | OK |  |
| 3.2 | mean ceiling semiarid | 0.754 | 0.754 | OK |  |
| 3.2 | mean ceiling dry-subhumid | 0.775 | 0.775 | OK |  |
| 3.2 | mean ceiling humid | 0.811 | 0.811 | OK |  |
| 3.2 / Abs | corr(ceil_lin_des, acf1_des) | 0.984 | 0.984 | OK |  |
| 3.2 | cells where MI bound < linear bound ('where they diverge, MI is the higher') | 0.0 | 128 | **MISMATCH** | MI uses 3 lags vs 12 for the linear bound, so it can sit below it |
| 3.2 / Abs | corr(ceil_mi_raw, ceil_lin_raw) | 0.937 | 0.937 | OK |  |
| Table 1 | Firozpur linear ceiling | 0.627 | 0.627 | OK |  |
| Table 1 | Firozpur deseasonalised ceiling | 0.474 | 0.474 | OK |  |
| Table 1 | Firozpur seasonal share | 0.443 | 0.443 | OK |  |
| Table 1 | Moga linear ceiling | 0.664 | 0.664 | OK |  |
| Table 1 | Moga deseasonalised ceiling | 0.51 | 0.510 | OK |  |
| Table 1 | Moga seasonal share | 0.476 | 0.476 | OK |  |
| Table 1 | Hoshiarpur linear ceiling | 0.734 | 0.734 | OK |  |
| Table 1 | Hoshiarpur deseasonalised ceiling | 0.571 | 0.571 | OK |  |
| Table 1 | Hoshiarpur seasonal share | 0.531 | 0.531 | OK |  |
| Table 2 | AR12 mean NSE | 0.687 | 0.687 | OK |  |
| Table 2 | AR12 SD | 0.21 | 0.210 | OK |  |
| Table 2 | AR12 cells won | 160.0 | 160 | OK |  |
| Table 2 | RF mean NSE | 0.662 | 0.662 | OK |  |
| Table 2 | RF SD | 0.227 | 0.227 | OK |  |
| Table 2 | RF cells won | 51.0 | 51 | OK |  |
| Table 2 | AdaBoost-CART mean NSE | 0.65 | 0.650 | OK |  |
| Table 2 | AdaBoost-CART SD | 0.244 | 0.244 | OK |  |
| Table 2 | AdaBoost-CART cells won | 16.0 | 16 | OK |  |
| Table 2 | ESN mean NSE | 0.634 | 0.634 | OK |  |
| Table 2 | ESN SD | 0.267 | 0.267 | OK |  |
| Table 2 | ESN cells won | 9.0 | 9 | OK |  |
| Table 2 | XGBoost mean NSE | 0.633 | 0.633 | OK |  |
| Table 2 | XGBoost SD | 0.269 | 0.269 | OK |  |
| Table 2 | XGBoost cells won | 6.0 | 6 | OK |  |
| Table 2 | LightGBM mean NSE | 0.616 | 0.616 | OK |  |
| Table 2 | LightGBM SD | 0.293 | 0.293 | OK |  |
| Table 2 | LightGBM cells won | 4.0 | 4 | OK |  |
| Table 2 | Persistence mean NSE | 0.49 | 0.490 | OK |  |
| Table 2 | Persistence SD | 0.213 | 0.213 | OK |  |
| Table 2 | Persistence cells won | 1.0 | 1 | OK |  |
| Table 2 | Climatology mean NSE | 0.354 | 0.354 | OK |  |
| Table 2 | Climatology SD | 0.787 | 0.787 | OK |  |
| Table 2 | Climatology cells won | 2.0 | 2 | OK |  |
| Table 2 | CART mean NSE | 0.348 | 0.348 | OK |  |
| Table 2 | CART SD | 0.5 | 0.500 | OK |  |
| Table 2 | CART cells won | 0.0 | 0 | OK |  |
| Table 2 | SeasonalNaive mean NSE | 0.125 | 0.125 | OK |  |
| Table 2 | SeasonalNaive SD | 0.596 | 0.596 | OK |  |
| Table 2 | SeasonalNaive cells won | 0.0 | 0 | OK |  |
| 3.3 | tuned tree tier mean (RF, XGBoost, LightGBM) | 0.637 | 0.637 | OK |  |
| 3.3 | tuning-free tier mean (ESN) | 0.634 | 0.634 | OK |  |
| 3.3 / Fig 4 | median seed s.d. | 0.0082 | 0.0082 | OK |  |
| 3.3 / Fig 4 | median between-model s.d. | 0.0954 | 0.0954 | OK |  |
| 3.3 / Fig 4 | between / seed ratio | 11.6 | 11.6 | OK |  |
| 3.3 / Abs | corr(best NSE, ceiling) | 0.936 | 0.936 | OK |  |
| 3.3 / 4.1 | mean gap ceiling - best | 0.058 | 0.058 | OK |  |
| 3.3 | AR12 win rate humid | 0.868 | 0.849 | **MISMATCH** | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | AR12 win rate hyperarid | 0.722 | 0.722 | OK | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | AR12 win rate semiarid | 0.63 | 0.630 | OK | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | AR12 win rate dry-subhumid | 0.593 | 0.574 | **MISMATCH** | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | AR12 win rate arid | 0.558 | 0.462 | **MISMATCH** | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | RF wins arid | 17.0 | 17 | OK | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | RF wins semiarid | 15.0 | 13 | **MISMATCH** | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | RF wins dry-subhumid | 12.0 | 12 | OK | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | RF wins humid | 3.0 | 3 | OK | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | AR12 win rate where MI > linear (%) | 59.5 | 56.2 | **MISMATCH** | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.3 | AR12 win rate where MI <= linear (%) | 74.2 | 71.9 | **MISMATCH** | paper value reproduces on stageC_legacy_results (9 models, before ESN; AR12 wins 167); Table 2 uses 10 models |
| 3.4 / Table 3 | lag-only, lags 1-3 (best per cell) | 0.693 | 0.693 | OK |  |
| 3.4 / Table 3 | lag+drivers, lags 1-3 | 0.74 | 0.740 | OK |  |
| 3.4 / Table 3 | driver gain, lags 1-3 | 0.047 | 0.047 | OK |  |
| 3.4 / Abs | Wilcoxon p, lags 1-3 | 1.3e-39 | 1.3e-39 | OK |  |
| 3.4 / Table 3 | cells above ceiling, lags 1-3 | 137.0 | 137 | OK |  |
| 3.4 / Table 3 | corr(acf1_des, gain), lags 1-3 | -0.353 | -0.353 | OK |  |
| 3.4 / Table 3 | p of that corr, lags 1-3 | 1e-08 | 1e-08 | OK |  |
| 3.4 | corr(sampen_des, gain), lags 1-3 | 0.204 | 0.204 | OK |  |
| 3.4 | p of sampen corr (paper: 0.001) | 0.001 | 0.001 | OK |  |
| Table 3 | lag-only, lags 0-2 | 0.693 | 0.693 | OK |  |
| Table 3 / 4.3 | lag+drivers, lags 0-2 | 0.93 | 0.930 | OK |  |
| 3.4 / Abs | driver gain, lags 0-2 | 0.238 | 0.238 | OK |  |
| 3.4 / Abs | cells above ceiling, lags 0-2 | 246.0 | 246 | OK |  |
| Table 3 | corr(acf1_des, gain), lags 0-2 | -0.302 | -0.302 | OK |  |
| Table 3 | p of that corr, lags 0-2 | 1e-06 | 1.2e-06 | OK |  |
| 3.4 / 4.3 | inflation factor gain0 / gain1 | 5.0 | 5.0 | OK |  |
| 3.4 | 'lagged meteorology alone' 0.664 [all-model mean basis] | 0.664 | 0.664 | OK |  |
| 3.4 | 'lagged wetness alone' 0.643 [all-model mean basis] | 0.643 | 0.643 | OK |  |
| 3.4 | same comparison on Table 3 basis: drivers_only lags 1-3 | 0.664 | 0.695 | **MISMATCH** | paper mixes bases: 0.664/0.643 are all-model means, Table 3's 0.693 is best-per-cell |
| 3.4 / 4.3 | 'drivers alone' lags 0-2 0.859 [all-model mean basis] | 0.859 | 0.859 | OK |  |
| 3.4 / 4.3 | same on Table 3 basis: drivers_only lags 0-2 | 0.859 | 0.887 | **MISMATCH** | 0.859 is an all-model mean; on the Table 3 basis it is 0.887 |
| 3.4 | driver gain hyperarid | 0.067 | 0.067 | OK |  |
| 3.4 | driver gain arid | 0.053 | 0.053 | OK |  |
| 3.4 | driver gain semiarid | 0.045 | 0.045 | OK |  |
| 3.4 | driver gain dry-subhumid | 0.041 | 0.041 | OK |  |
| 3.4 | driver gain humid | 0.038 | 0.038 | OK |  |
| Table 4 | Firozpur lag-only | 0.558 | 0.558 | OK |  |
| Table 4 | Firozpur lag+drivers | 0.627 | 0.627 | OK |  |
| Table 4 | Firozpur ceiling | 0.627 | 0.627 | OK |  |
| Table 4 | Firozpur exceedance | -0.001 | -0.001 | OK |  |
| Table 4 | Moga lag-only | 0.593 | 0.593 | OK |  |
| Table 4 | Moga lag+drivers | 0.657 | 0.657 | OK |  |
| Table 4 | Moga ceiling | 0.664 | 0.664 | OK |  |
| Table 4 | Moga exceedance | -0.007 | -0.007 | OK |  |
| Table 4 | Hoshiarpur lag-only | 0.682 | 0.682 | OK |  |
| Table 4 | Hoshiarpur lag+drivers | 0.735 | 0.735 | OK |  |
| Table 4 | Hoshiarpur ceiling | 0.734 | 0.734 | OK |  |
| Table 4 | Hoshiarpur exceedance | 0.001 | 0.001 | OK |  |
| 3.5 | cells above linear ceiling (Stage C best) | 49.0 | 49 | OK |  |
| 3.5 | max exceedance | 0.038 | 0.038 | OK |  |
| 3.5 | mean exceedance of over-cells | 0.012 | 0.012 | OK |  |
| 3.5 | corr(seas_share, exceedance) | 0.741 | 0.741 | OK |  |
| 3.5 | p of that corr | 1e-44 | 1.2e-44 | OK |  |
| 3.5 | mean seas_share over-cells | 0.768 | 0.768 | OK |  |
| 3.5 | mean seas_share other cells | 0.475 | 0.475 | OK |  |
| 3.5 | over-cells won by nonlinear models | 36.0 | 34 | **MISMATCH** | 36 = all non-AR12 winners, which includes 2 Climatology wins; nonlinear models are 34 |
| 3.5 | non-exceeding cells | 200.0 | 200 | OK |  |
| 3.5 | AR12 wins among non-exceeding | 147.0 | 147 | OK |  |
| 3.5 | cells where climatology is the best model AND exceeds the ceiling | 2.0 | 2 | OK |  |
| 3.5 | cells where climatology exceeds the ceiling (any rank) | 2.0 | 5 | **MISMATCH** | 'Climatology exceeds the ceiling in two cells' is true only for cells it wins |
| 4.6 | cells > 0.20 below ceiling | 12.0 | 12 | OK |  |
| 4.6 | worst shortfall | 0.43 | 0.430 | OK |  |
| 4.6 | mean seas_share of shortfall cells | 0.157 | 0.157 | OK |  |
| 4.6 | mean seas_share of panel | 0.532 | 0.532 | OK |  |
| 4.6 | shortfall cells: sample entropy below panel mean | 1.0 | 1 | OK |  |
| Fig 3 | model-class means above their class ceiling | 0.0 | 0 | OK |  |

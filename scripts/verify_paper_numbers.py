"""Recompute every numeric claim in the manuscript (revised version, Oct 2026) from the archived pipeline outputs.

Usage:  python scripts/verify_paper_numbers.py [--data data] [--report VERIFICATION_numbers.md]

Each claim is stated with the value printed in the manuscript and the number of decimals it is
printed to. A claim MATCHES when the recomputed value rounds to the printed value. Exit code is
the number of mismatches (0 = every claim reproduced).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ARID = ["hyperarid", "arid", "semiarid", "dry-subhumid", "humid"]
FLOORS = ["Climatology", "Persistence", "SeasonalNaive", "AR12"]
R_EARTH = 6371.0

rows = []


def claim(section, what, paper, value, dec=3, kind="num", note=""):
    """Register one claim. kind='num' rounds to dec; 'int' exact; 'p' compares the exponent."""
    if kind == "int":
        ok = int(value) == int(paper)
        shown = f"{int(value)}"
    elif kind == "p":   # paper states e.g. 1.3e-39 or 1e-08: match mantissa (if given) and exponent
        m_p, e_p = f"{paper:.1e}".split("e")
        m_v, e_v = f"{value:.1e}".split("e")
        ok = (int(e_p) == int(e_v)) and (dec == 0 or m_p == m_v)
        shown = f"{value:.2g}"
    else:
        ok = round(float(value), dec) == round(float(paper), dec)
        shown = f"{value:.{dec}f}"
    rows.append(dict(section=section, claim=what, paper=paper, recomputed=shown, ok=ok, note=note))


def best_per_cell(res):
    b = res.groupby(["cell_id", "model"]).nse.mean().reset_index()
    return b.loc[b.groupby("cell_id").nse.idxmax()]


def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def main(D: Path, report: Path):
    pan = pd.read_parquet(D / "panel_global.parquet")
    diag = pd.read_parquet(D / "stageA_diagnostics.parquet")
    ce = pd.read_parquet(D / "stageB_ceilings.parquet")
    res = pd.read_parquet(D / "stageC_all_results.parquet")
    s1 = pd.read_parquet(D / "stageD_summary_lag1.parquet")
    s0 = pd.read_parquet(D / "stageD_summary_lag0.parquet")
    d1 = pd.concat([pd.read_parquet(f) for f in sorted((D / "stageD_ck_lag1").glob("*.parquet"))])
    d0 = pd.concat([pd.read_parquet(f) for f in sorted((D / "stageD_ck_lag0").glob("*.parquet"))])
    d1 = d1[d1.cell_id.isin(pan.cell_id)]; d0 = d0[d0.cell_id.isin(pan.cell_id)]

    # ---------------- 2.2 panel construction (from the GEE chunks) ----------------
    g = pd.concat([pd.read_csv(f) for f in sorted(D.glob("gpc_*.csv"))], ignore_index=True)
    claim("2.2", "raw GEE records", 50860, len(g), kind="int")
    for c in ["lat", "lon", "land_frac", "AI", "P_ann", "PET_ann", "T2M_ann"]:
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g = g.dropna(subset=["lat", "lon", "AI", "T2M_ann", "PET_ann"]).drop_duplicates(["lat", "lon"])
    claim("2.2", "unique cells after chunk dedup", 50412, len(g), kind="int")
    g = g[(g.land_frac > 0.2) & (g.T2M_ann >= 5) & (g.PET_ann > 200) & (g.P_ann > 0)]
    claim("2.2", "cells after T/PET filters", 29951, len(g), kind="int")
    claim("2.2", "final panel size", 249, len(pan), kind="int")
    claim("2.2", "southern-most latitude (deg S)", 55.2, -pan.lat.min(), 1)
    claim("2.2", "northern-most latitude (deg N)", 64.0, pan.lat.max(), 1)
    claim("2.2", "min aridity index", 0.001, pan.AI.min(), 3)
    claim("2.2", "max aridity index", 2.83, pan.AI.max(), 2)
    claim("2.2", "min annual precip (mm)", 1, pan.P_ann.min(), 0)
    claim("2.2", "max annual precip (mm)", 4021, pan.P_ann.max(), 0)
    pj = pan[pan.replication].set_index("name")
    P = xyz(pj.lat.to_numpy(), pj.lon.to_numpy())
    dmin = min(np.linalg.norm(P[i] - P[j]) * R_EARTH for i in range(3) for j in range(i + 1, 3))
    claim("2.2", "closest Punjab pair (km)", 59.6, dmin, 1)

    # ---------------- 3.1 panel and series structure ----------------
    claim("3.1", "non-empty strata", 29, pan.stratum.nunique(), kind="int")
    claim("3.1", "northern-hemisphere cells", 134, (pan.hemi == "N").sum(), kind="int")
    claim("3.1", "southern-hemisphere cells", 115, (pan.hemi == "S").sum(), kind="int")
    claim("3.1", "corr(AI, irrig_index)", -0.073, stats.pearsonr(pan.AI, pan.irrig_index)[0], 3)
    nonrep = pan[~pan.replication]
    Pm = xyz(nonrep.lat.to_numpy(), nonrep.lon.to_numpy())
    Dm = np.linalg.norm(Pm[:, None] - Pm[None], axis=2); np.fill_diagonal(Dm, np.inf)
    claim("3.1", "min separation, non-replication cells (km)", 55.1, Dm.min() * R_EARTH, 1)
    # paper computes these from the DAILY series (notebook Cell 2), on the 249 analysed cells
    daily = pd.read_parquet(D / "power_daily_panel.parquet", columns=["cell_id", "GWETTOP"])
    sig = daily.groupby("cell_id").GWETTOP.apply(lambda v: hash(tuple(np.round(v.to_numpy(), 5))))
    claim("2.2", "every extracted cell returns a distinct series (250 incl. dropped cell)", 250, sig.nunique(), kind="int")
    gw = daily.groupby("cell_id").GWETTOP.mean().rename("gw")
    j = pan.set_index("cell_id")[["AI", "aridity_class"]].join(gw, how="inner")
    gm = j.groupby("aridity_class", observed=True).gw.mean()
    claim("3.1", "mean GWETTOP hyperarid", 0.186, gm["hyperarid"], 3)
    claim("3.1", "mean GWETTOP humid", 0.681, gm["humid"], 3)
    claim("2.7", "mean GWETTOP rises monotonically across the five aridity classes", 1,
          int(all(gm[a] < gm[b] for a, b in zip(ARID, ARID[1:]))), kind="int")
    rj = stats.pearsonr(j.AI, j.gw)[0]
    claim("1.2 / 2.7 / 3.1", "corr(AI, mean GWETTOP)", 0.802, rj, 3)
    vc = pan.stratum.value_counts()
    claim("2.2", "strata with fewer than 4 cells (stated: one, with a single candidate)", 1, (vc < 4).sum(), kind="int")
    claim("2.2", "cells in that stratum", 1, vc.min(), kind="int")
    claim("3.1", "seas_share min", 0.057, diag.seas_share.min(), 3)
    claim("3.1", "seas_share max", 0.944, diag.seas_share.max(), 3)
    claim("3.1", "seas_share mean", 0.532, diag.seas_share.mean(), 3)
    dp = diag[diag.replication]
    claim("3.1", "Punjab seas_share min", 0.443, dp.seas_share.min(), 3)
    claim("3.1", "Punjab seas_share max", 0.531, dp.seas_share.max(), 3)
    claim("3.1", "acf1_des min", 0.373, diag.acf1_des.min(), 3)
    claim("3.1", "acf1_des max", 0.952, diag.acf1_des.max(), 3)
    se = diag.groupby("aridity_class", observed=True).sampen_des.mean()
    for k, v in [("semiarid", 1.597), ("dry-subhumid", 1.621), ("hyperarid", 1.261), ("humid", 1.404)]:
        claim("3.1", f"sample entropy {k}", v, se[k], 3)

    # ---------------- 3.2 ceilings ----------------
    claim("3.2 / Abs", "panel-mean linear ceiling", 0.751, ce.ceil_lin_raw.mean(), 3)
    claim("3.2", "ceiling min", 0.272, ce.ceil_lin_raw.min(), 3)
    claim("3.2", "ceiling max", 0.951, ce.ceil_lin_raw.max(), 3)
    cb = ce.groupby("aridity_class", observed=True).ceil_lin_raw.mean()
    for k, v in zip(ARID, [0.637, 0.742, 0.754, 0.775, 0.811]):
        claim("3.2", f"mean ceiling {k}", v, cb[k], 3)
    claim("3.2 / Abs", "corr(ceil_lin_des, acf1_des)", 0.984, ce[["ceil_lin_des", "acf1_des"]].corr().iloc[0, 1], 3)
    claim("3.2", "cells where MI bound > linear bound", 121, (ce.ceil_mi_raw > ce.ceil_lin_raw).sum(), kind="int")
    claim("3.2", "cells where MI bound < linear bound", 128, (ce.ceil_mi_raw < ce.ceil_lin_raw).sum(), kind="int")
    claim("3.2 / Abs", "corr(ceil_mi_raw, ceil_lin_raw)", 0.937, ce[["ceil_mi_raw", "ceil_lin_raw"]].corr().iloc[0, 1], 3)
    cp = ce[ce.replication].set_index("name")
    for nm, lin, des, ss in [("Firozpur", .627, .474, .443), ("Moga", .664, .510, .476), ("Hoshiarpur", .734, .571, .531)]:
        claim("Table 1", f"{nm} linear ceiling", lin, cp.at[nm, "ceil_lin_raw"], 3)
        claim("Table 1", f"{nm} deseasonalised ceiling", des, cp.at[nm, "ceil_lin_des"], 3)
        claim("Table 1", f"{nm} seasonal share", ss, cp.at[nm, "seas_share"], 3)

    # ---------------- 3.3 benchmark ladder ----------------
    tab = res.groupby("model").nse.agg(["mean", "std"])
    top = best_per_cell(res)
    wins = top.model.value_counts()
    T2 = [("AR12", .687, .210, 160), ("RF", .662, .227, 51), ("AdaBoost-CART", .650, .244, 16),
          ("ESN", .634, .267, 9), ("XGBoost", .633, .269, 6), ("LightGBM", .616, .293, 4),
          ("Persistence", .490, .213, 1), ("Climatology", .354, .787, 2), ("CART", .348, .500, 0),
          ("SeasonalNaive", .125, .596, 0)]
    for m, mu, sd, w in T2:
        claim("Table 2", f"{m} mean NSE", mu, tab.at[m, "mean"], 3)
        claim("Table 2", f"{m} SD", sd, tab.at[m, "std"], 3)
        claim("Table 2", f"{m} cells won", w, wins.get(m, 0), kind="int")
    claim("3.3", "tree ensemble mean (RF, XGBoost, LightGBM)", 0.637,
          res[res.model.isin(["RF", "XGBoost", "LightGBM"])].nse.mean(), 3)
    claim("3.3", "reservoir tier mean (ESN)", 0.634, res[res.model == "ESN"].nse.mean(), 3)
    gap = res[res.model.isin(["RF", "XGBoost", "LightGBM"])].nse.mean() - res[res.model == "ESN"].nse.mean()
    claim("3.3 / 4.2 / Abs / 5", "tree ensembles vs ESN differ by less than 0.003 NSE", 1, int(abs(gap) < 0.003), kind="int")
    ml = res[~res.model.isin(FLOORS)]
    seed = ml.groupby(["cell_id", "fold", "model"]).nse.std().dropna().median()
    betw = ml.groupby(["cell_id", "fold", "model"]).nse.mean().groupby(level=[0, 1]).std().dropna().median()
    claim("3.3 / Fig 4", "median seed s.d.", 0.0082, seed, 4)
    claim("3.3 / Fig 4", "median between-model s.d.", 0.0954, betw, 4)
    claim("3.3 / Fig 4", "between / seed ratio", 11.6, betw / seed, 1)
    t = top.merge(ce, on="cell_id")
    claim("3.3 / Abs", "corr(best NSE, ceiling)", 0.936, t[["nse", "ceil_lin_raw"]].corr().iloc[0, 1], 3)
    claim("3.3 / 4.1", "mean gap ceiling - best", 0.058, (t.ceil_lin_raw - t.nse).mean(), 3)
    t["ar12"] = t.model == "AR12"
    NOTE33 = ""
    wr = t.groupby("aridity_class", observed=True).ar12.mean()
    for k, v in [("humid", .849), ("hyperarid", .722), ("semiarid", .630), ("dry-subhumid", .574), ("arid", .462)]:
        claim("3.3", f"AR12 win rate {k}", v, wr[k], 3, note=NOTE33)
    rf = t[t.model == "RF"].aridity_class.value_counts()
    for k, v in [("arid", 17), ("semiarid", 13), ("dry-subhumid", 12), ("humid", 3)]:
        claim("3.3", f"RF wins {k}", v, rf.get(k, 0), kind="int", note=NOTE33)
    gt = t.ceil_mi_raw > t.ceil_lin_raw
    claim("3.3", "AR12 win rate where MI > linear (%)", 56.2, 100 * t[gt].ar12.mean(), 1, note=NOTE33)
    claim("3.3", "AR12 win rate where MI <= linear (%)", 71.9, 100 * t[~gt].ar12.mean(), 1, note=NOTE33)

    # ---------------- 3.4 / Table 3 / Table 4 ----------------
    claim("3.4 / Table 3", "lag-only, lags 1-3 (best per cell)", 0.693, s1.lag_only.mean(), 3)
    claim("3.4 / Table 3", "lag+drivers, lags 1-3", 0.740, s1["lag+drivers"].mean(), 3)
    claim("3.4 / Table 3", "driver gain, lags 1-3", 0.047, s1.driver_gain.mean(), 3)
    claim("3.4 / Abs", "Wilcoxon p, lags 1-3", 1.3e-39, stats.wilcoxon(s1["lag+drivers"], s1.lag_only)[1], 1, kind="p")
    claim("3.4 / Table 3", "cells above ceiling, lags 1-3", 137, (s1.above_ceiling > 0).sum(), kind="int")
    r1, p1 = stats.pearsonr(s1.acf1_des.astype(float), s1.driver_gain.astype(float))
    claim("3.4 / Table 3", "corr(acf1_des, gain), lags 1-3", -0.353, r1, 3)
    claim("3.4 / Table 3", "p of that corr, lags 1-3", 1e-8, p1, 0, kind="p")
    rs, ps = stats.pearsonr(s1.sampen_des.astype(float), s1.driver_gain.astype(float))
    claim("3.4", "corr(sampen_des, gain), lags 1-3", 0.204, rs, 3)
    claim("3.4", "p of sampen corr (paper: 0.001)", 0.001, ps, 3)
    claim("Table 3", "lag-only, lags 0-2", 0.693, s0.lag_only.mean(), 3)
    claim("Table 3 / 4.3", "lag+drivers, lags 0-2", 0.930, s0["lag+drivers"].mean(), 3)
    claim("3.4 / Abs", "driver gain, lags 0-2", 0.238, s0.driver_gain.mean(), 3)
    claim("3.4 / Abs", "cells above ceiling, lags 0-2", 246, (s0.above_ceiling > 0).sum(), kind="int")
    r0, p0 = stats.pearsonr(s0.acf1_des.astype(float), s0.driver_gain.astype(float))
    claim("Table 3", "corr(acf1_des, gain), lags 0-2", -0.302, r0, 3)
    claim("Table 3", "p of that corr, lags 0-2", 1e-6, p0, 0, kind="p")
    claim("3.4 / 4.3", "inflation factor gain0 / gain1", 5.0, s0.driver_gain.mean() / s1.driver_gain.mean(), 1)
    m1 = d1.groupby("inputs").nse.mean(); m0 = d0.groupby("inputs").nse.mean()
    claim("3.4", "lagged meteorology alone, lags 1-3 (best per cell)", 0.695, s1.drivers_only.mean(), 3)
    claim("3.4", "lagged wetness alone, lags 1-3 (best per cell)", 0.693, s1.lag_only.mean(), 3)
    claim("3.4 / 4.3", "drivers alone, lags 0-2 (best per cell)", 0.887, s0.drivers_only.mean(), 3)
    ga = s1.groupby("aridity_class", observed=True).driver_gain.mean()
    for k, v in zip(ARID, [.067, .053, .045, .041, .038]):
        claim("3.4", f"driver gain {k}", v, ga[k], 3)
    sp = s1[s1.replication].set_index("name")
    for nm, lo, ld, cl, ex in [("Firozpur", .558, .627, .627, -.001), ("Moga", .593, .657, .664, -.007),
                               ("Hoshiarpur", .682, .735, .734, .001)]:
        claim("Table 4", f"{nm} lag-only", lo, sp.at[nm, "lag_only"], 3)
        claim("Table 4", f"{nm} lag+drivers", ld, sp.at[nm, "lag+drivers"], 3)
        claim("Table 4", f"{nm} ceiling", cl, sp.at[nm, "ceil_lin_raw"], 3)
        claim("Table 4", f"{nm} exceedance", ex, sp.at[nm, "above_ceiling"], 3)

    # ---------------- 3.5 / 4.5 / 4.6 exceedance and shortfall ----------------
    t["exceed"] = t.nse - t.ceil_lin_raw
    over = t.exceed > 0
    claim("3.5", "cells above linear ceiling (Stage C best)", 49, over.sum(), kind="int")
    claim("3.5", "max exceedance", 0.038, t.exceed.max(), 3)
    claim("3.5", "mean exceedance of over-cells", 0.012, t.loc[over, "exceed"].mean(), 3)
    re_, pe_ = stats.pearsonr(t.seas_share, t.exceed)
    claim("3.5", "corr(seas_share, exceedance)", 0.741, re_, 3)
    claim("3.5", "p of that corr", 1e-44, pe_, 0, kind="p")
    claim("3.5", "mean seas_share over-cells", 0.768, t.loc[over, "seas_share"].mean(), 3)
    claim("3.5", "mean seas_share other cells", 0.475, t.loc[~over, "seas_share"].mean(), 3)
    claim("3.5 / 4.5", "over-cells won by nonlinear models", 34, (~t.loc[over, "model"].isin(FLOORS)).sum(), kind="int")
    claim("3.5", "over-cells won by OLS (AR12)", 13, (t.loc[over, "model"] == "AR12").sum(), kind="int")
    claim("3.5", "over-cells won by climatology", 2, (t.loc[over, "model"] == "Climatology").sum(), kind="int")
    claim("3.5", "non-exceeding cells", 200, (~over).sum(), kind="int")
    claim("3.5", "AR12 wins among non-exceeding", 147, (t.loc[~over, "model"] == "AR12").sum(), kind="int")
    clim = res[res.model == "Climatology"].groupby("cell_id").nse.mean().rename("clim").reset_index().merge(ce, on="cell_id")
    claim("3.5", "cells where climatology exceeds the ceiling", 5, (clim.clim > clim.ceil_lin_raw).sum(), kind="int")
    claim("3.5", "of which climatology wins outright", 2, ((t.model == "Climatology") & over).sum(), kind="int")
    sh = t.exceed < -0.20
    claim("4.6", "cells > 0.20 below ceiling", 12, sh.sum(), kind="int")
    claim("4.6", "worst shortfall", 0.430, -t.exceed.min(), 3)
    claim("4.6", "mean seas_share of shortfall cells", 0.157, t.loc[sh, "seas_share"].mean(), 3)
    claim("4.6", "mean seas_share of panel", 0.532, t.seas_share.mean(), 3)
    claim("4.6", "shortfall cells: sample entropy below panel mean", 1, int(t.loc[sh, "sampen_des"].mean() < t.sampen_des.mean()), kind="int")
    claim("Fig 3", "model-class means above their class ceiling", 0,
          int((res.merge(ce[["cell_id", "aridity_class"]], on="cell_id")
               .groupby(["aridity_class", "model"], observed=True).nse.mean().unstack()
               .gt(ce.groupby("aridity_class", observed=True).ceil_lin_raw.mean(), axis=0)).sum().sum()), kind="int")

    # ---------------- report ----------------
    df = pd.DataFrame(rows)
    bad = df[~df.ok]
    lines = ["# Manuscript number audit", "",
             f"{len(df)} numeric claims recomputed from the archived outputs: "
             f"**{int(df.ok.sum())} match, {len(bad)} do not.**", "",
             "| Section | Claim | Paper | Recomputed | | Note |", "|---|---|---|---|---|---|"]
    for r in df.itertuples():
        lines.append(f"| {r.section} | {r.claim} | {r.paper} | {r.recomputed} | {'OK' if r.ok else '**MISMATCH**'} | {r.note} |")
    report.write_text("\n".join(lines) + "\n")
    print(f"{len(df)} claims | {int(df.ok.sum())} match | {len(bad)} mismatch")
    if len(bad):
        print(bad[["section", "claim", "paper", "recomputed"]].to_string(index=False))
    return len(bad)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("data"))
    ap.add_argument("--report", type=Path, default=Path("VERIFICATION_numbers.md"))
    a = ap.parse_args()
    sys.exit(main(a.data, a.report))

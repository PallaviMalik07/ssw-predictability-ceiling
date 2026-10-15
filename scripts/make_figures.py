"""Render Figures 1-6 of the paper at 300 dpi from the result tables in data/.

Usage:  python scripts/make_figures.py [--data data] [--out figures]

Inputs (produced by the pipeline notebook, see data/README.md):
  panel_global.parquet, stageB_ceilings.parquet, stageC_all_results.parquet,
  stageD_summary_lag0.parquet, stageD_summary_lag1.parquet
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ARIDITY_ORDER = ["hyperarid", "arid", "semiarid", "dry-subhumid", "humid"]
FLOORS = ["Climatology", "Persistence", "SeasonalNaive", "AR12"]


def load(data: Path):
    need = ["stageB_ceilings.parquet", "stageC_all_results.parquet", "panel_global.parquet",
            "stageD_summary_lag1.parquet", "stageD_summary_lag0.parquet"]
    missing = [f for f in need if not (data / f).exists()]
    if missing:
        raise SystemExit(f"Missing in {data}/: {', '.join(missing)}")
    return [pd.read_parquet(data / f) for f in need]


def main(data: Path, fig: Path):
    fig.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "font.family": "serif",
                         "savefig.bbox": "tight", "savefig.dpi": 300})
    ceil, res, pan, sd1, sd0 = load(data)

    # Fig 1 - global panel
    cl = ceil.merge(pan[["cell_id", "lat", "lon"]], on="cell_id")
    f, a = plt.subplots(figsize=(7.2, 3.6))
    sc = a.scatter(cl.lon, cl.lat, c=cl.AI, s=14 + 90 * cl.irrig_index.fillna(0), cmap="BrBG",
                   vmin=0, vmax=1.5, edgecolor="k", linewidth=.3)
    plt.colorbar(sc, label="aridity index $P/PET$")
    a.set_xlabel("longitude (°E)"); a.set_ylabel("latitude (°N)")
    a.set_xlim(-180, 180); a.set_ylim(-60, 80)
    f.savefig(fig / "fig1_global_panel.png"); plt.close(f)

    # Fig 2 - ceiling vs best achieved NSE
    best = res.groupby(["cell_id", "model"]).nse.mean().reset_index()
    top = best.loc[best.groupby("cell_id").nse.idxmax()].merge(ceil, on="cell_id")
    f, a = plt.subplots(figsize=(4.0, 3.8))
    for c_, g in top.groupby("aridity_class", observed=True):
        a.scatter(g.ceil_lin_raw, g.nse, s=13, label=c_, alpha=.85)
    a.plot([0, 1], [0, 1], "k--", lw=1, label="1:1")
    a.set_xlabel("linear predictability ceiling"); a.set_ylabel("best achieved NSE")
    a.legend(fontsize=7, frameon=False)
    f.savefig(fig / "fig2_ceiling_vs_achieved.png"); plt.close(f)

    # Fig 3 - benchmark ladder by aridity class
    order = res.groupby("model").nse.mean().sort_values().index.tolist()
    sub = res.merge(ceil[["cell_id", "aridity_class"]], on="cell_id")
    f, a = plt.subplots(figsize=(6.0, 3.6))
    for c_ in [x for x in ARIDITY_ORDER if x in sub.aridity_class.unique()]:
        m_ = sub[sub.aridity_class == c_].groupby("model").nse.mean().reindex(order)
        a.plot(range(len(order)), m_.values, "o-", ms=3.5, lw=1.1, label=c_)
        a.axhline(ceil[ceil.aridity_class == c_].ceil_lin_raw.mean(), ls=":", lw=.8,
                  color=a.lines[-1].get_color())
    a.set_xticks(range(len(order))); a.set_xticklabels(order, rotation=40, ha="right")
    a.set_ylabel("mean NSE")
    a.legend(fontsize=7, frameon=False, title="dotted = class ceiling", title_fontsize=7)
    f.savefig(fig / "fig3_ladder.png"); plt.close(f)

    # Fig 4 - seed vs between-model dispersion (density)
    ml = res[~res.model.isin(FLOORS)]
    seed_sd = ml.groupby(["cell_id", "fold", "model"]).nse.std().dropna()
    betw_sd = (ml.groupby(["cell_id", "fold", "model"]).nse.mean()
                 .groupby(level=["cell_id", "fold"]).std().dropna())
    f, a = plt.subplots(figsize=(4.4, 3.4))
    bins = np.linspace(0, 0.35, 60)
    a.hist(seed_sd, bins=bins, density=True, alpha=.6,
           label=f"within-model, across seeds (med {seed_sd.median():.4f})")
    a.hist(betw_sd, bins=bins, density=True, alpha=.6,
           label=f"between-model (med {betw_sd.median():.4f})")
    a.axvline(seed_sd.median(), color="C0", ls="--", lw=1)
    a.axvline(betw_sd.median(), color="C1", ls="--", lw=1)
    a.set_xlabel("s.d. of NSE"); a.set_ylabel("density"); a.legend(fontsize=7, frameon=False)
    f.savefig(fig / "fig4_seed_vs_model.png"); plt.close(f)

    # Fig 5 - driver gain vs deseasonalised ACF1, both lag structures
    f, axes = plt.subplots(1, 2, figsize=(7.0, 3.3), sharey=True)
    for ax, s_, ttl in [(axes[0], sd0, "(a) drivers incl. concurrent month"),
                        (axes[1], sd1, "(b) drivers lagged 1–3 months")]:
        for c_, g in s_.groupby("irrig_class", observed=True):
            ax.scatter(g.acf1_des, g.driver_gain, s=12, label=c_, alpha=.8)
        x, y = s_.acf1_des.astype(float), s_.driver_gain.astype(float)
        ok = x.notna() & y.notna()
        sl, ic, r_, p_, _ = stats.linregress(x[ok], y[ok])
        xx = np.linspace(x[ok].min(), x[ok].max(), 50)
        ax.plot(xx, sl * xx + ic, "k-", lw=1.1, label=f"r = {r_:.2f}")
        ax.axhline(0, color="grey", lw=.7)
        ax.set_xlabel("deseasonalised lag-1 autocorrelation")
        ax.set_title(ttl, fontsize=8.5); ax.legend(fontsize=6.5, frameon=False)
    axes[0].set_ylabel("NSE gain from drivers")
    f.savefig(fig / "fig5_driver_gain_both.png"); plt.close(f)

    # Fig 6 - ceiling exceedance, forecast-realistic configuration
    f, a = plt.subplots(figsize=(4.4, 3.4))
    s_ = sd1.sort_values("above_ceiling")
    a.barh(range(len(s_)), s_.above_ceiling,
           color=["#b2434a" if v < 0 else "#3d6d9e" for v in s_.above_ceiling], height=1.0)
    a.axvline(0, color="k", lw=.9)
    a.set_xlabel("NSE with lagged drivers  −  lag-only ceiling")
    a.set_ylabel(f"cells (n = {len(s_)}, sorted)"); a.set_yticks([])
    f.savefig(fig / "fig6_exceedance.png"); plt.close(f)

    for p in sorted(fig.glob("fig*.png")):
        print(f"{p.name:32s} {p.stat().st_size // 1024:5d} KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", type=Path, default=Path("data"))
    ap.add_argument("--out", type=Path, default=Path("figures"))
    a = ap.parse_args()
    main(a.data, a.out)

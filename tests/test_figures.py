"""Smoke test: scripts/make_figures.py renders all six figures from tables with the expected schema."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.make_figures import main as make_figures  # noqa: E402


def test_make_figures_on_synthetic_tables(tmp_path):
    rng = np.random.default_rng(0); n = 30; ids = [f"c{i}" for i in range(n)]
    ar = ["hyperarid", "arid", "semiarid", "dry-subhumid", "humid"]
    d = tmp_path / "data"; d.mkdir()
    pd.DataFrame(dict(cell_id=ids, lat=rng.uniform(-55, 64, n), lon=rng.uniform(-180, 180, n))).to_parquet(d / "panel_global.parquet")
    pd.DataFrame(dict(cell_id=ids, AI=rng.uniform(0, 2.8, n), irrig_index=rng.uniform(0, .7, n),
                      aridity_class=[ar[i % 5] for i in range(n)], ceil_lin_raw=rng.uniform(.3, .95, n))).to_parquet(d / "stageB_ceilings.parquet")
    rows = [(c, f, m, s, rng.uniform(0, 1)) for c in ids for f in range(5) for m in ["AR12", "RF", "XGBoost", "Persistence"] for s in range(5)]
    pd.DataFrame(rows, columns=["cell_id", "fold", "model", "seed", "nse"]).to_parquet(d / "stageC_all_results.parquet")
    for k in ["lag0", "lag1"]:
        pd.DataFrame(dict(cell_id=ids, irrig_class=["low", "med", "high"] * 10, acf1_des=rng.uniform(.37, .95, n),
                          driver_gain=rng.normal(.05, .03, n), above_ceiling=rng.normal(0, .03, n))).to_parquet(d / f"stageD_summary_{k}.parquet")
    make_figures(d, tmp_path / "figs")
    assert sorted(p.name for p in (tmp_path / "figs").glob("*.png")) == [
        "fig1_global_panel.png", "fig2_ceiling_vs_achieved.png", "fig3_ladder.png",
        "fig4_seed_vs_model.png", "fig5_driver_gain_both.png", "fig6_exceedance.png"]

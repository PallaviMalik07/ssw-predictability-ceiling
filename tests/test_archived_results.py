"""Regression tests against the archived pipeline outputs (skipped if data/ lacks them).

These pin the paper's headline numbers to the result tables; the full claim-by-claim audit
is scripts/verify_paper_numbers.py.
"""
import numpy as np
import pandas as pd
from scipy import stats


def test_panel_and_table_integrity(data_dir):
    pan = pd.read_parquet(data_dir / "panel_global.parquet")
    mon = pd.read_parquet(data_dir / "power_monthly_panel.parquet")
    res = pd.read_parquet(data_dir / "stageC_all_results.parquet")
    ce = pd.read_parquet(data_dir / "stageB_ceilings.parquet")
    assert len(pan) == 249 and pan.cell_id.is_unique
    assert set(mon.cell_id) == set(pan.cell_id) == set(res.cell_id) == set(ce.cell_id)
    assert (mon.groupby("cell_id").size() == 504).all()
    assert mon.GWETTOP.between(0, 1).all()
    assert np.isfinite(res.nse).all() and sorted(res.seed.unique()) == [0, 1, 2, 3, 4]
    for c in ["ceil_lin_raw", "ceil_lin_des", "ceil_mi_raw", "ceil_mi_des"]:
        assert ce[c].between(0, 1).all()
    assert np.isfinite(ce[["mi_raw", "mi_des"]]).all().all()


def test_table2_headline(data_dir):
    res = pd.read_parquet(data_dir / "stageC_all_results.parquet")
    m = res.groupby("model").nse.mean().round(3)
    assert m.idxmax() == "AR12"
    expected = {"AR12": .687, "RF": .662, "AdaBoost-CART": .650, "ESN": .634, "XGBoost": .633,
                "LightGBM": .616, "Persistence": .490, "Climatology": .354, "CART": .348, "SeasonalNaive": .125}
    assert m.to_dict() == expected
    b = res.groupby(["cell_id", "model"]).nse.mean().reset_index()
    assert (b.loc[b.groupby("cell_id").nse.idxmax()].model == "AR12").sum() == 160


def test_ceiling_and_stageD_headline(data_dir):
    ce = pd.read_parquet(data_dir / "stageB_ceilings.parquet")
    s1 = pd.read_parquet(data_dir / "stageD_summary_lag1.parquet")
    s0 = pd.read_parquet(data_dir / "stageD_summary_lag0.parquet")
    assert round(ce.ceil_lin_raw.mean(), 3) == 0.751
    assert round(ce[["ceil_mi_raw", "ceil_lin_raw"]].corr().iloc[0, 1], 3) == 0.937
    assert round(s1.driver_gain.mean(), 3) == 0.047 and int((s1.above_ceiling > 0).sum()) == 137
    assert round(s0.driver_gain.mean(), 3) == 0.238 and int((s0.above_ceiling > 0).sum()) == 246
    assert stats.wilcoxon(s1["lag+drivers"], s1.lag_only)[1] < 1e-38

"""Re-execute the pipeline notebook's own cells and compare against the archived outputs.

Usage:
  python scripts/rerun_check.py --archive data [--cells N] [--work /tmp/ssw_rerun]

What it does, using the cell code exactly as it stands in notebooks/ssw_global_pipeline.ipynb:
  1. Cell 3 on the archived daily POWER download -> monthly panel + Stage A, ALL cells
  2. Cell 4 linear ceilings, ALL cells (KSG is verified separately: it needs the full
     sequential run, ~3 min; pass --full-mi to include it)
  3. Cells 5, 6, 7, 7b (Stage C ladder, ESN, Stage D lag 1-3 and lag 0-2) retrained from
     scratch on a sample of cells: the 3 Punjab replication sites plus one cell from each
     aridity class, compared per (cell, fold, model, seed) with the archived checkpoints.
Cell 2 (the POWER download) is not re-run: it needs network access to power.larc.nasa.gov.
"""
import argparse
import contextlib
import io
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

NB = Path(__file__).resolve().parents[1] / "notebooks" / "ssw_global_pipeline.ipynb"


def cells():
    nb = json.loads(NB.read_text())
    out = {}
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        s = "".join(c["source"])
        for key, marker in [("c3", "AGG = {"), ("c4", "def ceiling_linear"), ("c5", "def make_models"),
                            ("c6", "class ESN"), ("c7", "def run_stageD"), ("c7b", "d0,sd0 = run_stageD")]:
            if marker in s:
                out[key] = s
    return out


def run(src, ns, quiet=True):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(src, ns)
    return buf.getvalue()


def compare(new, old, keys, col="nse"):
    m = new.merge(old, on=keys, suffixes=("_new", "_old"))
    d = (m[f"{col}_new"] - m[f"{col}_old"]).abs()
    return len(new), len(old), len(m), float(d.max()) if len(d) else np.nan, m.assign(diff=d)


def main(A: Path, W: Path, n_extra: int, full_mi: bool, resume: bool = False):
    C = cells()
    if W.exists() and not resume:
        shutil.rmtree(W)
    (W / "data").mkdir(parents=True, exist_ok=True)
    OUT = W / "data"
    for f in ["power_daily_panel.parquet", "panel_global.parquet"]:
        shutil.copy(A / f, OUT / f)
    report = []

    # 1. Cell 3 on all cells ---------------------------------------------------
    from scipy import stats   # imported by notebook Cell 1, which this harness does not run
    ns = {"OUT": OUT, "Path": Path, "stats": stats}
    t0 = time.time(); run("import numpy as np, pandas as pd\n" + C["c3"], ns)
    mon_new = pd.read_parquet(OUT / "power_monthly_panel.parquet")
    mon_old = pd.read_parquet(A / "power_monthly_panel.parquet")
    k = ["cell_id", "month"]
    m = mon_new.merge(mon_old, on=k, suffixes=("", "_o"))
    cols = [c for c in mon_old.columns if c not in k + ["name"]]
    dmax = max(float((m[c] - m[f"{c}_o"]).abs().max()) for c in cols)
    report.append(("Cell 3: monthly aggregation (all cells, 12 variables)",
                   f"{mon_new.cell_id.nunique()} cells / {len(mon_new)} rows vs archived {mon_old.cell_id.nunique()} / {len(mon_old)}",
                   dmax, time.time() - t0))
    dg_new = pd.read_parquet(OUT / "stageA_diagnostics.parquet")
    dg_old = pd.read_parquet(A / "stageA_diagnostics.parquet")
    dm = dg_new.merge(dg_old, on="cell_id", suffixes=("", "_o"))
    sa = ["seas_share", "acf1_raw", "acf12_raw", "acf1_des", "acf2_des", "acf12_des", "pacf1_des", "sampen_des"]
    report.append(("Cell 3: Stage A diagnostics (all cells, 8 statistics)",
                   f"{len(dg_new)} vs {len(dg_old)} cells",
                   max(float((dm[c] - dm[f"{c}_o"]).abs().max()) for c in sa), 0.0))

    # 2. Cell 4 ----------------------------------------------------------------
    t0 = time.time()
    c4 = C["c4"]
    if not full_mi:   # linear ceilings only: stop before the KSG loop, then compute ceilings directly
        c4 = c4[:c4.index("rows = []")]
        run(c4, ns)
        mon = pd.read_parquet(OUT / "power_monthly_panel.parquet")
        lin = []
        for cid, gg in mon.groupby("cell_id"):
            y = gg.sort_values("month").GWETTOP.to_numpy(float)
            lin.append(dict(cell_id=cid, ceil_lin_raw=ns["ceiling_linear"](y),
                            ceil_lin_des=ns["ceiling_linear"](ns["deseason"](y))))
        ce_new = pd.DataFrame(lin)
        shutil.copy(A / "stageB_ceilings.parquet", OUT / "stageB_ceilings.parquet")  # downstream input
        what = "Cell 4: linear ceilings raw + deseasonalised (all cells)"
        cc = ["ceil_lin_raw", "ceil_lin_des"]
    else:
        run(c4, ns)
        ce_new = pd.read_parquet(OUT / "stageB_ceilings.parquet")
        what = "Cell 4: linear ceilings + KSG MI bounds (all cells, full sequential run)"
        cc = ["ceil_lin_raw", "ceil_lin_des", "mi_raw", "mi_des", "ceil_mi_raw", "ceil_mi_des"]
    ce_old = pd.read_parquet(A / "stageB_ceilings.parquet")
    cm = ce_new.merge(ce_old, on="cell_id", suffixes=("", "_o"))
    report.append((what, f"{len(ce_new)} vs {len(ce_old)} cells",
                   max(float((cm[c] - cm[f"{c}_o"]).abs().max()) for c in cc), time.time() - t0))

    # 3. Cells 5, 6, 7, 7b on a sample ----------------------------------------
    ce = pd.read_parquet(A / "stageB_ceilings.parquet")
    pick = list(ce[ce.replication].cell_id)
    for k_ in ["hyperarid", "semiarid", "humid", "arid", "dry-subhumid"][:n_extra]:
        pick.append(ce[(ce.aridity_class == k_) & ~ce.replication].sort_values("cell_id").cell_id.iloc[0])
    mon = pd.read_parquet(OUT / "power_monthly_panel.parquet")
    mon[mon.cell_id.isin(pick)].to_parquet(OUT / "power_monthly_panel.parquet", index=False)
    pd.read_parquet(A / "stageB_ceilings.parquet").to_parquet(OUT / "stageB_ceilings.parquet", index=False)

    t0 = time.time(); run(C["c5"], ns)
    new = pd.concat([pd.read_parquet(f) for f in (OUT / "stageC_ck").glob("*.parquet")])
    old = pd.concat([pd.read_parquet(A / "stageC_ck" / f"{c}.parquet") for c in pick])
    r5 = compare(new, old, ["cell_id", "fold", "model", "seed"])
    report.append((f"Cell 5: Stage C ladder retrained ({len(pick)} cells, 9 models, 5 seeds)",
                   f"{r5[0]} fits vs {r5[1]} archived, {r5[2]} matched", r5[3], time.time() - t0))

    t0 = time.time(); run(C["c6"], ns)
    new = pd.concat([pd.read_parquet(f) for f in (OUT / "stageE_ck").glob("*.parquet")])
    old = pd.concat([pd.read_parquet(A / "stageE_ck" / f"{c}.parquet") for c in pick])
    r6 = compare(new, old, ["cell_id", "fold", "model", "seed"])
    report.append((f"Cell 6: ESN retrained ({len(pick)} cells, 5 seeds)",
                   f"{r6[0]} fits vs {r6[1]} archived, {r6[2]} matched", r6[3], time.time() - t0))

    t0 = time.time(); run(C["c7"], ns)
    new = pd.concat([pd.read_parquet(f) for f in (OUT / "stageD_ck_lag1").glob("*.parquet")])
    old = pd.concat([pd.read_parquet(A / "stageD_ck_lag1" / f"{c}.parquet") for c in pick])
    r7 = compare(new, old, ["cell_id", "fold", "inputs", "model", "seed"])
    report.append((f"Cell 7: Stage D lags 1-3 retrained ({len(pick)} cells)",
                   f"{r7[0]} fits vs {r7[1]} archived, {r7[2]} matched", r7[3], time.time() - t0))

    t0 = time.time(); run(C["c7b"], ns)
    new = pd.concat([pd.read_parquet(f) for f in (OUT / "stageD_ck_lag0").glob("*.parquet")])
    old = pd.concat([pd.read_parquet(A / "stageD_ck_lag0" / f"{c}.parquet") for c in pick])
    r7b = compare(new, old, ["cell_id", "fold", "inputs", "model", "seed"])
    report.append((f"Cell 7b: Stage D lags 0-2 retrained ({len(pick)} cells)",
                   f"{r7b[0]} fits vs {r7b[1]} archived, {r7b[2]} matched", r7b[3], time.time() - t0))

    # per-model detail for the retrained stages
    detail = []
    for tag, r in [("Stage C", r5), ("ESN", r6), ("Stage D lag1", r7), ("Stage D lag0", r7b)]:
        g = r[4].groupby("model")["diff"].max()
        detail += [(tag, mdl, v) for mdl, v in g.items()]

    print("\nRE-EXECUTION CHECK  (max abs. difference vs archived, NSE or value)\n")
    for what, n, d, sec in report:
        print(f"  {what}\n      {n} | max |diff| = {d:.2e} | {sec:.0f}s")
    print("\n  per model:")
    for tag, mdl, v in detail:
        print(f"    {tag:13s} {mdl:15s} {v:.2e}")
    print("\n  sample cells:", pick)
    return report, detail, pick


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, default=Path("data"))
    ap.add_argument("--work", type=Path, default=Path("/tmp/ssw_rerun"))
    ap.add_argument("--cells", type=int, default=3, help="extra non-Punjab cells (one per aridity class)")
    ap.add_argument("--full-mi", action="store_true")
    ap.add_argument("--resume", action="store_true", help="keep checkpoints from an earlier run in --work")
    a = ap.parse_args()
    main(a.archive, a.work, a.cells, a.full_mi, a.resume)

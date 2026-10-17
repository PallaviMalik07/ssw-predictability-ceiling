"""Load function/class definitions straight from the pipeline notebook, so tests exercise the
exact code that produced the paper (no second copy to drift out of sync)."""
import ast
import json
import re
from pathlib import Path

NB = Path(__file__).resolve().parents[1] / "notebooks" / "ssw_global_pipeline.ipynb"
KEEP_ASSIGN = {"LAGS", "LAGS_LIN", "LAGS_MI", "N_FOLDS", "TEST_LEN", "SEEDS", "rng_j"}


def load():
    ns = {}
    nb = json.loads(NB.read_text())
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "\n".join(l for l in "".join(c["source"]).splitlines() if not re.match(r"\s*(!|%[a-zA-Z])", l))
        tree = ast.parse(src)
        keep = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
                keep.append(node)
            elif isinstance(node, ast.Assign):
                names = {t.id for t in node.targets if isinstance(t, ast.Name)}
                names |= {e.id for t in node.targets if isinstance(t, ast.Tuple) for e in t.elts if isinstance(e, ast.Name)}
                if names & KEEP_ASSIGN:
                    keep.append(node)
        mod = ast.Module(body=keep, type_ignores=[])
        try:
            exec(compile(mod, str(NB), "exec"), ns)
        except ImportError:   # optional deps (google.colab, chronos) - skip that cell's imports
            for node in keep:
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    exec(compile(ast.Module(body=[node], type_ignores=[]), str(NB), "exec"), ns)
    return ns

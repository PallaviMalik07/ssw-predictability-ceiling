import os
from pathlib import Path

import pytest

from _nb import load

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def nb():
    return load()


@pytest.fixture(scope="session")
def data_dir():
    d = Path(os.environ.get("SSW_DATA", ROOT / "data"))
    if not (d / "stageC_all_results.parquet").exists():
        pytest.skip(f"archived pipeline outputs not found in {d} (set SSW_DATA)")
    return d

"""Colab helpers: archive data/ for download, and restore it from an uploaded zip.

Colab runtimes recycle and wipe local files; every heavy pipeline stage checkpoints per
grid cell, and these helpers move data/ (including checkpoint folders) in and out.

    from scripts.colab_io import backup, restore
    backup("ssw_global_complete")   # zips data/ and downloads it
    restore()                       # upload a zip, unpack into data/, report key files
"""
import shutil
import zipfile
from pathlib import Path

OUT = Path("data")
KEY_FILES = ["panel_global.parquet", "power_monthly_panel.parquet", "stageB_ceilings.parquet",
             "stageC_all_results.parquet", "stageD_summary_lag1.parquet",
             "stageD_summary_lag0.parquet"]


def backup(name: str = "ssw_global_complete") -> str:
    path = shutil.make_archive(name, "zip", OUT)
    try:
        from google.colab import files
        files.download(path)
    except ImportError:
        pass
    return path


def report() -> None:
    print("--- data/ ---")
    for p in sorted(OUT.glob("*")):
        print(f"  {p.name}/ ({len(list(p.glob('*')))} files)" if p.is_dir()
              else f"  {p.name}  {p.stat().st_size // 1024} KB")
    print("\nkey files present:")
    for f in KEY_FILES:
        print(f"  {'OK     ' if (OUT / f).exists() else 'MISSING'} {f}")


def restore() -> None:
    from google.colab import files
    OUT.mkdir(exist_ok=True)
    for name in files.upload():
        if name.lower().endswith(".zip"):
            with zipfile.ZipFile(name) as z:
                z.extractall(OUT)
            print(f"unpacked {name}")
    report()

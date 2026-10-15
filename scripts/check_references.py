"""Resolve every DOI cited in the paper against Crossref / DataCite and print title metadata."""
import requests

CROSSREF = ["10.1038/sdata.2017.191", "10.1175/JCLI-D-16-0758.1", "10.1016/j.rse.2017.06.031",
            "10.1038/s41598-026-50687-9", "10.1103/PhysRevE.69.066138",
            "10.1016/0022-1694(70)90255-6", "10.1016/j.earscirev.2010.02.004",
            "10.1016/j.rse.2018.12.013"]
DATACITE = ["10.5067/MODIS/MCD12Q1.006"]

for d in CROSSREF:
    try:
        r = requests.get(f"https://api.crossref.org/works/{d}", timeout=15)
        if r.ok:
            m = r.json()["message"]
            yr = m.get("issued", {}).get("date-parts", [["?"]])[0][0]
            print(f"OK   {d}\n     {m.get('container-title', [''])[0]} {m.get('volume', '')} ({yr})")
        else:
            print(f"FAIL {d}  HTTP {r.status_code}")
    except Exception as e:
        print(f"ERR  {d}  {e}")

for d in DATACITE:
    try:
        r = requests.get(f"https://api.datacite.org/dois/{d}", timeout=15)
        if r.ok:
            a = r.json()["data"]["attributes"]
            print(f"OK   {d}\n     {a.get('titles', [{}])[0].get('title')} | {a.get('publisher')} {a.get('publicationYear')}")
        else:
            print(f"FAIL {d}  HTTP {r.status_code}")
    except Exception as e:
        print(f"ERR  {d}  {e}")

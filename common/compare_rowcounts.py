#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def rows(dbms):
    d = {}
    with open(ROOT / "results" / dbms / "results.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["param_idx"] == "0" and r["rep"] == "0" and r["variant"] == "idx" and r.get("run", "1") == "1":
                d[(r["scale"], r["query"])] = int(r["rows"])
    return d


a, b = (rows(x) for x in sys.argv[1:3])
bad = 0
for k in sorted(set(a) & set(b)):
    if a[k] != b[k]:
        bad += 1
        print(f"ROZBIEŻNOŚĆ skala={k[0]} {k[1]}: {sys.argv[1]}={a[k]} {sys.argv[2]}={b[k]}")
print("OK - wszystkie zgodne" if not bad else f"{bad} rozbieżności")

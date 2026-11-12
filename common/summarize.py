#!/usr/bin/env python3
import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def summarize(dbms):
    samples = defaultdict(list)
    units = defaultdict(lambda: defaultdict(list))
    timeouts = defaultdict(int)
    with open(ROOT / "results" / dbms / "results.csv", newline="") as f:
        for r in csv.DictReader(f):
            k = (int(r["scale"]), r["variant"], r["query"])
            t = float(r["time_ms"])
            samples[k].append(t)
            units[k][(r.get("run", "1"), r["param_idx"])].append(t)
            if r["rows"] == "-1":
                timeouts[k] += 1
    out = ROOT / "results" / dbms / "summary.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scale", "variant", "query", "n", "samples", "mean_ms", "sd_ms", "ci95_ms",
                    "median_ms", "p95_ms", "run_spread_pct", "runmed_ms", "timeouts"])
        for k in sorted(samples):
            s = sorted(samples[k])
            u = [statistics.mean(v) for v in units[k].values()]
            sd = statistics.stdev(u) if len(u) > 1 else 0.0
            mean = statistics.mean(u)
            runs = defaultdict(list)
            for (run, _), v in units[k].items():
                runs[run].append(statistics.mean(v))
            rm = [statistics.mean(v) for v in runs.values()]
            spread = (max(rm) - min(rm)) / mean * 100 if len(rm) > 1 and mean else 0.0
            w.writerow([k[0], k[1], k[2], len(u), len(s), f"{mean:.3f}", f"{sd:.3f}",
                        f"{1.96 * sd / math.sqrt(len(u)):.3f}", f"{statistics.median(s):.3f}",
                        f"{s[min(len(s) - 1, int(0.95 * len(s)))]:.3f}", f"{spread:.1f}", f"{statistics.median(rm):.3f}", timeouts[k]])
    print("->", out)


if __name__ == "__main__":
    for d in (sys.argv[1:] or ["postgres"]):
        summarize(d)

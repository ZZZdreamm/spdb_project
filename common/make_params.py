#!/usr/bin/env python3
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
N, SEED = 20, 42
BUILT_UP = {"residential", "commercial", "industrial", "retail"}
csv.field_size_limit(sys.maxsize)


def square(cx, cy, side):
    h = side / 2
    pts = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h), (cx - h, cy - h)]
    return "POLYGON ((" + ", ".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "))"


def first_ring_area(wkt):
    m = re.search(r"\(\(+([^()]+)\)", wkt)
    if not m:
        return 0.0
    pts = [tuple(map(float, p.split()[:2])) for p in m.group(1).split(",")]
    s = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    return abs(s) / 2


def main():
    rnd = random.Random(SEED)
    pois = []
    with open(PROC / "pois.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            m = re.match(r"POINT \(([-\d.e+]+) ([-\d.e+]+)\)", r["wkt"])
            if m:
                pois.append((float(m.group(1)), float(m.group(2))))
    containers = []
    with open(PROC / "areas.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "landuse" and r["subtype"] in BUILT_UP and 300_000 <= first_ring_area(r["wkt"]) <= 5_000_000 \
                    and r["wkt"].startswith(("POLYGON", "MULTIPOLYGON")):
                containers.append(r["wkt"])
    if not containers:
        sys.exit("brak obszarów zabudowa 0,3-5 km2 - zmień zakres w make_params.py")

    sets = []
    for _ in range(N):
        px, py = rnd.choice(pois)
        cx, cy = rnd.choice(pois)
        ang_x, ang_y = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        norm = (ang_x ** 2 + ang_y ** 2) ** 0.5 or 1
        ex, ey = px + 500 * ang_x / norm, py + 500 * ang_y / norm
        sets.append({
            "px": round(px, 2), "py": round(py, 2),
            "wkt_seg": f"LINESTRING ({px:.2f} {py:.2f}, {ex:.2f} {ey:.2f})",
            "wkt_rect_small": square(cx, cy, 1000),
            "wkt_rect_big": square(cx, cy, 4000),
            "wkt_container": rnd.choice(containers),
            "category": "restaurant", "k": 10, "radius": 500,
        })
    out = ROOT / "params" / "params.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(sets, indent=1))
    print(f"zapisano {len(sets)} zestawów -> {out}")


if __name__ == "__main__":
    main()

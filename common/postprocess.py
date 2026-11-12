#!/usr/bin/env python3
import csv
import hashlib
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
csv.field_size_limit(sys.maxsize)


def bucket(osm_id: str) -> int:
    return zlib.crc32(osm_id.encode()) % 100


def convert(name, header, mapper):
    n = 0
    with open(RAW / f"{name}.csv", newline="", encoding="utf-8") as fin, \
         open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as fout:
        w = csv.writer(fout)
        w.writerow(["id", "bucket"] + header + ["wkt"])
        for r in csv.DictReader(fin):
            wkt = r["WKT"].strip()
            if not wkt:
                continue
            attrs, osm_id = mapper(r)
            if not osm_id:
                continue
            n += 1
            w.writerow([n, bucket(osm_id)] + attrs + [wkt])
    return n


def area_map(r):
    for kind in ("building", "landuse", "leisure", "natural_"):
        if r[kind]:
            return [r["name"], kind.rstrip("_"), r[kind]], (r["osm_id"] or r["osm_way_id"])
    return None, None


def main():
    counts = {
        "pois": convert("pois", ["osm_id", "name", "category"],
                        lambda r: ([r["osm_id"], r["name"], r["amenity"]], r["osm_id"])),
        "roads": convert("roads", ["osm_id", "name", "highway"],
                         lambda r: ([r["osm_id"], r["name"], r["highway"]], r["osm_id"])),
    }
    n = 0
    with open(RAW / "areas.csv", newline="", encoding="utf-8") as fin, \
         open(OUT / "areas.csv", "w", newline="", encoding="utf-8") as fout:
        w = csv.writer(fout)
        w.writerow(["id", "bucket", "osm_id", "name", "kind", "subtype", "wkt"])
        for r in csv.DictReader(fin):
            wkt = r["WKT"].strip()
            attrs, osm_id = area_map(r)
            if not wkt or not osm_id:
                continue
            n += 1
            w.writerow([n, bucket(osm_id), osm_id, attrs[0], attrs[1], attrs[2], wkt])
    counts["areas"] = n

    with open(OUT / "MANIFEST.txt", "w") as m:
        for t, c in counts.items():
            h = hashlib.sha256((OUT / f"{t}.csv").read_bytes()).hexdigest()
            m.write(f"{t}.csv rows={c} sha256={h}\n")
    print((OUT / "MANIFEST.txt").read_text())


if __name__ == "__main__":
    main()

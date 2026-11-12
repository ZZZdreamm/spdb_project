#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
DBS = [d for d in ("postgres", "mysql", "mongodb", "cassandra") if (RES / d / "summary.csv").exists()]
NAME = {"postgres": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB", "cassandra": "Cassandra"}
SCALES = [10, 25, 50, 100]
QUERIES = ["Q1a", "Q1b", "Q2a", "Q2b", "Q3a", "Q3b", "Q4a", "Q4b", "Q5a", "Q5b", "Q6", "Q7a", "Q7b", "Q7c"]
QDESC = {"Q1a": "punkt w obszarze", "Q1b": "drogi ≤5 m od punktu", "Q2a": "drogi × odcinek", "Q2b": "obszary × kwadrat 1 km",
         "Q3a": "POI w kwadracie 4 km", "Q3b": "budynki w dużym obszarze", "Q4a": "10 najbliższych (kNN)",
         "Q4b": "POI w promieniu 500 m", "Q5a": "suma pól budynków", "Q5b": "10 największych budynków",
         "Q6": "drogi ≤1 km wg odległości", "Q7a": "korel.: szkoły → restauracje 300 m",
         "Q7b": "korel.: apteki → najbliższa droga", "Q7c": "korel.: join budynki × POI"}

S = {}
for d in DBS:
    with open(RES / d / "summary.csv", newline="") as f:
        for r in csv.DictReader(f):
            S[(d, int(r["scale"]), r["variant"], r["query"])] = {k: (float(v) if k not in ("variant", "query") else v)
                                                                    for k, v in r.items()}


R = "runmed_ms"


def g(d, sc, var, q, key="mean_ms"):
    r = S.get((d, sc, var, q))
    return r[key] if r else None


def fmt(x):
    if x is None:
        return "–"
    return f"{x:,.2f}" if x < 100 else f"{x:,.0f}".replace(",", " ")


def ratio(a, b):
    return None if a is None or b is None or b == 0 else a / b


def fr(x):
    return "–" if x is None else (f"{x:.1f}×" if x >= 10 else f"{x:.2f}×")


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] + ["---:"] * (len(header) - 1)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def qlabel(q):
    return f"**{q}** {QDESC[q]}"


def read(path):
    p = RES / path
    return p.read_text().strip() if p.exists() else ""


md = ["# Zestawienie wyników – wydajność modułów przestrzennych", ""]

any_db = DBS[0]
n_units = {d: S[(d, 100, "idx", "Q1a")]["n"] for d in DBS if (d, 100, "idx", "Q1a") in S}
n_samp = {d: S[(d, 100, "idx", "Q1a")]["samples"] for d in DBS if (d, 100, "idx", "Q1a") in S}
md += ["## 1. Protokół i dane", "",
       "* Dane: OpenStreetMap, Warszawa; skale 10/25/50/100 % (deterministyczne podzbiory), układ EPSG:2180, tylko poprawne geometrie.",
       "* Liczności (POI / drogi / obszary): 10 % – 6 799 / 37 078 / 53 286; 25 % – 17 095 / 91 970 / 134 040; "
       "50 % – 34 367 / 184 454 / 268 102; 100 % – 68 741 / 368 902 / 534 834.",
       "* Każde zapytanie: 20 zestawów parametrów × 3 powtórzenia × N niezależnych przebiegów całości (po 1 przebiegu rozgrzewającym); "
       "wariant bez indeksów: 10 zestawów.",
       "* Podawana średnia = średnia z jednostek (przebieg, zestaw parametrów), „±” = przedział ufności 95 % średniej (1,96·sd/√n). "
       "Duże sd wynika z różnej wielkości wyników dla różnych parametrów, nie z niestabilności pomiaru; "
       "powtarzalność mierzy kolumna „rozrzut przebiegów” w sekcji 6.",
       "* Próbki na zapytanie (skala 100 %): " + ", ".join(f"{NAME[d]} n={n_units[d]:.0f} jednostek ({n_samp[d]:.0f} próbek)" for d in n_units) + ".",
       ""]
for d in DBS:
    e = read(f"{d}/env.txt")
    if e:
        md += [f"**{NAME[d]}:** `" + e.splitlines()[0][:110] + "`  ", ""]

md += ["## 2. Średni czas zapytania [ms] (indeksy podstawowe)", ""]
hdr = ["Zapytanie"] + [f"{NAME[d]} {s}%" for d in DBS for s in SCALES]
rows = []
for q in QUERIES:
    row = [qlabel(q)]
    for d in DBS:
        for s in SCALES:
            m, ci = g(d, s, "idx", q), g(d, s, "idx", q, "ci95_ms")
            row.append("–" if m is None else f"{fmt(m)} ±{fmt(ci)}")
    rows.append(row)
md += [table(hdr, rows), ""]

md += ["### 2b. Estymata odporna: mediana ze średnich poszczególnych przebiegów [ms]", "",
       "Używana w sekcjach 3–5. Odporna na pojedynczy przebieg zakłócony przez inne obciążenie maszyny (WSL2, współdzielony host).", ""]
md += [table(["Zapytanie"] + [f"{NAME[d]} {s}%" for d in DBS for s in SCALES],
             [[qlabel(q)] + [fmt(g(d, s, "idx", q, R)) for d in DBS for s in SCALES] for q in QUERIES]), ""]

if len(DBS) > 1:
    md += ["## 3. Porównanie systemów (stosunek czasów – mediany ze średnich przebiegów; >1 = pierwszy wolniejszy)", ""]
    base = DBS[0]
    others = DBS[1:]
    hdr = ["Zapytanie"] + [f"{NAME[o]}/{NAME[base]} {s}%" for o in others for s in SCALES] + ["szybszy @100 %"]
    rows = []
    for q in QUERIES:
        row = [qlabel(q)]
        for o in others:
            for s in SCALES:
                row.append(fr(ratio(g(o, s, "idx", q, R), g(base, s, "idx", q, R))))
        best = min(((g(d, 100, "idx", q, R), d) for d in DBS if g(d, 100, "idx", q, R) is not None))[1]
        row.append(NAME[best])
        rows.append(row)
    md += [table(hdr, rows), ""]

md += ["## 4. Skalowalność: czas @100 % / czas @10 % (dane rosną 10×)", "",
       "Wartość ≈1 → czas praktycznie niezależny od ilości danych (indeks), ≈10 → liniowo, >10 → szybciej niż liniowo.", ""]
hdr = ["Zapytanie"] + [NAME[d] for d in DBS]
md += [table(hdr, [[qlabel(q)] + [fr(ratio(g(d, 100, "idx", q, R), g(d, 10, "idx", q, R))) for d in DBS] for q in QUERIES]), ""]

md += ["## 5. Wpływ indeksów i indeksu kompozytowego", "",
       "### 5a. Bez indeksów vs z indeksami (skala 10 %, mediana ze średnich przebiegów)", ""]
hdr = ["Zapytanie"]
for d in DBS:
    hdr += [f"{NAME[d]} bez idx [ms]", f"{NAME[d]} z idx [ms]", f"{NAME[d]} przyspieszenie"]
rows = []
for q in QUERIES:
    row = [qlabel(q)]
    for d in DBS:
        a, b = g(d, 10, "noidx", q, R), g(d, 10, "idx", q, R)
        row += [fmt(a), fmt(b), fr(ratio(a, b))]
    rows.append(row)
md += [table(hdr, rows), ""]

if any(k[2] == "comp" for k in S):
    md += ["### 5b. PostgreSQL: dodatkowy indeks kompozytowy GiST `(category, geom)` / `(kind, geom)` vs indeksy podstawowe", "",
           "Wariant `comp` = indeksy podstawowe + indeksy kompozytowe (planer wybiera najlepszy). "
           "Przyspieszenie = czas(idx) / czas(comp); >1 → kompozytowy pomaga, <1 → szkodzi.", ""]
    hdr = ["Zapytanie"] + [f"idx {s}% [ms]" for s in SCALES] + [f"comp {s}% [ms]" for s in SCALES] + [f"przyspieszenie {s}%" for s in SCALES]
    rows = []
    for q in QUERIES:
        rows.append([qlabel(q)] + [fmt(g("postgres", s, "idx", q, R)) for s in SCALES] + [fmt(g("postgres", s, "comp", q, R)) for s in SCALES]
                    + [fr(ratio(g("postgres", s, "idx", q, R), g("postgres", s, "comp", q, R))) for s in SCALES])
    md += [table(hdr, rows), ""]

sz = read("postgres/sizes.csv")
szm = read("mysql/sizes.csv")
if sz or szm:
    md += ["### 5c. Rozmiary tabel i indeksów (skala 100 %, MB)", ""]
    rows = []
    for d, txt in (("postgres", sz), ("mysql", szm)):
        for r in csv.DictReader(txt.splitlines()) if txt else []:
            rows.append([NAME[d], r["variant"], r["data_mb"], r["index_mb"]])
    md += [table(["SZBD", "wariant", "dane [MB]", "indeksy [MB]"], rows), "",
           "Uwaga: `information_schema` MySQL najpewniej nie wlicza indeksów SPATIAL do `index_length` (14 MB to praktycznie tylko B-tree) – "
           "rozmiaru indeksów przestrzennych MySQL nie należy porównywać z PostgreSQL bez weryfikacji (`mysql.innodb_index_stats`).", ""]

md += ["## 6. Powtarzalność: rozrzut średnich między niezależnymi przebiegami (max−min)/średnia [%]", ""]
hdr = ["Zapytanie"] + [f"{NAME[d]} {s}%" for d in DBS for s in (10, 100)]
md += [table(hdr, [[qlabel(q)] + [f"{g(d, s, 'idx', q, 'run_spread_pct'):.1f}" if g(d, s, 'idx', q) is not None else "–" for d in DBS for s in (10, 100)] for q in QUERIES]), ""]
md += ["## 7. Uwagi interpretacyjne", "",
       "* Pomiary na współdzielonej maszynie (WSL2 + inne procesy) – stąd rozrzut między przebiegami; wnioski opieraj na sekcjach 3–5 (mediana ze średnich przebiegów) i trendach, nie na różnicach <20–30 %.",
       "* PostgreSQL domyślnie używa zapytań równoległych (`max_parallel_workers_per_gather=2`). Od skali 25 % część zapytań (np. Q5a, Q2b, Q6) dostaje plan `Gather`, "
       "którego narzut startowy zawyża czas zapytań rzędu kilku ms (skok 2,6 → 13 ms w Q5a między 10 % a 25 %). MySQL 8.4 wykonuje te zapytania jednowątkowo.",
       "* Q2b @100 % w PG: w pełnym zbiorze pojawiają się duże wielokąty (tereny), których przecięcie i odczyt geometrii są kosztowne – stąd skok względem 50 %.",
       "* MySQL: brak ST_DWithin i kNN z indeksem oraz korelowanego LATERAL z indeksem – zapytania Q4a, Q7a–c zapisane alternatywnie (patrz `mysql/queries.sql`).", ""]
md += ["Liczba przekroczeń limitu czasu: " + (", ".join(f"{NAME[d]}: {int(sum(r['timeouts'] for k, r in S.items() if k[0] == d))}" for d in DBS)), ""]

(RES / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

with open(RES / "comparison.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dbms", "scale", "variant", "query", "n", "mean_ms", "sd_ms", "ci95_ms", "median_ms", "p95_ms", "run_spread_pct"])
    for (d, sc, var, q), r in sorted(S.items()):
        w.writerow([d, sc, var, q, int(r["n"]), r["mean_ms"], r["sd_ms"], r["ci95_ms"], r["median_ms"], r["p95_ms"], r["run_spread_pct"]])
print("->", RES / "REPORT.md", "i", RES / "comparison.csv")

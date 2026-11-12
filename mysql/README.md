# MySQL 8.4 (Część A – razem z PostgreSQL)

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install mysql-connector-python
docker compose -f mysql/docker-compose.yml up -d
docker exec -i spdb_mysql mysql -uroot -pspdb < mysql/01_load.sql        # ~2,5 min
python mysql/benchmark.py --scales s10 --nparams 3 --reps 1 --fresh       # szybki test
python mysql/benchmark.py --fresh                                         # pełny
python mysql/benchmark.py --explain                                       # plany -> results/mysql/plans/
python common/summarize.py mysql
python common/compare_rowcounts.py postgres mysql
```

## Schemat i indeksy

Bazy `s10`, `s25`, `s50`, `s100`, `s10_noidx`; tabele `pois (POINT)`, `roads (LINESTRING)`, `areas (GEOMETRY)`,
kolumna `geom ... NOT NULL SRID 2180`, InnoDB. Indeksy: `SPATIAL INDEX` (R-drzewo) na `geom`, B-tree na
`pois.category` i `areas.kind`, PK `id`. `s10_noidx` – bez indeksów (poza PK).

## Różnice względem PostGIS (wpływają na wyniki – opisać w dokumentacji)

* brak `ST_DWithin` → `MBRIntersects` (indeks) + `ST_Distance <= r`,
* brak kNN z indeksem → `ORDER BY ST_Distance LIMIT 10` (Q4a),
* korelowany `LATERAL` nie używa indeksu przestrzennego (skan `roads` dla każdej apteki, ~76 s) → Q7b przepisane na JOIN + `ROW_NUMBER()` z oknem 500 m,
* optymalizator potrafi wybrać indeks `kind` zamiast przestrzennego (Q7c: skan 534 tys. wierszy po `kind='building'`),
* brak `ST_MakeValid` → odrzucone 51 niepoprawnych obszarów (ta sama reguła w PG).

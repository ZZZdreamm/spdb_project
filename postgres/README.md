# Część A – PostgreSQL + PostGIS

## Uruchomienie krok po kroku

```bash
# 0. wymagania: Docker (w WSL włącz integrację Docker Desktop z dystrybucją), python3
python3 -m venv .venv && . .venv/bin/activate && pip install "psycopg[binary]"

# 1. dane wspólne (OSM -> CSV w EPSG:2180 + params/params.json)
bash common/prepare_data.sh

# 2. baza
docker compose -f postgres/docker-compose.yml up -d
docker exec -i spdb_postgres psql -U postgres -d spdb -v ON_ERROR_STOP=1 < postgres/01_load.sql

# 3. test szybki, potem pełny
python postgres/benchmark.py --scales s10 --nparams 3 --reps 1 --fresh
python postgres/benchmark.py --fresh --runs 5   # 5 niezależnych przebiegów, warianty idx/noidx/comp
python postgres/benchmark.py --explain          # plany -> results/postgres/plans/
python common/summarize.py postgres mysql && python common/report.py   # -> results/REPORT.md
```

Zapytania ręcznie: `docker exec -i spdb_postgres psql -U postgres -d spdb < postgres/queries.sql`.

## Schemat i indeksy

Tabele (w schematach `s10`, `s25`, `s50`, `s100`, `s10_noidx`): `pois(id, osm_id, name, category, geom Point)`,
`roads(…, highway, geom LineString)`, `areas(…, kind, subtype, geom MultiPolygon)`, SRID 2180.

| Indeks | Typ | Cel |
|---|---|---|
| `*_geom_gist` (pois, roads, areas) | GiST (R-drzewo) | Q1–Q7, operator `<->` dla kNN |
| `pois_category_btree`, `areas_kind_btree` | B-tree | filtry kategorii / rodzaju |
| PK `id` | B-tree | – |
| `pois_cat_geom_gist (category, geom)`, `areas_kind_geom_gist (kind, geom)` | GiST kompozytowy (`btree_gist`) | wariant `*_comp`: atrybut + geometria w jednym indeksie |

`s10_noidx` ma te same dane bez indeksów (wpływ indeksu przestrzennego). Niepoprawne geometrie `areas`
(51 z 534 885) są odrzucane (`ST_IsValid`), tak samo jak w MySQL; kontrola liczności w ostatnim zapytaniu `01_load.sql`.
Schematy `s10_comp … s100_comp` = indeksy podstawowe + kompozytowe.

## Uwagi do dokumentacji

* kNN (Q4a, Q7b): `ORDER BY geom <-> pt LIMIT k` korzysta z indeksu GiST; przy filtrze `category` planer
  może skanować indeks z filtrem – opisz plan.
* Q5b i Q3b/Q5a z `kind='building'` – pokazują współpracę indeksu przestrzennego z nieprzestrzennym.
* Wyniki: `results/postgres/results.csv`, `summary.csv`, `env.txt`, `plans/`.

# Część B – MongoDB (do wykonania przez drugą osobę)

Wg `docs/QUERIES_SPEC.md`, ten sam protokół i format wyników (`results/mongodb/results.csv`, `dbms=mongodb`).
Wzorce do skopiowania: `postgres/` i `mysql/` (docker-compose, loader, benchmark, EXPLAIN).

Na co uważać:
1. **2dsphere liczy na sferze (WGS84)** – dane w CSV są w EPSG:2180. Trzeba je przekonwertować do EPSG:4326 (GeoJSON lon/lat),
   np. ponownie `ogr2ogr -t_srs EPSG:4326` (zmiana w `common/prepare_data.sh`) albo `pyproj`. Parametry
   (`params.json`) również przeliczyć tym samym przekształceniem. Odległości wychodzą w metrach (sfera), więc
   drobne różnice względem planarnego 2180 są normalne – opisz je i porównuj liczby wierszy z tolerancją.
2. Kolekcje `pois`, `roads`, `areas` w bazach `s10…s100`, `s10_noidx`; reguła: tylko poprawne geometrie (Mongo odrzuca
   niepoprawne przy tworzeniu indeksu 2dsphere – tego samego zbioru 51 obiektów nie ładuj).
3. Indeksy: `2dsphere` na `geom`, zwykłe na `category`, `kind`.
4. Mapowanie zapytań: Q1 `$geoIntersects` (punkt), Q2/Q3 `$geoIntersects`/`$geoWithin` (`$geometry`), Q4a `$nearSphere`
   lub `$geoNear` (+`distanceField`), Q4b `$geoWithin: {$centerSphere}` lub `$maxDistance`, Q6 `$geoNear`,
   Q7 skorelowane: `$lookup` z pipeline / pętla po stronie klienta (opisać).
5. **Pole (Q5)** – Mongo nie ma funkcji pola geometrii: policzyć w aplikacji (np. shapely/pyproj) lub zapisać
   pole jako atrybut przy ładowaniu i opisać jako ograniczenie.
6. Plany: `explain("executionStats")` dla `param_idx=0`, skala 100 → `results/mongodb/plans/`.

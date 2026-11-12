# Część B – Cassandra (do wykonania przez drugą osobę)

Wg `docs/QUERIES_SPEC.md`, format wyników `results/cassandra/results.csv` (`dbms=cassandra`).

**Cassandra nie ma natywnego modułu przestrzennego** (brak typów geometrii, indeksów R-drzewo, funkcji `ST_*`),
więc część zadania polega na pokazaniu, jak daleko da się dojść i gdzie są granice. Proponowane podejście:

1. Model: partycjonowanie siatką – klucz partycji = komórka (geohash/kwadrat o ustalonym boku w EPSG:2180), kolumny:
   `id, osm_id, name, category/kind, geom_wkt, minx, miny, maxx, maxy` (obwiednia). Osobne tabele pod zapytania (modelowanie
   „query-first”): np. `pois_by_cell_category`.
2. Zapytania: filtr przestrzenny = odczyt komórek pokrywających obszar (`WHERE cell IN (...)`) + filtr po obwiedni, a dokładny
   predykat (zawieranie/przecięcie/odległość/pole) w kliencie (shapely). Wynik: liczby wierszy muszą zgadzać się z PG/MySQL.
3. Opcjonalnie (jeśli wersja/obraz pozwala): SAI na kolumnach liczbowych obwiedni jako „indeks pierwszego stopnia”.
4. Skale `s10…s100` jako oddzielne keyspace’y; wariant `noidx` = pełny skan (`ALLOW FILTERING`) z filtrem w kliencie.
5. Zapytania, których nie da się sensownie wykonać (np. kNN globalne, join przestrzenny Q7c) – zapisać jako „nie wspierane /
   zrealizowane po stronie klienta”, z czasem i opisem kosztu.
6. Plany: `TRACING ON` (cqlsh) dla `param_idx=0`, skala 100 → `results/cassandra/plans/`.

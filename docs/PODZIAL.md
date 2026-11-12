# Podział zadań (grupa 2-osobowa, jeden SZBD na osobę)

Projekt nr 7: porównanie wydajności modułów przestrzennych w SZBD.

## Zasada podziału

Wynik jest porównywalny tylko wtedy, gdy obie osoby testują **te same dane, te same parametry zapytań
i ten sam protokół pomiarowy**. Dlatego warstwa wspólna jest zamrożona (katalogi `common/`, `params/`,
`docs/QUERIES_SPEC.md`), a każda osoba robi własny SZBD w oddzielnym katalogu.

| Część | Zakres | Katalog | Status |
|---|---|---|---|
| **Wspólna** | pobranie i przygotowanie danych OSM (CSV z WKT, EPSG:2180), generator parametrów zapytań, specyfikacja zapytań i protokołu | `common/`, `params/`, `docs/` | zrobione |
| **A – systemy relacyjne: PostgreSQL + PostGIS, MySQL 8.4** | schemat, ładowanie, indeksy (GiST / SPATIAL, B-tree), 4 skale + wariant bez indeksu, zapytania Q1–Q7, benchmark, plany | `postgres/`, `mysql/` | **zrobione** |
| **B – systemy NoSQL: MongoDB, Cassandra** | to samo wg specyfikacji; MongoDB (2dsphere, WGS84), Cassandra (brak modułu przestrzennego – siatka + filtr w kliencie) | `mongodb/`, `cassandra/` | do zrobienia, patrz README w katalogach |

Po obu częściach: wspólna analiza (`results/`) i dokumentacja końcowa (schemat, indeksy, dane, zapytania,
plany, wyniki + komentarz). Prezentacja na końcu.

## Kontrakt między częściami B i A

* Dane: wyłącznie `data/processed/{pois,roads,areas}.csv` (ten sam `MANIFEST.txt` = te same liczby i sumy SHA-256).
* Układ współrzędnych: **EPSG:2180** (metry, płaski) – odległości i pola w metrach / m² (wyjątek: MongoDB wymaga WGS84).
* Reguła danych: tylko poprawne geometrie (odrzucone 51 z 534 885 obiektów `areas`).
* Skale: `bucket < 10 | 25 | 50 | 100` (kolumna `bucket` w CSV, deterministyczna).
* Parametry: `params/params.json` (20 zestawów, seed 42), nazwy parametrów jak w `docs/QUERIES_SPEC.md`.
* Wyniki: CSV o kolumnach `dbms,scale,variant,query,param_idx,rep,time_ms,rows,run` (variant: `idx`/`noidx`/`comp`).
* Kontrola poprawności: liczba wierszy zwracana przez każde zapytanie dla `param_idx=0` musi być zgodna
  między SZBD (`results/*/results.csv`, skrypt `common/compare_rowcounts.py`; NoSQL: tolerancja z uwagi na sferę / obliczenia po stronie klienta).

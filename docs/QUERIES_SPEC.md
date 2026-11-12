# Specyfikacja zapytań i protokołu pomiarowego (wspólna dla wszystkich SZBD)

## Model danych (logiczny)

| Tabela | Geometria | Kolumny | Źródło OSM |
|---|---|---|---|
| `pois`  | Point | id, osm_id, name, category (wartość `amenity`) | warstwa `points`, `amenity` NOT NULL |
| `roads` | LineString | id, osm_id, name, highway | warstwa `lines`, `highway` NOT NULL |
| `areas` | (Multi)Polygon | id, osm_id, name, kind (`building`/`landuse`/`leisure`/`natural`), subtype | warstwa `multipolygons` |

SRID wszędzie 2180. Skala `S` = podzbiór wierszy z `bucket < S` (S ∈ {10, 25, 50, 100}).

## Parametry (`params/params.json`, lista 20 zestawów)

`px, py` punkt · `wkt_seg` odcinek ~500 m · `wkt_rect_small` kwadrat 1×1 km · `wkt_rect_big` kwadrat 4×4 km ·
`wkt_container` duży obszar (landuse zabudowy (residential/commercial/industrial/retail) 0,3–5 km²) · `category` (restaurant) · `k` (10) · `radius` (500 m).

## Zapytania

| ID | Typ (z treści zadania) | Opis |
|---|---|---|
| Q1a | punktowe | `areas` zawierające punkt |
| Q1b | punktowe | `roads` w odległości ≤ 5 m od punktu |
| Q2a | przecięcie | `roads` przecinające odcinek |
| Q2b | przecięcie | `areas` mające część wspólną z kwadratem 1×1 km |
| Q3a | zawieranie | `pois` zawarte w kwadracie 4×4 km |
| Q3b | zawieranie | budynki zawarte w dużym obszarze (`wkt_container`) |
| Q4a | sąsiedzi | k najbliższych `pois` danej kategorii |
| Q4b | sąsiedzi | `pois` danej kategorii w promieniu `radius` |
| Q5a | pole | suma/liczba `ST_Area` budynków zawartych w kwadracie 4×4 km |
| Q5b | pole | 10 największych budynków (skan całej tabeli) |
| Q6  | odległość | odległość punktu do `roads` w promieniu 1 km, rosnąco |
| Q7a | skorelowane | dla każdej szkoły w kwadracie 4×4 km: liczba restauracji w 300 m |
| Q7b | skorelowane | dla każdej apteki w kwadracie 4×4 km: najbliższa droga i odległość |
| Q7c | skorelowane | budynki w kwadracie 1×1 km + liczba POI wewnątrz (join przestrzenny) |

Zawieranie = „obiekt w całości wewnątrz”, przecięcie = `ST_Intersects`. Wyniki Q4a/Q5b/Q6 są sortowane;
przy remisach kolejność nieistotna – porównujemy liczbę wierszy.

## Protokół

1. Dla każdej skali i każdego zapytania: 20 zestawów parametrów, każdy: 1 przebieg rozgrzewający (niezliczany) + 3 pomiary;
   cały test powtarzany w 3 niezależnych przebiegach (`--runs 3`, kolumna `run`) – średnia z (przebieg × zestaw), przedział ufności 95 %.
2. Czas = czas po stronie klienta do pobrania pełnego wyniku (ms), plus `rows`.
3. Pomiary na „ciepłym” cache (zimny cache poza zakresem – ograniczenie opisać w dokumentacji).
4. Limit czasu zapytania 120 s; przekroczenie → `time_ms = timeout`, `rows = -1`.
5. Wariant `noidx` (skala 10, 10 zestawów parametrów) – to samo bez indeksów przestrzennych, do pokazania wpływu indeksu.
   Wariant `comp` (tylko PostgreSQL) – dodatkowe indeksy kompozytowe GiST `(category, geom)` i `(kind, geom)`.
6. Plany wykonania: `EXPLAIN ANALYZE` (lub odpowiednik) dla `param_idx=0`, skala 100, po jednym na zapytanie.
7. Zapisać wersje SZBD, parametry serwera i sprzęt (`results/<dbms>/env.txt`).

## Reguły przygotowania danych (wspólne)

* Do tabel trafiają tylko obiekty z poprawną geometrią (`ST_IsValid`). W obecnym zbiorze odrzucane jest 51 z 534 885
  obiektów `areas` (0,01%); `pois` i `roads` są poprawne. Nie naprawiamy geometrii (MySQL nie ma `ST_MakeValid`).
* Odległości i pola liczone planarnie w EPSG:2180 (metry, m²).
* Zapytanie bez odpowiednika w SZBD (np. brak `ST_DWithin`/kNN) realizujemy najbliższym możliwym wzorcem
  i opisujemy różnicę w dokumentacji (patrz komentarze w `queries.sql` danego SZBD).

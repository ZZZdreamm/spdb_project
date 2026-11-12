# Zestawienie wyników – wydajność modułów przestrzennych

## 1. Protokół i dane

* Dane: OpenStreetMap, Warszawa; skale 10/25/50/100 % (deterministyczne podzbiory), układ EPSG:2180, tylko poprawne geometrie.
* Liczności (POI / drogi / obszary): 10 % – 6 799 / 37 078 / 53 286; 25 % – 17 095 / 91 970 / 134 040; 50 % – 34 367 / 184 454 / 268 102; 100 % – 68 741 / 368 902 / 534 834.
* Każde zapytanie: 20 zestawów parametrów × 3 powtórzenia × N niezależnych przebiegów całości (po 1 przebiegu rozgrzewającym); wariant bez indeksów: 10 zestawów.
* Podawana średnia = średnia z jednostek (przebieg, zestaw parametrów), „±” = przedział ufności 95 % średniej (1,96·sd/√n). Duże sd wynika z różnej wielkości wyników dla różnych parametrów, nie z niestabilności pomiaru; powtarzalność mierzy kolumna „rozrzut przebiegów” w sekcji 6.
* Próbki na zapytanie (skala 100 %): PostgreSQL n=100 jednostek (300 próbek), MySQL n=60 jednostek (180 próbek).

**PostgreSQL:** `PostgreSQL 17.5 (Debian 17.5-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 202`  

**MySQL:** `MySQL 8.4.13`  

## 2. Średni czas zapytania [ms] (indeksy podstawowe)

| Zapytanie | PostgreSQL 10% | PostgreSQL 25% | PostgreSQL 50% | PostgreSQL 100% | MySQL 10% | MySQL 25% | MySQL 50% | MySQL 100% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Q1a** punkt w obszarze | 0.39 ±0.01 | 0.37 ±0.01 | 0.38 ±0.01 | 0.39 ±0.01 | 0.41 ±0.01 | 0.45 ±0.01 | 0.56 ±0.08 | 0.74 ±0.06 |
| **Q1b** drogi ≤5 m od punktu | 0.31 ±0.03 | 0.30 ±0.01 | 0.31 ±0.01 | 0.35 ±0.01 | 0.46 ±0.01 | 0.51 ±0.03 | 0.55 ±0.03 | 0.69 ±0.05 |
| **Q2a** drogi × odcinek | 0.40 ±0.03 | 0.42 ±0.01 | 0.46 ±0.01 | 0.64 ±0.03 | 0.52 ±0.02 | 0.66 ±0.04 | 0.93 ±0.08 | 1.52 ±0.17 |
| **Q2b** obszary × kwadrat 1 km | 0.63 ±0.07 | 0.89 ±0.05 | 1.41 ±0.09 | 17.67 ±3.48 | 1.74 ±0.16 | 3.67 ±0.38 | 9.11 ±1.15 | 14.34 ±1.03 |
| **Q3a** POI w kwadracie 4 km | 0.84 ±0.10 | 1.67 ±0.26 | 2.77 ±0.47 | 6.39 ±1.09 | 4.13 ±0.58 | 10.12 ±1.70 | 16.64 ±2.38 | 33.06 ±4.72 |
| **Q3b** budynki w dużym obszarze | 1.79 ±0.43 | 3.51 ±0.98 | 6.79 ±2.11 | 14.88 ±4.15 | 1.54 ±0.27 | 4.22 ±0.94 | 6.89 ±1.38 | 13.58 ±2.55 |
| **Q4a** 10 najbliższych (kNN) | 0.58 ±0.03 | 0.63 ±0.03 | 0.60 ±0.02 | 0.58 ±0.02 | 1.40 ±0.04 | 4.13 ±0.56 | 6.10 ±0.35 | 12.91 ±0.83 |
| **Q4b** POI w promieniu 500 m | 0.34 ±0.01 | 0.39 ±0.04 | 0.37 ±0.01 | 0.42 ±0.01 | 0.49 ±0.02 | 0.94 ±0.31 | 0.77 ±0.07 | 1.30 ±0.22 |
| **Q5a** suma pól budynków | 1.97 ±0.10 | 29.71 ±3.27 | 29.82 ±2.29 | 32.55 ±1.72 | 5.89 ±0.37 | 19.49 ±2.47 | 32.86 ±3.19 | 72.95 ±5.40 |
| **Q5b** 10 największych budynków | 29.94 ±1.72 | 35.81 ±3.04 | 43.44 ±1.22 | 59.08 ±1.79 | 95.09 ±3.84 | 265 ±23.22 | 566 ±31.55 | 1 230 ±76.45 |
| **Q6** drogi ≤1 km wg odległości | 0.82 ±0.04 | 6.55 ±2.28 | 25.33 ±2.81 | 28.83 ±2.19 | 8.09 ±0.69 | 18.33 ±1.81 | 44.84 ±5.07 | 99.77 ±16.78 |
| **Q7a** korel.: szkoły → restauracje 300 m | 0.43 ±0.02 | 0.53 ±0.03 | 1.10 ±0.11 | 2.49 ±0.27 | 3.40 ±0.46 | 20.30 ±3.44 | 120 ±22.49 | 437 ±73.06 |
| **Q7b** korel.: apteki → najbliższa droga | 0.54 ±0.02 | 0.78 ±0.05 | 1.27 ±0.09 | 3.41 ±0.32 | 6.42 ±0.81 | 39.91 ±6.76 | 175 ±25.96 | 803 ±145 |
| **Q7c** korel.: join budynki × POI | 0.94 ±0.09 | 1.70 ±0.17 | 3.30 ±0.32 | 6.95 ±0.64 | 140 ±16.02 | 396 ±18.45 | 832 ±113 | 1 900 ±100 |

### 2b. Estymata odporna: mediana ze średnich poszczególnych przebiegów [ms]

Używana w sekcjach 3–5. Odporna na pojedynczy przebieg zakłócony przez inne obciążenie maszyny (WSL2, współdzielony host).

| Zapytanie | PostgreSQL 10% | PostgreSQL 25% | PostgreSQL 50% | PostgreSQL 100% | MySQL 10% | MySQL 25% | MySQL 50% | MySQL 100% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Q1a** punkt w obszarze | 0.38 | 0.37 | 0.37 | 0.39 | 0.41 | 0.43 | 0.55 | 0.76 |
| **Q1b** drogi ≤5 m od punktu | 0.30 | 0.30 | 0.30 | 0.35 | 0.46 | 0.47 | 0.54 | 0.74 |
| **Q2a** drogi × odcinek | 0.38 | 0.42 | 0.46 | 0.63 | 0.49 | 0.63 | 0.94 | 1.64 |
| **Q2b** obszary × kwadrat 1 km | 0.57 | 0.81 | 1.21 | 19.16 | 1.44 | 2.97 | 7.55 | 15.22 |
| **Q3a** POI w kwadracie 4 km | 0.66 | 1.24 | 1.94 | 4.82 | 3.92 | 7.27 | 14.85 | 36.04 |
| **Q3b** budynki w dużym obszarze | 1.18 | 1.84 | 3.30 | 9.09 | 1.53 | 2.82 | 7.72 | 14.51 |
| **Q4a** 10 najbliższych (kNN) | 0.59 | 0.62 | 0.60 | 0.58 | 1.41 | 2.70 | 5.42 | 13.99 |
| **Q4b** POI w promieniu 500 m | 0.34 | 0.35 | 0.39 | 0.42 | 0.49 | 0.59 | 0.69 | 1.42 |
| **Q5a** suma pól budynków | 1.92 | 30.29 | 33.04 | 34.03 | 5.63 | 13.78 | 29.34 | 79.35 |
| **Q5b** 10 największych budynków | 34.45 | 33.97 | 44.07 | 63.35 | 88.29 | 217 | 566 | 1 386 |
| **Q6** drogi ≤1 km wg odległości | 0.83 | 7.61 | 30.80 | 33.22 | 7.63 | 16.06 | 51.72 | 89.82 |
| **Q7a** korel.: szkoły → restauracje 300 m | 0.43 | 0.52 | 1.06 | 2.43 | 3.27 | 17.69 | 137 | 420 |
| **Q7b** korel.: apteki → najbliższa droga | 0.54 | 0.78 | 1.26 | 3.13 | 6.16 | 34.38 | 189 | 755 |
| **Q7c** korel.: join budynki × POI | 0.88 | 1.68 | 3.31 | 6.79 | 121 | 361 | 884 | 1 961 |

## 3. Porównanie systemów (stosunek czasów – mediany ze średnich przebiegów; >1 = pierwszy wolniejszy)

| Zapytanie | MySQL/PostgreSQL 10% | MySQL/PostgreSQL 25% | MySQL/PostgreSQL 50% | MySQL/PostgreSQL 100% | szybszy @100 % |
|---|---:|---:|---:|---:|---:|
| **Q1a** punkt w obszarze | 1.10× | 1.17× | 1.47× | 1.96× | PostgreSQL |
| **Q1b** drogi ≤5 m od punktu | 1.54× | 1.54× | 1.79× | 2.13× | PostgreSQL |
| **Q2a** drogi × odcinek | 1.29× | 1.50× | 2.02× | 2.61× | PostgreSQL |
| **Q2b** obszary × kwadrat 1 km | 2.54× | 3.68× | 6.26× | 0.79× | MySQL |
| **Q3a** POI w kwadracie 4 km | 5.98× | 5.86× | 7.65× | 7.47× | PostgreSQL |
| **Q3b** budynki w dużym obszarze | 1.29× | 1.53× | 2.34× | 1.60× | PostgreSQL |
| **Q4a** 10 najbliższych (kNN) | 2.39× | 4.37× | 9.10× | 24.3× | PostgreSQL |
| **Q4b** POI w promieniu 500 m | 1.46× | 1.66× | 1.81× | 3.40× | PostgreSQL |
| **Q5a** suma pól budynków | 2.94× | 0.45× | 0.89× | 2.33× | PostgreSQL |
| **Q5b** 10 największych budynków | 2.56× | 6.39× | 12.9× | 21.9× | PostgreSQL |
| **Q6** drogi ≤1 km wg odległości | 9.14× | 2.11× | 1.68× | 2.70× | PostgreSQL |
| **Q7a** korel.: szkoły → restauracje 300 m | 7.58× | 33.9× | 129.4× | 172.4× | PostgreSQL |
| **Q7b** korel.: apteki → najbliższa droga | 11.4× | 44.0× | 149.5× | 240.8× | PostgreSQL |
| **Q7c** korel.: join budynki × POI | 136.7× | 214.9× | 267.6× | 289.0× | PostgreSQL |

## 4. Skalowalność: czas @100 % / czas @10 % (dane rosną 10×)

Wartość ≈1 → czas praktycznie niezależny od ilości danych (indeks), ≈10 → liniowo, >10 → szybciej niż liniowo.

| Zapytanie | PostgreSQL | MySQL |
|---|---:|---:|
| **Q1a** punkt w obszarze | 1.03× | 1.83× |
| **Q1b** drogi ≤5 m od punktu | 1.17× | 1.61× |
| **Q2a** drogi × odcinek | 1.65× | 3.33× |
| **Q2b** obszary × kwadrat 1 km | 33.7× | 10.5× |
| **Q3a** POI w kwadracie 4 km | 7.36× | 9.20× |
| **Q3b** budynki w dużym obszarze | 7.68× | 9.50× |
| **Q4a** 10 najbliższych (kNN) | 0.98× | 9.96× |
| **Q4b** POI w promieniu 500 m | 1.24× | 2.89× |
| **Q5a** suma pól budynków | 17.8× | 14.1× |
| **Q5b** 10 największych budynków | 1.84× | 15.7× |
| **Q6** drogi ≤1 km wg odległości | 39.8× | 11.8× |
| **Q7a** korel.: szkoły → restauracje 300 m | 5.63× | 128.1× |
| **Q7b** korel.: apteki → najbliższa droga | 5.81× | 122.5× |
| **Q7c** korel.: join budynki × POI | 7.69× | 16.2× |

## 5. Wpływ indeksów i indeksu kompozytowego

### 5a. Bez indeksów vs z indeksami (skala 10 %, mediana ze średnich przebiegów)

| Zapytanie | PostgreSQL bez idx [ms] | PostgreSQL z idx [ms] | PostgreSQL przyspieszenie | MySQL bez idx [ms] | MySQL z idx [ms] | MySQL przyspieszenie |
|---|---:|---:|---:|---:|---:|---:|
| **Q1a** punkt w obszarze | 36.37 | 0.38 | 96.5× | 143 | 0.41 | 345.2× |
| **Q1b** drogi ≤5 m od punktu | 8.80 | 0.30 | 29.4× | 89.01 | 0.46 | 193.1× |
| **Q2a** drogi × odcinek | 6.65 | 0.38 | 17.5× | 89.59 | 0.49 | 182.1× |
| **Q2b** obszary × kwadrat 1 km | 34.66 | 0.57 | 60.9× | 164 | 1.44 | 113.6× |
| **Q3a** POI w kwadracie 4 km | 1.23 | 0.66 | 1.87× | 18.06 | 3.92 | 4.61× |
| **Q3b** budynki w dużym obszarze | 35.24 | 1.18 | 29.8× | 226 | 1.53 | 148.0× |
| **Q4a** 10 najbliższych (kNN) | 0.64 | 0.59 | 1.10× | 2.69 | 1.41 | 1.91× |
| **Q4b** POI w promieniu 500 m | 0.56 | 0.34 | 1.67× | 2.24 | 0.49 | 4.55× |
| **Q5a** suma pól budynków | 44.03 | 1.92 | 23.0× | 115 | 5.63 | 20.4× |
| **Q5b** 10 największych budynków | 34.32 | 34.45 | 1.00× | 89.94 | 88.29 | 1.02× |
| **Q6** drogi ≤1 km wg odległości | 9.33 | 0.83 | 11.2× | 95.61 | 7.63 | 12.5× |
| **Q7a** korel.: szkoły → restauracje 300 m | 5.73 | 0.43 | 13.3× | 8.14 | 3.27 | 2.49× |
| **Q7b** korel.: apteki → najbliższa droga | 47.48 | 0.54 | 87.9× | 839 | 6.16 | 136.2× |
| **Q7c** korel.: join budynki × POI | 218 | 0.88 | 247.0× | 783 | 121 | 6.49× |

### 5b. PostgreSQL: dodatkowy indeks kompozytowy GiST `(category, geom)` / `(kind, geom)` vs indeksy podstawowe

Wariant `comp` = indeksy podstawowe + indeksy kompozytowe (planer wybiera najlepszy). Przyspieszenie = czas(idx) / czas(comp); >1 → kompozytowy pomaga, <1 → szkodzi.

| Zapytanie | idx 10% [ms] | idx 25% [ms] | idx 50% [ms] | idx 100% [ms] | comp 10% [ms] | comp 25% [ms] | comp 50% [ms] | comp 100% [ms] | przyspieszenie 10% | przyspieszenie 25% | przyspieszenie 50% | przyspieszenie 100% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Q1a** punkt w obszarze | 0.38 | 0.37 | 0.37 | 0.39 | 0.40 | 0.39 | 0.43 | 0.49 | 0.94× | 0.94× | 0.87× | 0.79× |
| **Q1b** drogi ≤5 m od punktu | 0.30 | 0.30 | 0.30 | 0.35 | 0.30 | 0.30 | 0.30 | 0.35 | 1.01× | 1.00× | 1.02× | 1.01× |
| **Q2a** drogi × odcinek | 0.38 | 0.42 | 0.46 | 0.63 | 0.37 | 0.41 | 0.46 | 0.68 | 1.02× | 1.01× | 1.02× | 0.93× |
| **Q2b** obszary × kwadrat 1 km | 0.57 | 0.81 | 1.21 | 19.16 | 0.59 | 0.82 | 1.22 | 20.33 | 0.96× | 0.99× | 0.99× | 0.94× |
| **Q3a** POI w kwadracie 4 km | 0.66 | 1.24 | 1.94 | 4.82 | 0.66 | 1.15 | 2.02 | 4.60 | 1.00× | 1.08× | 0.96× | 1.05× |
| **Q3b** budynki w dużym obszarze | 1.18 | 1.84 | 3.30 | 9.09 | 0.79 | 1.11 | 1.58 | 4.14 | 1.50× | 1.65× | 2.09× | 2.19× |
| **Q4a** 10 najbliższych (kNN) | 0.59 | 0.62 | 0.60 | 0.58 | 0.35 | 0.37 | 0.38 | 0.38 | 1.65× | 1.68× | 1.56× | 1.50× |
| **Q4b** POI w promieniu 500 m | 0.34 | 0.35 | 0.39 | 0.42 | 0.36 | 0.37 | 0.39 | 0.42 | 0.94× | 0.95× | 0.99× | 0.99× |
| **Q5a** suma pól budynków | 1.92 | 30.29 | 33.04 | 34.03 | 1.21 | 30.87 | 33.58 | 32.92 | 1.58× | 0.98× | 0.98× | 1.03× |
| **Q5b** 10 największych budynków | 34.45 | 33.97 | 44.07 | 63.35 | 33.73 | 36.96 | 45.18 | 58.76 | 1.02× | 0.92× | 0.98× | 1.08× |
| **Q6** drogi ≤1 km wg odległości | 0.83 | 7.61 | 30.80 | 33.22 | 0.79 | 7.62 | 31.56 | 36.32 | 1.05× | 1.00× | 0.98× | 0.91× |
| **Q7a** korel.: szkoły → restauracje 300 m | 0.43 | 0.52 | 1.06 | 2.43 | 0.33 | 0.47 | 0.88 | 1.87 | 1.29× | 1.10× | 1.20× | 1.30× |
| **Q7b** korel.: apteki → najbliższa droga | 0.54 | 0.78 | 1.26 | 3.13 | 0.44 | 0.72 | 1.12 | 3.57 | 1.22× | 1.09× | 1.12× | 0.88× |
| **Q7c** korel.: join budynki × POI | 0.88 | 1.68 | 3.31 | 6.79 | 2.79 | 1.65 | 28.06 | 7.17 | 0.32× | 1.02× | 0.12× | 0.95× |

### 5c. Rozmiary tabel i indeksów (skala 100 %, MB)

| SZBD | wariant | dane [MB] | indeksy [MB] |
|---|---:|---:|---:|
| PostgreSQL | idx | 226.2 | 65.1 |
| PostgreSQL | comp | 226.2 | 109.7 |
| MySQL | idx | 211.8 | 14.0 |

Uwaga: `information_schema` MySQL najpewniej nie wlicza indeksów SPATIAL do `index_length` (14 MB to praktycznie tylko B-tree) – rozmiaru indeksów przestrzennych MySQL nie należy porównywać z PostgreSQL bez weryfikacji (`mysql.innodb_index_stats`).

## 6. Powtarzalność: rozrzut średnich między niezależnymi przebiegami (max−min)/średnia [%]

| Zapytanie | PostgreSQL 10% | PostgreSQL 100% | MySQL 10% | MySQL 100% |
|---|---:|---:|---:|---:|
| **Q1a** punkt w obszarze | 27.3 | 3.9 | 7.4 | 61.4 |
| **Q1b** drogi ≤5 m od punktu | 21.6 | 9.7 | 2.9 | 44.9 |
| **Q2a** drogi × odcinek | 26.7 | 13.7 | 16.9 | 46.7 |
| **Q2b** obszary × kwadrat 1 km | 38.1 | 119.1 | 55.8 | 41.8 |
| **Q3a** POI w kwadracie 4 km | 90.1 | 140.0 | 35.0 | 58.2 |
| **Q3b** budynki w dużym obszarze | 192.7 | 217.5 | 13.6 | 40.5 |
| **Q4a** 10 najbliższych (kNN) | 8.3 | 5.8 | 1.0 | 53.6 |
| **Q4b** POI w promieniu 500 m | 21.8 | 9.2 | 2.8 | 40.5 |
| **Q5a** suma pól budynków | 41.2 | 59.9 | 16.7 | 44.3 |
| **Q5b** 10 największych budynków | 72.6 | 31.9 | 25.2 | 45.2 |
| **Q6** drogi ≤1 km wg odległości | 11.3 | 99.8 | 19.7 | 83.8 |
| **Q7a** korel.: szkoły → restauracje 300 m | 8.9 | 25.3 | 14.2 | 68.8 |
| **Q7b** korel.: apteki → najbliższa droga | 6.6 | 45.0 | 17.5 | 74.7 |
| **Q7c** korel.: join budynki × POI | 21.3 | 27.3 | 51.9 | 38.0 |

## 7. Uwagi interpretacyjne

* Pomiary na współdzielonej maszynie (WSL2 + inne procesy) – stąd rozrzut między przebiegami; wnioski opieraj na sekcjach 3–5 (mediana ze średnich przebiegów) i trendach, nie na różnicach <20–30 %.
* PostgreSQL domyślnie używa zapytań równoległych (`max_parallel_workers_per_gather=2`). Od skali 25 % część zapytań (np. Q5a, Q2b, Q6) dostaje plan `Gather`, którego narzut startowy zawyża czas zapytań rzędu kilku ms (skok 2,6 → 13 ms w Q5a między 10 % a 25 %). MySQL 8.4 wykonuje te zapytania jednowątkowo.
* Q2b @100 % w PG: w pełnym zbiorze pojawiają się duże wielokąty (tereny), których przecięcie i odczyt geometrii są kosztowne – stąd skok względem 50 %.
* MySQL: brak ST_DWithin i kNN z indeksem oraz korelowanego LATERAL z indeksem – zapytania Q4a, Q7a–c zapisane alternatywnie (patrz `mysql/queries.sql`).

Liczba przekroczeń limitu czasu: PostgreSQL: 0, MySQL: 0

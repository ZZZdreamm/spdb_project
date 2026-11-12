\set ON_ERROR_STOP on
SET search_path TO s100, public;

\set px 637000
\set py 486000
\set wkt_seg 'LINESTRING (637000 486000, 637400 486300)'
\set wkt_rect_small 'POLYGON ((636500 485500, 637500 485500, 637500 486500, 636500 486500, 636500 485500))'
\set wkt_rect_big   'POLYGON ((635000 484000, 639000 484000, 639000 488000, 635000 488000, 635000 484000))'
\set wkt_container  'POLYGON ((635000 484000, 639000 484000, 639000 488000, 635000 488000, 635000 484000))'
\set category restaurant
\set k 10
\set radius 500

-- name: Q1a
SELECT id, kind, subtype FROM areas
WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(:px, :py), 2180));

-- name: Q1b
SELECT id, highway FROM roads
WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:px, :py), 2180), 5);

-- name: Q2a
SELECT id, highway FROM roads
WHERE ST_Intersects(geom, ST_GeomFromText(:'wkt_seg', 2180));

-- name: Q2b
SELECT id, kind FROM areas
WHERE ST_Intersects(geom, ST_GeomFromText(:'wkt_rect_small', 2180));

-- name: Q3a
SELECT id, category FROM pois
WHERE ST_Within(geom, ST_GeomFromText(:'wkt_rect_big', 2180));

-- name: Q3b
SELECT id FROM areas
WHERE kind = 'building' AND ST_Within(geom, ST_GeomFromText(:'wkt_container', 2180));

-- name: Q4a
SELECT id, name, ST_Distance(geom, ST_SetSRID(ST_MakePoint(:px, :py), 2180)) AS dist
FROM pois
WHERE category = :'category'
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(:px, :py), 2180)
LIMIT :k;

-- name: Q4b
SELECT id, name FROM pois
WHERE category = :'category'
  AND ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:px, :py), 2180), :radius);

-- name: Q5a
SELECT count(*) AS n, COALESCE(sum(ST_Area(geom)), 0) AS total_area_m2
FROM areas
WHERE kind = 'building' AND ST_Within(geom, ST_GeomFromText(:'wkt_rect_big', 2180));

-- name: Q5b
SELECT id, ST_Area(geom) AS area_m2 FROM areas
WHERE kind = 'building'
ORDER BY area_m2 DESC
LIMIT 10;

-- name: Q6
SELECT id, highway, ST_Distance(geom, ST_SetSRID(ST_MakePoint(:px, :py), 2180)) AS dist
FROM roads
WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:px, :py), 2180), 1000)
ORDER BY dist;

-- name: Q7a
SELECT s.id,
       (SELECT count(*) FROM pois r
        WHERE r.category = 'restaurant' AND ST_DWithin(r.geom, s.geom, 300)) AS restaurants_300m
FROM pois s
WHERE s.category = 'school'
  AND ST_Within(s.geom, ST_GeomFromText(:'wkt_rect_big', 2180));

-- name: Q7b
SELECT p.id AS pharmacy_id, nr.id AS road_id, nr.dist
FROM pois p
CROSS JOIN LATERAL (
  SELECT r.id, ST_Distance(r.geom, p.geom) AS dist
  FROM roads r ORDER BY r.geom <-> p.geom LIMIT 1
) nr
WHERE p.category = 'pharmacy'
  AND ST_Within(p.geom, ST_GeomFromText(:'wkt_rect_big', 2180));

-- name: Q7c
SELECT a.id, count(p.id) AS pois_inside
FROM areas a
LEFT JOIN pois p ON ST_Contains(a.geom, p.geom)
WHERE a.kind = 'building'
  AND ST_Within(a.geom, ST_GeomFromText(:'wkt_rect_small', 2180))
GROUP BY a.id;

USE s100;

SET @px = 637000, @py = 486000, @category = 'restaurant', @radius = 500;
SET @wkt_seg = 'LINESTRING (637000 486000, 637400 486300)';
SET @wkt_rect_small = 'POLYGON ((636500 485500, 637500 485500, 637500 486500, 636500 486500, 636500 485500))';
SET @wkt_rect_big   = 'POLYGON ((635000 484000, 639000 484000, 639000 488000, 635000 488000, 635000 484000))';
SET @wkt_container  = 'POLYGON ((635000 484000, 639000 484000, 639000 488000, 635000 488000, 635000 484000))';

-- name: Q1a
SELECT id, kind, subtype FROM areas
WHERE ST_Contains(geom, ST_GeomFromText(CONCAT('POINT(', @px, ' ', @py, ')'), 2180));

-- name: Q1b
SELECT id, highway FROM roads
WHERE MBRIntersects(geom, ST_GeomFromText(CONCAT('POLYGON((', @px-5, ' ', @py-5, ',', @px+5, ' ', @py-5, ',', @px+5, ' ', @py+5, ',', @px-5, ' ', @py+5, ',', @px-5, ' ', @py-5, '))'), 2180))
  AND ST_Distance(geom, ST_GeomFromText(CONCAT('POINT(', @px, ' ', @py, ')'), 2180)) <= 5;

-- name: Q2a
SELECT id, highway FROM roads
WHERE ST_Intersects(geom, ST_GeomFromText(@wkt_seg, 2180));

-- name: Q2b
SELECT id, kind FROM areas
WHERE ST_Intersects(geom, ST_GeomFromText(@wkt_rect_small, 2180));

-- name: Q3a
SELECT id, category FROM pois
WHERE ST_Within(geom, ST_GeomFromText(@wkt_rect_big, 2180));

-- name: Q3b
SELECT id FROM areas
WHERE kind = 'building' AND ST_Within(geom, ST_GeomFromText(@wkt_container, 2180));

-- name: Q4a
SELECT id, name, ST_Distance(geom, ST_GeomFromText(CONCAT('POINT(', @px, ' ', @py, ')'), 2180)) AS dist
FROM pois
WHERE category = @category
ORDER BY dist
LIMIT 10;

-- name: Q4b
SELECT id, name FROM pois
WHERE category = @category
  AND MBRIntersects(geom, ST_GeomFromText(CONCAT('POLYGON((', @px-@radius, ' ', @py-@radius, ',', @px+@radius, ' ', @py-@radius, ',', @px+@radius, ' ', @py+@radius, ',', @px-@radius, ' ', @py+@radius, ',', @px-@radius, ' ', @py-@radius, '))'), 2180))
  AND ST_Distance(geom, ST_GeomFromText(CONCAT('POINT(', @px, ' ', @py, ')'), 2180)) <= @radius;

-- name: Q5a
SELECT COUNT(*) AS n, COALESCE(SUM(ST_Area(geom)), 0) AS total_area_m2
FROM areas
WHERE kind = 'building' AND ST_Within(geom, ST_GeomFromText(@wkt_rect_big, 2180));

-- name: Q5b
SELECT id, ST_Area(geom) AS area_m2 FROM areas
WHERE kind = 'building'
ORDER BY area_m2 DESC
LIMIT 10;

-- name: Q6
SELECT id, highway, ST_Distance(geom, ST_GeomFromText(CONCAT('POINT(', @px, ' ', @py, ')'), 2180)) AS dist
FROM roads
WHERE MBRIntersects(geom, ST_GeomFromText(CONCAT('POLYGON((', @px-1000, ' ', @py-1000, ',', @px+1000, ' ', @py-1000, ',', @px+1000, ' ', @py+1000, ',', @px-1000, ' ', @py+1000, ',', @px-1000, ' ', @py-1000, '))'), 2180))
  AND ST_Distance(geom, ST_GeomFromText(CONCAT('POINT(', @px, ' ', @py, ')'), 2180)) <= 1000
ORDER BY dist;

-- name: Q7a
SELECT s.id,
       (SELECT COUNT(*) FROM pois r
        WHERE r.category = 'restaurant'
          AND MBRIntersects(r.geom, ST_Buffer(s.geom, 300, ST_Buffer_Strategy('point_square')))
          AND ST_Distance(r.geom, s.geom) <= 300) AS restaurants_300m
FROM pois s
WHERE s.category = 'school'
  AND ST_Within(s.geom, ST_GeomFromText(@wkt_rect_big, 2180));

-- name: Q7b
SELECT pharmacy_id, road_id, dist FROM (
  SELECT p.id AS pharmacy_id, r.id AS road_id, ST_Distance(r.geom, p.geom) AS dist,
         ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY ST_Distance(r.geom, p.geom)) AS rn
  FROM pois p
  JOIN roads r ON MBRIntersects(r.geom, ST_Buffer(p.geom, 500, ST_Buffer_Strategy('point_square')))
  WHERE p.category = 'pharmacy'
    AND ST_Within(p.geom, ST_GeomFromText(@wkt_rect_big, 2180))
) x
WHERE rn = 1;

-- name: Q7c
SELECT a.id, COUNT(p.id) AS pois_inside
FROM areas a
LEFT JOIN pois p ON ST_Contains(a.geom, p.geom)
WHERE a.kind = 'building'
  AND ST_Within(a.geom, ST_GeomFromText(@wkt_rect_small, 2180))
GROUP BY a.id;

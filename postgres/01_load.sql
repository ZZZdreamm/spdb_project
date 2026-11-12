SET client_min_messages = warning;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS btree_gist;

DROP SCHEMA IF EXISTS staging CASCADE;
CREATE SCHEMA staging;

CREATE TABLE staging.pois  (id int, bucket int, osm_id bigint, name text, category text, wkt text);
CREATE TABLE staging.roads (id int, bucket int, osm_id bigint, name text, highway  text, wkt text);
CREATE TABLE staging.areas (id int, bucket int, osm_id bigint, name text, kind text, subtype text, wkt text);

COPY staging.pois  FROM '/data/pois.csv'  WITH (FORMAT csv, HEADER true);
COPY staging.roads FROM '/data/roads.csv' WITH (FORMAT csv, HEADER true);
COPY staging.areas FROM '/data/areas.csv' WITH (FORMAT csv, HEADER true);

DO $$
DECLARE
  r record;
BEGIN
  FOR r IN SELECT * FROM (VALUES
      ('s10', 10, true, false), ('s25', 25, true, false), ('s50', 50, true, false), ('s100', 100, true, false),
      ('s10_noidx', 10, false, false),
      ('s10_comp', 10, true, true), ('s25_comp', 25, true, true), ('s50_comp', 50, true, true), ('s100_comp', 100, true, true)
      ) AS v(sch, pct, idx, comp)
  LOOP
    EXECUTE format('DROP SCHEMA IF EXISTS %I CASCADE', r.sch);
    EXECUTE format('CREATE SCHEMA %I', r.sch);

    EXECUTE format($q$CREATE TABLE %I.pois AS
      SELECT id, osm_id, name, category,
             ST_GeomFromText(wkt, 2180)::geometry(Point, 2180) AS geom
      FROM staging.pois WHERE bucket < %s$q$, r.sch, r.pct);

    EXECUTE format($q$CREATE TABLE %I.roads AS
      SELECT id, osm_id, name, highway,
             ST_GeomFromText(wkt, 2180)::geometry(LineString, 2180) AS geom
      FROM staging.roads WHERE bucket < %s$q$, r.sch, r.pct);

    EXECUTE format($q$CREATE TABLE %I.areas AS
      SELECT id, osm_id, name, kind, subtype,
             ST_Multi(g)::geometry(MultiPolygon, 2180) AS geom
      FROM (SELECT *, ST_GeomFromText(wkt, 2180) AS g FROM staging.areas WHERE bucket < %s) t
      WHERE ST_IsValid(g)$q$, r.sch, r.pct);

    IF r.idx THEN
      EXECUTE format('ALTER TABLE %I.pois  ADD PRIMARY KEY (id)', r.sch);
      EXECUTE format('ALTER TABLE %I.roads ADD PRIMARY KEY (id)', r.sch);
      EXECUTE format('ALTER TABLE %I.areas ADD PRIMARY KEY (id)', r.sch);
      EXECUTE format('CREATE INDEX pois_geom_gist  ON %I.pois  USING gist (geom)', r.sch);
      EXECUTE format('CREATE INDEX roads_geom_gist ON %I.roads USING gist (geom)', r.sch);
      EXECUTE format('CREATE INDEX areas_geom_gist ON %I.areas USING gist (geom)', r.sch);
      EXECUTE format('CREATE INDEX pois_category_btree ON %I.pois (category)', r.sch);
      EXECUTE format('CREATE INDEX areas_kind_btree    ON %I.areas (kind)', r.sch);
    END IF;

    IF r.comp THEN
      EXECUTE format('CREATE INDEX pois_cat_geom_gist ON %I.pois  USING gist (category, geom)', r.sch);
      EXECUTE format('CREATE INDEX areas_kind_geom_gist ON %I.areas USING gist (kind, geom)', r.sch);
    END IF;

    EXECUTE format('ANALYZE %I.pois',  r.sch);
    EXECUTE format('ANALYZE %I.roads', r.sch);
    EXECUTE format('ANALYZE %I.areas', r.sch);
  END LOOP;
END $$;

SELECT 's100' AS scale, (SELECT count(*) FROM s100.pois) pois, (SELECT count(*) FROM s100.roads) roads,
       (SELECT count(*) FROM s100.areas) areas,
       (SELECT count(*) FROM staging.areas) areas_in_csv,
       (SELECT count(*) FROM s100.areas) - (SELECT count(*) FROM staging.areas) AS diff_invalid_dropped;

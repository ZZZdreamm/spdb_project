DROP DATABASE IF EXISTS staging;
CREATE DATABASE staging;

CREATE TABLE staging.pois  (id INT, bucket INT, osm_id BIGINT, name TEXT, category VARCHAR(64), wkt LONGTEXT);
CREATE TABLE staging.roads (id INT, bucket INT, osm_id BIGINT, name TEXT, highway  VARCHAR(64), wkt LONGTEXT);
CREATE TABLE staging.areas (id INT, bucket INT, osm_id BIGINT, name TEXT, kind VARCHAR(16), subtype VARCHAR(64), wkt LONGTEXT);

LOAD DATA INFILE '/data/pois.csv'  INTO TABLE staging.pois  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;
LOAD DATA INFILE '/data/roads.csv' INTO TABLE staging.roads FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;
LOAD DATA INFILE '/data/areas.csv' INTO TABLE staging.areas FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;

DELIMITER //

DROP PROCEDURE IF EXISTS staging.run //
CREATE PROCEDURE staging.run(IN q LONGTEXT)
BEGIN
  SET @q = q;
  PREPARE s FROM @q;
  EXECUTE s;
  DEALLOCATE PREPARE s;
END //

DROP PROCEDURE IF EXISTS staging.build //
CREATE PROCEDURE staging.build(IN sch VARCHAR(32), IN pct INT, IN with_idx BOOL)
BEGIN
  CALL staging.run(CONCAT('DROP DATABASE IF EXISTS `', sch, '`'));
  CALL staging.run(CONCAT('CREATE DATABASE `', sch, '`'));

  CALL staging.run(CONCAT('CREATE TABLE `', sch, '`.pois (id INT NOT NULL, osm_id BIGINT, name TEXT, ',
      'category VARCHAR(64), geom POINT NOT NULL SRID 2180, PRIMARY KEY (id)) ENGINE=InnoDB'));
  CALL staging.run(CONCAT('CREATE TABLE `', sch, '`.roads (id INT NOT NULL, osm_id BIGINT, name TEXT, ',
      'highway VARCHAR(64), geom LINESTRING NOT NULL SRID 2180, PRIMARY KEY (id)) ENGINE=InnoDB'));
  CALL staging.run(CONCAT('CREATE TABLE `', sch, '`.areas (id INT NOT NULL, osm_id BIGINT, name TEXT, ',
      'kind VARCHAR(16), subtype VARCHAR(64), geom GEOMETRY NOT NULL SRID 2180, PRIMARY KEY (id)) ENGINE=InnoDB'));

  CALL staging.run(CONCAT('INSERT INTO `', sch, '`.pois SELECT id, osm_id, name, category, ',
      'ST_GeomFromText(wkt, 2180) FROM staging.pois WHERE bucket < ', pct));
  CALL staging.run(CONCAT('INSERT INTO `', sch, '`.roads SELECT id, osm_id, name, highway, ',
      'ST_GeomFromText(wkt, 2180) FROM staging.roads WHERE bucket < ', pct));
  CALL staging.run(CONCAT('INSERT INTO `', sch, '`.areas SELECT id, osm_id, name, kind, subtype, g ',
      'FROM (SELECT *, ST_GeomFromText(wkt, 2180) AS g FROM staging.areas WHERE bucket < ', pct,
      ') t WHERE ST_IsValid(g)'));

  IF with_idx THEN
    CALL staging.run(CONCAT('ALTER TABLE `', sch, '`.pois  ADD SPATIAL INDEX pois_geom (geom), ADD INDEX pois_category (category)'));
    CALL staging.run(CONCAT('ALTER TABLE `', sch, '`.roads ADD SPATIAL INDEX roads_geom (geom)'));
    CALL staging.run(CONCAT('ALTER TABLE `', sch, '`.areas ADD SPATIAL INDEX areas_geom (geom), ADD INDEX areas_kind (kind)'));
  END IF;

  CALL staging.run(CONCAT('ANALYZE TABLE `', sch, '`.pois, `', sch, '`.roads, `', sch, '`.areas'));
END //

DELIMITER ;

CALL staging.build('s10', 10, TRUE);
CALL staging.build('s25', 25, TRUE);
CALL staging.build('s50', 50, TRUE);
CALL staging.build('s100', 100, TRUE);
CALL staging.build('s10_noidx', 10, FALSE);

SELECT 's100' AS scale,
       (SELECT COUNT(*) FROM s100.pois)  AS pois,
       (SELECT COUNT(*) FROM s100.roads) AS roads,
       (SELECT COUNT(*) FROM s100.areas) AS areas,
       (SELECT COUNT(*) FROM staging.areas) AS areas_in_csv;

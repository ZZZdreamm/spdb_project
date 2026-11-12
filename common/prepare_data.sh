#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PBF_URL="${PBF_URL:-https://download.geofabrik.de/europe/poland/mazowieckie-latest.osm.pbf}"
BBOX="${BBOX:-20.85 52.09 21.27 52.37}"
GDAL_IMG="${GDAL_IMG:-ghcr.io/osgeo/gdal:alpine-small-latest}"
RAW=data/raw

mkdir -p "$RAW" data/processed
[ -f "$RAW/region.osm.pbf" ] || curl -L -o "$RAW/region.osm.pbf" "$PBF_URL"

ogr() {
  rm -f "$RAW/$1"
  docker run --rm -v "$PWD/$RAW":/d "$GDAL_IMG" \
    ogr2ogr -f CSV "/d/$1" /d/region.osm.pbf -dialect OGRSQL -sql "$2" \
    -spat $BBOX -t_srs EPSG:2180 -lco GEOMETRY=AS_WKT
}

ogr pois.csv  "SELECT osm_id, name, hstore_get_value(other_tags,'amenity') AS amenity FROM points WHERE hstore_get_value(other_tags,'amenity') IS NOT NULL"
ogr roads.csv "SELECT osm_id, name, highway FROM lines WHERE highway IS NOT NULL"
ogr areas.csv "SELECT osm_id, osm_way_id, name, building, landuse, leisure, \"natural\" AS natural_ FROM multipolygons WHERE building IS NOT NULL OR landuse IS NOT NULL OR leisure IS NOT NULL OR \"natural\" IS NOT NULL"

python3 common/postprocess.py
python3 common/make_params.py

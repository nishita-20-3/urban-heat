import json
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select, literal
from app.models.spatial import City, GridCell
from app.models.predictions import HeatPrediction
from app.schemas.grid import GridFeatureCollection, GridFeature, GridFeatureProperties


def parse_bbox(bbox_str: str) -> Tuple[float, float, float, float]:
    """
    Parse and validate a bounding box string in the format 'min_lon,min_lat,max_lon,max_lat'.
    """
    try:
        parts = [float(x.strip()) for x in bbox_str.split(",")]
        if len(parts) != 4:
            raise ValueError
        min_lon, min_lat, max_lon, max_lat = parts
        if min_lon > max_lon or min_lat > max_lat:
            raise ValueError("min coordinates cannot be greater than max coordinates")
        return min_lon, min_lat, max_lon, max_lat
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid bbox parameter '{bbox_str}'. Expected format: 'min_lon,min_lat,max_lon,max_lat' (e.g. '72.7,21.1,72.9,21.3'). {str(e)}",
        )


def get_grid_features(
    db: Session,
    city_id: int,
    bbox: Optional[str] = None,
    limit: Optional[int] = None,
    season: Optional[str] = None,
) -> GridFeatureCollection:
    """
    Query grid cells for a city as GeoJSON Features using PostGIS ST_AsGeoJSON().
    Optionally joins heat_predictions to attach predicted_lst for the specified season in a single query.
    """
    # 1. Verify city exists
    city_exists = db.query(City.city_id).filter(City.city_id == city_id).scalar()
    if not city_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id {city_id} not found",
        )

    # 2. Build query selecting cell_id and ST_AsGeoJSON(geom), optionally joining predicted_lst
    if season:
        query = (
            select(
                GridCell.cell_id,
                func.ST_AsGeoJSON(GridCell.geom).label("geojson_geom"),
                HeatPrediction.predicted_lst,
                GridCell.area_id,
                GridCell.zone_id,
            )
            .outerjoin(
                HeatPrediction,
                (HeatPrediction.cell_id == GridCell.cell_id) & (func.lower(HeatPrediction.season) == func.lower(season)),
            )
            .where(GridCell.city_id == city_id)
        )
    else:
        query = (
            select(
                GridCell.cell_id,
                func.ST_AsGeoJSON(GridCell.geom).label("geojson_geom"),
                literal(None).label("predicted_lst"),
                GridCell.area_id,
                GridCell.zone_id,
            )
            .where(GridCell.city_id == city_id)
        )

    # 3. Apply bbox filter if provided
    if bbox:
        min_lon, min_lat, max_lon, max_lat = parse_bbox(bbox)
        envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        query = query.where(func.ST_Intersects(GridCell.geom, envelope))

    # 4. Apply limit if provided
    if limit is not None and limit > 0:
        query = query.limit(limit)

    results = db.execute(query).fetchall()

    features: List[GridFeature] = []
    for row in results:
        cell_id = row[0]
        raw_geojson = row[1]
        predicted_lst = row[2]
        area_id = row[3] if len(row) > 3 else None
        zone_id = row[4] if len(row) > 4 else None
        geom_dict = json.loads(raw_geojson) if isinstance(raw_geojson, str) else raw_geojson
        features.append(
            GridFeature(
                geometry=geom_dict,
                properties=GridFeatureProperties(
                    cell_id=cell_id,
                    predicted_lst=predicted_lst,
                    area_id=area_id,
                    zone_id=zone_id,
                ),
            )
        )

    return GridFeatureCollection(features=features)

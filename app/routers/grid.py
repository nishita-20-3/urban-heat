from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.grid import GridFeatureCollection
from app.services.grid_service import get_grid_features

router = APIRouter(tags=["Spatial Grid"])


@router.get("/grid/{city_id}", response_model=GridFeatureCollection)
def get_city_grid(
    city_id: int,
    bbox: Optional[str] = Query(
        default=None,
        description="Bounding box filter formatted as 'min_lon,min_lat,max_lon,max_lat'",
        examples=["72.7,21.1,72.9,21.3"],
    ),
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        description="Maximum number of grid cell features to return",
    ),
    season: Optional[str] = Query(
        default=None,
        description="Optional season to pre-attach predicted_lst in GeoJSON properties (e.g. 'summer')",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns grid cells for a city as GeoJSON FeatureCollection using PostGIS ST_AsGeoJSON().
    Supports spatial bounding box (bbox), limit, and season query parameters.
    """
    return get_grid_features(db=db, city_id=city_id, bbox=bbox, limit=limit, season=season)

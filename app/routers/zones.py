from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.zone import ZoneFeatureCollection, ZoneSummaryResponse
from app.services.zone_service import get_zones_for_city, get_zone_summary

router = APIRouter(tags=["Municipal Zones"])


@router.get("/zones/{city_id}", response_model=ZoneFeatureCollection)
def get_city_zones(
    city_id: int,
    season: Optional[str] = Query(
        default="summer",
        description="Filter zonal thermal aggregation by season (e.g. 'summer', 'monsoon', 'postmonsoon', 'winter')",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns administrative zones for a city as GeoJSON FeatureCollection with aggregated
    temperature, hotspot count, LULC area, budget, and thermal priority rankings.
    """
    return get_zones_for_city(db=db, city_id=city_id, season=season)


@router.get("/zones/summary/{zone_id}", response_model=ZoneSummaryResponse)
def get_single_zone_summary(
    zone_id: int,
    season: Optional[str] = Query(
        default="summer",
        description="Filter summary by season",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns deep-dive summary metrics, land use distribution, and top recommended interventions for a specific zone.
    """
    return get_zone_summary(db=db, zone_id=zone_id, season=season)

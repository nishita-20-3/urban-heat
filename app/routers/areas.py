from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.area import AreaFeatureCollection, AreaDetailResponse
from app.services.area_service import get_areas_for_city, get_area_recommendations

router = APIRouter(tags=["Planning Areas"])


@router.get("/areas/{city_id}", response_model=AreaFeatureCollection)
def get_city_areas(
    city_id: int,
    season: Optional[str] = Query(
        default="summer",
        description="Filter area thermal aggregation by season ('summer', 'monsoon', 'postmonsoon', 'winter')",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns GeoJSON FeatureCollection of all Planning Areas in a city with land metrics,
    temperatures, hotspot counts, and realistic budgets.
    """
    return get_areas_for_city(db=db, city_id=city_id, season=season)


@router.get("/areas/detail/{area_id}", response_model=AreaDetailResponse)
def get_single_area_detail(
    area_id: int,
    season: Optional[str] = Query(
        default="summer",
        description="Filter detail by season",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns deep-dive land feasibility distribution, categorized recommendations 
    (Rooftops, Roads, Open Grounds, Water), and realistic CPWD budgets in ₹ Lakhs.
    """
    return get_area_recommendations(db=db, area_id=area_id, season=season)

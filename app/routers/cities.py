from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.spatial import City
from app.schemas.city import CityResponse

router = APIRouter(tags=["Cities"])


@router.get("/cities", response_model=List[CityResponse])
def get_cities(db: Session = Depends(get_db)):
    """
    Returns all cities registered in the cities table.
    """
    cities = (
        db.query(
            City.city_id,
            City.name,
            City.state,
            City.is_prototype,
        )
        .order_by(City.city_id)
        .all()
    )
    return [
        CityResponse(
            city_id=c[0],
            name=c[1],
            state=c[2],
            is_prototype=c[3],
        )
        for c in cities
    ]

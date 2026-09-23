from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import get_recommendations_for_cell

router = APIRouter(tags=["Recommendations"])


@router.get("/recommendations/{cell_id}", response_model=RecommendationResponse)
def get_cell_recommendations(
    cell_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns cooling intervention recommendations for a grid cell, grouped by scenario
    (e.g., 'max_cooling', 'balanced', 'budget').
    If the recommendations table does not exist or has no rows for this cell,
    returns 200 OK with an empty scenarios object.
    """
    return get_recommendations_for_cell(db=db, cell_id=cell_id)

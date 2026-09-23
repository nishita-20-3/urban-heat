from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.interventions import InterventionType
from app.schemas.intervention import InterventionTypeResponse

router = APIRouter(tags=["Interventions"])


@router.get("/interventions", response_model=List[InterventionTypeResponse])
def get_interventions(db: Session = Depends(get_db)):
    """
    Returns the full reference catalog of cooling intervention types,
    including unit costs, cooling coefficients, and applicability.
    """
    interventions = db.query(InterventionType).order_by(InterventionType.intervention_id).all()
    return interventions

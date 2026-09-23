from typing import Optional, List, Union, Dict
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.prediction import HeatPredictionResponse, ShapResponse, BulkPredictionRequest
from app.services.prediction_service import (
    get_predictions_for_cell,
    get_bulk_predictions_for_cells,
    get_shap_breakdown_for_cell,
)

router = APIRouter(tags=["Predictions & SHAP"])


@router.get("/predict/bulk", response_model=Dict[str, List[HeatPredictionResponse]])
def get_bulk_predictions(
    cell_ids: str = Query(
        ...,
        description="Comma-separated list of cell IDs (e.g. '72564,72565,72566')",
    ),
    season: Optional[str] = Query(
        default=None,
        description="Filter by season (e.g. 'summer', 'monsoon', 'postmonsoon', 'winter')",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns predicted LST for multiple grid cells in a single optimized query.
    """
    try:
        parsed_ids = [int(x.strip()) for x in cell_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cell_ids parameter must be a comma-separated list of integers",
        )
    return get_bulk_predictions_for_cells(db=db, cell_ids=parsed_ids, season=season)


@router.post("/predict/bulk", response_model=Dict[str, List[HeatPredictionResponse]])
def post_bulk_predictions(
    payload: BulkPredictionRequest,
    db: Session = Depends(get_db),
):
    """
    Returns predicted LST for multiple grid cells via JSON POST payload (useful for large batches).
    """
    return get_bulk_predictions_for_cells(db=db, cell_ids=payload.cell_ids, season=payload.season)


@router.get("/predict/{cell_id}", response_model=List[HeatPredictionResponse])
def get_cell_predictions(
    cell_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns predicted LST for a grid cell across all available seasons.
    If the cell exists but is not in the hot set (no predictions), returns [] with 200 OK.
    If the cell does not exist in grid_cells, returns 404.
    """
    return get_predictions_for_cell(db=db, cell_id=cell_id)


@router.get("/shap/{cell_id}", response_model=Union[ShapResponse, List[ShapResponse]])
def get_cell_shap(
    cell_id: int,
    season: Optional[str] = Query(
        default=None,
        description="Filter by season (e.g. 'summer', 'monsoon', 'postmonsoon', 'winter'). If omitted, returns all available seasons.",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns SHAP feature contribution breakdown for a grid cell's heat prediction.
    If season query param is provided, returns single ShapResponse object.
    If season is omitted, returns a list of ShapResponse objects across all available seasons.
    """
    return get_shap_breakdown_for_cell(db=db, cell_id=cell_id, season=season)

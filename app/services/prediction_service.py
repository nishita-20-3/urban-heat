import json
from typing import Optional, List, Union, Any, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.spatial import GridCell
from app.models.predictions import HeatPrediction
from app.schemas.prediction import HeatPredictionResponse, ShapResponse


def verify_cell_exists(db: Session, cell_id: int) -> None:
    """
    Check if a grid cell exists in the grid_cells table.
    Raises a 404 HTTPException if not found.
    """
    cell_exists = db.query(GridCell.cell_id).filter(GridCell.cell_id == cell_id).scalar()
    if not cell_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid cell with ID {cell_id} not found",
        )


def get_predictions_for_cell(db: Session, cell_id: int) -> List[HeatPredictionResponse]:
    """
    Returns predicted LST for a cell across all seasons available in heat_predictions.
    If the cell exists but is not in the hot cell set (no prediction rows),
    returns an empty list with 200 OK.
    """
    verify_cell_exists(db, cell_id)

    predictions = (
        db.query(HeatPrediction)
        .filter(HeatPrediction.cell_id == cell_id)
        .order_by(HeatPrediction.season)
        .all()
    )

    return [
        HeatPredictionResponse(
            season=p.season,
            predicted_lst=p.predicted_lst,
            actual_lst=p.actual_lst,
            prediction_date=p.prediction_date,
        )
        for p in predictions
    ]


def get_bulk_predictions_for_cells(
    db: Session,
    cell_ids: List[int],
    season: Optional[str] = None,
) -> Dict[str, List[HeatPredictionResponse]]:
    """
    Returns predicted LST for a list of cells in a single optimized SQL query.
    Returns mapping of stringified cell_id -> List[HeatPredictionResponse].
    """
    if not cell_ids:
        return {}

    query = db.query(HeatPrediction).filter(HeatPrediction.cell_id.in_(cell_ids))
    if season:
        query = query.filter(func.lower(HeatPrediction.season) == func.lower(season))

    predictions = query.order_by(HeatPrediction.cell_id, HeatPrediction.season).all()

    result: Dict[str, List[HeatPredictionResponse]] = {str(cid): [] for cid in cell_ids}
    for p in predictions:
        str_id = str(p.cell_id)
        if str_id not in result:
            result[str_id] = []
        result[str_id].append(
            HeatPredictionResponse(
                season=p.season,
                predicted_lst=p.predicted_lst,
                actual_lst=p.actual_lst,
                prediction_date=p.prediction_date,
            )
        )
    return result


def parse_shap_data(
    cell_id: int,
    season: str,
    predicted_lst: float,
    raw_shap: Any,
) -> ShapResponse:
    """
    Extract and structure base value and feature contributions from the JSONB shap_values column.
    """
    if raw_shap is None:
        return ShapResponse(
            cell_id=cell_id,
            season=season,
            predicted_lst=predicted_lst,
            shap_base_value=None,
            shap_contributions={},
        )

    if isinstance(raw_shap, str):
        try:
            raw_shap = json.loads(raw_shap)
        except Exception:
            raw_shap = {}

    if not isinstance(raw_shap, dict):
        raw_shap = {}

    base_val = None
    contributions: Dict[str, float] = {}

    if "contributions" in raw_shap and isinstance(raw_shap["contributions"], dict):
        contributions = {str(k): float(v) for k, v in raw_shap["contributions"].items() if v is not None}
        if "base_value" in raw_shap:
            base_val = float(raw_shap["base_value"])
        elif "shap_base_value" in raw_shap:
            base_val = float(raw_shap["shap_base_value"])
    elif "shap_contributions" in raw_shap and isinstance(raw_shap["shap_contributions"], dict):
        contributions = {str(k): float(v) for k, v in raw_shap["shap_contributions"].items() if v is not None}
        if "shap_base_value" in raw_shap:
            base_val = float(raw_shap["shap_base_value"])
        elif "base_value" in raw_shap:
            base_val = float(raw_shap["base_value"])
    else:
        for k, v in raw_shap.items():
            if k in ("base_value", "shap_base_value", "_base_value") and v is not None:
                try:
                    base_val = float(v)
                except (ValueError, TypeError):
                    pass
            elif v is not None:
                try:
                    contributions[str(k)] = float(v)
                except (ValueError, TypeError):
                    pass

    # If base_value is not explicitly provided in the json, compute it via predicted_lst - sum(contributions)
    if base_val is None and contributions:
        sum_contribs = sum(contributions.values())
        base_val = round(predicted_lst - sum_contribs, 4)

    return ShapResponse(
        cell_id=cell_id,
        season=season,
        predicted_lst=predicted_lst,
        shap_base_value=base_val,
        shap_contributions=contributions,
    )


def get_shap_breakdown_for_cell(
    db: Session,
    cell_id: int,
    season: Optional[str] = None,
) -> Union[ShapResponse, List[ShapResponse]]:
    """
    Returns the SHAP value breakdown for a cell.
    If season is specified: returns single ShapResponse or 404 if no prediction for that season.
    If season is omitted: returns List[ShapResponse] across all available seasons.
    """
    verify_cell_exists(db, cell_id)

    query = db.query(HeatPrediction).filter(HeatPrediction.cell_id == cell_id)

    if season:
        prediction = query.filter(HeatPrediction.season.ilike(season)).first()
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No heat prediction found for cell {cell_id} for season '{season}'",
            )
        return parse_shap_data(
            cell_id=prediction.cell_id,
            season=prediction.season,
            predicted_lst=prediction.predicted_lst,
            raw_shap=prediction.shap_values,
        )
    else:
        predictions = query.order_by(HeatPrediction.season).all()
        return [
            parse_shap_data(
                cell_id=p.cell_id,
                season=p.season,
                predicted_lst=p.predicted_lst,
                raw_shap=p.shap_values,
            )
            for p in predictions
        ]

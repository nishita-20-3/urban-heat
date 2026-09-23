from datetime import date
from typing import Optional, Dict, List
from pydantic import BaseModel, ConfigDict


class HeatPredictionResponse(BaseModel):
    season: str
    predicted_lst: float
    actual_lst: Optional[float] = None
    prediction_date: date

    model_config = ConfigDict(from_attributes=True)


class BulkPredictionItem(BaseModel):
    cell_id: int
    season: str
    predicted_lst: float
    actual_lst: Optional[float] = None
    prediction_date: date

    model_config = ConfigDict(from_attributes=True)


class BulkPredictionRequest(BaseModel):
    cell_ids: List[int]
    season: Optional[str] = None


class ShapResponse(BaseModel):
    cell_id: int
    season: str
    predicted_lst: float
    shap_base_value: Optional[float] = None
    shap_contributions: Dict[str, float]

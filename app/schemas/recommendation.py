from typing import Dict, List
from pydantic import BaseModel


class InterventionItem(BaseModel):
    name: str
    quantity: float
    unit: str
    cooling_contribution_c: float
    cost_inr: float


class ScenarioDetail(BaseModel):
    total_cooling_c: float
    total_cost_inr: float
    interventions: List[InterventionItem]


class RecommendationResponse(BaseModel):
    cell_id: int
    scenarios: Dict[str, ScenarioDetail]

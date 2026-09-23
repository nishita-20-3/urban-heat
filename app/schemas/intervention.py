from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class InterventionTypeResponse(BaseModel):
    intervention_id: int
    name: str
    unit: str
    cost_per_unit: float
    cooling_coefficient: float
    cooling_unit: str
    applicable_lulc_classes: Optional[List[str]] = None
    data_confidence: str
    notes: Optional[str] = None
    coverage_ratio: float
    max_cooling_ceiling: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

from typing import List, Any, Dict, Literal, Optional
from pydantic import BaseModel


class GridFeatureProperties(BaseModel):
    cell_id: int
    predicted_lst: Optional[float] = None
    area_id: Optional[int] = None
    zone_id: Optional[int] = None


class GridFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: Dict[str, Any]
    properties: GridFeatureProperties


class GridFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GridFeature]

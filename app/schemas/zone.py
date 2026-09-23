from typing import List, Any, Dict, Literal, Optional
from pydantic import BaseModel


class ZoneProperties(BaseModel):
    zone_id: int
    name: str
    code: str
    description: Optional[str] = None
    color: Optional[str] = None
    avg_lst: float
    peak_lst: float
    hotspot_cell_count: int
    total_cell_count: int
    priority_level: str  # 'High', 'Moderate', 'Low'
    built_up_area_sqm: float
    open_area_sqm: float
    green_cover_sqm: float
    total_budget_inr: float
    avg_cooling_potential_c: float


class ZoneFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: Dict[str, Any]
    properties: ZoneProperties


class ZoneFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[ZoneFeature]


class TopInterventionSummary(BaseModel):
    name: str
    display_name: str
    total_quantity: float
    unit: str
    total_cooling_c: float
    total_cost_inr: float


class ZoneSummaryResponse(BaseModel):
    zone_id: int
    name: str
    code: str
    description: Optional[str] = None
    color: Optional[str] = None
    priority_level: str
    avg_lst: float
    peak_lst: float
    hotspot_cell_count: int
    total_cell_count: int
    built_up_sqm: float
    open_soil_sqm: float
    tree_cover_sqm: float
    water_sqm: float
    total_budget_inr: float
    avg_cooling_potential_c: float
    top_interventions: List[TopInterventionSummary]

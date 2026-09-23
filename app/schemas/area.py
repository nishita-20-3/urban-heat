from typing import List, Any, Dict, Literal, Optional
from pydantic import BaseModel


class AreaProperties(BaseModel):
    area_id: int
    zone_id: int
    city_id: int
    name: str
    code: str
    area_type: str
    is_hotspot: bool = False
    description: Optional[str] = None
    building_rooftop_sqm: float
    road_paved_sqm: float
    open_ground_sqm: float
    water_body_sqm: float
    existing_tree_cover_sqm: float
    total_land_area_sqm: float
    avg_lst: float
    peak_lst: float
    hotspot_cell_count: int
    total_cell_count: int
    priority_level: str  # 'High', 'Moderate', 'Low'
    total_budget_inr: float
    avg_cooling_potential_c: float


class AreaFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: Dict[str, Any]
    properties: AreaProperties


class AreaFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[AreaFeature]


class LandCategoryIntervention(BaseModel):
    category: Literal["rooftop", "road", "open_ground", "water_body"]
    category_title: str
    available_land_sqm: float
    targeted_measure: str
    recommended_quantity: float
    unit: str
    cost_per_unit_inr: float
    total_cost_inr: float
    cooling_drop_c: float
    feasibility_check: str
    engineering_rationale: str
    recommended_materials_species: List[str]


class LandDistribution(BaseModel):
    building_rooftop_sqm: float
    building_pct: float
    road_paved_sqm: float
    road_pct: float
    open_ground_sqm: float
    open_pct: float
    water_body_sqm: float
    water_pct: float
    existing_tree_cover_sqm: float
    tree_pct: float
    total_area_sqm: float


class AreaDetailResponse(BaseModel):
    area_id: int
    zone_id: int
    zone_name: str
    city_id: int
    name: str
    code: str
    area_type: str
    is_hotspot: bool = False
    description: Optional[str] = None
    avg_lst: float
    peak_lst: float
    priority_level: str
    hotspot_cell_count: int
    total_cell_count: int
    land_distribution: LandDistribution
    rooftop_interventions: List[LandCategoryIntervention]
    road_interventions: List[LandCategoryIntervention]
    open_ground_interventions: List[LandCategoryIntervention]
    water_interventions: List[LandCategoryIntervention]
    total_budget_inr: float
    total_cooling_potential_c: float
    implementation_timeline: str

export interface City {
  city_id: number;
  name: string;
  state: string;
  is_prototype: boolean;
  latitude?: number;
  longitude?: number;
}

export interface ZoneProperties {
  zone_id: number;
  name: string;
  code: string;
  description?: string;
  color?: string;
  avg_lst: number;
  peak_lst: number;
  hotspot_cell_count: number;
  total_cell_count: number;
  priority_level: 'High' | 'Moderate' | 'Low' | string;
  built_up_area_sqm: number;
  open_area_sqm: number;
  green_cover_sqm: number;
  total_budget_inr: number;
  avg_cooling_potential_c: number;
}

export interface ZoneFeature {
  type: "Feature";
  geometry: {
    type: "MultiPolygon" | "Polygon";
    coordinates: any;
  };
  properties: ZoneProperties;
}

export interface ZoneFeatureCollection {
  type: "FeatureCollection";
  features: ZoneFeature[];
}

export interface TopInterventionSummary {
  name: string;
  display_name: string;
  total_quantity: number;
  unit: string;
  total_cooling_c: number;
  total_cost_inr: number;
}

export interface ZoneSummaryResponse {
  zone_id: number;
  name: string;
  code: string;
  description?: string;
  color?: string;
  priority_level: string;
  avg_lst: number;
  peak_lst: number;
  hotspot_cell_count: number;
  total_cell_count: number;
  built_up_sqm: number;
  open_soil_sqm: number;
  tree_cover_sqm: number;
  water_sqm: number;
  total_budget_inr: number;
  avg_cooling_potential_c: number;
  top_interventions: TopInterventionSummary[];
}

export interface GridFeatureProperties {
  cell_id: number;
  predicted_lst?: number;
  area_id?: number | null;
  zone_id?: number | null;
}

export interface GridFeature {
  type: "Feature";
  geometry: {
    type: "Polygon";
    coordinates: number[][][];
  };
  properties: GridFeatureProperties;
}

export interface GridFeatureCollection {
  type: "FeatureCollection";
  features: GridFeature[];
}

export interface HeatPrediction {
  season: "summer" | "monsoon" | "postmonsoon" | "winter" | string;
  predicted_lst: number;
  actual_lst: number | null;
  prediction_date: string;
}

export interface ShapResponse {
  cell_id: number;
  season: string;
  predicted_lst: number;
  shap_base_value: number | null;
  shap_contributions: Record<string, number>;
}

export interface InterventionItem {
  name: string;
  quantity: number;
  unit: string;
  cooling_contribution_c: number;
  cost_inr: number;
}

export interface ScenarioDetail {
  total_cooling_c: number;
  total_cost_inr: number;
  interventions: InterventionItem[];
}

export interface RecommendationResponse {
  cell_id: number;
  scenarios: {
    max_cooling?: ScenarioDetail;
    balanced?: ScenarioDetail;
    budget?: ScenarioDetail;
    [key: string]: ScenarioDetail | undefined;
  };
}

export interface AreaProperties {
  area_id: number;
  zone_id: number;
  city_id: number;
  name: string;
  code: string;
  area_type: string;
  is_hotspot?: boolean;
  description?: string;
  building_rooftop_sqm: number;
  road_paved_sqm: number;
  open_ground_sqm: number;
  water_body_sqm: number;
  existing_tree_cover_sqm: number;
  total_land_area_sqm: number;
  avg_lst: number;
  peak_lst: number;
  hotspot_cell_count: number;
  total_cell_count: number;
  priority_level: 'High' | 'Moderate' | 'Low' | string;
  total_budget_inr: number;
  avg_cooling_potential_c: number;
}

export interface AreaFeature {
  type: "Feature";
  geometry: {
    type: "MultiPolygon" | "Polygon";
    coordinates: any;
  };
  properties: AreaProperties;
}

export interface AreaFeatureCollection {
  type: "FeatureCollection";
  features: AreaFeature[];
}

export interface LandCategoryIntervention {
  category: "rooftop" | "road" | "open_ground" | "water_body";
  category_title: string;
  available_land_sqm: number;
  targeted_measure: string;
  recommended_quantity: number;
  unit: string;
  cost_per_unit_inr: number;
  total_cost_inr: number;
  cooling_drop_c: number;
  feasibility_check: string;
  engineering_rationale: string;
  recommended_materials_species: string[];
}

export interface LandDistribution {
  building_rooftop_sqm: number;
  building_pct: number;
  road_paved_sqm: number;
  road_pct: number;
  open_ground_sqm: number;
  open_pct: number;
  water_body_sqm: number;
  water_pct: number;
  existing_tree_cover_sqm: number;
  tree_pct: number;
  total_area_sqm: number;
}

export interface AreaDetailResponse {
  area_id: number;
  zone_id: number;
  zone_name: string;
  city_id: number;
  name: string;
  code: string;
  area_type: string;
  is_hotspot?: boolean;
  description?: string;
  avg_lst: number;
  peak_lst: number;
  priority_level: string;
  hotspot_cell_count: number;
  total_cell_count: number;
  land_distribution: LandDistribution;
  rooftop_interventions: LandCategoryIntervention[];
  road_interventions: LandCategoryIntervention[];
  open_ground_interventions: LandCategoryIntervention[];
  water_interventions: LandCategoryIntervention[];
  total_budget_inr: number;
  total_cooling_potential_c: number;
  implementation_timeline: string;
}

export type ConfidenceLevel = 'strong' | 'moderate' | 'weak';

export interface InterventionType {
  intervention_id: number;
  name: string;
  unit: string;
  cost_per_unit: number;
  cooling_coefficient: number;
  cooling_unit: string;
  applicable_lulc_classes: string[] | null;
  data_confidence: ConfidenceLevel;
  notes: string | null;
  coverage_ratio: number;
  max_cooling_ceiling: number | null;
}

export interface HealthStatus {
  status: string;
  database: string;
  details?: string | null;
}

export type Season = 'summer' | 'monsoon' | 'postmonsoon' | 'winter';
export type ViewMode = 'zones' | 'areas' | 'cells';


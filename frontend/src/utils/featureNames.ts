/**
 * Mapping of raw model feature keys to professional, planner-friendly names and descriptions.
 */

export interface FeatureMeta {
  displayName: string;
  category: 'satellite' | 'weather' | 'lulc' | 'season';
  unit?: string;
  description: string;
}

export const FEATURE_METADATA: Record<string, FeatureMeta> = {
  ndbi: {
    displayName: 'NDBI (Built-up Index)',
    category: 'satellite',
    unit: 'index (-1 to +1)',
    description: 'Normalized Difference Built-up Index; highlights concrete, asphalt, and dense impervious surfaces.',
  },
  ndvi: {
    displayName: 'NDVI (Vegetation Index)',
    category: 'satellite',
    unit: 'index (-1 to +1)',
    description: 'Normalized Difference Vegetation Index; measures healthy green plant biomass.',
  },
  air_temp: {
    displayName: 'Air Temperature (2m ERA5)',
    category: 'weather',
    unit: '°C',
    description: 'Near-surface ambient air temperature from ECMWF ERA5 reanalysis.',
  },
  humidity: {
    displayName: 'Relative Humidity',
    category: 'weather',
    unit: '%',
    description: 'Atmospheric moisture content affecting evaporative cooling.',
  },
  wind_speed: {
    displayName: 'Surface Wind Speed',
    category: 'weather',
    unit: 'm/s',
    description: 'Wind velocity at 10m height facilitating convective heat dissipation.',
  },
  'Built-up_pct': {
    displayName: 'Built-up Land Area',
    category: 'lulc',
    unit: '%',
    description: 'Percentage of cell covered by buildings, paved roads, and infrastructure.',
  },
  'Tree cover_pct': {
    displayName: 'Tree Canopy Cover',
    category: 'lulc',
    unit: '%',
    description: 'Percentage of cell covered by dense tree crown providing shading and transpiration.',
  },
  'Cropland_pct': {
    displayName: 'Cropland & Open Fields',
    category: 'lulc',
    unit: '%',
    description: 'Agricultural plots or seasonal cultivation zones.',
  },
  'Grassland_pct': {
    displayName: 'Grassland & Turf',
    category: 'lulc',
    unit: '%',
    description: 'Short vegetation, open lawns, and vacant unpaved ground.',
  },
  'Bare / sparse vegetation_pct': {
    displayName: 'Bare Soil / Exposed Ground',
    category: 'lulc',
    unit: '%',
    description: 'Dry, barren soil or cleared land with high thermal inertia.',
  },
  'Permanent water bodies_pct': {
    displayName: 'Permanent Water Bodies',
    category: 'lulc',
    unit: '%',
    description: 'Lakes, rivers, ponds, and reservoirs offering direct evaporative cooling.',
  },
  'Mangroves_pct': {
    displayName: 'Coastal Mangrove Cover',
    category: 'lulc',
    unit: '%',
    description: 'Tidal saline wetland vegetation along Surat estuarine channels.',
  },
  'Herbaceous wetland_pct': {
    displayName: 'Herbaceous Wetlands',
    category: 'lulc',
    unit: '%',
    description: 'Marshes and periodically inundated wetland areas.',
  },
  'Shrubland_pct': {
    displayName: 'Shrubland / Scrub',
    category: 'lulc',
    unit: '%',
    description: 'Low woody vegetation and perennial scrub.',
  },
  season_summer: {
    displayName: 'Summer Seasonal Effect',
    category: 'season',
    description: 'Base temperature shift specific to the peak summer dry period (March–May).',
  },
  season_monsoon: {
    displayName: 'Monsoon Seasonal Effect',
    category: 'season',
    description: 'Base temperature shift during the south-west monsoon rainfall months.',
  },
  season_postmonsoon: {
    displayName: 'Post-Monsoon Seasonal Effect',
    category: 'season',
    description: 'Base temperature shift during post-monsoon transition (October–November).',
  },
  season_winter: {
    displayName: 'Winter Seasonal Effect',
    category: 'season',
    description: 'Base temperature shift during winter months (December–February).',
  },
};

/**
 * Returns a human-friendly label for any model feature key.
 */
export function formatFeatureName(rawKey: string): string {
  if (FEATURE_METADATA[rawKey]) {
    return FEATURE_METADATA[rawKey].displayName;
  }
  // Fallback cleanup
  return rawKey
    .replace(/_pct$/i, ' %')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Human-readable names and icons for the 7 standard interventions.
 */
export const INTERVENTION_METADATA: Record<
  string,
  { label: string; icon: string; category: string; description: string }
> = {
  tree_planting: {
    label: 'Urban Tree Canopy Planting',
    icon: 'Trees',
    category: 'Nature-Based',
    description: 'Planting native shade trees (Neem, Peepal, Gulmohar) in open soil and road verges.',
  },
  cool_roofing: {
    label: 'High-Albedo Cool Roofing',
    icon: 'Home',
    category: 'Material / Albedo',
    description: 'Reflective solar coating or lime wash on residential and commercial building rooftops.',
  },
  green_corridors_parks: {
    label: 'Green Corridors & Pocket Parks',
    icon: 'Flower2',
    category: 'Nature-Based',
    description: 'Connected urban green spaces and micro-parks along transit corridors.',
  },
  permeable_pavement: {
    label: 'Permeable & Porous Pavements',
    icon: 'Grid',
    category: 'Hydrological',
    description: 'Interlocking porous pavers facilitating moisture retention and lower surface heat capacity.',
  },
  green_walls: {
    label: 'Vertical Living Walls (Green Facades)',
    icon: 'Layers',
    category: 'Nature-Based',
    description: 'Modular vegetated building facade systems reducing wall surface absorption.',
  },
  constructed_water_bodies: {
    label: 'Constructed Water Bodies & Retention Ponds',
    icon: 'Droplets',
    category: 'Hydrological',
    description: 'Urban retention ponds and bio-swales providing localized evaporative microclimate cooling.',
  },
  shade_structures: {
    label: 'Engineered Shading & Tensile Canopies',
    icon: 'Umbrella',
    category: 'Engineered',
    description: 'High-tensile UV reflective shade canopies over public walkways, markets, and bus stops.',
  },
};

export function formatInterventionName(rawName: string): string {
  if (INTERVENTION_METADATA[rawName]) {
    return INTERVENTION_METADATA[rawName].label;
  }
  return rawName.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

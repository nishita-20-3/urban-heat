/**
 * Color scales for Urban Heat choropleth mapping and data visualization.
 * Strictly adheres to the project palette:
 * - Teal/Cyan (#0FB5AE) for cool zones
 * - Transition through Amber (#F59E0B) and Warm Orange (#F97316)
 * - Orange-Red (#E8543E) for high heat / hot zones
 * - Deep Red (#D63031) for extreme thermal hotspots
 */

export interface TempCategory {
  label: string;
  min: number;
  max: number;
  color: string;
  fillOpacity: number;
  description: string;
}

export const TEMPERATURE_BINS: TempCategory[] = [
  {
    label: '< 38°C',
    min: 0,
    max: 38,
    color: '#06B6D4', // Cool Cyan / Blue (Tapi riverfront & water corridors)
    fillOpacity: 0.55,
    description: 'Cool corridors, water bodies & riverfront parks',
  },
  {
    label: '38°C – 42°C',
    min: 38,
    max: 42,
    color: '#10B981', // Emerald Green (Botanic parks, low-density green verges)
    fillOpacity: 0.55,
    description: 'Moderate surface temperatures / Suburban green cover',
  },
  {
    label: '42°C – 45°C',
    min: 42,
    max: 45,
    color: '#F59E0B', // Amber (Standard residential & mixed urban)
    fillOpacity: 0.6,
    description: 'Elevated urban built-up threshold',
  },
  {
    label: '45°C – 48°C',
    min: 45,
    max: 48,
    color: '#F97316', // Warm Orange (High heat zone / dense urban fabric)
    fillOpacity: 0.65,
    description: 'High heat zone / Dense urban fabric',
  },
  {
    label: '48°C – 50°C',
    min: 48,
    max: 50,
    color: '#E8543E', // Orange-Red / Critical
    fillOpacity: 0.72,
    description: 'Critical heat vulnerability area',
  },
  {
    label: '> 50°C',
    min: 50,
    max: 100,
    color: '#D63031', // Deep Crimson / Extreme Hotspot
    fillOpacity: 0.8,
    description: 'Extreme thermal hotspot (Pandesara GIDC, Katargam)',
  },
];

/**
 * Returns the hex color for a given Land Surface Temperature (°C).
 */
export function getLSTColor(temp: number | undefined | null): string {
  if (temp === undefined || temp === null || isNaN(temp)) {
    return '#334155'; // Muted slate gray for cells without data
  }
  for (const bin of TEMPERATURE_BINS) {
    if (temp < bin.max) {
      return bin.color;
    }
  }
  return '#D63031';
}

/**
 * Returns the fill opacity for a given LST.
 */
export function getLSTOpacity(temp: number | undefined | null): number {
  if (temp === undefined || temp === null || isNaN(temp)) {
    return 0.2;
  }
  if (temp > 48) return 0.75;
  if (temp > 44) return 0.65;
  return 0.55;
}

/**
 * SHAP Bar Colors:
 * - Positive SHAP (pushes temp up / warming): Orange-Red (#E8543E)
 * - Negative SHAP (pushes temp down / cooling): Teal (#0FB5AE)
 */
export const SHAP_COLORS = {
  positive: '#E8543E', // Warming driver
  negative: '#0FB5AE', // Cooling driver
  neutral: '#64748B',
  base: '#38BDF8',
};

import type {
  City,
  ZoneFeatureCollection,
  ZoneSummaryResponse,
  AreaFeatureCollection,
  AreaDetailResponse,
  GridFeatureCollection,
  HeatPrediction,
  ShapResponse,
  RecommendationResponse,
  InterventionType,
  HealthStatus,
} from './types';

// Use environment variable if specified; in dev mode default to '' (Vite proxy) or http://127.0.0.1:8000
const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : (import.meta.env.DEV ? '' : 'http://127.0.0.1:8000');

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' 
            ? errorJson.detail 
            : JSON.stringify(errorJson.detail);
        }
      } catch {
        // ignore json parse error
      }
      throw new Error(errorDetail);
    }

    return response.json() as Promise<T>;
  } catch (err: any) {
    // If relative fetch failed and base URL was empty, attempt direct 127.0.0.1 fallback
    if (API_BASE_URL === '' && !url.startsWith('http')) {
      const fallbackUrl = `http://127.0.0.1:8000${endpoint}`;
      const response = await fetch(fallbackUrl, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json() as Promise<T>;
    }
    throw err;
  }
}

export const api = {
  getHealth: async (signal?: AbortSignal): Promise<HealthStatus> => {
    return fetchJson<HealthStatus>('/health', { signal });
  },

  getCities: async (signal?: AbortSignal): Promise<City[]> => {
    return fetchJson<City[]>('/cities', { signal });
  },

  getZones: async (
    cityId: number,
    season?: string,
    signal?: AbortSignal
  ): Promise<ZoneFeatureCollection> => {
    const params = season ? `?season=${encodeURIComponent(season)}` : '';
    return fetchJson<ZoneFeatureCollection>(`/zones/${cityId}${params}`, { signal });
  },

  getZoneSummary: async (
    zoneId: number,
    season?: string,
    signal?: AbortSignal
  ): Promise<ZoneSummaryResponse> => {
    const params = season ? `?season=${encodeURIComponent(season)}` : '';
    return fetchJson<ZoneSummaryResponse>(`/zones/summary/${zoneId}${params}`, { signal });
  },

  getAreas: async (
    cityId: number,
    season?: string,
    signal?: AbortSignal
  ): Promise<AreaFeatureCollection> => {
    const params = season ? `?season=${encodeURIComponent(season)}` : '';
    return fetchJson<AreaFeatureCollection>(`/areas/${cityId}${params}`, { signal });
  },

  getAreaDetail: async (
    areaId: number,
    season?: string,
    signal?: AbortSignal
  ): Promise<AreaDetailResponse> => {
    const params = season ? `?season=${encodeURIComponent(season)}` : '';
    return fetchJson<AreaDetailResponse>(`/areas/detail/${areaId}${params}`, { signal });
  },

  getGrid: async (
    cityId: number,
    bbox: string,
    limit?: number,
    season?: string,
    signal?: AbortSignal
  ): Promise<GridFeatureCollection> => {
    const params = new URLSearchParams({ bbox });
    if (limit) {
      params.append('limit', limit.toString());
    }
    if (season) {
      params.append('season', season);
    }
    return fetchJson<GridFeatureCollection>(`/grid/${cityId}?${params.toString()}`, { signal });
  },

  getPredictions: async (cellId: number, signal?: AbortSignal): Promise<HeatPrediction[]> => {
    return fetchJson<HeatPrediction[]>(`/predict/${cellId}`, { signal });
  },

  getBulkPredictions: async (
    cellIds: number[],
    season?: string,
    signal?: AbortSignal
  ): Promise<Record<string, HeatPrediction[]>> => {
    return fetchJson<Record<string, HeatPrediction[]>>('/predict/bulk', {
      method: 'POST',
      body: JSON.stringify({ cell_ids: cellIds, season }),
      signal,
    });
  },

  getShap: async (cellId: number, season?: string, signal?: AbortSignal): Promise<ShapResponse> => {
    const params = season ? `?season=${encodeURIComponent(season)}` : '';
    const res = await fetchJson<ShapResponse | ShapResponse[]>(`/shap/${cellId}${params}`, { signal });
    if (Array.isArray(res)) {
      return res[0];
    }
    return res;
  },

  getRecommendations: async (
    cellId: number,
    signal?: AbortSignal
  ): Promise<RecommendationResponse> => {
    return fetchJson<RecommendationResponse>(`/recommendations/${cellId}`, { signal });
  },

  getInterventions: async (signal?: AbortSignal): Promise<InterventionType[]> => {
    return fetchJson<InterventionType[]>('/interventions', { signal });
  },
};

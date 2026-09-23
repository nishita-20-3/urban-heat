import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../api/client';
import type { GridFeature, HeatPrediction, Season } from '../api/types';

interface UseGridDataProps {
  cityId: number | null;
  bbox: string | null;
  selectedSeason: Season;
  zoomLevel: number;
}

export function useGridData({ cityId, bbox, selectedSeason, zoomLevel }: UseGridDataProps) {
  const [features, setFeatures] = useState<GridFeature[]>([]);
  const [isLoadingGrid, setIsLoadingGrid] = useState<boolean>(false);
  const [gridError, setGridError] = useState<string | null>(null);
  
  // Cache of cell_id -> HeatPrediction[]
  const [predictionCache, setPredictionCache] = useState<Record<number, HeatPrediction[]>>({});
  const predictionCacheRef = useRef<Record<number, HeatPrediction[]>>({});
  predictionCacheRef.current = predictionCache;

  const activeFetchAbortRef = useRef<AbortController | null>(null);

  // 1. Fetch spatial grid cells with pre-joined predicted_lst for the active season
  useEffect(() => {
    if (cityId === null || bbox === null || zoomLevel < 11) {
      if (zoomLevel < 11) {
        setFeatures([]);
      }
      return;
    }

    const currentCityId = cityId;
    const currentBbox = bbox;
    const currentSeason = selectedSeason;

    if (activeFetchAbortRef.current) {
      activeFetchAbortRef.current.abort();
    }
    const controller = new AbortController();
    activeFetchAbortRef.current = controller;

    async function loadGrid() {
      setIsLoadingGrid(true);
      setGridError(null);

      try {
        // Fetch spatial grid cells with season-specific LST in a single optimized database query
        const res = await api.getGrid(
          currentCityId,
          currentBbox,
          undefined,
          currentSeason,
          controller.signal
        );
        
        if (!controller.signal.aborted) {
          const rawFeatures = res.features || [];
          setFeatures(rawFeatures);

          // Pre-populate prediction cache from returned features
          const seeded: Record<number, HeatPrediction[]> = {};
          for (const f of rawFeatures) {
            const cid = f.properties.cell_id;
            const lst = f.properties.predicted_lst;
            if (lst !== undefined && lst !== null) {
              const existing = predictionCacheRef.current[cid] || [];
              const otherSeasons = existing.filter((p) => p.season.toLowerCase() !== currentSeason.toLowerCase());
              seeded[cid] = [
                ...otherSeasons,
                {
                  season: currentSeason,
                  predicted_lst: lst,
                  actual_lst: null,
                  prediction_date: new Date().toISOString().split('T')[0],
                },
              ];
            }
          }
          if (Object.keys(seeded).length > 0) {
            setPredictionCache((prev) => ({ ...prev, ...seeded }));
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          setGridError(err.message || 'Failed to fetch spatial grid');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingGrid(false);
        }
      }
    }

    loadGrid();

    return () => {
      controller.abort();
    };
  }, [cityId, bbox, selectedSeason, zoomLevel]);

  // Helper to fetch full prediction record across all seasons for a single clicked cell
  const fetchCellPrediction = useCallback(async (cellId: number) => {
    try {
      const preds = await api.getPredictions(cellId);
      setPredictionCache((prev) => ({ ...prev, [cellId]: preds }));
      return preds;
    } catch {
      return [];
    }
  }, []);

  // Helper to get predicted LST for a specific season
  const getCellLST = useCallback(
    (cellId: number, season: Season = selectedSeason): number | null => {
      // 1. Check feature properties directly
      const feature = features.find((f) => f.properties.cell_id === cellId);
      if (feature && feature.properties.predicted_lst !== undefined && feature.properties.predicted_lst !== null) {
        return feature.properties.predicted_lst;
      }
      // 2. Check cached prediction array
      const preds = predictionCache[cellId];
      if (!preds || preds.length === 0) return null;
      const match = preds.find((p) => p.season.toLowerCase() === season.toLowerCase());
      return match ? match.predicted_lst : null;
    },
    [features, predictionCache, selectedSeason]
  );

  return {
    features,
    isLoadingGrid,
    gridError,
    predictionCache,
    fetchCellPrediction,
    getCellLST,
  };
}

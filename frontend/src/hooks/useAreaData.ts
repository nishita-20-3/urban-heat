import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { AreaFeature, AreaDetailResponse, Season } from '../api/types';

interface UseAreaDataProps {
  cityId: number | null;
  selectedSeason: Season;
}

export function useAreaData({ cityId, selectedSeason }: UseAreaDataProps) {
  const [areas, setAreas] = useState<AreaFeature[]>([]);
  const [isLoadingAreas, setIsLoadingAreas] = useState<boolean>(false);
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(null);
  const [selectedAreaDetail, setSelectedAreaDetail] = useState<AreaDetailResponse | null>(null);
  const [isLoadingAreaDetail, setIsLoadingAreaDetail] = useState<boolean>(false);

  // 1. Fetch all planning areas for city & season
  useEffect(() => {
    if (cityId === null) return;
    const currentCityId = cityId;

    const controller = new AbortController();

    async function loadAreas() {
      setIsLoadingAreas(true);
      try {
        const res = await api.getAreas(currentCityId, selectedSeason, controller.signal);
        if (!controller.signal.aborted) {
          setAreas(res.features || []);
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('Failed to load planning areas:', err);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingAreas(false);
        }
      }
    }

    loadAreas();

    return () => {
      controller.abort();
    };
  }, [cityId, selectedSeason]);

  // 2. Fetch area deep-dive land feasibility detail when an area is selected
  useEffect(() => {
    if (selectedAreaId === null) {
      setSelectedAreaDetail(null);
      return;
    }
    const currentAreaId = selectedAreaId;

    const controller = new AbortController();

    async function loadDetail() {
      setIsLoadingAreaDetail(true);
      try {
        const res = await api.getAreaDetail(currentAreaId, selectedSeason, controller.signal);
        if (!controller.signal.aborted) {
          setSelectedAreaDetail(res);
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('Failed to load area land feasibility detail:', err);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingAreaDetail(false);
        }
      }
    }

    loadDetail();

    return () => {
      controller.abort();
    };
  }, [selectedAreaId, selectedSeason]);

  return {
    areas,
    isLoadingAreas,
    selectedAreaId,
    setSelectedAreaId,
    selectedAreaDetail,
    isLoadingAreaDetail,
  };
}


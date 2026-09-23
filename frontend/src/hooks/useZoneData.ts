import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { ZoneFeature, ZoneSummaryResponse, Season } from '../api/types';

interface UseZoneDataProps {
  cityId: number | null;
  selectedSeason: Season;
}

export function useZoneData({ cityId, selectedSeason }: UseZoneDataProps) {
  const [zones, setZones] = useState<ZoneFeature[]>([]);
  const [isLoadingZones, setIsLoadingZones] = useState<boolean>(false);
  const [selectedZoneId, setSelectedZoneId] = useState<number | null>(null);
  const [selectedZoneSummary, setSelectedZoneSummary] = useState<ZoneSummaryResponse | null>(null);
  const [isLoadingZoneSummary, setIsLoadingZoneSummary] = useState<boolean>(false);

  // 1. Fetch all zones when city or season changes
  useEffect(() => {
    if (cityId === null) return;
    const currentCityId = cityId;

    const controller = new AbortController();

    async function loadZones() {
      setIsLoadingZones(true);
      try {
        const res = await api.getZones(currentCityId, selectedSeason, controller.signal);
        if (!controller.signal.aborted) {
          setZones(res.features || []);
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('Failed to load zones:', err);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingZones(false);
        }
      }
    }

    loadZones();

    return () => {
      controller.abort();
    };
  }, [cityId, selectedSeason]);

  // 2. Fetch zone deep-dive summary when a zone is selected
  useEffect(() => {
    if (selectedZoneId === null) {
      setSelectedZoneSummary(null);
      return;
    }
    const currentZoneId = selectedZoneId;

    const controller = new AbortController();

    async function loadSummary() {
      setIsLoadingZoneSummary(true);
      try {
        const res = await api.getZoneSummary(currentZoneId, selectedSeason, controller.signal);
        if (!controller.signal.aborted) {
          setSelectedZoneSummary(res);
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('Failed to load zone summary:', err);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingZoneSummary(false);
        }
      }
    }

    loadSummary();

    return () => {
      controller.abort();
    };
  }, [selectedZoneId, selectedSeason]);

  return {
    zones,
    isLoadingZones,
    selectedZoneId,
    setSelectedZoneId,
    selectedZoneSummary,
    isLoadingZoneSummary,
  };
}

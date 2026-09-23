import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { City, HealthStatus } from '../api/types';

// Known default centers for Indian cities (can be augmented dynamically)
export const CITY_COORDINATES: Record<string, { lat: number; lng: number; zoom: number }> = {
  Surat: { lat: 21.1702, lng: 72.8311, zoom: 13 },
  Ahmedabad: { lat: 23.0225, lng: 72.5714, zoom: 12 },
  Vadodara: { lat: 22.3072, lng: 73.1812, zoom: 12 },
  Rajkot: { lat: 22.3039, lng: 70.8022, zoom: 12 },
  Pune: { lat: 18.5204, lng: 73.8567, zoom: 12 },
};

export function useCityData() {
  const [cities, setCities] = useState<City[]>([]);
  const [selectedCity, setSelectedCity] = useState<City | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initial load: fetch health and cities
  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    async function init() {
      setIsLoading(true);
      setError(null);

      try {
        const [healthRes, citiesRes] = await Promise.all([
          api.getHealth(controller.signal).catch(() => ({ status: 'unreachable', database: 'disconnected' })),
          api.getCities(controller.signal),
        ]);

        if (isMounted) {
          setHealth(healthRes);
          setCities(citiesRes);
          if (citiesRes.length > 0) {
            setSelectedCity(citiesRes[0]);
          }
        }
      } catch (err: any) {
        if (isMounted && err.name !== 'AbortError') {
          setError(err.message || 'Failed to connect to GIS backend');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    init();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  const refreshHealth = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch {
      setHealth({ status: 'unreachable', database: 'disconnected' });
    }
  };

  return {
    cities,
    selectedCity,
    setSelectedCity,
    health,
    refreshHealth,
    isLoading,
    error,
  };
}

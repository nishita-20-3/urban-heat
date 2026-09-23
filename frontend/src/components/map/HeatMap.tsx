import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap, useMapEvents } from 'react-leaflet';
import type { Layer } from 'leaflet';
import type { 
  City, 
  GridFeature, 
  GridFeatureCollection, 
  ZoneFeature, 
  ZoneFeatureCollection,
  AreaFeature,
  AreaFeatureCollection,
  Season, 
  ViewMode 
} from '../../api/types';
import { getLSTColor, getLSTOpacity } from '../../utils/colorScales';
import { formatTemp } from '../../utils/formatters';
import { MapLegend } from './MapLegend';
import { MapControls } from './MapControls';
import type { BasemapType } from './MapControls';
import { CITY_COORDINATES } from '../../hooks/useCityData';
import { AlertCircle, ZoomIn, Loader2, Layers } from 'lucide-react';

interface HeatMapProps {
  city: City | null;
  features: GridFeature[];
  zones: ZoneFeature[];
  areas: AreaFeature[];
  viewMode: ViewMode;
  onToggleViewMode: (mode: ViewMode) => void;
  selectedSeason: Season;
  selectedCellId: number | null;
  selectedZoneId: number | null;
  selectedAreaId: number | null;
  onSelectCell: (cellId: number) => void;
  onSelectZone: (zoneId: number) => void;
  onSelectArea: (areaId: number) => void;
  onViewportChange: (bbox: string, zoom: number) => void;
  getCellLST: (cellId: number, season: Season) => number | null;
  isLoadingGrid: boolean;
  isLoadingZones: boolean;
  isLoadingAreas: boolean;
}

// Subcomponent to listen to map pan/zoom and update BBox
function MapEventsHandler({
  onViewportChange,
  setZoomLevel,
}: {
  onViewportChange: (bbox: string, zoom: number) => void;
  setZoomLevel: (z: number) => void;
}) {
  const map = useMapEvents({
    moveend: () => {
      const bounds = map.getBounds();
      const zoom = map.getZoom();
      setZoomLevel(zoom);
      
      const minLng = bounds.getSouthWest().lng;
      const minLat = bounds.getSouthWest().lat;
      const maxLng = bounds.getNorthEast().lng;
      const maxLat = bounds.getNorthEast().lat;

      // Format: min_lon,min_lat,max_lon,max_lat
      const bboxStr = `${minLng.toFixed(6)},${minLat.toFixed(6)},${maxLng.toFixed(6)},${maxLat.toFixed(6)}`;
      onViewportChange(bboxStr, zoom);
    },
  });

  // Initial trigger on mount
  useEffect(() => {
    const bounds = map.getBounds();
    const zoom = map.getZoom();
    setZoomLevel(zoom);
    const minLng = bounds.getSouthWest().lng;
    const minLat = bounds.getSouthWest().lat;
    const maxLng = bounds.getNorthEast().lng;
    const maxLat = bounds.getNorthEast().lat;
    const bboxStr = `${minLng.toFixed(6)},${minLat.toFixed(6)},${maxLng.toFixed(6)},${maxLat.toFixed(6)}`;
    onViewportChange(bboxStr, zoom);
  }, [map, onViewportChange, setZoomLevel]);

  return null;
}

// Subcomponent to programmatically pan/recenter map
function MapController({
  center,
  zoom,
}: {
  center: [number, number];
  zoom: number;
}) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
}

const BASEMAP_URLS: Record<BasemapType, { url: string; attribution: string }> = {
  dark: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, HERE, Garmin, &copy; OpenStreetMap contributors',
  },
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
  },
  street: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
};

export const HeatMap: React.FC<HeatMapProps> = ({
  city,
  features,
  zones,
  areas,
  viewMode,
  onToggleViewMode,
  selectedSeason,
  selectedCellId,
  selectedZoneId,
  selectedAreaId,
  onSelectCell,
  onSelectZone,
  onSelectArea,
  onViewportChange,
  getCellLST,
  isLoadingGrid,
  isLoadingZones,
  isLoadingAreas,
}) => {
  const [basemap, setBasemap] = useState<BasemapType>('dark');
  const [opacity, setOpacity] = useState<number>(0.65);
  const [showOutlines, setShowOutlines] = useState<boolean>(true);
  const [zoomLevel, setZoomLevel] = useState<number>(12);
  const [currentBbox, setCurrentBbox] = useState<string | null>(null);

  // Derive city center
  const defaultCityCenter = useMemo<[number, number]>(() => {
    if (city && CITY_COORDINATES[city.name]) {
      const c = CITY_COORDINATES[city.name];
      return [c.lat, c.lng];
    }
    return [21.1702, 72.8311]; // Surat fallback
  }, [city]);

  const [mapCenter, setMapCenter] = useState<[number, number]>(defaultCityCenter);
  const [mapZoom, setMapZoom] = useState<number>(12);

  // Recenter when city prop changes
  useEffect(() => {
    setMapCenter(defaultCityCenter);
    setMapZoom(viewMode === 'zones' ? 12 : 14);
  }, [defaultCityCenter, viewMode]);

  const handleResetView = () => {
    setMapCenter([...defaultCityCenter]);
    setMapZoom(viewMode === 'zones' ? 12 : 14);
  };

  const handleInternalViewportChange = (bbox: string, zoom: number) => {
    setCurrentBbox(bbox);
    onViewportChange(bbox, zoom);
  };
  const [showZonesLayer, setShowZonesLayer] = useState<boolean>(true);
  const [showAreasLayer, setShowAreasLayer] = useState<boolean>(true);
  const [showGridLayer, setShowGridLayer] = useState<boolean>(true);

  // Sync layer toggles if user explicitly clicks 1-tier focus button in Header
  useEffect(() => {
    if (viewMode === 'zones') {
      setShowZonesLayer(true);
    } else if (viewMode === 'areas') {
      setShowAreasLayer(true);
      setShowGridLayer(true);
    } else if (viewMode === 'cells') {
      setShowGridLayer(true);
      setShowAreasLayer(true);
    }
  }, [viewMode]);

  const areaFeatureCollection = useMemo<AreaFeatureCollection>(() => ({
    type: 'FeatureCollection',
    features: areas,
  }), [areas]);

  const zoneFeatureCollection = useMemo<ZoneFeatureCollection>(() => ({
    type: 'FeatureCollection',
    features: zones,
  }), [zones]);

  const cellFeatureCollection = useMemo<GridFeatureCollection>(() => ({
    type: 'FeatureCollection',
    features,
  }), [features]);

  const zoneGeojsonKey = useMemo(() => {
    return `zone-geojson-${selectedSeason}-${selectedZoneId}-${opacity}-${zones.length}-${showZonesLayer}`;
  }, [selectedSeason, selectedZoneId, opacity, zones, showZonesLayer]);

  const areaGeojsonKey = useMemo(() => {
    return `area-geojson-${selectedSeason}-${selectedAreaId}-${opacity}-${areas.length}-${showAreasLayer}`;
  }, [selectedSeason, selectedAreaId, opacity, areas, showAreasLayer]);

  const cellGeojsonKey = useMemo(() => {
    return `cell-geojson-${selectedSeason}-${selectedCellId}-${opacity}-${showOutlines}-${features.length}-${features[0]?.properties?.cell_id || 0}-${showGridLayer}`;
  }, [selectedSeason, selectedCellId, opacity, showOutlines, features, showGridLayer]);

  const onEachCellFeature = (feature: any, layer: Layer) => {
    const cellId = feature.properties.cell_id;
    const predictedLST = getCellLST(cellId, selectedSeason);
    const cellColor = getLSTColor(predictedLST);
    const tempStr = predictedLST !== null ? formatTemp(predictedLST) : 'Loading...';

    layer.on({
      click: () => onSelectCell(cellId),
    });

    layer.bindTooltip(
      `<div class="space-y-1 font-mono">
        <div class="flex items-center justify-between gap-3 text-xs border-b border-slate-700 pb-1 font-bold text-teal-300">
          <span>100m Heat Pixel #${cellId}</span>
          <span class="uppercase text-[10px] text-slate-400 font-mono">${selectedSeason}</span>
        </div>
        <div class="flex items-center justify-between gap-3 text-xs pt-1">
          <span class="text-slate-300">Predicted LST:</span>
          <span class="font-bold text-xs" style="color: ${cellColor}">${tempStr}</span>
        </div>
        <div class="text-[10px] text-slate-400 italic pt-0.5">Click to view area land feasibility & recommendations</div>
      </div>`,
      {
        className: 'gis-tooltip',
        sticky: true,
        direction: 'top',
        opacity: 0.95,
      }
    );
  };

  const onEachAreaFeature = (feature: any, layer: Layer) => {
    const p = feature.properties;

    layer.on({
      click: () => onSelectArea(p.area_id),
    });

    const formatRupees = (amount: number) => {
      if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
      if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} Lakh`;
      return `₹${amount.toLocaleString('en-IN')}`;
    };

    layer.bindTooltip(
      `<div class="space-y-1.5 font-sans p-1.5 min-w-[220px]">
        <div class="flex items-center justify-between gap-3 text-xs border-b border-slate-700 pb-1 font-bold text-slate-100">
          <div class="flex items-center gap-1.5">
            ${p.is_hotspot ? '<span class="text-amber-400 font-bold">⭐</span>' : ''}
            <span>${p.name}</span>
          </div>
          <span class="px-1.5 py-0.2 rounded text-[10px] font-mono ${
            p.is_hotspot || p.priority_level === 'High' ? 'bg-rose-500/30 text-rose-300' : 'bg-teal-500/30 text-teal-300'
          }">${p.code}</span>
        </div>
        ${p.is_hotspot ? '<div class="text-[10px] text-amber-300 font-semibold bg-amber-500/20 px-1.5 py-0.5 rounded border border-amber-500/40">⭐ Critical Heat Hotspot Area</div>' : ''}
        <div class="text-[10px] text-[#0FB5AE] font-mono">${p.area_type}</div>
        <div class="grid grid-cols-2 gap-2 text-xs pt-0.5">
          <div><span class="text-slate-400">Avg LST:</span> <span class="font-bold text-rose-400">${p.avg_lst}°C</span></div>
          <div><span class="text-slate-400">Cooling:</span> <span class="font-bold text-teal-300">-${p.avg_cooling_potential_c}°C</span></div>
        </div>
        <div class="text-[10px] text-slate-300 pt-1 border-t border-slate-800 grid grid-cols-3 gap-1">
          <div>🏢 ${(p.building_rooftop_sqm / 1000).toFixed(0)}k m²</div>
          <div>🛣️ ${(p.road_paved_sqm / 1000).toFixed(0)}k m²</div>
          <div>🌳 ${(p.open_ground_sqm / 1000).toFixed(0)}k m²</div>
        </div>
        <div class="text-[11px] text-amber-300 font-semibold pt-0.5">
          Area Budget: ${formatRupees(p.total_budget_inr)}
        </div>
        <div class="text-[10px] text-slate-400 italic">Click for Area-Wise Land Feasibility Package</div>
      </div>`,
      {
        className: 'gis-tooltip',
        sticky: true,
        direction: 'top',
        opacity: 0.95,
      }
    );
  };

  const onEachZoneFeature = (feature: any, layer: Layer) => {
    const p = feature.properties;

    layer.on({
      click: () => onSelectZone(p.zone_id),
    });

    const formatRupees = (amount: number) => {
      if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
      if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} Lakh`;
      return `₹${amount.toLocaleString('en-IN')}`;
    };

    layer.bindTooltip(
      `<div class="space-y-1.5 font-sans p-1">
        <div class="flex items-center justify-between gap-3 text-xs border-b border-slate-700 pb-1 font-bold text-slate-100">
          <span>${p.name}</span>
          <span class="px-1.5 py-0.2 rounded text-[10px] font-mono ${
            p.priority_level === 'High' ? 'bg-rose-500/30 text-rose-300' : 'bg-teal-500/30 text-teal-300'
          }">${p.priority_level} Priority</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs pt-0.5">
          <div><span class="text-slate-400">Avg LST:</span> <span class="font-bold text-rose-400">${p.avg_lst}°C</span></div>
          <div><span class="text-slate-400">Hotspots:</span> <span class="font-bold text-amber-300">${p.hotspot_cell_count}</span></div>
        </div>
        <div class="text-[11px] text-teal-300 font-semibold pt-0.5 border-t border-slate-800">
          Est. Budget: ${formatRupees(p.total_budget_inr)}
        </div>
        <div class="text-[10px] text-slate-400 italic">Click to inspect municipal zone summary</div>
      </div>`,
      {
        className: 'gis-tooltip',
        sticky: true,
        direction: 'top',
        opacity: 0.95,
      }
    );
  };

  return (
    <div className="relative w-full h-full bg-[#0B1929] overflow-hidden">
      {/* Top Left View Mode Switcher: 3-Tier Layer Controls */}
      <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-1.5 bg-[#0E2238]/95 p-2 rounded-xl border border-slate-700/60 backdrop-blur-md shadow-2xl">
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              setShowZonesLayer(true);
              setShowAreasLayer(true);
              setShowGridLayer(true);
            }}
            className="flex items-center gap-1 px-2.5 py-1 rounded text-xs font-semibold bg-[#0FB5AE]/20 text-[#0FB5AE] hover:bg-[#0FB5AE]/30 border border-[#0FB5AE]/40 transition-all cursor-pointer"
            title="Display all 3 tiers simultaneously"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>3-Tier View</span>
          </button>

          <button
            onClick={() => {
              setShowZonesLayer(true);
              setShowAreasLayer(false);
              setShowGridLayer(false);
              onToggleViewMode('zones');
            }}
            className={`px-2 py-1 rounded text-xs font-medium transition-all cursor-pointer ${
              showZonesLayer && !showAreasLayer && !showGridLayer
                ? 'bg-[#0FB5AE] text-[#0B1929] font-bold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            Zones
          </button>

          <button
            onClick={() => {
              setShowZonesLayer(false);
              setShowAreasLayer(true);
              setShowGridLayer(false);
              onToggleViewMode('areas');
            }}
            className={`px-2 py-1 rounded text-xs font-medium transition-all cursor-pointer ${
              !showZonesLayer && showAreasLayer && !showGridLayer
                ? 'bg-[#0FB5AE] text-[#0B1929] font-bold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            Areas
          </button>

          <button
            onClick={() => {
              setShowZonesLayer(false);
              setShowAreasLayer(false);
              setShowGridLayer(true);
              onToggleViewMode('cells');
            }}
            className={`px-2 py-1 rounded text-xs font-medium transition-all cursor-pointer ${
              !showZonesLayer && !showAreasLayer && showGridLayer
                ? 'bg-[#0FB5AE] text-[#0B1929] font-bold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            100m Grid
          </button>
        </div>

        {/* Simultaneous Layer Checkboxes */}
        <div className="flex items-center gap-3 pt-1 border-t border-slate-700/60 text-[11px] font-mono text-slate-300 px-1">
          <label className="flex items-center gap-1.5 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              checked={showZonesLayer}
              onChange={(e) => setShowZonesLayer(e.target.checked)}
              className="rounded bg-slate-800 border-slate-600 text-[#0FB5AE] focus:ring-0 cursor-pointer w-3.5 h-3.5"
            />
            <span>Zones (7)</span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              checked={showAreasLayer}
              onChange={(e) => setShowAreasLayer(e.target.checked)}
              className="rounded bg-slate-800 border-slate-600 text-[#38BDF8] focus:ring-0 cursor-pointer w-3.5 h-3.5"
            />
            <span>Areas (34)</span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              checked={showGridLayer}
              onChange={(e) => setShowGridLayer(e.target.checked)}
              className="rounded bg-slate-800 border-slate-600 text-[#F59E0B] focus:ring-0 cursor-pointer w-3.5 h-3.5"
            />
            <span>100m Heat Pixels</span>
          </label>
        </div>
      </div>

      {/* Map Container */}
      <MapContainer
        center={defaultCityCenter}
        zoom={12}
        minZoom={10}
        maxZoom={18}
        className="w-full h-full"
        zoomControl={false}
      >
        <MapEventsHandler
          onViewportChange={handleInternalViewportChange}
          setZoomLevel={setZoomLevel}
        />
        <MapController center={mapCenter} zoom={mapZoom} />

        {/* Basemap Tile Layer */}
        <TileLayer
          url={BASEMAP_URLS[basemap].url}
          attribution={BASEMAP_URLS[basemap].attribution}
          maxZoom={19}
        />

        {/* ── TIER 1 (BASE LAYER): 100m Microclimate Heat Pixels ── */}
        {showGridLayer && features.length > 0 && (
          <GeoJSON
            key={cellGeojsonKey}
            data={cellFeatureCollection as any}
            style={(feature: any) => {
              if (!feature) return {};
              const cellId = feature.properties.cell_id;
              const isSelected = selectedCellId === cellId;
              const predictedLST = getCellLST(cellId, selectedSeason);
              const cellColor = getLSTColor(predictedLST);
              const fillOp = isSelected ? 0.9 : (getLSTOpacity(predictedLST) * opacity);

              return {
                color: isSelected ? '#0FB5AE' : showOutlines ? '#1E293B' : 'transparent',
                weight: isSelected ? 3 : 0.6,
                fillColor: cellColor,
                fillOpacity: fillOp,
              };
            }}
            onEachFeature={onEachCellFeature}
          />
        )}

        {/* ── TIER 2 (MIDDLE LAYER): 34 Official Planning Sub-Area Boundaries ── */}
        {showAreasLayer && areas.length > 0 && (
          <GeoJSON
            key={areaGeojsonKey}
            data={areaFeatureCollection as any}
            style={(feature: any) => {
              if (!feature) return {};
              const p = feature.properties;
              const isSelected = selectedAreaId === p.area_id;

              return {
                color: isSelected ? '#FFFFFF' : p.is_hotspot ? '#F59E0B' : '#38BDF8',
                weight: isSelected ? 3.5 : p.is_hotspot ? 2.4 : 1.6,
                fillColor: isSelected ? '#38BDF8' : p.is_hotspot ? '#F59E0B' : '#0284C7',
                // Keep fill translucent so the 100m microclimate heat pixels underneath show through clearly
                fillOpacity: isSelected ? 0.35 : showGridLayer ? 0.04 : 0.35,
                dashArray: isSelected ? undefined : p.is_hotspot ? undefined : '3, 4',
              };
            }}
            onEachFeature={onEachAreaFeature}
          />
        )}

        {/* ── TIER 3 (TOP LAYER): 7 SMC Municipal Zone Perimeter Outlines ── */}
        {showZonesLayer && zones.length > 0 && (
          <GeoJSON
            key={zoneGeojsonKey}
            data={zoneFeatureCollection as any}
            style={(feature: any) => {
              if (!feature) return {};
              const p = feature.properties;
              const isSelected = selectedZoneId === p.zone_id;
              const zoneColor = p.color || '#0FB5AE';

              return {
                color: isSelected ? '#FFFFFF' : zoneColor,
                weight: isSelected ? 4 : 2.8,
                fillColor: 'transparent',
                fillOpacity: isSelected ? 0.15 : 0,
              };
            }}
            onEachFeature={onEachZoneFeature}
          />
        )}
      </MapContainer>

      {/* Loading Overlay Indicator */}
      {(isLoadingGrid || isLoadingZones || isLoadingAreas) && (
        <div className="absolute top-20 left-4 z-[1000] bg-[#0E2238]/90 border border-[#0FB5AE]/50 text-[#0FB5AE] px-3 py-1.5 rounded backdrop-blur-md shadow-xl flex items-center gap-2 text-xs font-mono">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-[#0FB5AE]" />
          <span>Syncing Geospatial Layers...</span>
        </div>
      )}

      {/* Zoom Warning Banner for Cell Mode if zoomed out */}
      {showGridLayer && zoomLevel < 11 && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-[1000] bg-[#0E2238]/95 border border-amber-500/60 text-amber-300 px-4 py-2 rounded-md shadow-xl flex items-center gap-3 text-xs backdrop-blur-md">
          <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span>Zoom in closer to view high-resolution 100m microclimate heat pixels for Surat.</span>
          <button
            onClick={() => setMapZoom(13)}
            className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/40 rounded text-xs font-semibold flex items-center gap-1 font-mono transition-colors"
          >
            <ZoomIn className="w-3.5 h-3.5" />
            <span>Zoom to Grid</span>
          </button>
        </div>
      )}

      {/* Map Controls (Top Right) */}
      <MapControls
        onResetView={handleResetView}
        basemap={basemap}
        onChangeBasemap={setBasemap}
        opacity={opacity}
        onChangeOpacity={setOpacity}
        showOutlines={showOutlines}
        onToggleOutlines={() => setShowOutlines(!showOutlines)}
        zoomLevel={zoomLevel}
        bbox={currentBbox}
      />

      {/* Map Legend (Bottom Left) */}
      <MapLegend 
        season={selectedSeason} 
        visibleCount={features.length > 0 ? features.length : areas.length} 
      />
    </div>
  );
};


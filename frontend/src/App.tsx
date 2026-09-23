import { useState, useCallback } from 'react';
import { useCityData } from './hooks/useCityData';
import { useGridData } from './hooks/useGridData';
import { useZoneData } from './hooks/useZoneData';
import { useAreaData } from './hooks/useAreaData';
import { useDebounce } from './hooks/useDebounce';
import { Header } from './components/common/Header';
import { HeatMap } from './components/map/HeatMap';
import { CellDetailDrawer } from './components/drawer/CellDetailDrawer';
import { ZoneDetailDrawer } from './components/drawer/ZoneDetailDrawer';
import { AreaDetailDrawer } from './components/drawer/AreaDetailDrawer';
import { InterventionsCatalog } from './components/catalog/InterventionsCatalog';
import type { Season, ViewMode } from './api/types';
import { AlertTriangle, Loader2 } from 'lucide-react';

export function App() {
  const {
    cities,
    selectedCity,
    setSelectedCity,
    health,
    refreshHealth,
    isLoading: isInitLoading,
    error: initError,
  } = useCityData();

  const [selectedSeason, setSelectedSeason] = useState<Season>('summer');
  const [activeView, setActiveView] = useState<'map' | 'catalog'>('map');
  const [viewMode, setViewMode] = useState<ViewMode>('areas');
  const [selectedCellId, setSelectedCellId] = useState<number | null>(null);

  // Map viewport state
  const [rawBbox, setRawBbox] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(13);

  // Debounce BBox query by 400ms to prevent excessive API hammering on pan/zoom
  const debouncedBbox = useDebounce(rawBbox, 400);

  // 1. Municipal Zones Data
  const {
    zones,
    isLoadingZones,
    selectedZoneId,
    setSelectedZoneId,
    selectedZoneSummary,
    isLoadingZoneSummary,
  } = useZoneData({
    cityId: selectedCity?.city_id ?? null,
    selectedSeason,
  });

  // 2. Planning Areas Data (Neighborhood level)
  const {
    areas,
    isLoadingAreas,
    selectedAreaId,
    setSelectedAreaId,
    selectedAreaDetail,
    isLoadingAreaDetail,
  } = useAreaData({
    cityId: selectedCity?.city_id ?? null,
    selectedSeason,
  });

  // 3. 100m Grid Cells Data
  const {
    features,
    isLoadingGrid,
    getCellLST,
  } = useGridData({
    cityId: selectedCity?.city_id ?? null,
    bbox: debouncedBbox,
    selectedSeason,
    zoomLevel,
  });

  const handleViewportChange = useCallback((bbox: string, zoom: number) => {
    setRawBbox(bbox);
    setZoomLevel(zoom);
  }, []);

  const handleSelectCell = useCallback((cellId: number) => {
    setSelectedCellId(cellId);
    setSelectedZoneId(null);
    setSelectedAreaId(null);
  }, [setSelectedZoneId, setSelectedAreaId]);

  const handleSelectZone = useCallback((zoneId: number) => {
    setSelectedZoneId(zoneId);
    setSelectedAreaId(null);
    setSelectedCellId(null);
  }, [setSelectedZoneId, setSelectedAreaId]);

  const handleSelectArea = useCallback((areaId: number) => {
    setSelectedAreaId(areaId);
    setSelectedZoneId(null);
    setSelectedCellId(null);
  }, [setSelectedZoneId, setSelectedAreaId]);

  const handleCloseCellDrawer = useCallback(() => {
    setSelectedCellId(null);
  }, []);

  const handleCloseZoneDrawer = useCallback(() => {
    setSelectedZoneId(null);
  }, [setSelectedZoneId]);

  const handleCloseAreaDrawer = useCallback(() => {
    setSelectedAreaId(null);
  }, [setSelectedAreaId]);

  const handleDrillDownToArea = useCallback((_zoneId: number) => {
    setViewMode('areas');
    setSelectedZoneId(null);
  }, [setSelectedZoneId]);

  const handleDrillDownToCells = useCallback((_areaId: number) => {
    setViewMode('cells');
    setSelectedAreaId(null);
  }, [setSelectedAreaId]);

  if (isInitLoading) {
    return (
      <div className="h-screen w-screen bg-[#0B1929] flex flex-col items-center justify-center gap-3 text-slate-100 font-mono text-xs">
        <Loader2 className="w-8 h-8 animate-spin text-[#0FB5AE]" />
        <div className="text-sm font-semibold tracking-wider uppercase">
          Initializing Urban Heat GIS System...
        </div>
        <p className="text-slate-400 text-xs">
          Connecting to Surat PostGIS Spatial & Zonal Engine
        </p>
      </div>
    );
  }

  if (initError) {
    return (
      <div className="h-screen w-screen bg-[#0B1929] flex flex-col items-center justify-center p-6 text-center">
        <div className="p-6 bg-[#0E2238] border border-rose-500/50 rounded-lg max-w-md space-y-4 shadow-2xl">
          <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-100">GIS Engine Connection Failure</h2>
          <p className="text-xs text-slate-400 font-mono leading-relaxed">
            {initError}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-[#0FB5AE] hover:bg-[#0FB5AE]/90 text-[#0B1929] font-bold rounded text-xs uppercase font-mono transition-colors cursor-pointer"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const currentItemCount = viewMode === 'zones'
    ? zones.length
    : viewMode === 'areas'
    ? areas.length
    : features.length;

  return (
    <div className="h-screen w-screen flex flex-col bg-[#0B1929] text-slate-100 overflow-hidden select-none font-sans">
      {/* Top Navigation & Controls Header */}
      <Header
        cities={cities}
        selectedCity={selectedCity}
        onSelectCity={(city) => {
          setSelectedCity(city);
          setSelectedCellId(null);
          setSelectedZoneId(null);
          setSelectedAreaId(null);
        }}
        selectedSeason={selectedSeason}
        onSelectSeason={setSelectedSeason}
        activeView={activeView}
        onSelectView={setActiveView}
        health={health}
        onRefreshHealth={refreshHealth}
        cellCount={currentItemCount}
      />

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-hidden">
        {activeView === 'map' ? (
          <>
            <HeatMap
              city={selectedCity}
              features={features}
              zones={zones}
              areas={areas}
              viewMode={viewMode}
              onToggleViewMode={(mode) => {
                setViewMode(mode);
                setSelectedZoneId(null);
                setSelectedAreaId(null);
                setSelectedCellId(null);
              }}
              selectedSeason={selectedSeason}
              selectedCellId={selectedCellId}
              selectedZoneId={selectedZoneId}
              selectedAreaId={selectedAreaId}
              onSelectCell={handleSelectCell}
              onSelectZone={handleSelectZone}
              onSelectArea={handleSelectArea}
              onViewportChange={handleViewportChange}
              getCellLST={getCellLST}
              isLoadingGrid={isLoadingGrid}
              isLoadingZones={isLoadingZones}
              isLoadingAreas={isLoadingAreas}
            />

            {/* Slide-out Zone Detail Drawer */}
            {selectedZoneId !== null && (
              <ZoneDetailDrawer
                summary={selectedZoneSummary}
                isLoading={isLoadingZoneSummary}
                selectedSeason={selectedSeason}
                onClose={handleCloseZoneDrawer}
                onDrillDown={handleDrillDownToArea}
              />
            )}

            {/* Slide-out Planning Area Detail Drawer (Physical Land Feasibility Inspector) */}
            {selectedAreaId !== null && (
              <AreaDetailDrawer
                detail={selectedAreaDetail}
                isLoading={isLoadingAreaDetail}
                selectedSeason={selectedSeason}
                onClose={handleCloseAreaDrawer}
                onDrillDownToCells={handleDrillDownToCells}
                cityName={selectedCity?.name || 'Surat'}
              />
            )}

            {/* Slide-out Cell Detail Drawer */}
            {selectedCellId !== null && (
              <CellDetailDrawer
                cellId={selectedCellId}
                selectedSeason={selectedSeason}
                onClose={handleCloseCellDrawer}
                cityName={selectedCity?.name || 'Surat'}
                areas={areas}
                zones={zones}
                features={features}
                onSelectArea={handleSelectArea}
              />
            )}
          </>
        ) : (
          <InterventionsCatalog />
        )}
      </main>
    </div>
  );
}

export default App;


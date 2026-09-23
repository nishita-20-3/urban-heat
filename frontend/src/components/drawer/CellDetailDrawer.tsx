import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import type {
  HeatPrediction,
  ShapResponse,
  Season,
  AreaFeature,
  ZoneFeature,
  GridFeature,
} from '../../api/types';
import { SeasonTable } from './SeasonTable';
import { ShapChart } from './ShapChart';
import { HotCellBadge } from '../common/Badge';
import { formatTemp } from '../../utils/formatters';
import { getLSTColor } from '../../utils/colorScales';
import {
  X,
  MapPin,
  Flame,
  Download,
  Building,
  ArrowRight,
  TreeDeciduous,
  Home,
  Droplets,
  Layers,
} from 'lucide-react';

interface CellDetailDrawerProps {
  cellId: number | null;
  selectedSeason: Season;
  onClose: () => void;
  cityName?: string;
  areas?: AreaFeature[];
  zones?: ZoneFeature[];
  features?: GridFeature[];
  onSelectArea?: (areaId: number) => void;
}

export const CellDetailDrawer: React.FC<CellDetailDrawerProps> = ({
  cellId,
  selectedSeason,
  onClose,
  cityName = 'Surat',
  areas = [],
  zones = [],
  features = [],
  onSelectArea,
}) => {
  const [activeSeason, setActiveSeason] = useState<string>(selectedSeason);
  const [predictions, setPredictions] = useState<HeatPrediction[]>([]);
  const [shapData, setShapData] = useState<ShapResponse | null>(null);

  const [isLoadingPreds, setIsLoadingPreds] = useState<boolean>(false);
  const [isLoadingShap, setIsLoadingShap] = useState<boolean>(false);

  // Sync internal season when global season changes
  useEffect(() => {
    setActiveSeason(selectedSeason);
  }, [selectedSeason]);

  // Find parent planning area and zone
  const currentFeature = features.find((f) => f.properties.cell_id === cellId);
  const parentArea = areas.find((a) => a.properties.area_id === currentFeature?.properties.area_id);
  const parentZone = zones.find(
    (z) => z.properties.zone_id === (currentFeature?.properties.zone_id || parentArea?.properties.zone_id)
  );

  // Fetch cell data on cellId or season change
  useEffect(() => {
    if (cellId === null) return;

    const currentCellId = cellId;
    const controller = new AbortController();

    async function loadData() {
      setIsLoadingPreds(true);

      try {
        const preds = await api.getPredictions(currentCellId, controller.signal).catch(() => []);

        if (!controller.signal.aborted) {
          setPredictions(preds);
        }
      } catch {
        // Handled
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingPreds(false);
        }
      }
    }

    loadData();

    return () => {
      controller.abort();
    };
  }, [cellId]);

  // Fetch SHAP whenever cellId or activeSeason changes
  useEffect(() => {
    if (cellId === null) return;

    const currentCellId = cellId;
    const controller = new AbortController();

    async function loadShap() {
      setIsLoadingShap(true);
      try {
        const data = await api.getShap(currentCellId, activeSeason, controller.signal);
        if (!controller.signal.aborted) {
          setShapData(data);
        }
      } catch {
        if (!controller.signal.aborted) {
          setShapData(null);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingShap(false);
        }
      }
    }

    loadShap();

    return () => {
      controller.abort();
    };
  }, [cellId, activeSeason]);

  if (cellId === null) return null;

  const currentPred = predictions.find((p) => p.season.toLowerCase() === activeSeason.toLowerCase());
  const isHot = currentPred ? currentPred.predicted_lst >= 44.0 : predictions.length > 0;
  const currentLST = currentPred ? currentPred.predicted_lst : shapData?.predicted_lst;

  const formatArea = (sqm: number | undefined) => {
    if (!sqm) return '0 m²';
    if (sqm >= 1000000) return `${(sqm / 1000000).toFixed(2)} km²`;
    return `${(sqm / 1000).toFixed(1)}k m²`;
  };

  const formatRupees = (amount: number | undefined) => {
    if (!amount) return '₹0';
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} Lakh`;
    return `₹${amount.toLocaleString('en-IN')}`;
  };

  return (
    <div className="fixed top-[53px] right-0 bottom-0 w-full sm:w-[500px] bg-[#0B1929] border-l border-slate-700/80 shadow-2xl z-[2000] flex flex-col select-none animate-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="p-3.5 bg-navy-950 border-b border-gis-border flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-teal-muted border border-teal-brand/40 flex items-center justify-center text-teal-brand">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-sm font-bold text-gis-textHeading font-mono">
                100m Heat Pixel #{cellId}
              </h2>
              <HotCellBadge isHot={isHot} />
              {parentArea?.properties?.is_hotspot && (
                <span className="px-1.5 py-0.2 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded text-[10px] font-semibold flex items-center gap-1">
                  <span>⭐</span> Star Hotspot
                </span>
              )}
            </div>
            <div className="text-[11px] text-gis-textMuted font-mono flex items-center gap-1.5 mt-0.5">
              <span>{parentArea ? parentArea.properties.name : `${cityName} Ward`}</span>
              <span>•</span>
              <span>{parentZone ? parentZone.properties.name : 'Surat SMC'}</span>
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded hover:bg-navy-800 text-gis-textMuted hover:text-gis-textHeading transition-colors border border-transparent hover:border-gis-border cursor-pointer"
          title="Close Inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Quick KPI Strip */}
      <div className="grid grid-cols-2 bg-navy-850 border-b border-gis-border px-3 py-2 text-xs font-mono">
        <div className="flex items-center gap-2 border-r border-gis-borderSubtle pr-2">
          <Flame className="w-4 h-4 text-heat-hot" />
          <div>
            <div className="text-[10px] text-gis-textMuted uppercase">Active Season LST</div>
            <div className="text-sm font-bold" style={{ color: getLSTColor(currentLST) }}>
              {formatTemp(currentLST)}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 pl-3">
          <Layers className="w-4 h-4 text-[#38BDF8]" />
          <div>
            <div className="text-[10px] text-gis-textMuted uppercase">Planning Boundary</div>
            <div className="text-xs font-bold text-[#38BDF8] truncate max-w-[170px]">
              {parentArea ? `${parentArea.properties.code} (${parentArea.properties.name})` : 'Surat Municipal Grid'}
            </div>
          </div>
        </div>
      </div>

      {/* Drawer Body (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-4">
        {/* Section 1: Area-Wise Land Feasibility Package (Primary Recommendation) */}
        {parentArea && (
          <section className="bg-navy-950/80 border border-[#0FB5AE]/40 rounded-xl p-3.5 space-y-3 shadow-lg">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center gap-1.5">
                <Building className="w-4 h-4 text-[#0FB5AE]" />
                <span className="text-xs font-bold text-slate-100 uppercase tracking-wide">
                  Area-Wise Land Feasibility Package
                </span>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#0FB5AE]/20 text-[#0FB5AE] border border-[#0FB5AE]/30">
                {parentArea.properties.name}
              </span>
            </div>

            <p className="text-[11px] text-slate-300 leading-relaxed">
              Municipal cooling interventions in Surat are formulated <strong className="text-white">area-wise</strong> by classifying physical land cover (Rooftops, Roads, Open ground, Water buffers) across this planning boundary:
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 bg-navy-900/90 rounded border border-slate-800 space-y-1">
                <div className="flex items-center gap-1.5 text-sky-400 font-semibold text-[11px]">
                  <Home className="w-3.5 h-3.5" />
                  <span>Building Rooftops</span>
                </div>
                <div className="font-mono text-xs font-bold text-slate-100">
                  {formatArea(parentArea.properties.building_rooftop_sqm)}
                </div>
                <div className="text-[10px] text-slate-400">Cool Roofs & White Solar Coating</div>
              </div>

              <div className="p-2 bg-navy-900/90 rounded border border-slate-800 space-y-1">
                <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-[11px]">
                  <Layers className="w-3.5 h-3.5" />
                  <span>Road & Paved Verge</span>
                </div>
                <div className="font-mono text-xs font-bold text-slate-100">
                  {formatArea(parentArea.properties.road_paved_sqm)}
                </div>
                <div className="text-[10px] text-slate-400">Avenue Shade Trees & Shading</div>
              </div>

              <div className="p-2 bg-navy-900/90 rounded border border-slate-800 space-y-1">
                <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px]">
                  <TreeDeciduous className="w-3.5 h-3.5" />
                  <span>Open Ground Parcels</span>
                </div>
                <div className="font-mono text-xs font-bold text-slate-100">
                  {formatArea(parentArea.properties.open_ground_sqm)}
                </div>
                <div className="text-[10px] text-slate-400">Miyawaki Forests & Micro-Parks</div>
              </div>

              <div className="p-2 bg-navy-900/90 rounded border border-slate-800 space-y-1">
                <div className="flex items-center gap-1.5 text-cyan-400 font-semibold text-[11px]">
                  <Droplets className="w-3.5 h-3.5" />
                  <span>Water & Creek Buffer</span>
                </div>
                <div className="font-mono text-xs font-bold text-slate-100">
                  {formatArea(parentArea.properties.water_body_sqm)}
                </div>
                <div className="text-[10px] text-slate-400">Riparian Wetlands & Creek Banks</div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
              <div className="text-[11px] font-mono">
                <span className="text-slate-400">Total Feasible Budget: </span>
                <span className="font-bold text-amber-300">{formatRupees(parentArea.properties.total_budget_inr)}</span>
              </div>

              {onSelectArea && (
                <button
                  onClick={() => onSelectArea(parentArea.properties.area_id)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-[#0FB5AE] hover:bg-[#0FB5AE]/90 text-[#0B1929] font-bold text-xs rounded transition-all cursor-pointer shadow-md"
                >
                  <span>Open Area Action Plan</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </section>
        )}

        {/* Section 2: Seasonal Microclimate Heat Profile for this 100m Cell */}
        <section>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200 uppercase font-mono mb-2">
            <Flame className="w-3.5 h-3.5 text-heat-hot" />
            <span>100m Microclimate Seasonal Profile</span>
          </div>
          <SeasonTable
            predictions={predictions}
            isLoading={isLoadingPreds}
            selectedSeason={activeSeason}
            onSelectSeason={setActiveSeason}
          />
        </section>

        {/* Section 3: SHAP Feature Explainability */}
        <section>
          <ShapChart
            shapData={shapData}
            isLoading={isLoadingShap}
            selectedSeason={activeSeason}
            onSeasonChange={setActiveSeason}
            availableSeasons={
              predictions.length > 0
                ? predictions.map((p) => p.season)
                : ['summer', 'monsoon', 'postmonsoon', 'winter']
            }
          />
        </section>
      </div>

      {/* Drawer Footer */}
      <div className="p-2.5 bg-navy-950 border-t border-gis-border flex items-center justify-between text-[11px] font-mono text-gis-textMuted">
        <div className="flex items-center gap-1.5">
          <Building className="w-3 h-3 text-teal-brand" />
          <span>Surat Municipal Corporation GIS</span>
        </div>
        <button
          onClick={() => window.print()}
          className="flex items-center gap-1 px-2.5 py-1 bg-navy-800 hover:bg-navy-700 text-gis-textHeading rounded border border-gis-border text-xs transition-colors cursor-pointer"
          title="Print or Export Cell Summary Report"
        >
          <Download className="w-3 h-3" />
          <span>Export Summary</span>
        </button>
      </div>
    </div>
  );
};


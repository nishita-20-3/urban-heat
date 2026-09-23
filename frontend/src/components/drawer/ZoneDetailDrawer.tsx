import { 
  X, 
  Flame, 
  Building2, 
  Trees, 
  Waves, 
  IndianRupee, 
  TrendingDown, 
  MapPin, 
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Compass
} from 'lucide-react';
import type { ZoneSummaryResponse, Season } from '../../api/types';

interface ZoneDetailDrawerProps {
  summary: ZoneSummaryResponse | null;
  isLoading: boolean;
  selectedSeason: Season;
  onClose: () => void;
  onDrillDown: (zoneId: number) => void;
}

export function ZoneDetailDrawer({
  summary,
  isLoading,
  selectedSeason,
  onClose,
  onDrillDown,
}: ZoneDetailDrawerProps) {
  if (!summary && !isLoading) return null;

  const formatRupees = (amount: number) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Cr`;
    }
    if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)} Lakh`;
    }
    return `₹${amount.toLocaleString('en-IN')}`;
  };

  const formatArea = (sqm: number) => {
    if (sqm >= 1000000) {
      return `${(sqm / 1000000).toFixed(2)} km²`;
    }
    return `${(sqm / 1000).toFixed(1)}k m²`;
  };

  const totalArea = summary 
    ? (summary.built_up_sqm + summary.open_soil_sqm + summary.tree_cover_sqm + summary.water_sqm) || 1
    : 1;

  const builtUpPct = summary ? Math.round((summary.built_up_sqm / totalArea) * 100) : 0;
  const openSoilPct = summary ? Math.round((summary.open_soil_sqm / totalArea) * 100) : 0;
  const treePct = summary ? Math.round((summary.tree_cover_sqm / totalArea) * 100) : 0;
  const waterPct = summary ? Math.round((summary.water_sqm / totalArea) * 100) : 0;

  return (
    <aside
      className="fixed top-[53px] right-0 bottom-0 w-full sm:w-[500px] bg-[#0B1929] border-l border-slate-700/80 shadow-2xl z-[2000] flex flex-col text-slate-100 select-none animate-in slide-in-from-right duration-200"
      aria-label="Zone Detail Drawer"
    >
      {/* Header */}
      <div className="p-5 border-b border-slate-700/60 flex items-start justify-between bg-[#0E2238]/60">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 text-xs font-mono font-semibold rounded bg-[#0FB5AE]/20 text-[#0FB5AE] border border-[#0FB5AE]/30">
              {summary?.code || 'ZONE'}
            </span>
            {summary && (
              <span 
                className={`px-2 py-0.5 text-xs font-medium rounded flex items-center gap-1 ${
                  summary.priority_level === 'High'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : summary.priority_level === 'Moderate'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-teal-500/20 text-teal-300 border border-teal-500/30'
                }`}
              >
                <ShieldAlert className="w-3 h-3" />
                {summary.priority_level} Priority
              </span>
            )}
          </div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">
            {summary?.name || 'Loading Zone Details...'}
          </h2>
          <p className="text-xs text-slate-400 capitalize mt-0.5">
            Surat Municipal Corporation • {selectedSeason} Season Analysis
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
          title="Close Drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar">
        {isLoading ? (
          <div className="space-y-4 animate-pulse">
            <div className="h-20 bg-slate-800/60 rounded-xl" />
            <div className="h-32 bg-slate-800/60 rounded-xl" />
            <div className="h-44 bg-slate-800/60 rounded-xl" />
          </div>
        ) : summary ? (
          <>
            {/* Description */}
            {summary.description && (
              <p className="text-xs text-slate-300/90 leading-relaxed bg-[#0E2238]/40 p-3 rounded-lg border border-slate-800/60">
                {summary.description}
              </p>
            )}

            {/* Thermal KPI Cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-[#0E2238]/80 p-3.5 rounded-xl border border-slate-700/50">
                <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                  <Flame className="w-3.5 h-3.5 text-[#E8543E]" />
                  Average LST
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {summary.avg_lst.toFixed(1)} <span className="text-sm font-normal text-slate-400">°C</span>
                </div>
                <div className="text-[11px] text-rose-400/90 mt-1 font-medium">
                  Peak: {summary.peak_lst.toFixed(1)} °C
                </div>
              </div>

              <div className="bg-[#0E2238]/80 p-3.5 rounded-xl border border-slate-700/50">
                <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                  <TrendingDown className="w-3.5 h-3.5 text-[#0FB5AE]" />
                  Cooling Potential
                </div>
                <div className="text-2xl font-bold text-[#0FB5AE]">
                  -{summary.avg_cooling_potential_c.toFixed(1)} <span className="text-sm font-normal text-slate-400">°C</span>
                </div>
                <div className="text-[11px] text-teal-400/90 mt-1 font-medium">
                  {summary.hotspot_cell_count} Critical Hotspots
                </div>
              </div>
            </div>

            {/* Total Estimated Budget */}
            <div className="bg-gradient-to-r from-[#0E2238] to-[#132F4C] p-4 rounded-xl border border-[#0FB5AE]/30 flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-400 flex items-center gap-1">
                  <IndianRupee className="w-3.5 h-3.5 text-[#0FB5AE]" />
                  Total Zone CapEx Budget
                </div>
                <div className="text-xl font-bold text-[#0FB5AE] mt-0.5">
                  {formatRupees(summary.total_budget_inr)}
                </div>
                <div className="text-[10px] text-slate-400">
                  Balanced Municipal Cooling Plan
                </div>
              </div>
              <button
                onClick={() => onDrillDown(summary.zone_id)}
                className="px-3.5 py-2 bg-[#0FB5AE] hover:bg-[#0FB5AE]/90 text-[#0B1929] font-semibold text-xs rounded-lg flex items-center gap-1.5 shadow-lg shadow-[#0FB5AE]/20 transition-all cursor-pointer"
              >
                <span>Drill Down</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Land Feasibility & Physical Suitability Inspector */}
            <div className="bg-[#0E2238]/70 p-4 rounded-xl border border-slate-700/50 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
                  <Compass className="w-4 h-4 text-[#0FB5AE]" />
                  Physical Land Suitability & Feasibility
                </h3>
                <span className="text-[11px] text-slate-400">
                  {summary.total_cell_count} cells ({formatArea(totalArea)})
                </span>
              </div>

              {/* Progress Distribution Bar */}
              <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
                <div 
                  className="bg-amber-600/90 h-full" 
                  style={{ width: `${builtUpPct}%` }} 
                  title={`Built-up: ${builtUpPct}%`}
                />
                <div 
                  className="bg-emerald-600/90 h-full" 
                  style={{ width: `${openSoilPct}%` }} 
                  title={`Open Soil: ${openSoilPct}%`}
                />
                <div 
                  className="bg-teal-500/90 h-full" 
                  style={{ width: `${treePct}%` }} 
                  title={`Tree Canopy: ${treePct}%`}
                />
                <div 
                  className="bg-cyan-600/90 h-full" 
                  style={{ width: `${waterPct}%` }} 
                  title={`Water: ${waterPct}%`}
                />
              </div>

              {/* Land breakdown itemized list */}
              <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-amber-400/90 font-medium">
                    <Building2 className="w-3.5 h-3.5" />
                    Built-up Footprint
                  </div>
                  <div className="text-sm font-semibold text-slate-100 mt-1">
                    {formatArea(summary.built_up_sqm)} <span className="text-[10px] text-slate-400 font-normal">({builtUpPct}%)</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    ✓ Feasible for Cool Roofs & Facades
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-emerald-400/90 font-medium">
                    <Trees className="w-3.5 h-3.5" />
                    Open Soil & Verges
                  </div>
                  <div className="text-sm font-semibold text-slate-100 mt-1">
                    {formatArea(summary.open_soil_sqm)} <span className="text-[10px] text-slate-400 font-normal">({openSoilPct}%)</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    ✓ Feasible for Trees & Pocket Parks
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-teal-400/90 font-medium">
                    <Trees className="w-3.5 h-3.5" />
                    Existing Tree Cover
                  </div>
                  <div className="text-sm font-semibold text-slate-100 mt-1">
                    {formatArea(summary.tree_cover_sqm)} <span className="text-[10px] text-slate-400 font-normal">({treePct}%)</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    Preservation Priority
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-cyan-400/90 font-medium">
                    <Waves className="w-3.5 h-3.5" />
                    Water & Lowlands
                  </div>
                  <div className="text-sm font-semibold text-slate-100 mt-1">
                    {formatArea(summary.water_sqm)} <span className="text-[10px] text-slate-400 font-normal">({waterPct}%)</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    Restricted (No construction)
                  </div>
                </div>
              </div>
            </div>

            {/* Top Recommended Interventions */}
            <div className="bg-[#0E2238]/70 p-4 rounded-xl border border-slate-700/50 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  Top Priority Interventions for this Zone
                </h3>
              </div>

              <div className="space-y-2">
                {summary.top_interventions && summary.top_interventions.length > 0 ? (
                  summary.top_interventions.map((item, idx) => (
                    <div 
                      key={idx}
                      className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-semibold text-slate-200">
                          {item.display_name}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          Capacity: {item.total_quantity.toLocaleString()} {item.unit}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-[#0FB5AE]">
                          {formatRupees(item.total_cost_inr)}
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          -{item.total_cooling_c.toFixed(1)} °C drop
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 text-center py-2">
                    No major interventions required for this zone.
                  </p>
                )}
              </div>
            </div>
          </>
        ) : null}
      </div>

      {/* Footer Drilldown Action */}
      {summary && (
        <div className="p-4 border-t border-slate-700/60 bg-[#0E2238]/80 flex gap-2">
          <button
            onClick={() => onDrillDown(summary.zone_id)}
            className="w-full py-2.5 px-4 bg-[#0FB5AE] hover:bg-[#0FB5AE]/90 text-[#0B1929] font-bold text-xs uppercase tracking-wider rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-[#0FB5AE]/20 transition-all cursor-pointer"
          >
            <MapPin className="w-4 h-4" />
            <span>Explore 100m Neighborhood Grid Cells</span>
          </button>
        </div>
      )}
    </aside>
  );
}

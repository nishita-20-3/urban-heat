import { useState } from 'react';
import { 
  X, 
  Flame, 
  IndianRupee, 
  TrendingDown, 
  Sparkles,
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  Layers,
  Info,
  Calendar
} from 'lucide-react';
import type { AreaDetailResponse, Season } from '../../api/types';

interface AreaDetailDrawerProps {
  detail: AreaDetailResponse | null;
  isLoading: boolean;
  selectedSeason: Season;
  onClose: () => void;
  onDrillDownToCells?: (areaId: number) => void;
  cityName?: string;
}

export function AreaDetailDrawer({
  detail,
  isLoading,
  selectedSeason,
  onClose,
  onDrillDownToCells,
  cityName = 'Surat',
}: AreaDetailDrawerProps) {
  const [activeTab, setActiveTab] = useState<'all' | 'rooftop' | 'road' | 'open_ground'>('all');

  if (!detail && !isLoading) return null;

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

  const allInterventions = detail ? [
    ...detail.rooftop_interventions,
    ...detail.road_interventions,
    ...detail.open_ground_interventions,
    ...detail.water_interventions,
  ] : [];

  const filteredInterventions = activeTab === 'all'
    ? allInterventions
    : allInterventions.filter(i => i.category === activeTab);

  return (
    <aside
      className="fixed top-[53px] right-0 bottom-0 w-full sm:w-[500px] bg-[#0B1929] border-l border-slate-700/80 shadow-2xl z-[2000] flex flex-col text-slate-100 font-sans select-none animate-in slide-in-from-right duration-200"
      aria-label="Planning Area Land Feasibility Drawer"
    >
      {/* Drawer Header */}
      <div className="p-5 border-b border-slate-700/60 flex items-start justify-between bg-[#0E2238]/80">
        <div>
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="px-2.5 py-0.5 text-xs font-mono font-semibold rounded bg-[#0FB5AE]/20 text-[#0FB5AE] border border-[#0FB5AE]/30">
              {detail?.code || 'AREA'}
            </span>
            <span className="px-2 py-0.5 text-xs font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">
              {detail?.zone_name || 'Zone'}
            </span>
            {detail?.is_hotspot && (
              <span className="px-2 py-0.5 text-xs font-semibold rounded flex items-center gap-1 bg-amber-500/20 text-amber-300 border border-amber-500/40">
                <span>⭐</span> Star Hotspot
              </span>
            )}
            {detail && (
              <span 
                className={`px-2 py-0.5 text-xs font-medium rounded flex items-center gap-1 ${
                  detail.priority_level === 'High'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : detail.priority_level === 'Moderate'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-teal-500/20 text-teal-300 border border-teal-500/30'
                }`}
              >
                <ShieldAlert className="w-3 h-3" />
                {detail.priority_level} Priority
              </span>
            )}
          </div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            {detail?.is_hotspot && <span className="text-amber-400">⭐</span>}
            <span>{detail?.name || 'Loading Planning Area...'}</span>
          </h2>
          <div className="flex items-center gap-2 mt-1 text-xs text-slate-400">
            <span className="text-[#0FB5AE] font-semibold">{detail?.area_type || 'Urban Planning Area'}</span>
            <span>•</span>
            <span className="capitalize">{cityName} Municipal Corporation</span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors cursor-pointer"
          title="Close Drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar">
        {isLoading ? (
          <div className="h-64 flex flex-col items-center justify-center gap-3 text-slate-400">
            <div className="w-8 h-8 border-2 border-[#0FB5AE] border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-mono uppercase tracking-wider">Evaluating Land Feasibility...</span>
          </div>
        ) : detail ? (
          <>
            {/* Hotspot Alert Banner if applicable */}
            {detail.is_hotspot && (
              <div className="p-3.5 bg-gradient-to-r from-amber-950/50 to-rose-950/40 border border-amber-500/50 rounded-xl flex items-start gap-3">
                <span className="text-xl">⭐</span>
                <div>
                  <div className="text-xs font-bold text-amber-300 uppercase tracking-wider">
                    High-Vulnerability Critical Heat Hotspot
                  </div>
                  <div className="text-xs text-amber-200/90 mt-0.5 leading-relaxed">
                    This sub-area is officially designated as a primary thermal hotspot requiring urgent Phase 1 municipal interventions across high-exposure surfaces.
                  </div>
                </div>
              </div>
            )}

            {/* Area Description */}
            {detail.description && (
              <div className="p-3 bg-[#0E2238]/60 border border-slate-700/50 rounded-lg text-xs text-slate-300 flex items-start gap-2.5 leading-relaxed">
                <Info className="w-4 h-4 text-[#0FB5AE] flex-shrink-0 mt-0.5" />
                <span>{detail.description}</span>
              </div>
            )}

            {/* Key Microclimate Heat Metrics */}
            <div className="grid grid-cols-3 gap-2.5">
              <div className="p-3 bg-[#0E2238] border border-slate-700/50 rounded-lg">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px] mb-1">
                  <Flame className="w-3.5 h-3.5 text-rose-400" />
                  <span>Avg LST ({selectedSeason})</span>
                </div>
                <div className="text-xl font-bold font-mono text-rose-400">
                  {detail.avg_lst}°C
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">
                  Peak: {detail.peak_lst}°C
                </div>
              </div>

              <div className="p-3 bg-[#0E2238] border border-slate-700/50 rounded-lg">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px] mb-1">
                  <TrendingDown className="w-3.5 h-3.5 text-[#0FB5AE]" />
                  <span>Cooling Drop</span>
                </div>
                <div className="text-xl font-bold font-mono text-[#0FB5AE]">
                  -{detail.total_cooling_potential_c}°C
                </div>
                <div className="text-[10px] text-teal-400/80 mt-0.5 font-mono">
                  Mitigation Target
                </div>
              </div>

              <div className="p-3 bg-[#0E2238] border border-slate-700/50 rounded-lg">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px] mb-1">
                  <IndianRupee className="w-3.5 h-3.5 text-amber-400" />
                  <span>Area Budget</span>
                </div>
                <div className="text-lg font-bold font-mono text-amber-300">
                  {formatRupees(detail.total_budget_inr)}
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">
                  CPWD Schedule
                </div>
              </div>
            </div>

            {/* Physical Land Surface Distribution */}
            <div className="p-4 bg-[#0E2238] border border-slate-700/60 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-[#0FB5AE]" />
                  <span className="text-xs font-bold text-slate-100 uppercase tracking-wider font-mono">
                    Physical Land Suitability Distribution
                  </span>
                </div>
                <span className="text-xs font-mono text-slate-400">
                  Total: {formatArea(detail.land_distribution.total_area_sqm)}
                </span>
              </div>

              {/* Proportional Segment Bar */}
              <div className="w-full h-3.5 bg-slate-800 rounded-full overflow-hidden flex border border-slate-700/80">
                {detail.land_distribution.building_pct > 0 && (
                  <div 
                    className="h-full bg-rose-500" 
                    style={{ width: `${detail.land_distribution.building_pct}%` }} 
                    title={`Building Rooftops: ${detail.land_distribution.building_pct}%`}
                  />
                )}
                {detail.land_distribution.road_pct > 0 && (
                  <div 
                    className="h-full bg-amber-500" 
                    style={{ width: `${detail.land_distribution.road_pct}%` }} 
                    title={`Roads & Pavements: ${detail.land_distribution.road_pct}%`}
                  />
                )}
                {detail.land_distribution.open_pct > 0 && (
                  <div 
                    className="h-full bg-teal-400" 
                    style={{ width: `${detail.land_distribution.open_pct}%` }} 
                    title={`Open Ground / Soil: ${detail.land_distribution.open_pct}%`}
                  />
                )}
                {detail.land_distribution.water_pct > 0 && (
                  <div 
                    className="h-full bg-cyan-400" 
                    style={{ width: `${detail.land_distribution.water_pct}%` }} 
                    title={`Water Bodies: ${detail.land_distribution.water_pct}%`}
                  />
                )}
              </div>

              {/* Land breakdown chips */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                <div className="p-2 bg-[#0B1929]/80 rounded border border-rose-500/20">
                  <div className="flex items-center gap-1 text-[10px] text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-rose-500" />
                    <span>Rooftops</span>
                  </div>
                  <div className="text-xs font-bold font-mono text-slate-200 mt-0.5">
                    {formatArea(detail.land_distribution.building_rooftop_sqm)}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {detail.land_distribution.building_pct}% Area
                  </div>
                </div>

                <div className="p-2 bg-[#0B1929]/80 rounded border border-amber-500/20">
                  <div className="flex items-center gap-1 text-[10px] text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-amber-500" />
                    <span>Roads & Corridors</span>
                  </div>
                  <div className="text-xs font-bold font-mono text-slate-200 mt-0.5">
                    {formatArea(detail.land_distribution.road_paved_sqm)}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {detail.land_distribution.road_pct}% Area
                  </div>
                </div>

                <div className="p-2 bg-[#0B1929]/80 rounded border border-teal-500/20">
                  <div className="flex items-center gap-1 text-[10px] text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-teal-400" />
                    <span>Open Ground</span>
                  </div>
                  <div className="text-xs font-bold font-mono text-slate-200 mt-0.5">
                    {formatArea(detail.land_distribution.open_ground_sqm)}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {detail.land_distribution.open_pct}% Area
                  </div>
                </div>

                <div className="p-2 bg-[#0B1929]/80 rounded border border-emerald-500/20">
                  <div className="flex items-center gap-1 text-[10px] text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span>Tree Cover</span>
                  </div>
                  <div className="text-xs font-bold font-mono text-slate-200 mt-0.5">
                    {formatArea(detail.land_distribution.existing_tree_cover_sqm)}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {detail.land_distribution.tree_pct}% Canopy
                  </div>
                </div>
              </div>
            </div>

            {/* Land-Type Categorized Recommendations Header & Filters */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-[#0FB5AE]" />
                  <span>Physical Land Feasibility Action Plan</span>
                </h3>
                <span className="text-[11px] font-mono text-slate-400">
                  {filteredInterventions.length} Actionable Measures
                </span>
              </div>

              {/* Category Filter Pills */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
                <button
                  onClick={() => setActiveTab('all')}
                  className={`px-2.5 py-1 rounded text-xs font-semibold font-mono transition-colors whitespace-nowrap cursor-pointer ${
                    activeTab === 'all'
                      ? 'bg-[#0FB5AE] text-[#0B1929]'
                      : 'bg-[#0E2238] text-slate-400 hover:text-white border border-slate-700'
                  }`}
                >
                  All ({allInterventions.length})
                </button>
                <button
                  onClick={() => setActiveTab('rooftop')}
                  className={`px-2.5 py-1 rounded text-xs font-semibold font-mono transition-colors whitespace-nowrap cursor-pointer ${
                    activeTab === 'rooftop'
                      ? 'bg-rose-500 text-white'
                      : 'bg-[#0E2238] text-slate-400 hover:text-white border border-slate-700'
                  }`}
                >
                  🏢 Rooftops ({detail.rooftop_interventions.length})
                </button>
                <button
                  onClick={() => setActiveTab('road')}
                  className={`px-2.5 py-1 rounded text-xs font-semibold font-mono transition-colors whitespace-nowrap cursor-pointer ${
                    activeTab === 'road'
                      ? 'bg-amber-500 text-slate-900'
                      : 'bg-[#0E2238] text-slate-400 hover:text-white border border-slate-700'
                  }`}
                >
                  🛣️ Roads & Verges ({detail.road_interventions.length})
                </button>
                <button
                  onClick={() => setActiveTab('open_ground')}
                  className={`px-2.5 py-1 rounded text-xs font-semibold font-mono transition-colors whitespace-nowrap cursor-pointer ${
                    activeTab === 'open_ground'
                      ? 'bg-teal-500 text-[#0B1929]'
                      : 'bg-[#0E2238] text-slate-400 hover:text-white border border-slate-700'
                  }`}
                >
                  🌳 Open Ground ({detail.open_ground_interventions.length})
                </button>
              </div>

              {/* Intervention Cards List */}
              <div className="space-y-3">
                {filteredInterventions.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 bg-[#0E2238] border border-slate-700/60 hover:border-[#0FB5AE]/50 rounded-xl space-y-3 transition-colors shadow-sm"
                  >
                    {/* Title & Category Badge */}
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase tracking-wider">
                          {item.category_title}
                        </span>
                        <h4 className="text-sm font-bold text-slate-100 mt-1">
                          {item.targeted_measure}
                        </h4>
                      </div>
                      <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-[#0FB5AE]/20 text-[#0FB5AE] border border-[#0FB5AE]/30 whitespace-nowrap">
                        -{item.cooling_drop_c}°C Drop
                      </span>
                    </div>

                    {/* Quantities & Cost Matrix */}
                    <div className="grid grid-cols-2 gap-2 p-2.5 bg-[#0B1929]/70 rounded-lg text-xs font-mono">
                      <div>
                        <span className="text-slate-400 text-[10px]">Target Deployment:</span>
                        <div className="font-bold text-slate-200">
                          {item.recommended_quantity.toLocaleString('en-IN')} {item.unit}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px]">Estimated Cost:</span>
                        <div className="font-bold text-amber-300">
                          {formatRupees(item.total_cost_inr)}
                        </div>
                      </div>
                    </div>

                    {/* Physical Feasibility Check */}
                    <div className="p-2.5 bg-emerald-950/30 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span className="leading-snug">{item.feasibility_check}</span>
                    </div>

                    {/* Engineering Rationale */}
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {item.engineering_rationale}
                    </p>

                    {/* Recommended Materials / Native Species */}
                    {item.recommended_materials_species.length > 0 && (
                      <div className="pt-2 border-t border-slate-800">
                        <span className="text-[10px] font-mono text-slate-400 block mb-1">
                          Recommended Materials / Native Botanical Species:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {item.recommended_materials_species.map((m, mIdx) => (
                            <span 
                              key={mIdx}
                              className="px-2 py-0.5 bg-slate-800/80 border border-slate-700 rounded text-[11px] text-slate-300"
                            >
                              {m}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Implementation Timeline */}
            <div className="p-4 bg-[#0E2238] border border-slate-700/60 rounded-xl space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-100 uppercase tracking-wider font-mono">
                <Calendar className="w-4 h-4 text-amber-400" />
                <span>Municipal Phasing Timeline</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {detail.implementation_timeline}
              </p>
            </div>
          </>
        ) : null}
      </div>

      {/* Drawer Footer Actions */}
      {detail && (
        <div className="p-4 border-t border-slate-700/60 bg-[#0E2238]/90 flex items-center justify-between gap-3">
          <div>
            <span className="text-[10px] text-slate-400 font-mono block">Total Feasible Investment</span>
            <span className="text-base font-bold font-mono text-[#0FB5AE]">
              {formatRupees(detail.total_budget_inr)}
            </span>
          </div>

          {onDrillDownToCells && (
            <button
              onClick={() => onDrillDownToCells(detail.area_id)}
              className="px-4 py-2 bg-[#0FB5AE] hover:bg-[#0FB5AE]/90 text-[#0B1929] font-bold text-xs font-mono uppercase tracking-wider rounded-lg flex items-center gap-1.5 transition-all shadow-lg cursor-pointer"
            >
              <span>Inspect 100m Grid</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}
    </aside>
  );
}


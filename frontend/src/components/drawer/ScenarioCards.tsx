import React, { useState } from 'react';
import type { RecommendationResponse, ScenarioDetail } from '../../api/types';
import { formatINR, formatINRCompact, formatQuantity } from '../../utils/formatters';
import { formatInterventionName, INTERVENTION_METADATA } from '../../utils/featureNames';
import {
  Sparkles,
  DollarSign,
  TrendingDown,
  Info,
  Layers,
  Target,
  TreeDeciduous,
  Home,
  Droplets,
  Flower2,
  Grid,
  Umbrella,
  Loader2,
} from 'lucide-react';

interface ScenarioCardsProps {
  recommendations: RecommendationResponse | null;
  isLoading: boolean;
}

type ScenarioKey = 'balanced' | 'max_cooling' | 'budget';

const SCENARIO_META: Record<
  ScenarioKey,
  { label: string; tag: string; description: string; badgeColor: string }
> = {
  balanced: {
    label: 'Balanced Scenario',
    tag: 'Optimal ROI',
    description: 'Optimal trade-off between thermal mitigation and capital expenditure for municipal budgets.',
    badgeColor: 'bg-teal-brand/20 text-teal-brand border-teal-brand/50',
  },
  max_cooling: {
    label: 'Maximum Cooling',
    tag: 'Highest Impact',
    description: 'Aggressive intervention portfolio maximizing total Celsius reduction across all feasible surfaces.',
    badgeColor: 'bg-emerald-950/60 text-emerald-300 border-emerald-500/50',
  },
  budget: {
    label: 'Budget Priority',
    tag: 'Fast Deployment',
    description: 'High-efficiency low-cost interventions for rapid municipal deployment under limited grants.',
    badgeColor: 'bg-amber-950/60 text-amber-300 border-amber-500/50',
  },
};

const INTERVENTION_ICONS: Record<string, React.ReactNode> = {
  tree_planting: <TreeDeciduous className="w-3.5 h-3.5 text-emerald-400" />,
  cool_roofing: <Home className="w-3.5 h-3.5 text-sky-400" />,
  green_corridors_parks: <Flower2 className="w-3.5 h-3.5 text-emerald-300" />,
  permeable_pavement: <Grid className="w-3.5 h-3.5 text-slate-300" />,
  green_walls: <Layers className="w-3.5 h-3.5 text-emerald-400" />,
  constructed_water_bodies: <Droplets className="w-3.5 h-3.5 text-cyan-400" />,
  shade_structures: <Umbrella className="w-3.5 h-3.5 text-amber-400" />,
};

export const ScenarioCards: React.FC<ScenarioCardsProps> = ({
  recommendations,
  isLoading,
}) => {
  const [activeScenarioKey, setActiveScenarioKey] = useState<ScenarioKey>('balanced');

  if (isLoading) {
    return (
      <div className="p-6 bg-navy-950/60 border border-gis-border rounded flex flex-col items-center justify-center gap-2 text-xs font-mono text-gis-textMuted min-h-[220px]">
        <Loader2 className="w-5 h-5 animate-spin text-teal-brand" />
        <span>Optimizing Cooling Intervention Scenarios...</span>
      </div>
    );
  }

  const scenarios = recommendations?.scenarios;
  const hasScenarios =
    scenarios &&
    Object.keys(scenarios).length > 0 &&
    (scenarios.balanced || scenarios.max_cooling || scenarios.budget);

  if (!recommendations || !hasScenarios) {
    return (
      <div className="p-4 bg-navy-950/60 border border-gis-border rounded text-xs space-y-2 text-gis-textMuted">
        <div className="flex items-center gap-2 text-slate-300 font-semibold">
          <Info className="w-4 h-4 text-teal-brand" />
          <span>No Interventions Required or Feasible</span>
        </div>
        <p className="text-[11px] leading-relaxed">
          No cooling interventions are currently feasible or scheduled for this grid cell. This occurs when the cell contains protected water bodies, heavy infrastructure with zero retrofittable footprint, or is already below thermal action thresholds.
        </p>
      </div>
    );
  }

  const activeScenario: ScenarioDetail | undefined =
    scenarios[activeScenarioKey] ||
    scenarios.balanced ||
    scenarios.max_cooling ||
    scenarios.budget;

  if (!activeScenario) {
    return null;
  }

  // Calculate efficiency index: Cooling (°C) per ₹1 Lakh invested
  const coolingPerLakh =
    activeScenario.total_cost_inr > 0
      ? (activeScenario.total_cooling_c / (activeScenario.total_cost_inr / 100000)).toFixed(2)
      : '0.00';

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-gis-borderSubtle">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-gis-textHeading uppercase font-mono">
          <Sparkles className="w-3.5 h-3.5 text-teal-brand" />
          <span>Cooling Intervention Scenarios</span>
        </div>
        <span className="text-[10px] text-gis-textMuted font-mono">
          3 Feasible Scenarios
        </span>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="grid grid-cols-3 gap-1.5 bg-navy-950 p-1 rounded border border-gis-border">
        {(['balanced', 'max_cooling', 'budget'] as ScenarioKey[]).map((key) => {
          const s = scenarios[key];
          if (!s) return null;
          const isSelected = activeScenarioKey === key;
          const meta = SCENARIO_META[key];

          return (
            <button
              key={key}
              onClick={() => setActiveScenarioKey(key)}
              className={`p-2 rounded text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-navy-800 border border-teal-brand/60 shadow'
                  : 'bg-transparent border border-transparent hover:bg-navy-900/60 opacity-75 hover:opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span
                  className={`text-[10px] uppercase font-mono px-1 py-0.2 rounded border ${meta.badgeColor}`}
                >
                  {meta.tag}
                </span>
              </div>
              <div
                className={`text-xs font-bold leading-tight ${
                  isSelected ? 'text-teal-brand' : 'text-gis-textMain'
                }`}
              >
                {meta.label.split(' ')[0]}
              </div>
              <div className="text-[11px] font-mono text-gis-textMuted mt-1">
                <span className="text-emerald-400 font-semibold">
                  -{s.total_cooling_c.toFixed(1)}°C
                </span>{' '}
                • {formatINRCompact(s.total_cost_inr)}
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Scenario Overview Card */}
      <div className="bg-navy-950/80 p-3 rounded border border-gis-border space-y-2.5">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-gis-textHeading">
              {SCENARIO_META[activeScenarioKey].label}
            </h4>
            <p className="text-[10px] text-gis-textMuted">
              {SCENARIO_META[activeScenarioKey].description}
            </p>
          </div>
        </div>

        {/* Big KPI Metrics */}
        <div className="grid grid-cols-3 gap-2 pt-1">
          <div className="bg-navy-900/90 p-2 rounded border border-gis-borderSubtle text-center font-mono">
            <div className="text-[10px] text-gis-textMuted uppercase flex items-center justify-center gap-1">
              <TrendingDown className="w-3 h-3 text-emerald-400" />
              <span>Total Cooling</span>
            </div>
            <div className="text-sm font-bold text-emerald-400">
              -{activeScenario.total_cooling_c.toFixed(2)} °C
            </div>
          </div>

          <div className="bg-navy-900/90 p-2 rounded border border-gis-borderSubtle text-center font-mono">
            <div className="text-[10px] text-gis-textMuted uppercase flex items-center justify-center gap-1">
              <DollarSign className="w-3 h-3 text-teal-brand" />
              <span>Est. CapEx</span>
            </div>
            <div className="text-sm font-bold text-gis-textHeading">
              {formatINR(activeScenario.total_cost_inr)}
            </div>
          </div>

          <div className="bg-navy-900/90 p-2 rounded border border-gis-borderSubtle text-center font-mono">
            <div className="text-[10px] text-gis-textMuted uppercase flex items-center justify-center gap-1">
              <Target className="w-3 h-3 text-amber-400" />
              <span>Efficiency</span>
            </div>
            <div className="text-xs font-bold text-amber-300">
              {coolingPerLakh} °C / ₹1L
            </div>
          </div>
        </div>
      </div>

      {/* Itemized Interventions Table */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] font-mono text-gis-textMuted">
          <span className="uppercase">Recommended Package Items ({activeScenario.interventions.length})</span>
          <span>Quantities & Budget</span>
        </div>

        <div className="overflow-hidden rounded border border-gis-border bg-navy-950/60 divide-y divide-gis-borderSubtle">
          {activeScenario.interventions.map((item, idx) => {
            const meta = INTERVENTION_METADATA[item.name];
            const icon = INTERVENTION_ICONS[item.name] || <Layers className="w-3.5 h-3.5 text-teal-brand" />;

            return (
              <div key={idx} className="p-2.5 hover:bg-navy-800/70 transition-colors text-xs">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="p-1 rounded bg-navy-900 border border-slate-700">
                      {icon}
                    </span>
                    <div>
                      <div className="font-semibold text-gis-textHeading text-[11px]">
                        {formatInterventionName(item.name)}
                      </div>
                      <div className="text-[10px] text-gis-textMuted font-mono">
                        Scope: {formatQuantity(item.quantity, item.unit)}
                      </div>
                    </div>
                  </div>

                  <div className="text-right font-mono">
                    <div className="font-bold text-gis-textHeading text-xs">
                      {formatINR(item.cost_inr)}
                    </div>
                    <div className="text-[10px] text-emerald-400 font-semibold">
                      -{item.cooling_contribution_c.toFixed(2)} °C
                    </div>
                  </div>
                </div>

                {meta && (
                  <p className="text-[10px] text-slate-400 pl-7 leading-tight line-clamp-1">
                    {meta.description}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

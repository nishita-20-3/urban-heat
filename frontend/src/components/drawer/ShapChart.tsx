import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Cell,
} from 'recharts';
import type { ShapResponse } from '../../api/types';
import { formatFeatureName, FEATURE_METADATA } from '../../utils/featureNames';
import { SHAP_COLORS } from '../../utils/colorScales';
import { formatTemp } from '../../utils/formatters';
import { Activity, TrendingUp, Info, Loader2 } from 'lucide-react';

interface ShapChartProps {
  shapData: ShapResponse | null;
  isLoading: boolean;
  selectedSeason: string;
  onSeasonChange: (season: string) => void;
  availableSeasons?: string[];
}

interface ProcessedShapItem {
  featureKey: string;
  name: string;
  value: number;
  absVal: number;
  isPositive: boolean;
  category: string;
  description: string;
}

export const ShapChart: React.FC<ShapChartProps> = ({
  shapData,
  isLoading,
  selectedSeason,
  onSeasonChange,
  availableSeasons = ['summer', 'monsoon', 'postmonsoon', 'winter'],
}) => {
  // Transform and sort SHAP contributions by absolute magnitude
  const chartData = useMemo<ProcessedShapItem[]>(() => {
    if (!shapData || !shapData.shap_contributions) return [];

    const items: ProcessedShapItem[] = Object.entries(shapData.shap_contributions).map(
      ([key, val]) => {
        const meta = FEATURE_METADATA[key];
        return {
          featureKey: key,
          name: formatFeatureName(key),
          value: parseFloat(val.toFixed(3)),
          absVal: Math.abs(val),
          isPositive: val >= 0,
          category: meta?.category || 'other',
          description: meta?.description || 'Model input feature attribution',
        };
      }
    );

    // Sort by absolute impact descending
    items.sort((a, b) => b.absVal - a.absVal);

    // Take top 8-10 features to keep the chart dense & readable
    return items.slice(0, 10);
  }, [shapData]);

  // Find dominant positive and negative drivers
  const topDrivers = useMemo(() => {
    if (chartData.length === 0) return { positive: null, negative: null };
    const pos = chartData.find((d) => d.value > 0);
    const neg = chartData.find((d) => d.value < 0);
    return { positive: pos, negative: neg };
  }, [chartData]);

  if (isLoading) {
    return (
      <div className="p-6 bg-navy-950/60 border border-gis-border rounded flex flex-col items-center justify-center gap-2 text-xs font-mono text-gis-textMuted min-h-[220px]">
        <Loader2 className="w-5 h-5 animate-spin text-teal-brand" />
        <span>Calculating SHAP Attribution Vectors...</span>
      </div>
    );
  }

  if (!shapData || chartData.length === 0) {
    return (
      <div className="p-4 bg-navy-950/60 border border-gis-border rounded text-xs space-y-2 text-gis-textMuted">
        <div className="flex items-center gap-2 text-slate-300 font-semibold">
          <Info className="w-4 h-4 text-teal-brand" />
          <span>No SHAP Attribution Available</span>
        </div>
        <p className="text-[11px] leading-relaxed">
          SHAP explainability vectors are computed for cells in the hotspot prediction set. If this cell is outside the threshold or data is unavailable for {selectedSeason}, try switching seasons above.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* SHAP Header & In-drawer Season Selector */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-gis-borderSubtle">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-gis-textHeading uppercase font-mono">
          <Activity className="w-3.5 h-3.5 text-teal-brand" />
          <span>SHAP Heat Drivers Breakdown</span>
        </div>

        {/* Season Pill Switcher */}
        <div className="flex bg-navy-950 p-0.5 rounded border border-gis-border text-[11px]">
          {availableSeasons.map((s) => (
            <button
              key={s}
              onClick={() => onSeasonChange(s)}
              className={`px-2 py-0.5 rounded-sm capitalize transition-all ${
                selectedSeason.toLowerCase() === s.toLowerCase()
                  ? 'bg-teal-brand text-navy-950 font-bold'
                  : 'text-gis-textMuted hover:text-white'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Model Base Value & Prediction Equation Bar */}
      <div className="grid grid-cols-3 gap-2 bg-navy-950/80 p-2.5 rounded border border-gis-border text-center font-mono">
        <div>
          <div className="text-[10px] text-gis-textMuted uppercase">Base LST</div>
          <div className="text-xs font-bold text-sky-400">
            {shapData.shap_base_value !== null ? formatTemp(shapData.shap_base_value) : '37.3 °C'}
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gis-textMuted uppercase">Attribution Sum</div>
          <div
            className={`text-xs font-bold ${
              (shapData.predicted_lst - (shapData.shap_base_value || 37.3)) >= 0
                ? 'text-heat-hot'
                : 'text-teal-brand'
            }`}
          >
            {(shapData.predicted_lst - (shapData.shap_base_value || 37.35)) >= 0 ? '+' : ''}
            {(shapData.predicted_lst - (shapData.shap_base_value || 37.35)).toFixed(2)} °C
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gis-textMuted uppercase">Predicted LST</div>
          <div className="text-xs font-bold text-heat-hot">
            {formatTemp(shapData.predicted_lst)}
          </div>
        </div>
      </div>

      {/* Summary Insight Callout */}
      {topDrivers.positive && (
        <div className="p-2.5 bg-heat-muted border border-heat-hot/40 rounded text-xs space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-heat-hot text-[11px]">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Primary Heating Factor: {topDrivers.positive.name}</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-snug">
            Adds <span className="font-bold text-heat-hot">+{topDrivers.positive.value.toFixed(2)}°C</span> to surface heat. {topDrivers.positive.description}
          </p>
        </div>
      )}

      {/* SHAP Horizontal Bar Chart */}
      <div className="bg-navy-950/80 p-2.5 rounded border border-gis-border">
        <div className="flex items-center justify-between text-[10px] font-mono text-gis-textMuted mb-2">
          <div className="flex items-center gap-1 text-teal-brand">
            <span className="w-2.5 h-2.5 rounded-sm bg-teal-brand inline-block" />
            <span>← Cooling Effect (-°C)</span>
          </div>
          <div className="flex items-center gap-1 text-heat-hot">
            <span>Warming Effect (+°C) →</span>
            <span className="w-2.5 h-2.5 rounded-sm bg-heat-hot inline-block" />
          </div>
        </div>

        <div className="h-[260px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
            >
              <XAxis
                type="number"
                domain={['auto', 'auto']}
                tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }}
                tickFormatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}°C`}
                stroke="#1E3A5F"
              />
              <YAxis
                type="category"
                dataKey="name"
                width={130}
                tick={{ fill: '#E2E8F0', fontSize: 10, fontFamily: 'monospace' }}
                stroke="#1E3A5F"
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload as ProcessedShapItem;
                    return (
                      <div className="bg-navy-900 border border-gis-border p-2.5 rounded shadow-panel text-xs space-y-1 font-mono max-w-[220px]">
                        <div className="font-bold text-gis-textHeading text-[11px]">{data.name}</div>
                        <div className="text-[10px] text-slate-400 capitalize">Category: {data.category}</div>
                        <div
                          className="font-bold text-xs pt-1 border-t border-slate-700"
                          style={{ color: data.isPositive ? SHAP_COLORS.positive : SHAP_COLORS.negative }}
                        >
                          Impact: {data.value > 0 ? '+' : ''}{data.value.toFixed(3)} °C
                        </div>
                        <p className="text-[10px] text-slate-300 font-sans leading-tight">
                          {data.description}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <ReferenceLine x={0} stroke="#475569" strokeWidth={1.5} />
              <Bar dataKey="value" radius={[2, 2, 2, 2]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.isPositive ? SHAP_COLORS.positive : SHAP_COLORS.negative}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  Cell,
} from 'recharts';
import type { InterventionType } from '../../api/types';
import { formatINR, formatINRCompact } from '../../utils/formatters';
import { formatInterventionName } from '../../utils/featureNames';
import { BarChart3, Info } from 'lucide-react';

interface InterventionMatrixProps {
  interventions: InterventionType[];
}

export const InterventionMatrix: React.FC<InterventionMatrixProps> = ({ interventions }) => {
  const chartData = interventions.map((item) => ({
    id: item.intervention_id,
    rawName: item.name,
    name: formatInterventionName(item.name),
    unitCost: item.cost_per_unit,
    coolingCoeff: item.cooling_coefficient,
    maxCeiling: item.max_cooling_ceiling || 2.0,
    confidence: item.data_confidence,
    unit: item.unit,
  }));

  const getColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'strong':
        return '#10B981'; // Emerald
      case 'moderate':
        return '#F59E0B'; // Amber
      case 'weak':
        return '#E8543E'; // Orange-Red
      default:
        return '#0FB5AE';
    }
  };

  return (
    <div className="bg-navy-900 border border-gis-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-gis-borderSubtle">
        <div className="flex items-center gap-2 text-xs font-bold text-gis-textHeading uppercase font-mono">
          <BarChart3 className="w-4 h-4 text-teal-brand" />
          <span>Intervention Efficacy vs. Unit Capital Cost</span>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-mono">
          <div className="flex items-center gap-1 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            <span>Strong Confidence</span>
          </div>
          <div className="flex items-center gap-1 text-amber-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
            <span>Moderate Confidence</span>
          </div>
          <div className="flex items-center gap-1 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
            <span>Preliminary</span>
          </div>
        </div>
      </div>

      {/* Scatter Chart */}
      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 15, right: 30, bottom: 20, left: 10 }}>
            <XAxis
              type="number"
              dataKey="unitCost"
              name="Unit Cost"
              unit="₹"
              stroke="#1E3A5F"
              tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }}
              tickFormatter={(v) => formatINRCompact(v)}
            />
            <YAxis
              type="number"
              dataKey="coolingCoeff"
              name="Cooling Impact"
              unit="°C"
              stroke="#1E3A5F"
              tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }}
              tickFormatter={(v) => `${v}°C`}
            />
            <ZAxis dataKey="maxCeiling" range={[120, 450]} name="Max Cooling Ceiling (°C)" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3', stroke: '#475569' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-navy-950 border border-gis-border p-2.5 rounded shadow-panel text-xs space-y-1 font-mono">
                      <div className="font-bold text-gis-textHeading text-xs">{data.name}</div>
                      <div className="text-[11px] text-teal-brand">
                        Unit Cost: {formatINR(data.unitCost)} / {data.unit}
                      </div>
                      <div className="text-[11px] text-emerald-400">
                        Cooling Coeff: -{data.coolingCoeff} °C
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Max Ceiling: -{data.maxCeiling} °C | Confidence: {data.confidence}
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Scatter name="Interventions" data={chartData}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.confidence)} fillOpacity={0.8} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="text-[11px] font-mono text-gis-textMuted bg-navy-950/60 p-2.5 rounded border border-gis-borderSubtle flex items-start gap-2">
        <Info className="w-4 h-4 text-teal-brand flex-shrink-0 mt-0.5" />
        <span>
          <strong>Municipal Decision Matrix:</strong> Bubble size indicates maximum cooling ceiling. Interventions in the top-left quadrant (high cooling, low unit cost, e.g., cool roofing and urban tree planting) offer the highest return on municipal capital expenditure for heat resilience.
        </span>
      </div>
    </div>
  );
};

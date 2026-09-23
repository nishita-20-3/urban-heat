import React from 'react';
import type { HeatPrediction } from '../../api/types';
import { formatTemp } from '../../utils/formatters';
import { getLSTColor } from '../../utils/colorScales';
import { Thermometer, Calendar, Flame, CheckCircle } from 'lucide-react';

interface SeasonTableProps {
  predictions: HeatPrediction[];
  isLoading: boolean;
  selectedSeason: string;
  onSelectSeason: (season: string) => void;
}

export const SeasonTable: React.FC<SeasonTableProps> = ({
  predictions,
  isLoading,
  selectedSeason,
  onSelectSeason,
}) => {
  if (isLoading) {
    return (
      <div className="p-4 bg-navy-800/60 border border-gis-border rounded animate-pulse text-xs font-mono text-gis-textMuted">
        Loading seasonal temperature profiles...
      </div>
    );
  }

  if (!predictions || predictions.length === 0) {
    return (
      <div className="p-3.5 bg-navy-800/70 border border-gis-borderSubtle rounded text-xs space-y-2">
        <div className="flex items-center gap-2 text-teal-brand font-semibold">
          <CheckCircle className="w-4 h-4 text-teal-brand" />
          <span>Moderate Temperature Zone</span>
        </div>
        <p className="text-gis-textMuted text-[11px] leading-relaxed">
          This grid cell is not classified in the top 25th percentile hotspot threshold. It maintains safe ambient temperatures within municipal baseline targets.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-gis-textHeading flex items-center gap-1.5 font-mono uppercase">
          <Thermometer className="w-3.5 h-3.5 text-heat-hot" />
          <span>Seasonal LST Predictions</span>
        </span>
        <span className="text-[10px] text-gis-textMuted font-mono">
          {predictions.length} Season(s) Recorded
        </span>
      </div>

      <div className="overflow-hidden rounded border border-gis-border bg-navy-950/60">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-gis-border bg-navy-800/80 text-[10px] font-mono text-gis-textMuted uppercase tracking-wider">
              <th className="py-2 px-3">Season</th>
              <th className="py-2 px-2 text-right">Predicted LST</th>
              <th className="py-2 px-2 text-right">Actual LST</th>
              <th className="py-2 px-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gis-borderSubtle font-mono text-xs">
            {predictions.map((p) => {
              const isSelected = p.season.toLowerCase() === selectedSeason.toLowerCase();
              const isHot = p.predicted_lst >= 40.0;
              const color = getLSTColor(p.predicted_lst);

              return (
                <tr
                  key={p.season}
                  onClick={() => onSelectSeason(p.season)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-teal-brand/15 border-l-2 border-teal-brand text-gis-textHeading'
                      : 'hover:bg-navy-800 text-gis-textMain'
                  }`}
                >
                  <td className="py-2 px-3 font-semibold capitalize flex items-center gap-1.5">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                    <span>{p.season}</span>
                  </td>
                  <td className="py-2 px-2 text-right font-bold" style={{ color }}>
                    {formatTemp(p.predicted_lst)}
                  </td>
                  <td className="py-2 px-2 text-right text-gis-textMuted">
                    {p.actual_lst !== null ? formatTemp(p.actual_lst) : '—'}
                  </td>
                  <td className="py-2 px-3 text-center">
                    {isHot ? (
                      <span className="inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.2 rounded bg-heat-hot/20 text-heat-hot border border-heat-hot/40">
                        <Flame className="w-2.5 h-2.5" />
                        <span>Hot</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.2 rounded bg-teal-muted text-teal-brand border border-teal-brand/30">
                        <span>Normal</span>
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-1 text-[10px] font-mono text-gis-textMuted pt-0.5">
        <Calendar className="w-3 h-3 text-slate-500" />
        <span>Prediction Model Run Date: {predictions[0]?.prediction_date || 'N/A'}</span>
      </div>
    </div>
  );
};

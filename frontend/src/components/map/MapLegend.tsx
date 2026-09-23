import React from 'react';
import { TEMPERATURE_BINS } from '../../utils/colorScales';
import type { Season } from '../../api/types';
import { Thermometer, Info } from 'lucide-react';

interface MapLegendProps {
  season: Season;
  visibleCount: number;
}

export const MapLegend: React.FC<MapLegendProps> = ({ season, visibleCount }) => {
  return (
    <div className="absolute bottom-6 left-6 z-[1000] bg-navy-900/90 border border-gis-border backdrop-blur-md rounded shadow-panel p-3 max-w-[280px] select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-gis-borderSubtle">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-gis-textHeading">
          <Thermometer className="w-3.5 h-3.5 text-heat-hot" />
          <span className="uppercase tracking-wider">Surface Heat Index (LST)</span>
        </div>
        <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 bg-navy-800 border border-slate-700 text-teal-brand rounded">
          {season}
        </span>
      </div>

      {/* Temperature Gradient Scale Bar */}
      <div className="mb-2.5">
        <div
          className="h-2.5 w-full rounded-sm border border-slate-700"
          style={{
            background:
              'linear-gradient(to right, #06B6D4 0%, #10B981 25%, #F59E0B 50%, #F97316 70%, #E8543E 88%, #D63031 100%)',
          }}
        />
        <div className="flex justify-between text-[10px] font-mono text-gis-textMuted mt-1">
          <span className="text-[#06B6D4]">&lt;38°C (Cool)</span>
          <span className="text-[#F59E0B]">44°C</span>
          <span className="text-rose-400 font-bold">&gt;50°C (Hotspot)</span>
        </div>
      </div>

      {/* Discrete Bins */}
      <div className="space-y-1 text-[11px]">
        {TEMPERATURE_BINS.map((bin, idx) => (
          <div key={idx} className="flex items-center justify-between py-0.5">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-sm border border-black/40 flex-shrink-0"
                style={{ backgroundColor: bin.color }}
              />
              <span className="font-mono text-gis-textMain">{bin.label}</span>
            </div>
            <span className="text-[10px] text-gis-textMuted text-right truncate max-w-[120px]">
              {bin.description.split('/')[0]}
            </span>
          </div>
        ))}
      </div>

      {/* Footer Info */}
      <div className="mt-2.5 pt-2 border-t border-gis-borderSubtle flex items-center justify-between text-[10px] font-mono text-gis-textMuted">
        <div className="flex items-center gap-1">
          <Info className="w-3 h-3 text-teal-brand" />
          <span>100m × 100m Spatial Grid</span>
        </div>
        <span>{visibleCount} in View</span>
      </div>
    </div>
  );
};

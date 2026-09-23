import React, { useState } from 'react';
import { Crosshair, Sliders, Layers, Eye, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';

export type BasemapType = 'dark' | 'satellite' | 'street';

interface MapControlsProps {
  onResetView: () => void;
  basemap: BasemapType;
  onChangeBasemap: (type: BasemapType) => void;
  opacity: number;
  onChangeOpacity: (val: number) => void;
  showOutlines: boolean;
  onToggleOutlines: () => void;
  zoomLevel: number;
  bbox: string | null;
}

export const MapControls: React.FC<MapControlsProps> = ({
  onResetView,
  basemap,
  onChangeBasemap,
  opacity,
  onChangeOpacity,
  showOutlines,
  onToggleOutlines,
  zoomLevel,
  bbox,
}) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  return (
    <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2 select-none">
      {/* Floating Control Box */}
      <div className="bg-navy-900/95 border border-gis-border backdrop-blur-md rounded shadow-panel p-2.5 flex flex-col gap-2.5 w-64 text-xs transition-all">
        {/* Header & Reset View */}
        <div className="flex items-center justify-between pb-1 border-b border-gis-borderSubtle">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="font-semibold text-gis-textHeading flex items-center gap-1.5 hover:text-teal-brand transition-colors cursor-pointer"
            title="Toggle Map Controls"
          >
            <Sliders className="w-3.5 h-3.5 text-teal-brand" />
            <span>GIS Controls</span>
            {isCollapsed ? <ChevronDown className="w-3 h-3 text-slate-400" /> : <ChevronUp className="w-3 h-3 text-slate-400" />}
          </button>
          <button
            onClick={onResetView}
            className="flex items-center gap-1 px-2 py-0.5 bg-navy-800 hover:bg-navy-700 text-teal-brand border border-gis-border rounded text-[11px] font-mono transition-colors cursor-pointer"
            title="Reset Map to City Center"
          >
            <Crosshair className="w-3 h-3" />
            <span>Center</span>
          </button>
        </div>

        {!isCollapsed && (
          <>

        {/* Basemap Switcher */}
        <div>
          <div className="text-[11px] font-mono text-gis-textMuted mb-1 flex items-center gap-1">
            <Layers className="w-3 h-3 text-teal-brand" />
            <span>BASEMAP LAYER</span>
          </div>
          <div className="grid grid-cols-3 gap-1 bg-navy-950 p-0.5 rounded border border-gis-border">
            <button
              onClick={() => onChangeBasemap('dark')}
              className={`py-1 text-[11px] rounded transition-all font-medium ${
                basemap === 'dark'
                  ? 'bg-teal-brand text-navy-950 font-bold'
                  : 'text-gis-textMuted hover:text-white'
              }`}
            >
              Dark Matter
            </button>
            <button
              onClick={() => onChangeBasemap('satellite')}
              className={`py-1 text-[11px] rounded transition-all font-medium ${
                basemap === 'satellite'
                  ? 'bg-teal-brand text-navy-950 font-bold'
                  : 'text-gis-textMuted hover:text-white'
              }`}
            >
              Satellite
            </button>
            <button
              onClick={() => onChangeBasemap('street')}
              className={`py-1 text-[11px] rounded transition-all font-medium ${
                basemap === 'street'
                  ? 'bg-teal-brand text-navy-950 font-bold'
                  : 'text-gis-textMuted hover:text-white'
              }`}
            >
              OpenStreet
            </button>
          </div>
        </div>

        {/* Layer Opacity Slider */}
        <div>
          <div className="flex justify-between text-[11px] font-mono text-gis-textMuted mb-1">
            <span>CHOROPLETH OPACITY</span>
            <span className="text-teal-brand font-bold">{Math.round(opacity * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.05"
            value={opacity}
            onChange={(e) => onChangeOpacity(parseFloat(e.target.value))}
            className="w-full accent-teal-brand cursor-pointer h-1.5 bg-navy-950 rounded border border-slate-700"
          />
        </div>

        {/* Grid Outlines Toggle */}
        <div className="flex items-center justify-between pt-1 border-t border-gis-borderSubtle">
          <span className="text-[11px] text-gis-textMuted">Grid Cell Outlines</span>
          <button
            onClick={onToggleOutlines}
            className={`flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
              showOutlines
                ? 'bg-teal-muted text-teal-brand border border-teal-brand/40'
                : 'bg-navy-950 text-slate-500 border border-slate-700'
            }`}
          >
            {showOutlines ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            <span>{showOutlines ? 'Visible' : 'Hidden'}</span>
          </button>
        </div>

        {/* Coordinates / Zoom Readout */}
        <div className="pt-2 border-t border-gis-borderSubtle text-[10px] font-mono text-gis-textMuted space-y-0.5">
          <div className="flex justify-between">
            <span>Zoom Level:</span>
            <span className="text-gis-textHeading font-semibold">
              z{zoomLevel} {zoomLevel < 13 ? '(Low res - Zoom in)' : '(High res)'}
            </span>
          </div>
          {bbox && (
            <div className="truncate text-slate-400" title={`BBox: ${bbox}`}>
              BBox: {bbox}
            </div>
          )}
        </div>
      </>
    )}
      </div>
    </div>
  );
};


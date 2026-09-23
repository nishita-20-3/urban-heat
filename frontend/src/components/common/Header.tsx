import React from 'react';
import {
  Map,
  BookOpen,
  Layers,
  Calendar,
  Building2,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import type { City, HealthStatus, Season } from '../../api/types';

interface HeaderProps {
  cities: City[];
  selectedCity: City | null;
  onSelectCity: (city: City) => void;
  selectedSeason: Season;
  onSelectSeason: (season: Season) => void;
  activeView: 'map' | 'catalog';
  onSelectView: (view: 'map' | 'catalog') => void;
  health: HealthStatus | null;
  onRefreshHealth: () => void;
  cellCount: number;
}

const SEASONS: { id: Season; label: string; months: string; iconColor: string }[] = [
  { id: 'summer', label: 'Summer', months: 'Mar - May', iconColor: 'text-heat-hot' },
  { id: 'monsoon', label: 'Monsoon', months: 'Jun - Sep', iconColor: 'text-teal-brand' },
  { id: 'postmonsoon', label: 'Post-Monsoon', months: 'Oct - Nov', iconColor: 'text-amber-400' },
  { id: 'winter', label: 'Winter', months: 'Dec - Feb', iconColor: 'text-sky-400' },
];

export const Header: React.FC<HeaderProps> = ({
  cities,
  selectedCity,
  onSelectCity,
  selectedSeason,
  onSelectSeason,
  activeView,
  onSelectView,
  health,
  onRefreshHealth,
  cellCount,
}) => {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="bg-navy-900 border-b border-gis-border px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-md z-30 select-none">
      {/* Left: Branding & City Selector */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-teal-muted border border-teal-brand/40 flex items-center justify-center text-teal-brand font-bold text-base shadow-sm">
            <Layers className="w-4 h-4 text-teal-brand" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-sm tracking-wide text-gis-textHeading uppercase">
                Urban Heat Decision-Support System
              </h1>
              <span className="text-[10px] px-1.5 py-0.2 bg-slate-800 border border-slate-700 text-teal-brand rounded font-mono">
                v1.0-GIS
              </span>
            </div>
            <p className="text-[11px] text-gis-textMuted font-mono">
              Smart City Mission • Urban Local Body Planning Tool
            </p>
          </div>
        </div>

        {/* City Selector */}
        <div className="h-6 w-px bg-gis-border hidden md:block" />
        <div className="flex items-center gap-1.5 bg-navy-800 border border-gis-border px-2.5 py-1 rounded text-xs">
          <Building2 className="w-3.5 h-3.5 text-teal-brand" />
          <span className="text-gis-textMuted text-[11px] uppercase font-mono">City:</span>
          <select
            className="bg-transparent text-gis-textHeading font-semibold focus:outline-none cursor-pointer text-xs"
            value={selectedCity?.city_id || ''}
            onChange={(e) => {
              const id = parseInt(e.target.value, 10);
              const found = cities.find((c) => c.city_id === id);
              if (found) onSelectCity(found);
            }}
          >
            {cities.map((city) => (
              <option key={city.city_id} value={city.city_id} className="bg-navy-900 text-white">
                {city.name}, {city.state} {city.is_prototype ? '(Prototype)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Middle: Season Selector & View Mode Switcher */}
      <div className="flex items-center gap-3">
        {/* Season Selector */}
        <div className="flex items-center bg-navy-950 p-0.5 rounded border border-gis-border text-xs">
          <div className="px-2 py-1 flex items-center gap-1 text-[11px] font-mono text-gis-textMuted uppercase border-r border-gis-borderSubtle">
            <Calendar className="w-3 h-3 text-teal-brand" />
            <span>Season:</span>
          </div>
          {SEASONS.map((s) => {
            const isActive = selectedSeason === s.id;
            return (
              <button
                key={s.id}
                onClick={() => onSelectSeason(s.id)}
                className={`px-2.5 py-1 text-xs font-medium rounded-sm transition-all flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-teal-brand text-navy-950 font-bold shadow'
                    : 'text-gis-textMuted hover:text-gis-textMain hover:bg-navy-800'
                }`}
                title={`${s.label} (${s.months})`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isActive ? 'bg-navy-950' : s.iconColor.replace('text-', 'bg-')
                  }`}
                />
                <span>{s.label}</span>
              </button>
            );
          })}
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center bg-navy-800 p-0.5 rounded border border-gis-border text-xs">
          <button
            onClick={() => onSelectView('map')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium transition-all ${
              activeView === 'map'
                ? 'bg-teal-brand/20 text-teal-brand border border-teal-brand/40 font-semibold'
                : 'text-gis-textMuted hover:text-gis-textMain'
            }`}
          >
            <Map className="w-3.5 h-3.5" />
            <span>Spatial Explorer</span>
            {cellCount > 0 && (
              <span className="ml-1 text-[10px] font-mono px-1 py-0.2 bg-navy-950/80 rounded text-gis-textMuted">
                {cellCount} cells
              </span>
            )}
          </button>
          <button
            onClick={() => onSelectView('catalog')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium transition-all ${
              activeView === 'catalog'
                ? 'bg-teal-brand/20 text-teal-brand border border-teal-brand/40 font-semibold'
                : 'text-gis-textMuted hover:text-gis-textMain'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Interventions Catalog</span>
          </button>
        </div>
      </div>

      {/* Right: API Health Status & Info */}
      <div className="flex items-center gap-2.5">
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border text-[11px] font-mono ${
            isHealthy
              ? 'bg-emerald-950/40 border-emerald-600/40 text-emerald-300'
              : 'bg-rose-950/40 border-rose-600/40 text-rose-300'
          }`}
          title={`Backend: ${health?.status || 'Unknown'} | PostGIS DB: ${health?.database || 'Disconnected'}`}
        >
          {isHealthy ? (
            <CheckCircle className="w-3 h-3 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-3 h-3 text-rose-400" />
          )}
          <span>PostGIS {isHealthy ? 'Connected' : 'Offline'}</span>
          <button
            onClick={onRefreshHealth}
            className="ml-1 hover:text-white p-0.5"
            title="Refresh connection status"
          >
            <RefreshCw className="w-2.5 h-2.5" />
          </button>
        </div>
      </div>
    </header>
  );
};

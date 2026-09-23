import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import type { InterventionType } from '../../api/types';
import { ConfidenceBadge } from '../common/Badge';
import { InterventionMatrix } from './InterventionMatrix';
import { formatINR } from '../../utils/formatters';
import { formatInterventionName } from '../../utils/featureNames';
import {
  BookOpen,
  Search,
  Filter,
  Layers,
  TreeDeciduous,
  Home,
  Droplets,
  Flower2,
  Grid,
  Umbrella,
  Loader2,
  AlertCircle,
} from 'lucide-react';

const INTERVENTION_ICONS: Record<string, React.ReactNode> = {
  tree_planting: <TreeDeciduous className="w-4 h-4 text-emerald-400" />,
  cool_roofing: <Home className="w-4 h-4 text-sky-400" />,
  green_corridors_parks: <Flower2 className="w-4 h-4 text-emerald-300" />,
  permeable_pavement: <Grid className="w-4 h-4 text-slate-300" />,
  green_walls: <Layers className="w-4 h-4 text-emerald-400" />,
  constructed_water_bodies: <Droplets className="w-4 h-4 text-cyan-400" />,
  shade_structures: <Umbrella className="w-4 h-4 text-amber-400" />,
};

export const InterventionsCatalog: React.FC = () => {
  const [interventions, setInterventions] = useState<InterventionType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedConfidence, setSelectedConfidence] = useState<string>('all');
  const [selectedLulc, setSelectedLulc] = useState<string>('all');

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    async function loadCatalog() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.getInterventions(controller.signal);
        if (isMounted) {
          setInterventions(data);
        }
      } catch (err: any) {
        if (isMounted && err.name !== 'AbortError') {
          setError(err.message || 'Failed to fetch interventions reference catalog');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadCatalog();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  // Filtered interventions
  const filteredInterventions = interventions.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.notes && item.notes.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesConfidence =
      selectedConfidence === 'all' ||
      item.data_confidence.toLowerCase() === selectedConfidence.toLowerCase();

    const matchesLulc =
      selectedLulc === 'all' ||
      (item.applicable_lulc_classes &&
        item.applicable_lulc_classes.some((c) =>
          c.toLowerCase().includes(selectedLulc.toLowerCase())
        ));

    return matchesSearch && matchesConfidence && matchesLulc;
  });

  return (
    <div className="h-full overflow-y-auto bg-navy-950 p-6 space-y-6 select-none">
      {/* Header Banner */}
      <div className="bg-navy-900 border border-gis-border rounded-lg p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-teal-brand font-mono text-xs uppercase tracking-wider mb-1">
            <BookOpen className="w-4 h-4 text-teal-brand" />
            <span>Standard Operating Procedure • Cooling Reference Catalog</span>
          </div>
          <h2 className="text-xl font-bold text-gis-textHeading">
            Cooling Interventions & Engineering Catalog
          </h2>
          <p className="text-xs text-gis-textMuted max-w-2xl mt-1">
            Official municipal unit rates, empirical cooling coefficients, land-use applicability, and data confidence levels for urban thermal mitigation in Surat and Indian smart cities.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-navy-950 px-3.5 py-2.5 rounded border border-gis-border font-mono text-xs">
          <div>
            <div className="text-[10px] text-gis-textMuted uppercase">Catalog Count</div>
            <div className="text-sm font-bold text-teal-brand">{interventions.length} Technologies</div>
          </div>
          <div className="h-6 w-px bg-gis-border" />
          <div>
            <div className="text-[10px] text-gis-textMuted uppercase">Currency Unit</div>
            <div className="text-sm font-bold text-gis-textHeading">INR (₹)</div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-navy-900 border border-gis-border rounded-lg p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 bg-navy-950 border border-gis-border px-3 py-1.5 rounded flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-gis-textMuted" />
          <input
            type="text"
            placeholder="Search intervention name, notes, materials..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-transparent text-gis-textHeading focus:outline-none w-full text-xs placeholder:text-slate-600"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Confidence Filter */}
          <div className="flex items-center gap-1.5 bg-navy-950 border border-gis-border px-2.5 py-1.5 rounded">
            <Filter className="w-3.5 h-3.5 text-teal-brand" />
            <span className="text-gis-textMuted font-mono text-[11px]">Confidence:</span>
            <select
              value={selectedConfidence}
              onChange={(e) => setSelectedConfidence(e.target.value)}
              className="bg-transparent text-gis-textHeading font-semibold focus:outline-none cursor-pointer text-xs"
            >
              <option value="all" className="bg-navy-900">All Levels</option>
              <option value="strong" className="bg-navy-900">Strong Empirical</option>
              <option value="moderate" className="bg-navy-900">Moderate</option>
              <option value="weak" className="bg-navy-900">Preliminary / Weak</option>
            </select>
          </div>

          {/* LULC Filter */}
          <div className="flex items-center gap-1.5 bg-navy-950 border border-gis-border px-2.5 py-1.5 rounded">
            <Layers className="w-3.5 h-3.5 text-teal-brand" />
            <span className="text-gis-textMuted font-mono text-[11px]">Land Cover:</span>
            <select
              value={selectedLulc}
              onChange={(e) => setSelectedLulc(e.target.value)}
              className="bg-transparent text-gis-textHeading font-semibold focus:outline-none cursor-pointer text-xs"
            >
              <option value="all" className="bg-navy-900">All Land Uses</option>
              <option value="Built-up" className="bg-navy-900">Built-up Surfaces</option>
              <option value="Cropland" className="bg-navy-900">Cropland / Open Soil</option>
              <option value="Grassland" className="bg-navy-900">Grassland / Turf</option>
              <option value="Bare" className="bg-navy-900">Bare Soil</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading & Error States */}
      {isLoading && (
        <div className="p-12 bg-navy-900 border border-gis-border rounded-lg flex flex-col items-center justify-center gap-3 text-xs font-mono text-gis-textMuted">
          <Loader2 className="w-6 h-6 animate-spin text-teal-brand" />
          <span>Loading Municipal Interventions Knowledge Base...</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-950/40 border border-rose-600/50 rounded-lg text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>Error loading interventions catalog: {error}</span>
        </div>
      )}

      {/* Main Catalog Table */}
      {!isLoading && !error && (
        <div className="bg-navy-900 border border-gis-border rounded-lg overflow-hidden shadow-panel">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-navy-950 border-b border-gis-border text-[11px] font-mono text-gis-textMuted uppercase tracking-wider">
                  <th className="py-3 px-4">Intervention Technology</th>
                  <th className="py-3 px-3">Unit Schedule Rate</th>
                  <th className="py-3 px-3">Cooling Coefficient</th>
                  <th className="py-3 px-3">Evidence Confidence</th>
                  <th className="py-3 px-3">Target Land Covers</th>
                  <th className="py-3 px-3 text-right">Max Ceiling</th>
                  <th className="py-3 px-4">Municipal & Engineering Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gis-borderSubtle">
                {filteredInterventions.map((item) => {
                  const icon = INTERVENTION_ICONS[item.name] || (
                    <Layers className="w-4 h-4 text-teal-brand" />
                  );

                  return (
                    <tr
                      key={item.intervention_id}
                      className="hover:bg-navy-800/60 transition-colors"
                    >
                      {/* Name & Icon */}
                      <td className="py-3 px-4 align-top">
                        <div className="flex items-start gap-2.5">
                          <span className="p-1.5 rounded bg-navy-950 border border-slate-700 flex-shrink-0 mt-0.5">
                            {icon}
                          </span>
                          <div>
                            <div className="font-bold text-gis-textHeading text-xs">
                              {formatInterventionName(item.name)}
                            </div>
                            <div className="text-[10px] text-teal-brand font-mono">
                              code: {item.name}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Unit Cost */}
                      <td className="py-3 px-3 align-top font-mono">
                        <div className="font-bold text-gis-textHeading text-xs">
                          {formatINR(item.cost_per_unit)}
                        </div>
                        <div className="text-[10px] text-gis-textMuted">
                          {item.unit}
                        </div>
                      </td>

                      {/* Cooling Coefficient */}
                      <td className="py-3 px-3 align-top font-mono">
                        <div className="font-bold text-emerald-400 text-xs">
                          -{item.cooling_coefficient} °C
                        </div>
                        <div className="text-[10px] text-gis-textMuted max-w-[130px] leading-tight">
                          {item.cooling_unit}
                        </div>
                      </td>

                      {/* Confidence Badge */}
                      <td className="py-3 px-3 align-top">
                        <ConfidenceBadge level={item.data_confidence} />
                      </td>

                      {/* Applicable LULC */}
                      <td className="py-3 px-3 align-top">
                        <div className="flex flex-wrap gap-1 max-w-[160px]">
                          {item.applicable_lulc_classes && item.applicable_lulc_classes.length > 0 ? (
                            item.applicable_lulc_classes.map((cls, idx) => (
                              <span
                                key={idx}
                                className="px-1.5 py-0.5 rounded bg-navy-950 border border-slate-700 text-[10px] font-mono text-slate-300"
                              >
                                {cls}
                              </span>
                            ))
                          ) : (
                            <span className="text-[10px] text-slate-500 font-mono">All zones</span>
                          )}
                        </div>
                      </td>

                      {/* Max Ceiling & Coverage Ratio */}
                      <td className="py-3 px-3 align-top text-right font-mono">
                        <div className="font-bold text-cyan-400 text-xs">
                          -{item.max_cooling_ceiling?.toFixed(1) || '—'} °C
                        </div>
                        <div className="text-[10px] text-gis-textMuted">
                          cov: {Math.round(item.coverage_ratio * 100)}%
                        </div>
                      </td>

                      {/* Notes */}
                      <td className="py-3 px-4 align-top">
                        <p className="text-[11px] text-slate-300 leading-relaxed font-sans max-w-sm">
                          {item.notes || 'Standard urban planning schedule rate.'}
                        </p>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Comparison Efficacy Matrix Chart */}
      {!isLoading && !error && interventions.length > 0 && (
        <InterventionMatrix interventions={interventions} />
      )}
    </div>
  );
};

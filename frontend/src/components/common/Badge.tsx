import React from 'react';
import { ShieldCheck, ShieldAlert, Shield, Flame, CheckCircle2 } from 'lucide-react';
import type { ConfidenceLevel } from '../../api/types';

interface ConfidenceBadgeProps {
  level: ConfidenceLevel | string;
  showIcon?: boolean;
  className?: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  level,
  showIcon = true,
  className = '',
}) => {
  const norm = level.toLowerCase();

  if (norm === 'strong') {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold uppercase tracking-wider rounded border border-emerald-500/50 bg-emerald-950/60 text-emerald-300 ${className}`}
        title="Strong Empirical Evidence: Direct pilot studies or municipal engineering schedules"
      >
        {showIcon && <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
        <span>Strong Confidence</span>
      </span>
    );
  }

  if (norm === 'moderate') {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold uppercase tracking-wider rounded border border-amber-500/50 bg-amber-950/40 text-amber-300 ${className}`}
        title="Moderate Confidence: Scaled from global studies or regional approximations"
      >
        {showIcon && <Shield className="w-3.5 h-3.5 text-amber-400" />}
        <span>Moderate Confidence</span>
      </span>
    );
  }

  // Weak confidence: Distinct dashed border and amber-red badge
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold uppercase tracking-wider rounded border border-dashed border-rose-500/70 bg-rose-950/30 text-rose-300 ${className}`}
      title="Preliminary / Weak Confidence: Requires localized field validation or soil testing"
    >
      {showIcon && <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />}
      <span>Preliminary Data</span>
    </span>
  );
};

export const HotCellBadge: React.FC<{ isHot: boolean; className?: string }> = ({
  isHot,
  className = '',
}) => {
  if (isHot) {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold uppercase tracking-wider rounded bg-heat-hot/20 text-heat-hot border border-heat-hot/50 ${className}`}
      >
        <Flame className="w-3.5 h-3.5 text-heat-hot" />
        <span>Top 25% Hotspot</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium uppercase tracking-wider rounded bg-slate-800 text-slate-400 border border-slate-700 ${className}`}
    >
      <CheckCircle2 className="w-3.5 h-3.5 text-teal-brand" />
      <span>Moderate Temp Zone</span>
    </span>
  );
};

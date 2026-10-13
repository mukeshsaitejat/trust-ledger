import type { RiskLevel } from '../../types';

const riskStyles: Record<RiskLevel, string> = {
  'Low Risk': 'bg-emerald-100 text-emerald-700',
  'Medium Risk': 'bg-amber-100 text-amber-700',
  'High Risk': 'bg-red-100 text-red-700',
  Pending: 'bg-slate-100 text-slate-600',
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  return <span className={`badge ${riskStyles[level]}`}>{level}</span>;
}

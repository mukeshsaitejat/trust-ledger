import type { Finding } from '../../types';

const severityStyles = {
  Low: 'bg-slate-100 text-slate-700',
  Medium: 'bg-amber-100 text-amber-700',
  High: 'bg-red-100 text-red-700',
};

export function FindingsList({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return (
      <div className="panel p-5 text-sm text-slate-600">
        No discrepancies were detected by the configured verification checks.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {findings.map((finding) => (
        <div key={finding.id} className="panel p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-base font-semibold text-text">{finding.type}</div>
              <div className="text-sm text-slate-500">Field: {finding.field}</div>
            </div>
            <span className={`badge ${severityStyles[finding.severity]}`}>{finding.severity}</span>
          </div>

          <div className="mt-3 grid gap-3 text-sm text-slate-600 md:grid-cols-2">
            <div className="rounded-xl bg-slate-50 p-3">
              <div className="text-xs uppercase tracking-wide text-slate-500">Observed value</div>
              <div className="mt-1 font-medium text-text">{finding.observedValue}</div>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <div className="text-xs uppercase tracking-wide text-slate-500">Expected value</div>
              <div className="mt-1 font-medium text-text">{finding.expectedValue}</div>
            </div>
          </div>

          <p className="mt-3 text-sm text-slate-700">{finding.explanation}</p>
        </div>
      ))}
    </div>
  );
}

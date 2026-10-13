import type { ComparisonRow } from '../../types';

export function ComparisonTable({ rows }: { rows: ComparisonRow[] }) {
  return (
    <div className="panel overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-border text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 font-semibold">Field</th>
              <th className="px-4 py-3 font-semibold">Invoice</th>
              <th className="px-4 py-3 font-semibold">Purchase Order</th>
              <th className="px-4 py-3 font-semibold">Delivery Receipt</th>
              <th className="px-4 py-3 font-semibold">Comparison Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-white">
            {rows.map((row) => (
              <tr key={row.field} className={row.status === 'Mismatch' ? 'bg-amber-50/50' : ''}>
                <td className="px-4 py-3 font-medium text-text">{row.field}</td>
                <td className="px-4 py-3 text-slate-700">{row.invoice}</td>
                <td className="px-4 py-3 text-slate-700">{row.po}</td>
                <td className="px-4 py-3 text-slate-700">{row.receipt}</td>
                <td className="px-4 py-3">
                  <span
                    className={`badge ${
                      row.status === 'Match'
                        ? 'bg-emerald-100 text-emerald-700'
                        : row.status === 'Mismatch'
                          ? 'bg-amber-100 text-amber-700'
                          : row.status === 'Missing'
                            ? 'bg-slate-100 text-slate-600'
                            : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rows.filter((row) => row.status === 'Mismatch').length > 0 && (
        <div className="border-t border-border bg-slate-50 px-4 py-4">
          <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Discrepancy notes</h4>
          <ul className="space-y-3 text-sm text-slate-700">
            {rows
              .filter((row) => row.status === 'Mismatch')
              .map((row) => (
                <li key={`${row.field}-note`} className="rounded-xl border border-amber-200 bg-amber-50 p-3">
                  <div className="font-medium text-text">{row.field}</div>
                  <div className="mt-1">{row.explanation ?? 'This field differs between the invoice and supporting documents.'}</div>
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}

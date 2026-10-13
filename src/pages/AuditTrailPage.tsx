import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchAuditTrail } from '../lib/demoApi';
import type { AuditTrailEntry } from '../types';

const formatTimestamp = (value: string) => new Date(value).toLocaleString();

type AuditTableRow = AuditTrailEntry & { invoiceId: string };

export default function AuditTrailPage() {
  const [events, setEvents] = useState<AuditTableRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setIsLoading(true);

      try {
        const result = await fetchAuditTrail();
        if (!active) return;
        setEvents(result as AuditTableRow[]);
      } catch (loadError) {
        if (!active) return;
        setError(loadError instanceof Error ? loadError.message : 'Audit events could not be loaded.');
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    load();
    return () => {
      active = false;
    };
  }, []);

  if (isLoading) {
    return <div className="panel h-48 animate-pulse bg-slate-100" />;
  }

  if (error) {
    return <div className="panel border-red-200 bg-red-50 p-5 text-red-700">{error}</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="section-title">Audit Trail</h1>
          <p className="mt-1 text-sm text-slate-500">Review invoice verification history and chain integrity events.</p>
        </div>
      </div>

      {events.length === 0 ? (
        <div className="panel p-5 text-sm text-slate-600">
          No audit events have been recorded yet. Invoice verification activity will appear here after submission.
        </div>
      ) : (
        <div className="panel overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-5 py-3 font-semibold">Event type</th>
                  <th className="px-5 py-3 font-semibold">Invoice ID</th>
                  <th className="px-5 py-3 font-semibold">Timestamp</th>
                  <th className="px-5 py-3 font-semibold">Hash</th>
                  <th className="px-5 py-3 font-semibold">Chain status</th>
                  <th className="px-5 py-3 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-white">
                {events.map((event) => (
                  <tr key={`${event.invoiceId}-${event.id}`}>
                    <td className="px-5 py-3 font-medium text-text">{event.eventType}</td>
                    <td className="px-5 py-3 text-slate-700">{event.invoiceId}</td>
                    <td className="px-5 py-3 text-slate-700">{formatTimestamp(event.timestamp)}</td>
                    <td className="px-5 py-3 text-slate-700">{event.hash.slice(0, 18)}...</td>
                    <td className="px-5 py-3">
                      <span className="badge bg-slate-100 text-slate-700">{event.chainStatus}</span>
                    </td>
                    <td className="px-5 py-3">
                      <Link to={`/invoices/${event.invoiceId}`} className="font-medium text-blue hover:text-blue/80">
                        Open invoice
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

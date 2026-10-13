import { Copy, ShieldCheck } from 'lucide-react';
import type { AuditEvent } from '../../types';

const formatTimestamp = (timestamp: string) =>
  new Date(timestamp).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

const truncateHash = (hash: string) => `${hash.slice(0, 10)}...${hash.slice(-8)}`;

export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  return (
    <div className="space-y-4">
      {events.map((event) => (
        <div key={event.id} className="panel p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-base font-semibold text-text">{event.eventType}</div>
              <div className="mt-1 text-sm text-slate-500">{formatTimestamp(event.timestamp)}</div>
            </div>
            <div className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
              {event.chainStatus}
            </div>
          </div>

          <p className="mt-3 text-sm text-slate-700">{event.description}</p>

          <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
            <span className="rounded-full border border-border bg-slate-50 px-2.5 py-1.5">Event ID: {event.id}</span>
            <span className="rounded-full border border-border bg-slate-50 px-2.5 py-1.5">Hash: {truncateHash(event.hash)}</span>
            {event.previousHash && <span className="rounded-full border border-border bg-slate-50 px-2.5 py-1.5">Prev: {truncateHash(event.previousHash)}</span>}
            <button type="button" className="inline-flex items-center gap-1 rounded-full border border-border bg-white px-2.5 py-1.5 text-slate-600 hover:border-slate-300">
              <Copy size={12} />
              Copy full hash
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

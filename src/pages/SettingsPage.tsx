import { CheckCircle2, Cpu, Database, Globe, Info } from 'lucide-react';
import { API_BASE_URL, getDemoModeStatus } from '../lib/demoApi';

export default function SettingsPage() {
  const demoMode = getDemoModeStatus();

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="section-title">Settings</h1>
          <p className="mt-1 text-sm text-slate-500">System configuration and demo environment state.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <div className="flex items-center gap-2 text-lg font-semibold text-text">
            <Info size={18} className="text-blue" />
            Application information
          </div>
          <div className="mt-5 space-y-4 text-sm text-slate-600">
            <div className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3">
              <span>Application</span>
              <span className="font-medium text-text">InvoiceShield</span>
            </div>
            <div className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3">
              <span>Frontend stack</span>
              <span className="font-medium text-text">React + TypeScript + Vite + Tailwind</span>
            </div>
            <div className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3">
              <span>Environment</span>
              <span className="font-medium text-text">Demo workflow</span>
            </div>
          </div>
        </div>

        <div className="panel p-5">
          <div className="flex items-center gap-2 text-lg font-semibold text-text">
            <Globe size={18} className="text-blue" />
            Backend connection status
          </div>
          <div className="mt-5 space-y-4 text-sm text-slate-600">
            <div className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3">
              <span>API base URL</span>
              <span className="font-medium text-text">{API_BASE_URL}</span>
            </div>
            <div className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3">
              <span>Connection</span>
              <span className="inline-flex items-center gap-1 font-medium text-emerald-700">
                <CheckCircle2 size={14} /> Demo backend available
              </span>
            </div>
            <div className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3">
              <span>Demo mode</span>
              <span className="font-medium text-text">{demoMode ? 'Enabled' : 'Disabled'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <div className="flex items-center gap-2 text-lg font-semibold text-text">
            <Cpu size={18} className="text-blue" />
            Verification configuration
          </div>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-600">
            <li>Three invoice documents are required before a verification request is submitted.</li>
            <li>Only PDF uploads are accepted by the frontend and validation layer.</li>
            <li>Large files are rejected before submission to match expected operational limits.</li>
          </ul>
        </div>

        <div className="panel p-5">
          <div className="flex items-center gap-2 text-lg font-semibold text-text">
            <Database size={18} className="text-blue" />
            Data handling
          </div>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-600">
            <li>Demo data is clearly isolated from any live API response path.</li>
            <li>UI flows are prepared for a real FastAPI backend contract.</li>
            <li>All request logic is centralized in the frontend API layer.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

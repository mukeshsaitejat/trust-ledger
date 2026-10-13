import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { fetchDashboard } from '../lib/demoApi';
import type { DashboardSummary, RiskPoint } from '../types';

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [distribution, setDistribution] = useState<RiskPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setIsLoading(true);

      try {
        const result = await fetchDashboard();
        if (!active) return;
        setSummary(result.summary);
        setDistribution(result.riskDistribution);
      } catch (loadError) {
        if (!active) return;
        setError(loadError instanceof Error ? loadError.message : 'Analytics could not be loaded.');
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

  const pieData = distribution.length ? distribution : [{ name: 'No data', value: 1 }];
  const pieColors = ['#16A36A', '#E9A23B', '#DC4545'];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="section-title">Analytics</h1>
          <p className="mt-1 text-sm text-slate-500">Verification statistics from the current dataset and demo mode environment.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatTile label="Total invoices" value={summary?.totalInvoices ?? 0} />
        <StatTile label="Low risk" value={summary?.lowRisk ?? 0} />
        <StatTile label="High risk" value={summary?.highRisk ?? 0} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <div className="panel p-5">
          <h2 className="text-lg font-semibold text-text">Invoice count by risk level</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution}>
                <CartesianGrid stroke="#E2E8F0" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {distribution.map((entry, index) => (
                    <Cell key={`${entry.name}-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel p-5">
          <h2 className="text-lg font-semibold text-text">Risk mix</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={80} paddingAngle={4}>
                  {pieData.map((entry, index) => (
                    <Cell key={`${entry.name}-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: number }) {
  return (
    <div className="panel p-5">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-3 text-3xl font-semibold tracking-tight text-text">{value}</div>
    </div>
  );
}

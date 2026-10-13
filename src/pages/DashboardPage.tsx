import { ArrowRight, BriefcaseBusiness, CircleAlert, FileText, ShieldCheck, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { RiskBadge } from '../components/verification/RiskBadge';
import { fetchDashboard } from '../lib/demoApi';
import type { DashboardSummary, InvoiceRecord, RiskPoint } from '../types';

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

const renderStatusBadge = (status: InvoiceRecord['verificationStatus']) => {
  const classes =
    status === 'Verified'
      ? 'bg-emerald-100 text-emerald-700'
      : status === 'Under Review'
        ? 'bg-amber-100 text-amber-700'
        : 'bg-red-100 text-red-700';

  return <span className={`badge ${classes}`}>{status}</span>;
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [riskDistribution, setRiskDistribution] = useState<RiskPoint[]>([]);
  const [recentInvoices, setRecentInvoices] = useState<InvoiceRecord[]>([]);
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
        setRiskDistribution(result.riskDistribution);
        setRecentInvoices(result.recentInvoices);
        setError(null);
      } catch (loadError) {
        if (!active) return;
        setError(loadError instanceof Error ? loadError.message : 'Dashboard data could not be loaded.');
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

  const palette = ['#16A36A', '#E9A23B', '#DC4545'];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="panel h-20 animate-pulse bg-slate-100" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="panel h-28 animate-pulse bg-slate-100" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel border-red-200 bg-red-50 p-5 text-red-700">
        <div className="flex items-center gap-3">
          <CircleAlert size={18} />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="section-title">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">Overview of invoice verification and financing risk.</p>
        </div>
        <Link
          to="/verify"
          className="inline-flex items-center gap-2 rounded-xl bg-blue px-4 py-2.5 font-medium text-white transition hover:bg-blue/90"
        >
          Verify New Invoice
          <ArrowRight size={16} />
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Total Invoices" value={summary?.totalInvoices ?? 0} icon={<BriefcaseBusiness size={18} />} accent="bg-blue/10 text-blue" />
        <SummaryCard label="Low Risk" value={summary?.lowRisk ?? 0} icon={<ShieldCheck size={18} />} accent="bg-emerald-100 text-emerald-700" />
        <SummaryCard label="Under Review" value={summary?.underReview ?? 0} icon={<FileText size={18} />} accent="bg-amber-100 text-amber-700" />
        <SummaryCard label="High Risk" value={summary?.highRisk ?? 0} icon={<TrendingUp size={18} />} accent="bg-red-100 text-red-700" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="panel p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-text">Risk distribution</h2>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistribution}>
                <CartesianGrid stroke="#E2E8F0" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) => [`${value} invoices`, 'Count']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`${entry.name}-${index}`} fill={palette[index % palette.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel p-5">
          <h2 className="text-lg font-semibold text-text">Verification queue</h2>
          <div className="mt-5 space-y-4">
            {recentInvoices.map((invoice) => (
              <div key={invoice.id} className="rounded-xl border border-border bg-slate-50 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-semibold text-text">{invoice.invoiceNumber}</div>
                    <div className="text-sm text-slate-500">{invoice.supplier}</div>
                  </div>
                  <RiskBadge level={invoice.riskLevel} />
                </div>
                <div className="mt-2 flex items-center justify-between text-sm text-slate-600">
                  <span>{invoice.verificationStatus}</span>
                  <span>{currency.format(invoice.amount)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 panel overflow-hidden">
        <div className="border-b border-border px-5 py-4">
          <h2 className="text-lg font-semibold text-text">Recent invoices</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-5 py-3 font-semibold">Invoice ID</th>
                <th className="px-5 py-3 font-semibold">Supplier</th>
                <th className="px-5 py-3 font-semibold">Amount</th>
                <th className="px-5 py-3 font-semibold">Risk</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="px-5 py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-white">
              {recentInvoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="px-5 py-3 font-medium text-text">{invoice.invoiceNumber}</td>
                  <td className="px-5 py-3 text-slate-700">{invoice.supplier}</td>
                  <td className="px-5 py-3 text-slate-700">{currency.format(invoice.amount)}</td>
                  <td className="px-5 py-3"><RiskBadge level={invoice.riskLevel} /></td>
                  <td className="px-5 py-3">{renderStatusBadge(invoice.verificationStatus)}</td>
                  <td className="px-5 py-3">
                    <Link to={`/invoices/${invoice.id}`} className="text-sm font-medium text-blue hover:text-blue/80">
                      View result
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-sm text-slate-500">{label}</div>
          <div className="mt-2 text-3xl font-semibold tracking-tight text-text">{value}</div>
        </div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${accent}`}>{icon}</div>
      </div>
    </div>
  );
}

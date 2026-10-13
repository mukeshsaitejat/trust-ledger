import { Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { RiskBadge } from '../components/verification/RiskBadge';
import { fetchInvoices } from '../lib/api';
import type { InvoiceRecord } from '../types';

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<InvoiceRecord[]>([]);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setIsLoading(true);
      try {
        const result = await fetchInvoices();
        if (!active) return;
        setInvoices(result);
      } catch (loadError) {
        if (!active) return;
        setError(loadError instanceof Error ? loadError.message : 'Invoice records could not be loaded.');
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

  const filteredInvoices = useMemo(() => {
    const q = search.trim().toLowerCase();

    return invoices.filter((invoice) => {
      const matchesSearch =
        !q || invoice.invoiceNumber.toLowerCase().includes(q) || invoice.supplier.toLowerCase().includes(q);
      const matchesRisk = riskFilter === 'all' || invoice.riskLevel === riskFilter;
      const matchesStatus = statusFilter === 'all' || invoice.verificationStatus === statusFilter;

      return matchesSearch && matchesRisk && matchesStatus;
    });
  }, [invoices, riskFilter, search, statusFilter]);

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
          <h1 className="section-title">Invoices</h1>
          <p className="mt-1 text-sm text-slate-500">Browse all available invoice verification records.</p>
        </div>
      </div>

      <div className="panel mb-6 p-4">
        <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr_0.8fr]">
          <label className="relative block">
            <span className="sr-only">Search invoice</span>
            <Search className="pointer-events-none absolute left-3 top-3.5 text-slate-400" size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by invoice ID or supplier"
              className="w-full rounded-xl border border-border bg-slate-50 py-2.5 pl-10 pr-3 text-sm text-text outline-none transition focus:border-blue"
            />
          </label>

          <select
            value={riskFilter}
            onChange={(event) => setRiskFilter(event.target.value)}
            className="rounded-xl border border-border bg-slate-50 px-3 py-2.5 text-sm text-text outline-none focus:border-blue"
          >
            <option value="all">All risk levels</option>
            <option value="Low Risk">Low Risk</option>
            <option value="Medium Risk">Medium Risk</option>
            <option value="High Risk">High Risk</option>
          </select>

          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="rounded-xl border border-border bg-slate-50 px-3 py-2.5 text-sm text-text outline-none focus:border-blue"
          >
            <option value="all">All statuses</option>
            <option value="Verified">Verified</option>
            <option value="Under Review">Under Review</option>
            <option value="Rejected">Rejected</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
      </div>

      <div className="panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-5 py-3 font-semibold">Invoice ID</th>
                <th className="px-5 py-3 font-semibold">Supplier</th>
                <th className="px-5 py-3 font-semibold">Buyer</th>
                <th className="px-5 py-3 font-semibold">Amount</th>
                <th className="px-5 py-3 font-semibold">Submission date</th>
                <th className="px-5 py-3 font-semibold">Risk level</th>
                <th className="px-5 py-3 font-semibold">Verification status</th>
                <th className="px-5 py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-white">
              {filteredInvoices.length > 0 ? (
                filteredInvoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td className="px-5 py-3 font-medium text-text">{invoice.invoiceNumber}</td>
                    <td className="px-5 py-3 text-slate-700">{invoice.supplier}</td>
                    <td className="px-5 py-3 text-slate-700">{invoice.buyer}</td>
                    <td className="px-5 py-3 text-slate-700">{currency.format(invoice.amount)}</td>
                    <td className="px-5 py-3 text-slate-700">{invoice.submissionDate}</td>
                    <td className="px-5 py-3"><RiskBadge level={invoice.riskLevel} /></td>
                    <td className="px-5 py-3">{invoice.verificationStatus}</td>
                    <td className="px-5 py-3">
                      <Link to={`/invoices/${invoice.id}`} className="font-medium text-blue hover:text-blue/80">
                        Open
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-slate-500">
                    No invoice records match the current search and filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

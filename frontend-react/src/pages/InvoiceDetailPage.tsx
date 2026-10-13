import { ArrowLeft, CheckCircle2, ShieldCheck, TriangleAlert } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AuditTimeline } from '../components/verification/AuditTimeline';
import { ComparisonTable } from '../components/verification/ComparisonTable';
import { FindingsList } from '../components/verification/FindingsList';
import { RiskBadge } from '../components/verification/RiskBadge';
import { fetchInvoiceData, getDocumentIntegrity } from '../lib/api';
import type { InvoiceRecord } from '../types';

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

type TabKey = 'overview' | 'comparison' | 'findings' | 'audit';

export default function InvoiceDetailPage() {
  const { invoiceId } = useParams();
  const [invoice, setInvoice] = useState<InvoiceRecord | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [integrityStatus, setIntegrityStatus] = useState<{ status: string; hash: string } | null>(null);
  const [integrityLoading, setIntegrityLoading] = useState(false);

  useEffect(() => {
    if (!invoiceId) return;

    let active = true;

    const load = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await fetchInvoiceData(invoiceId);
        if (!active) return;
        setInvoice(result);
      } catch (loadError) {
        if (!active) return;
        setError(loadError instanceof Error ? loadError.message : 'Invoice could not be loaded.');
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
  }, [invoiceId]);

  const tabs = useMemo(
    () => [
      { key: 'overview', label: 'Overview' },
      { key: 'comparison', label: 'Document Comparison' },
      { key: 'findings', label: 'Findings' },
      { key: 'audit', label: 'Audit Trail' },
    ],
    [],
  );

  const verifyIntegrity = async () => {
    if (!invoice) return;
    setIntegrityLoading(true);

    try {
      const result = await getDocumentIntegrity(invoice.id);
      setIntegrityStatus({ status: result.integrity_verified ? 'verified' : 'tampered', hash: result.message ?? '' });
    } catch {
      setIntegrityStatus({ status: 'error', hash: 'Could not verify integrity' });
    } finally {
      setIntegrityLoading(false);
    }
  };

  if (isLoading) {
    return <div className="panel h-48 animate-pulse bg-slate-100" />;
  }

  if (error || !invoice) {
    return (
      <div className="panel border-red-200 bg-red-50 p-5 text-red-700">
        <div className="flex items-center gap-2">
          <TriangleAlert size={18} />
          <span>{error ?? 'Invoice result was not found.'}</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <Link to="/invoices" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-text">
            <ArrowLeft size={16} />
            Back to invoices
          </Link>
        </div>
      </div>

      <div className="page-header">
        <div>
          <h1 className="section-title">Verification Result</h1>
          <p className="mt-1 text-sm text-slate-500">{invoice.invoiceNumber} · {new Date(invoice.submissionDate).toLocaleDateString()}</p>
        </div>
        <RiskBadge level={invoice.riskLevel} />
      </div>

      <div className="panel mb-6 p-5">
        <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <div className="text-sm uppercase tracking-[0.18em] text-slate-500">Risk summary</div>
            <div className="mt-3 flex items-center justify-between gap-4">
              <div>
                <div className="text-4xl font-semibold tracking-tight text-text">{invoice.riskScore}</div>
                <div className="text-sm text-slate-500">Risk score</div>
              </div>
              <RiskBadge level={invoice.riskLevel} />
            </div>
            <div className="mt-4 text-lg font-semibold text-text">{invoice.recommendation}</div>
            <p className="mt-2 max-w-xl text-sm text-slate-600">
              Risk scoring is provided by the backend signal. A mismatch or exception is a reason for investigation rather than proof of fraud.
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-slate-50 p-4">
            <div className="text-sm uppercase tracking-[0.18em] text-slate-500">Document statuses</div>
            <div className="mt-3 space-y-2 text-sm text-slate-700">
              <div className="flex items-center justify-between">
                <span>Invoice</span>
                <span className="font-medium text-text">{invoice.documentStatus.invoice}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Purchase order</span>
                <span className="font-medium text-text">{invoice.documentStatus.purchaseOrder}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Delivery receipt</span>
                <span className="font-medium text-text">{invoice.documentStatus.deliveryReceipt}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap gap-2 rounded-xl border border-border bg-white p-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key as TabKey)}
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
              activeTab === tab.key ? 'bg-blue text-white' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="panel p-5">
            <h2 className="text-lg font-semibold text-text">Invoice overview</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Invoice number" value={invoice.invoiceNumber} />
              <DetailItem label="Supplier" value={invoice.supplier} />
              <DetailItem label="Buyer" value={invoice.buyer} />
              <DetailItem label="Invoice amount" value={currency.format(invoice.amount)} />
              <DetailItem label="PO reference" value={invoice.purchaseOrderRef} />
              <DetailItem label="Invoice date" value={invoice.invoiceDate} />
              <DetailItem label="Delivery date" value={invoice.deliveryDate} />
              <DetailItem label="Verification status" value={invoice.verificationStatus} />
            </div>
          </div>

          <div className="panel p-5">
            <h2 className="text-lg font-semibold text-text">Financing recommendation</h2>
            <div className="mt-4 rounded-2xl border border-border bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Recommendation</div>
              <div className="mt-2 text-lg font-semibold text-text">{invoice.recommendation}</div>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                <li>• Review the amount variance before approval.</li>
                <li>• Confirm the delivery receipt quantity and timeline.</li>
                <li>• Escalate for manual review if discrepancy remains unresolved.</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'comparison' && <ComparisonTable rows={invoice.comparisonRows} />}
      {activeTab === 'findings' && <FindingsList findings={invoice.findings} />}
      {activeTab === 'audit' && <AuditTimeline events={invoice.auditTrail} />}

      <div className="mt-6 panel p-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="text-sm uppercase tracking-[0.18em] text-slate-500">Document integrity</div>
            <div className="mt-2 text-lg font-semibold text-text">{invoice.invoiceNumber}</div>
          </div>
          <button
            type="button"
            onClick={verifyIntegrity}
            disabled={integrityLoading}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {integrityLoading ? 'Verifying...' : 'Verify Integrity'}
          </button>
        </div>

        {integrityStatus ? (
          <div className="mt-4 rounded-2xl border border-border bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <CheckCircle2 size={16} className="text-emerald-600" />
              <span>Integrity status: {integrityStatus.status}</span>
            </div>
            <div className="mt-2 text-xs text-slate-500">Recorded hash: {integrityStatus.hash}</div>
          </div>
        ) : (
          <div className="mt-4 text-sm text-slate-500">Integrity verification is available when the backend exposes the document fingerprint service.</div>
        )}
      </div>
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-slate-50 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 font-medium text-text">{value}</div>
    </div>
  );
}

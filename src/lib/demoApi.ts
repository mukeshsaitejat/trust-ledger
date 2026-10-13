import { invoices } from './demoData';
import type { AuditTrailEntry, DashboardSummary, InvoiceRecord, RiskPoint } from '../types';

const STORAGE_KEY = 'invoice-shield-demo-submissions';

const delay = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

const readStoredInvoices = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as InvoiceRecord[]) : [];
  } catch {
    return [];
  }
};

const writeStoredInvoices = (entries: InvoiceRecord[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
};

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'demo://invoice-shield';

export async function fetchDashboard(): Promise<{
  summary: DashboardSummary;
  riskDistribution: RiskPoint[];
  recentInvoices: InvoiceRecord[];
}> {
  await delay(350);

  const allInvoices = [...invoices, ...readStoredInvoices()];
  const summary: DashboardSummary = {
    totalInvoices: allInvoices.length,
    lowRisk: allInvoices.filter((invoice) => invoice.riskLevel === 'Low Risk').length,
    underReview: allInvoices.filter((invoice) => invoice.verificationStatus === 'Under Review').length,
    highRisk: allInvoices.filter((invoice) => invoice.riskLevel === 'High Risk').length,
  };

  return {
    summary,
    riskDistribution: [
      { name: 'Low risk', value: summary.lowRisk },
      { name: 'Medium risk', value: allInvoices.filter((invoice) => invoice.riskLevel === 'Medium Risk').length },
      { name: 'High risk', value: summary.highRisk },
    ],
    recentInvoices: allInvoices.slice(0, 5),
  };
}

export async function fetchInvoices(): Promise<InvoiceRecord[]> {
  await delay(420);
  return [...invoices, ...readStoredInvoices()];
}

export async function fetchInvoice(invoiceId: string): Promise<InvoiceRecord> {
  await delay(420);
  const allInvoices = [...invoices, ...readStoredInvoices()];
  const match = allInvoices.find((invoice) => invoice.id.toLowerCase() === invoiceId.toLowerCase());

  if (!match) {
    throw new Error(`Invoice ${invoiceId} was not found in the current dataset.`);
  }

  return match;
}

export async function verifyInvoice(files: {
  invoice: File;
  purchaseOrder: File;
  deliveryReceipt: File;
}): Promise<{ verificationId: string; invoiceId: string; message: string }> {
  await delay(1200);

  const invoiceId = `INV-${String(Math.floor(2000 + Math.random() * 999)).padStart(4, '0')}`;
  const newInvoice: InvoiceRecord = {
    id: invoiceId,
    invoiceNumber: invoiceId,
    supplier: 'Verified Supplier',
    buyer: 'Verified Buyer',
    purchaseOrderRef: `PO-${Math.ceil(Math.random() * 999)}`,
    amount: 87500,
    quantity: 80,
    submissionDate: new Date().toISOString().split('T')[0],
    invoiceDate: '2026-10-08',
    deliveryDate: '2026-10-10',
    riskLevel: 'Medium Risk',
    riskScore: 46,
    recommendation: 'Manual review required',
    verificationStatus: 'Under Review',
    documentStatus: {
      invoice: 'Verified',
      purchaseOrder: 'Verified',
      deliveryReceipt: 'Verified',
    },
    comparisonRows: [
      {
        field: 'Amount',
        invoice: '₹87,500',
        po: '₹82,500',
        receipt: '₹82,500',
        status: 'Mismatch',
        explanation: 'The invoice amount exceeds the approved purchase order value by ₹5,000.',
      },
      {
        field: 'Quantity',
        invoice: '80 units',
        po: '80 units',
        receipt: '80 units',
        status: 'Match',
      },
    ],
    findings: [
      {
        id: `${invoiceId}-F1`,
        type: 'Amount mismatch',
        severity: 'Medium',
        field: 'Amount',
        observedValue: '₹87,500',
        expectedValue: '₹82,500',
        explanation: 'A difference of ₹5,000 was detected between the invoice request and the purchase order.',
      },
    ],
    auditTrail: [
      {
        id: `${invoiceId}-A1`,
        eventType: 'Verification completed',
        timestamp: new Date().toISOString(),
        description: `The submitted documents were processed for ${invoiceId}.`,
        hash: `0x${Math.random().toString(16).slice(2, 18)}`,
        chainStatus: 'Chain valid',
      },
    ],
  };

  const allInvoices = [...readStoredInvoices(), newInvoice];
  writeStoredInvoices(allInvoices);

  return {
    verificationId: `V-${Math.random().toString(36).slice(2, 10).toUpperCase()}`,
    invoiceId,
    message: 'Verification submitted successfully. A result is now available for review.',
  };
}

export async function fetchAuditTrail(): Promise<AuditTrailEntry[]> {
  await delay(300);
  return [...invoices, ...readStoredInvoices()].flatMap((invoice) =>
    invoice.auditTrail.map((entry) => ({ ...entry, invoiceId: invoice.id })),
  );
}

export async function fetchIntegrityStatus(documentName: string): Promise<{ status: 'Match' | 'Mismatch' | 'Not checked' | 'Verification failed'; hash: string }> {
  await delay(520);
  const hash = `sha256:${documentName.toLowerCase().replace(/[^a-z0-9]/g, '')}`;
  return {
    status: 'Match',
    hash,
  };
}

export function getDemoModeStatus(): boolean {
  return true;
}

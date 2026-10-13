/**
 * Real API client for InvoiceShield backend (FastAPI @ localhost:8000)
 *
 * All functions talk directly to the backend. No demo/mock data is used.
 */

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface BackendInvoiceSummary {
  verification_id: string;
  invoice_id: string;
  invoice_number: string;
  supplier_name: string;
  buyer_name: string;
  amount: number;
  quantity: number;
  invoice_date: string | null;
  po_reference: string | null;
  verification_status: string; // approved | review_required | rejected
  risk_score: number | null;
  risk_level: string | null; // MINIMAL | LOW | MEDIUM | HIGH
  financing_recommendation: string | null;
  has_duplicates: boolean;
  findings_count: number;
  critical_count: number;
  verified_at: string;
}

export interface BackendListResponse {
  invoices: BackendInvoiceSummary[];
  total: number;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function mapVerificationStatus(status: string): 'Verified' | 'Under Review' | 'Rejected' | 'Pending' {
  switch (status) {
    case 'approved': return 'Verified';
    case 'review_required': return 'Under Review';
    case 'rejected': return 'Rejected';
    default: return 'Pending';
  }
}

function mapRiskLevel(level: string | null): 'Low Risk' | 'Medium Risk' | 'High Risk' | 'Pending' {
  switch (level) {
    case 'MINIMAL':
    case 'LOW': return 'Low Risk';
    case 'MEDIUM': return 'Medium Risk';
    case 'HIGH': return 'High Risk';
    default: return 'Pending';
  }
}

function mapRecommendation(rec: string | null, score: number | null): string {
  if (rec === 'APPROVED') return 'Safe to approve';
  if (rec === 'MANUAL_REVIEW') return 'Manual review required';
  if (rec === 'REJECT') return 'Reject — high risk detected';
  const s = score ?? 0;
  if (s >= 76) return 'Reject — high risk detected';
  if (s >= 51) return 'Manual review required';
  if (s >= 26) return 'Proceed with caution';
  return 'Safe to approve';
}

function getSeverityFromWeight(weight: number): 'Low' | 'Medium' | 'High' | 'Critical' {
  if (weight >= 40) return 'Critical';
  if (weight >= 20) return 'High';
  if (weight >= 10) return 'Medium';
  return 'Low';
}

const INR = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

// ─── Health ───────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<{ status: string; app_name: string; version: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) throw new Error('Backend health check failed');
  return response.json();
}

// ─── System stats ─────────────────────────────────────────────────────────────

export async function getSystemStats() {
  const response = await fetch(`${API_BASE_URL}/system/stats`);
  if (!response.ok) throw new Error('Failed to fetch system stats');
  return response.json();
}

// ─── Documents ────────────────────────────────────────────────────────────────

export async function uploadDocument(
  file: File,
  documentType: 'invoice' | 'purchase_order' | 'delivery_receipt',
) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
}

export async function getDocument(documentId: string) {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`);
  if (!response.ok) throw new Error('Failed to fetch document');
  return response.json();
}

// ─── Invoices ─────────────────────────────────────────────────────────────────

/** Fetch all invoices from the backend, transformed for the frontend. */
export async function fetchInvoices() {
  const response = await fetch(`${API_BASE_URL}/invoices/`);
  if (!response.ok) throw new Error('Failed to fetch invoice list');
  const data: BackendListResponse = await response.json();

  return data.invoices.map((inv) => ({
    id: inv.invoice_id,
    invoiceNumber: inv.invoice_number,
    supplier: inv.supplier_name,
    buyer: inv.buyer_name,
    purchaseOrderRef: inv.po_reference ?? 'N/A',
    amount: inv.amount,
    quantity: inv.quantity,
    submissionDate: inv.verified_at.slice(0, 10),
    invoiceDate: inv.invoice_date ?? inv.verified_at.slice(0, 10),
    deliveryDate: inv.verified_at.slice(0, 10),
    riskLevel: mapRiskLevel(inv.risk_level),
    riskScore: inv.risk_score ?? 0,
    recommendation: mapRecommendation(inv.financing_recommendation, inv.risk_score),
    verificationStatus: mapVerificationStatus(inv.verification_status),
    documentStatus: {
      invoice: 'Verified' as const,
      purchaseOrder: 'Verified' as const,
      deliveryReceipt: 'Verified' as const,
    },
    comparisonRows: [],
    findings: [],
    auditTrail: [],
  }));
}

/** Fetch dashboard aggregate data derived from the backend. */
export async function fetchDashboard() {
  const [invoices, stats] = await Promise.all([
    fetchInvoices(),
    getSystemStats(),
  ]);

  const summary = {
    totalInvoices: stats.total_verifications as number,
    lowRisk: invoices.filter((i) => i.riskLevel === 'Low Risk').length,
    underReview: invoices.filter((i) => i.verificationStatus === 'Under Review').length,
    highRisk: invoices.filter((i) => i.riskLevel === 'High Risk').length,
  };

  const riskDistribution = [
    { name: 'Low risk', value: summary.lowRisk },
    { name: 'Medium risk', value: invoices.filter((i) => i.riskLevel === 'Medium Risk').length },
    { name: 'High risk', value: summary.highRisk },
  ];

  return {
    summary,
    riskDistribution,
    recentInvoices: invoices.slice(0, 5),
  };
}

/** Full detail for a single invoice, using the real backend endpoints. */
export async function fetchInvoiceData(invoiceId: string) {
  // Run verification data + risk in parallel; audit trail may 404 on first upload
  const [verificationRes, riskRes] = await Promise.all([
    fetch(`${API_BASE_URL}/invoices/${invoiceId}/verification`),
    fetch(`${API_BASE_URL}/invoices/${invoiceId}/risk`),
  ]);

  if (!verificationRes.ok) {
    throw new Error(`Verification not found for invoice ${invoiceId}`);
  }
  if (!riskRes.ok) {
    throw new Error(`Risk data not found for invoice ${invoiceId}`);
  }

  const verification = await verificationRes.json();
  const riskData = await riskRes.json();

  // Audit trail — graceful fallback if no events yet
  let auditEvents: any[] = [];
  try {
    const auditRes = await fetch(`${API_BASE_URL}/audit/trail/${invoiceId}`);
    if (auditRes.ok) {
      const auditBody = await auditRes.json();
      auditEvents = auditBody.events ?? [];
    }
  } catch {
    // No audit events yet — fine
  }

  const fields = verification.invoice_fields ?? {};
  const score = riskData.risk_score ?? 0;

  return {
    id: invoiceId,
    invoiceNumber: fields.invoice_number ?? invoiceId,
    supplier: fields.supplier_name ?? 'Unknown Supplier',
    buyer: fields.buyer_name ?? 'Unknown Buyer',
    purchaseOrderRef: fields.po_reference ?? 'N/A',
    amount: fields.amount ?? 0,
    quantity: fields.quantity ?? 0,
    submissionDate: new Date().toISOString().slice(0, 10),
    invoiceDate: fields.invoice_date ?? new Date().toISOString().slice(0, 10),
    deliveryDate: fields.invoice_date ?? new Date().toISOString().slice(0, 10),
    riskLevel: mapRiskLevel(riskData.risk_level),
    riskScore: score,
    recommendation: mapRecommendation(riskData.financing_recommendation, score),
    verificationStatus: mapVerificationStatus(verification.comparison_result?.status ?? ''),
    documentStatus: {
      invoice: 'Verified' as const,
      purchaseOrder: verification.po_fields ? ('Verified' as const) : ('Missing' as const),
      deliveryReceipt: verification.delivery_fields ? ('Verified' as const) : ('Missing' as const),
    },
    comparisonRows: (verification.comparison_result?.findings ?? []).map((f: any) => ({
      field: f.field ?? f.finding_type,
      invoice: String(f.actual_value ?? '—'),
      po: String(f.expected_value ?? '—'),
      receipt: String(f.actual_value ?? '—'),
      status: f.severity === 'info' ? 'Match' : 'Mismatch',
      explanation: f.message,
    })),
    findings: (riskData.risk_factors ?? []).map((factor: any, index: number) => ({
      id: `${invoiceId}-F${index + 1}`,
      type: factor.factor,
      severity: getSeverityFromWeight(factor.weight ?? 0),
      field: factor.factor,
      observedValue: factor.description,
      expectedValue: 'N/A',
      explanation: factor.description,
    })),
    auditTrail: auditEvents.map((event: any) => ({
      id: String(event.id),
      eventType: event.event_type,
      timestamp: event.timestamp ?? event.created_at,
      description: event.event_data?.filename
        ? `Uploaded ${event.event_data.filename}`
        : event.event_type.replace(/_/g, ' '),
      hash: event.event_hash ?? '',
      previousHash: event.previous_hash ?? undefined,
      chainStatus: 'Chain valid' as const,
    })),
  };
}

/** Submit verification. */
export async function verifyInvoice(
  invoiceId: string,
  poId: string,
  deliveryReceiptId: string,
) {
  const response = await fetch(`${API_BASE_URL}/invoices/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      invoice_id: invoiceId,
      po_id: poId,
      delivery_receipt_id: deliveryReceiptId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Verification failed');
  }

  return response.json();
}

export async function getVerification(invoiceId: string) {
  const response = await fetch(`${API_BASE_URL}/invoices/${invoiceId}/verification`);
  if (!response.ok) throw new Error('Failed to fetch verification');
  return response.json();
}

export async function getRiskAssessment(invoiceId: string) {
  const response = await fetch(`${API_BASE_URL}/invoices/${invoiceId}/risk`);
  if (!response.ok) throw new Error('Failed to fetch risk assessment');
  return response.json();
}

// ─── Audit ────────────────────────────────────────────────────────────────────

/** Get all audit events across the platform (for the Audit Trail page). */
export async function fetchAuditTrail() {
  const response = await fetch(`${API_BASE_URL}/audit/events`);
  if (!response.ok) throw new Error('Failed to fetch audit events');
  const body = await response.json();

  return (body.events as any[]).map((event) => ({
    id: String(event.id),
    invoiceId: event.entity_id,
    eventType: event.event_type,
    timestamp: event.timestamp ?? event.created_at,
    description: event.event_data?.filename
      ? `Uploaded ${event.event_data.filename}`
      : event.event_type.replace(/_/g, ' '),
    hash: event.event_hash ?? '',
    previousHash: event.previous_hash ?? undefined,
    chainStatus: 'Chain valid' as const,
  }));
}

export async function getAuditTrail(entityId: string) {
  const response = await fetch(`${API_BASE_URL}/audit/trail/${entityId}`);
  if (!response.ok) throw new Error('Failed to fetch audit trail');
  return response.json();
}

export async function verifyAuditChain() {
  const response = await fetch(`${API_BASE_URL}/audit/verify-chain`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to verify audit chain');
  return response.json();
}

export async function getAuditStats() {
  const response = await fetch(`${API_BASE_URL}/audit/stats`);
  if (!response.ok) throw new Error('Failed to fetch audit stats');
  return response.json();
}

export async function getDocumentIntegrity(documentId: string) {
  const response = await fetch(
    `${API_BASE_URL}/audit/document/${documentId}/integrity`,
  );
  if (!response.ok) throw new Error('Failed to check document integrity');
  return response.json();
}

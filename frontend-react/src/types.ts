export type RiskLevel = 'Low Risk' | 'Medium Risk' | 'High Risk' | 'Pending';
export type VerificationStatus = 'Verified' | 'Under Review' | 'Rejected' | 'Pending';
export type ComparisonStatus = 'Match' | 'Mismatch' | 'Missing' | 'Unable to verify';
export type FindingSeverity = 'Low' | 'Medium' | 'High' | 'Critical';
export type ChainStatus = 'Chain valid' | 'Chain verification failed' | 'Verification unavailable';

export interface ComparisonRow {
  field: string;
  invoice: string;
  po: string;
  receipt: string;
  status: ComparisonStatus;
  explanation?: string;
}

export interface Finding {
  id: string;
  type: string;
  severity: FindingSeverity;
  field: string;
  observedValue: string;
  expectedValue: string;
  explanation: string;
}

export interface AuditEvent {
  id: string;
  eventType: string;
  timestamp: string;
  description: string;
  hash: string;
  previousHash?: string;
  chainStatus: ChainStatus;
}

export interface AuditTrailEntry extends AuditEvent {
  invoiceId: string;
}

export interface InvoiceRecord {
  id: string;
  invoiceNumber: string;
  supplier: string;
  buyer: string;
  purchaseOrderRef: string;
  amount: number;
  quantity: number;
  submissionDate: string;
  invoiceDate: string;
  deliveryDate: string;
  riskLevel: RiskLevel;
  riskScore: number;
  recommendation: string;
  verificationStatus: VerificationStatus;
  documentStatus: {
    invoice: 'Verified' | 'Pending' | 'Missing';
    purchaseOrder: 'Verified' | 'Pending' | 'Missing';
    deliveryReceipt: 'Verified' | 'Pending' | 'Missing';
  };
  comparisonRows: ComparisonRow[];
  findings: Finding[];
  auditTrail: AuditEvent[];
}

export interface DashboardSummary {
  totalInvoices: number;
  lowRisk: number;
  underReview: number;
  highRisk: number;
}

export interface RiskPoint {
  name: string;
  value: number;
}

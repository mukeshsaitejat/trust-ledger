/**
 * Real API client for InvoiceShield backend
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Check backend health
 */
export async function checkHealth(): Promise<{ status: string; app_name: string; version: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Backend health check failed');
  }
  return response.json();
}

/**
 * Get system statistics
 */
export async function getSystemStats() {
  const response = await fetch(`${API_BASE_URL}/system/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch system stats');
  }
  return response.json();
}

/**
 * Upload a document
 */
export async function uploadDocument(file: File, documentType: 'invoice' | 'purchase_order' | 'delivery_receipt') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
}

/**
 * Verify invoice
 */
export async function verifyInvoice(invoiceId: string, poId: string, deliveryReceiptId: string) {
  const response = await fetch(`${API_BASE_URL}/invoices/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      invoice_id: invoiceId,
      po_id: poId,
      delivery_receipt_id: deliveryReceiptId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Verification failed');
  }

  return response.json();
}

/**
 * Get verification result
 */
export async function getVerification(invoiceId: string) {
  const response = await fetch(`${API_BASE_URL}/invoices/${invoiceId}/verification`);
  if (!response.ok) {
    throw new Error('Failed to fetch verification');
  }
  return response.json();
}

/**
 * Get risk assessment
 */
export async function getRiskAssessment(invoiceId: string) {
  const response = await fetch(`${API_BASE_URL}/invoices/${invoiceId}/risk`);
  if (!response.ok) {
    throw new Error('Failed to fetch risk assessment');
  }
  return response.json();
}

/**
 * Get audit trail
 */
export async function getAuditTrail(entityId: string) {
  const response = await fetch(`${API_BASE_URL}/audit/trail/${entityId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch audit trail');
  }
  return response.json();
}

/**
 * Verify audit chain
 */
export async function verifyAuditChain() {
  const response = await fetch(`${API_BASE_URL}/audit/verify-chain`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to verify audit chain');
  }
  return response.json();
}

/**
 * Get document integrity
 */
export async function getDocumentIntegrity(documentId: string) {
  const response = await fetch(`${API_BASE_URL}/audit/document/${documentId}/integrity`);
  if (!response.ok) {
    throw new Error('Failed to check document integrity');
  }
  return response.json();
}

/**
 * Get audit statistics
 */
export async function getAuditStats() {
  const response = await fetch(`${API_BASE_URL}/audit/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch audit stats');
  }
  return response.json();
}

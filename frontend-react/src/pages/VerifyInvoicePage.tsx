import { AlertCircle, ArrowRight, CheckCircle2, FileText, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileUploadCard } from '../components/verification/FileUploadCard';
import { uploadDocument, verifyInvoice as realVerifyInvoice } from '../lib/api';

const MAX_FILE_SIZE = 10 * 1024 * 1024;

export default function VerifyInvoicePage() {
  const navigate = useNavigate();
  const [files, setFiles] = useState<Record<'invoice' | 'purchaseOrder' | 'deliveryReceipt', File | null>>({
    invoice: null,
    purchaseOrder: null,
    deliveryReceipt: null,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const validatePdf = (file: File) => file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');

  const handleFileChange = (key: keyof typeof files, file: File) => {
    const nextErrors = { ...errors };

    if (!validatePdf(file)) {
      nextErrors[key] = 'Unsupported file type. Please upload a PDF only.';
      setErrors(nextErrors);
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      nextErrors[key] = 'File exceeds the supported 10 MB limit for invoice verification.';
      setErrors(nextErrors);
      return;
    }

    delete nextErrors[key];
    setErrors(nextErrors);
    setFiles((previous) => ({ ...previous, [key]: file }));
  };

  const handleRemove = (key: keyof typeof files) => {
    setFiles((previous) => ({ ...previous, [key]: null }));
    setErrors((previous) => {
      const next = { ...previous };
      delete next[key];
      return next;
    });
  };

  const handleSubmit = async () => {
    const missingFiles = (Object.keys(files) as Array<keyof typeof files>).filter((key) => !files[key]);

    if (missingFiles.length > 0) {
      setSubmissionError('Please attach all three supporting documents before submitting the verification request.');
      return;
    }

    const invalidFiles = Object.entries(files) as Array<[keyof typeof files, File | null]>;
    const invalidType = invalidFiles.some(([key, file]) => file && !validatePdf(file));
    const invalidSize = invalidFiles.some(([key, file]) => file && file.size > MAX_FILE_SIZE);

    if (invalidType || invalidSize) {
      setSubmissionError('One or more files failed validation and must be corrected before continuing.');
      return;
    }

    setIsSubmitting(true);
    setSubmissionError(null);

    try {
      // Upload documents to real backend
      console.log('Uploading documents to backend...');
      
      const invoiceUpload = await uploadDocument(files.invoice!, 'invoice');
      const poUpload = await uploadDocument(files.purchaseOrder!, 'purchase_order');
      const receiptUpload = await uploadDocument(files.deliveryReceipt!, 'delivery_receipt');
      
      console.log('Documents uploaded successfully:', {
        invoice: invoiceUpload.document_id,
        po: poUpload.document_id,
        receipt: receiptUpload.document_id
      });

      // Verify invoice using real backend
      const verificationResult = await realVerifyInvoice(
        invoiceUpload.document_id,
        poUpload.document_id,
        receiptUpload.document_id
      );
      
      console.log('Verification result:', verificationResult);

      // Navigate to results page with the invoice ID
      navigate(`/invoices/${invoiceUpload.document_id}`);
    } catch (submitError) {
      console.error('Verification error:', submitError);
      setSubmissionError(
        submitError instanceof Error ? submitError.message : 'Verification could not complete. Please check the backend connection and try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const allFilesReady = Object.values(files).every(Boolean);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="section-title">Verify New Invoice</h1>
          <p className="mt-1 text-sm text-slate-500">Upload the supporting documents to begin verification.</p>
        </div>
      </div>


      <div className="grid gap-4 xl:grid-cols-3">
        <FileUploadCard
          label="Invoice PDF"
          description="Primary invoice request document"
          file={files.invoice}
          onSelect={(file) => handleFileChange('invoice', file)}
          onRemove={() => handleRemove('invoice')}
          error={errors.invoice}
        />
        <FileUploadCard
          label="Purchase Order PDF"
          description="Buyer-approved order details"
          file={files.purchaseOrder}
          onSelect={(file) => handleFileChange('purchaseOrder', file)}
          onRemove={() => handleRemove('purchaseOrder')}
          error={errors.purchaseOrder}
        />
        <FileUploadCard
          label="Delivery Receipt PDF"
          description="Evidence of quantity delivered"
          file={files.deliveryReceipt}
          onSelect={(file) => handleFileChange('deliveryReceipt', file)}
          onRemove={() => handleRemove('deliveryReceipt')}
          error={errors.deliveryReceipt}
        />
      </div>

      {submissionError && (
        <div className="mt-5 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle size={16} />
          <span>{submissionError}</span>
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-border bg-white p-4">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <FileText size={16} className="text-blue" />
          {allFilesReady ? 'All required documents are ready for verification.' : 'Three PDF documents are required to continue.'}
        </div>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!allFilesReady || isSubmitting}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue px-5 py-3 font-medium text-white transition hover:bg-blue/90 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {isSubmitting ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Verifying...
            </>
          ) : (
            <>
              Verify Invoice
              <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>

      {allFilesReady && (
        <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 size={16} />
            File validation passed
          </div>
          <p className="mt-1 text-emerald-700">The selected documents are valid PDFs and are ready for verification submission.</p>
        </div>
      )}
    </div>
  );
}

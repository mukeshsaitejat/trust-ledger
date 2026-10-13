# InvoiceShield Testing Guide

## Phase 2 Testing with Your Own PDFs

This guide will help you test the InvoiceShield system with your own invoice, purchase order, and delivery receipt PDFs.

## Prerequisites

1. **Server Running:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Server will be at: `http://localhost:8000`

2. **API Documentation:**
   Open `http://localhost:8000/docs` in your browser for interactive API testing

## Testing Workflow

### Step 1: Upload Your Documents

Upload each PDF document and save the `document_id` from each response.

#### Option A: Using Swagger UI (`http://localhost:8000/docs`)

1. Go to `POST /documents/upload`
2. Click "Try it out"
3. Upload your PDF file
4. Select `document_type` from dropdown:
   - `invoice`
   - `purchase_order`
   - `delivery_receipt`
5. Click "Execute"
6. **Copy the `document_id` from the response!**

#### Option B: Using curl (Command Line)

```bash
# Upload Invoice
curl -X POST "http://localhost:8000/documents/upload" ^
  -F "file=@path\to\your\invoice.pdf" ^
  -F "document_type=invoice"

# Upload Purchase Order
curl -X POST "http://localhost:8000/documents/upload" ^
  -F "file=@path\to\your\po.pdf" ^
  -F "document_type=purchase_order"

# Upload Delivery Receipt
curl -X POST "http://localhost:8000/documents/upload" ^
  -F "file=@path\to\your\delivery.pdf" ^
  -F "document_type=delivery_receipt"
```

**Expected Response:**
```json
{
  "document_id": "uuid-here",
  "filename": "invoice.pdf",
  "document_type": "invoice",
  "file_size": 12345,
  "sha256_hash": "abc123...",
  "uploaded_at": "2026-10-13T..."
}
```

### Step 2: Verify the Invoice

Now verify the invoice against PO and/or delivery receipt.

#### Option A: Using Swagger UI

1. Go to `POST /invoices/verify`
2. Click "Try it out"
3. Fill in the JSON body:
   ```json
   {
     "invoice_id": "your-invoice-document-id-here",
     "po_id": "your-po-document-id-here",
     "delivery_receipt_id": "your-delivery-document-id-here"
   }
   ```
4. Click "Execute"
5. Review the verification results

#### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/invoices/verify" ^
  -H "Content-Type: application/json" ^
  -d "{\"invoice_id\":\"uuid1\",\"po_id\":\"uuid2\",\"delivery_receipt_id\":\"uuid3\"}"
```

### Step 3: Understanding the Results

The verification response contains:

```json
{
  "verification_id": "unique-verification-id",
  "invoice_id": "...",
  "invoice_fields": {
    "invoice_number": "INV-001",
    "supplier_name": "Company A",
    "buyer_name": "Company B",
    "amount": 5000.00,
    "quantity": 100,
    "extraction_successful": true,
    "extraction_errors": []
  },
  "po_fields": { ... },
  "delivery_fields": { ... },
  "comparison_result": {
    "status": "approved | review_required | rejected",
    "findings": [
      {
        "finding_type": "amount_mismatch",
        "severity": "critical",
        "field": "amount",
        "message": "Invoice amount differs from PO by $1000.00",
        "expected_value": 5000.00,
        "actual_value": 6000.00
      }
    ],
    "findings_count": 1,
    "critical_count": 1,
    "high_count": 0,
    "medium_count": 0
  },
  "verified_at": "2026-10-13T..."
}
```

## What the System Checks

### 1. **Mandatory Fields**
- Invoice number
- Supplier name
- Buyer name
- Invoice amount

### 2. **Cross-Document Comparisons**
- **Amount Match:** Invoice amount vs PO amount
- **Quantity Match:** Invoice quantity vs delivered quantity vs PO quantity
- **Supplier Consistency:** Supplier name across all documents
- **Buyer Consistency:** Buyer name across all documents  
- **PO Reference:** PO number consistency

### 3. **Risk Findings**

| Finding Type | Severity | Description |
|---|---|---|
| `missing_field` | high | Mandatory field not found |
| `amount_mismatch` | critical/high | Invoice amount ≠ PO amount |
| `quantity_overcharge` | critical | Invoice qty > delivered qty |
| `supplier_mismatch` | critical | Different suppliers |
| `buyer_mismatch` | high | Different buyers |
| `po_mismatch` | critical | PO reference mismatch |

### 4. **Verification Status**
- **approved:** No issues found
- **review_required:** Medium/high severity findings
- **rejected:** Critical findings detected

## PDF Format Requirements

### For Best Results:
- **Text-based PDFs** (not scanned images)
- Clear field labels like:
  - "Invoice #", "Invoice Number", "INV #"
  - "Supplier:", "Vendor:", "From:"
  - "Total:", "Amount:", "Grand Total:"
  - "PO #", "Purchase Order"
  - "Quantity:", "Qty:", "Units:"

### Example Good Format:
```
Invoice #INV-2026-001
Date: 10/13/2026

From: TechSupply Inc
To: Acme Corporation

Purchase Order: PO-2026-100

Quantity: 100 units
Unit Price: $50.00
Total: $5,000.00
```

## Testing Scenarios

### ✅ Test Case 1: Clean Invoice (Should Pass)
- Upload matching invoice, PO, and delivery receipt
- All amounts, quantities, and parties should align
- Expected: `status: "approved"` or `"review_required"` with minor findings

### ❌ Test Case 2: Amount Mismatch
- Invoice amount > PO amount
- Expected: `amount_mismatch` finding with `severity: "critical"`

### ❌ Test Case 3: Quantity Overcharge  
- Invoice quantity > delivered quantity
- Expected: `quantity_overcharge` finding with `severity: "critical"`

### ❌ Test Case 4: Supplier Mismatch
- Different supplier name on invoice vs PO
- Expected: `supplier_mismatch` finding with `severity: "critical"`

### ❌ Test Case 5: Missing Fields
- Invoice without mandatory fields
- Expected: `missing_field` findings with `severity: "high"`

## Troubleshooting

### Problem: "Extraction not successful"
**Solution:**  
- Check if PDF is text-based (not a scanned image)
- Verify field labels are recognizable (see format requirements above)
- Check `extraction_errors` in response for details

### Problem: False positive findings
**Solution:**
- Check if field values are slightly different (spacing, punctuation)
- Normalization handles some differences but not all
- Example: "TechSupply Inc" vs "Tech Supply Inc." might mismatch

### Problem: Document not found error
**Solution:**
- Verify you're using the correct `document_id` from upload response
- Check that document was uploaded successfully
- Try retrieving document: `GET /documents/{document_id}`

## Advanced: Testing with Python

```python
import requests

# Upload documents
with open('invoice.pdf', 'rb') as f:
    inv_resp = requests.post(
        'http://localhost:8000/documents/upload',
        files={'file': f},
        data={'document_type': 'invoice'}
    )
invoice_id = inv_resp.json()['document_id']

with open('po.pdf', 'rb') as f:
    po_resp = requests.post(
        'http://localhost:8000/documents/upload',
        files={'file': f},
        data={'document_type': 'purchase_order'}
    )
po_id = po_resp.json()['document_id']

# Verify
verify_resp = requests.post(
    'http://localhost:8000/invoices/verify',
    json={
        'invoice_id': invoice_id,
        'po_id': po_id
    }
)

result = verify_resp.json()
print(f"Status: {result['comparison_result']['status']}")
print(f"Findings: {result['comparison_result']['findings_count']}")
for finding in result['comparison_result']['findings']:
    print(f"- {finding['message']}")
```

## What's Extracted from Each Document Type

### Invoice:
- invoice_number
- invoice_date
- supplier_name
- buyer_name
- po_reference
- amount
- quantity
- unit_price

### Purchase Order:
- po_number
- po_date
- supplier_name
- buyer_name
- amount
- quantity

### Delivery Receipt:
- receipt_number
- delivery_date
- supplier_name
- buyer_name
- po_reference
- delivered_quantity

## Need Help?

1. Check server logs for detailed error messages
2. Review `extraction_errors` in the response
3. Verify PDF format and content
4. Test with synthetic PDFs first (in `tests/test_phase2.py`)

## Push to GitHub

After testing, push your code:

```bash
git push -u origin main
```

If authentication fails, set up a Personal Access Token:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

Or use GitHub Desktop/GitHub CLI for easier authentication.

---

Happy Testing! 🚀

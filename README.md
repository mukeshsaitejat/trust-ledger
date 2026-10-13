# InvoiceShield 🛡️

**AI-Assisted Invoice Financing Verification Platform**  
*Built for Synesis 26 FinTech Hackathon*

## 🎯 Overview

InvoiceShield is an enterprise-grade REST API platform that helps financial institutions verify invoice financing requests with confidence. It provides:

- **Intelligent PDF Extraction** - Extract structured data from invoices, purchase orders, and delivery receipts
- **3-Way Verification** - Cross-check invoices against POs and delivery receipts
- **Duplicate Detection** - Identify exact file duplicates and business-logic duplicates
- **Risk Scoring Engine** - Calculate explainable risk scores (0-100) with financing recommendations
- **Audit Trail** - Maintain tamper-evident, hash-linked audit logs for compliance
- **Document Integrity** - Verify document authenticity using SHA-256 hashing

## 🚀 Quick Start

### Option 1: Web Interface (Easiest) ⭐

**One-command start:**
```bash
start_demo.bat
```

This will:
- Start the backend API server
- Start the frontend web interface
- Open your browser automatically

Then visit `http://localhost:3000` to use the web interface!

**Or manually:**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Backend**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Start Frontend** (in new terminal)
   ```bash
   cd frontend
   python serve.py
   ```

4. **Open Browser**
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`

### Option 2: API Only

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   copy .env.example .env
   ```

3. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

   **Server:** `http://localhost:8000`  
   **API Docs:** `http://localhost:8000/docs`  
   **ReDoc:** `http://localhost:8000/redoc`

### Option 3: Automated Demo Script

```bash
python demo_script.py
```

This will run a complete automated demo showcasing all features with test PDFs.

## 📚 API Endpoints

### Document Management
- `POST /documents/upload` - Upload invoice, PO, or delivery receipt
- `GET /documents/{document_id}` - Retrieve document metadata
- `GET /health` - Health check endpoint

### Invoice Verification
- `POST /invoices/verify` - Verify invoice against PO and delivery receipt
- `GET /invoices/{invoice_id}/verification` - Get verification results
- `GET /invoices/{invoice_id}/risk` - Get risk assessment

### Audit & Integrity
- `GET /audit/trail/{entity_id}` - Get complete audit trail for document/verification
- `GET /audit/verify-chain` - Verify audit chain integrity
- `GET /audit/document/{document_id}/integrity` - Verify document hasn't been tampered
- `GET /audit/stats` - Get audit statistics

### System
- `GET /system/stats` - Get platform usage statistics

## 🎬 Usage Examples

### Using Web Interface (Recommended)

1. **Visit** `http://localhost:3000` after starting servers
2. **Upload** your invoice, PO, and delivery receipt PDFs
3. **Click** "Upload All Documents"
4. **Click** "Verify Invoice"
5. **Review** results with visual risk meter and detailed findings

### Using Swagger UI

1. **Visit** `http://localhost:8000/docs`
2. **Try out** the endpoints interactively
3. **Upload** documents via `/documents/upload`
4. **Verify** via `/invoices/verify`

### Using cURL

```bash
# 1. Upload Invoice
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@invoice.pdf" \
  -F "document_type=invoice"

# 2. Upload Purchase Order
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@purchase_order.pdf" \
  -F "document_type=purchase_order"

# 3. Upload Delivery Receipt
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@delivery_receipt.pdf" \
  -F "document_type=delivery_receipt"

# 4. Verify Invoice
curl -X POST "http://localhost:8000/invoices/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "abc-123",
    "po_id": "def-456",
    "delivery_receipt_id": "ghi-789"
  }'

# 5. Check Risk Score
curl "http://localhost:8000/invoices/abc-123/risk"

# 6. Get System Stats
curl "http://localhost:8000/system/stats"
```

## 📊 Risk Assessment

The platform calculates risk scores based on configurable weights:

| Risk Factor | Weight | Description |
|------------|--------|-------------|
| Exact Duplicate | 50 | Same file uploaded before |
| Business Duplicate | 40 | Same invoice#, supplier, amount |
| Critical Finding | 30 | PO mismatch, supplier mismatch |
| High Finding | 20 | Amount/quantity mismatch |
| Medium Finding | 10 | Missing optional fields |

**Risk Levels:**
- **MINIMAL** (0-25): Low risk, safe to approve
- **LOW** (26-50): Minor issues, can approve
- **MEDIUM** (51-75): Review recommended
- **HIGH** (76-100): Reject or manual investigation

**Financing Recommendations:**
- **APPROVED** - Safe to finance
- **REVIEW** - Manual review recommended
- **MANUAL_REVIEW** - Requires investigation
- **REJECT** - Do not finance

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Phase

```bash
pytest tests/test_phase1.py -v
pytest tests/test_phase2.py -v
pytest tests/test_phase3.py -v
pytest tests/test_phase4.py -v
```

### Test with Synthetic PDFs

The project includes synthetic test PDFs in `InvoiceShield_Synthetic_Test_PDFs/`:
- **case1_clean** - Perfect match (should approve)
- **case2_amount_mismatch** - Invoice amount differs from PO
- **case3_quantity_mismatch** - Quantity discrepancy
- **case4_supplier_mismatch** - Different supplier names
- **case5_duplicate_invoice** - Duplicate submission test

## 📁 Project Structure

```
InvoiceShield/
├── app/                  # Backend application
│   ├── api/              # API route handlers
│   │   ├── routes_documents.py
│   │   ├── routes_invoices.py
│   │   ├── routes_audit.py
│   │   └── routes_system.py
│   ├── core/             # Configuration
│   │   └── config.py
│   ├── db/               # Database models
│   │   ├── database.py
│   │   └── models.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── documents.py
│   │   ├── verification.py
│   │   └── risk.py
│   ├── services/         # Business logic
│   │   ├── document_storage.py
│   │   ├── pdf_extractor.py
│   │   ├── field_normalizer.py
│   │   ├── document_comparator.py
│   │   ├── duplicate_detector.py
│   │   ├── risk_engine.py
│   │   └── audit_service.py
│   └── main.py           # FastAPI application
├── frontend/             # Web interface
│   ├── index.html        # Single-page app
│   ├── serve.py          # Development server
│   └── README.md         # Frontend docs
├── tests/                # Test suites
│   ├── test_phase1.py
│   ├── test_phase2.py
│   ├── test_phase3.py
│   ├── test_phase4.py
│   └── test_phase5.py
├── storage/              # Document storage
│   └── documents/
├── demo_script.py        # Automated demo
├── start_demo.bat        # One-click starter
├── requirements.txt
└── README.md
```

## ✅ Development Status

- [x] **Phase 1:** Backend Foundation and Document Intake
- [x] **Phase 2:** PDF Extraction and Document Verification
- [x] **Phase 3:** Duplicate Detection and Risk Engine
- [x] **Phase 4:** Audit Trail and Document Integrity
- [x] **Phase 5:** Integration, Testing and Demo Readiness

**All 37 tests passing** ✨

## 🛠️ Technology Stack

- **Framework:** FastAPI 0.115.0
- **Database:** SQLite with SQLAlchemy ORM
- **PDF Processing:** PyMuPDF (fitz) 1.24.13
- **Validation:** Pydantic 2.9.0
- **Testing:** pytest 8.3.3
- **Server:** Uvicorn with async support

## 🔒 Security Features

- SHA-256 document fingerprinting
- Hash-linked audit trail (blockchain-inspired)
- Duplicate detection at file and business logic levels
- Document integrity verification
- Tamper-evident event logging

## 🏆 Key Features

1. **Smart PDF Extraction** - Handles multiple currency formats (₹, $, USD, INR)
2. **Flexible Field Matching** - Robust pattern matching for various PDF layouts
3. **Explainable AI** - Every risk score comes with detailed explanations
4. **Audit Compliance** - Full event trail with hash chaining for immutability
5. **Production Ready** - Comprehensive error handling, validation, and testing

## 📝 License

Built for Synesis 26 FinTech Hackathon

## 👥 Team

Trust Ledger - Building the future of invoice financing verification

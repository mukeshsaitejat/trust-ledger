# InvoiceShield Backend

FastAPI-based REST API for invoice financing verification.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
uvicorn app.main:app --reload
```

**Server:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 3. Run Tests
```bash
pytest tests/ -v
```

### 4. Run Demo
```bash
python demo_script.py
```

## 📚 API Endpoints

### Document Management
- `POST /documents/upload` - Upload PDF documents
- `GET /documents/{id}` - Get document metadata

### Invoice Verification
- `POST /invoices/verify` - Verify invoice against PO and DR
- `GET /invoices/{id}/verification` - Get verification results
- `GET /invoices/{id}/risk` - Get risk assessment

### Audit & Integrity
- `GET /audit/trail/{id}` - Get audit trail
- `POST /audit/verify-chain` - Verify audit chain
- `GET /audit/document/{id}/integrity` - Verify document integrity
- `GET /audit/stats` - Get audit statistics

### System
- `GET /system/stats` - Get platform statistics
- `GET /health` - Health check

## 📁 Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Configuration
│   ├── db/           # Database models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── tests/            # Test suites (46 tests)
├── storage/          # Document storage
└── InvoiceShield_Synthetic_Test_PDFs/  # Test data
```

## ✅ Features

- 3-way document verification (Invoice-PO-DR)
- PDF text extraction & field parsing
- Duplicate detection (exact & business logic)
- Risk scoring (0-100 with explainable factors)
- Audit trail (hash-linked, tamper-evident)
- Document integrity verification

## 🧪 Testing

All 46 tests passing:
- Phase 1: Document management (9 tests)
- Phase 2: PDF extraction (6 tests)
- Phase 3: Risk engine (10 tests)
- Phase 4: Audit trail (12 tests)
- Phase 5: Integration (9 tests)

## 🔧 Tech Stack

- **Framework:** FastAPI 0.115.0
- **Database:** SQLite + SQLAlchemy
- **PDF Processing:** PyMuPDF
- **Validation:** Pydantic 2.9.0
- **Testing:** pytest 8.3.3

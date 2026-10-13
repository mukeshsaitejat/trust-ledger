# InvoiceShield - Invoice Financing Verification Platform

AI-powered invoice verification system for detecting fraud and assessing risk in invoice financing.

## 📁 Project Structure

```
InvoiceShield/
├── backend/              # FastAPI backend (Python)
│   ├── app/              # Application code
│   ├── tests/            # Test suites (46 tests)
│   └── README.md         # Backend documentation
│
├── frontend-react/       # React frontend (TypeScript + Vite)
│   ├── src/              # React components
│   └── README.md         # Frontend documentation
│
└── frontend-simple/      # Simple HTML/CSS/JS frontend
    └── index.html        # Single-page application
```

## 🚀 Quick Start

### Backend (Required)

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Server runs at: http://localhost:8000  
   API Docs: http://localhost:8000/docs

### Frontend (Choose One)

#### Option 1: React Frontend (Modern)

1. **Navigate to frontend:**
   ```bash
   cd frontend-react
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   Frontend runs at: http://localhost:5173

#### Option 2: Simple Frontend

1. **Navigate to frontend:**
   ```bash
   cd frontend-simple
   ```

2. **Run Python server:**
   ```bash
   python serve.py
   ```

   Frontend runs at: http://localhost:3000

## ✨ Features

### Backend Capabilities
- **3-Way Verification** - Cross-check invoice, PO, and delivery receipt
- **PDF Extraction** - Parse text from PDF documents
- **Duplicate Detection** - Exact file hash + business logic checks
- **Risk Scoring** - Explainable 0-100 risk scores
- **Audit Trail** - Hash-linked, tamper-evident logging
- **Document Integrity** - SHA-256 verification

### Frontend Features
- **Document Upload** - Easy file selection and upload
- **Real-time Verification** - Instant results
- **Visual Risk Meter** - Color-coded risk visualization
- **Detailed Findings** - All issues clearly displayed
- **Live Statistics** - Platform metrics dashboard

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

**All 46 tests passing:**
- Phase 1: Document Management (9 tests)
- Phase 2: PDF Extraction (6 tests)
- Phase 3: Risk Engine (10 tests)
- Phase 4: Audit Trail (12 tests)
- Phase 5: Integration (9 tests)

### Test with Sample PDFs
Located in `backend/InvoiceShield_Synthetic_Test_PDFs/`:
- **case1_clean** - Perfect match (should approve)
- **case2_amount_mismatch** - Amount discrepancy (should reject)
- **case3_quantity_mismatch** - Quantity issue (should review)
- **case4_supplier_mismatch** - Different suppliers (should reject)
- **case5_duplicate_invoice** - Duplicate test

## 📊 Risk Assessment

**Risk Scoring (0-100):**
- **MINIMAL** (0-25): Safe to approve
- **LOW** (26-50): Minor issues
- **MEDIUM** (51-75): Review recommended
- **HIGH** (76-100): Reject or investigate

**Risk Factors:**
| Factor | Weight | Description |
|--------|--------|-------------|
| Exact Duplicate | 50 | Same file uploaded before |
| Business Duplicate | 40 | Same invoice#, supplier, amount |
| Critical Finding | 30 | PO/supplier mismatch |
| High Finding | 20 | Amount/quantity mismatch |
| Medium Finding | 10 | Missing optional fields |

## 🔧 Tech Stack

### Backend
- FastAPI 0.115.0
- Python 3.9+
- SQLite + SQLAlchemy
- PyMuPDF (PDF processing)
- Pydantic 2.9.0

### Frontend (React)
- React 18
- TypeScript
- Vite
- Tailwind CSS

### Frontend (Simple)
- HTML5
- CSS3
- Vanilla JavaScript

## 📚 API Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints:
- `POST /documents/upload` - Upload documents
- `POST /invoices/verify` - Verify invoice
- `GET /invoices/{id}/risk` - Get risk score
- `GET /audit/trail/{id}` - View audit trail
- `GET /system/stats` - Platform statistics

## 🔒 Security Features

- SHA-256 document fingerprinting
- Hash-linked audit trail (blockchain-inspired)
- Duplicate detection (file & business logic)
- Document integrity verification
- Tamper-evident event logging

## 📝 Development Workflow

1. **Start backend:** `cd backend && uvicorn app.main:app --reload`
2. **Start frontend:** `cd frontend-react && npm run dev`
3. **Upload test PDFs** from backend/InvoiceShield_Synthetic_Test_PDFs/
4. **Verify and review results**

## 🎯 Production Readiness

✅ **Error Handling** - Comprehensive validation  
✅ **Type Safety** - Pydantic schemas  
✅ **Testing** - 46 tests passing  
✅ **Documentation** - API docs + guides  
✅ **CORS** - Configured for frontend  
✅ **Logging** - Audit trail for all operations  

## 🏆 Project Status

**All 5 Phases Complete:**
- ✅ Phase 1: Backend Foundation
- ✅ Phase 2: PDF Extraction & Verification
- ✅ Phase 3: Duplicate Detection & Risk Engine
- ✅ Phase 4: Audit Trail & Document Integrity
- ✅ Phase 5: Integration & Testing

**Status:** Production Ready 🚀

## 📞 Support

For issues:
1. Check backend logs
2. Verify backend is running on port 8000
3. Check browser console for errors
4. Ensure PDFs are valid format

## 📄 License

Built for Synesis 26 FinTech Hackathon

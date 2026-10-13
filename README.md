# InvoiceShield

AI-Assisted Invoice Financing Verification Platform for Synesis 26 FinTech Hackathon

## Overview

InvoiceShield helps financial institutions verify invoice financing requests by:
- Extracting data from invoice, PO, and delivery receipt PDFs
- Detecting discrepancies and duplicate submissions
- Calculating explainable risk scores
- Maintaining tamper-evident audit trails

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
copy .env.example .env
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Phase 1: Document Management

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /documents/upload` - Upload invoice, PO, or delivery receipt
- `GET /documents/{document_id}` - Retrieve document metadata

### Phase 2: Invoice Verification

- `POST /invoices/verify` - Verify invoice against PO and delivery receipt
- `GET /invoices/{invoice_id}/verification` - Get verification results

## Development Status

- [x] Phase 1: Backend Foundation and Document Intake
- [x] Phase 2: PDF Extraction and Document Verification
- [ ] Phase 3: Duplicate Detection and Risk Engine
- [ ] Phase 4: Audit Trail and Document Integrity
- [ ] Phase 5: Integration, Testing and Demo Readiness

## Technology Stack

- Python 3.9+
- FastAPI
- SQLite
- SQLAlchemy
- PyMuPDF
- Pydantic

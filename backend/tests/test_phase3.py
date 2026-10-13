"""
Phase 3 Tests: Duplicate Detection and Risk Engine
"""
import pytest
from fastapi.testclient import TestClient
import io

from app.main import app
from app.db.database import Base, engine
from app.services.risk_engine import RiskEngine
from app.services.duplicate_detector import DuplicateDetector

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- Reuse helpers from phase 2 tests ---

def make_pdf(content: str) -> bytes:
    """Create a minimal PDF with given text content."""
    content_stream = f"BT /F1 10 Tf 50 700 Td ({content}) Tj ET".encode("latin-1")
    length = len(content_stream)
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
        b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
        b"/MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(length).encode() + b" >>\nstream\n"
        + content_stream +
        b"\nendstream\nendobj\n"
        b"xref\n0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000300 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
    )


def upload(pdf_bytes: bytes, filename: str, doc_type: str) -> str:
    """Upload a PDF and return document_id."""
    resp = client.post(
        "/documents/upload",
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")},
        data={"document_type": doc_type}
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["document_id"]


def verify(invoice_id, po_id=None, delivery_id=None):
    """Run verification and return result."""
    payload = {"invoice_id": invoice_id}
    if po_id:
        payload["po_id"] = po_id
    if delivery_id:
        payload["delivery_receipt_id"] = delivery_id
    resp = client.post("/invoices/verify", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ===================== RISK ENGINE UNIT TESTS =====================

def test_risk_engine_clean_invoice():
    """Risk engine should return low score for no findings."""
    engine = RiskEngine()
    result = engine.calculate_risk_score(
        findings=[],
        duplicate_results={"has_duplicates": False, "exact_duplicate": None, "business_duplicate": None},
        invoice_fields={"extraction_successful": True, "invoice_number": "INV-001", "amount": 5000.0}
    )
    assert result["risk_score"] == 0
    assert result["risk_level"] == "MINIMAL"
    assert result["financing_recommendation"] == "APPROVED_FOR_CONSIDERATION"


def test_risk_engine_supplier_mismatch():
    """Supplier mismatch should raise risk score significantly."""
    engine = RiskEngine()
    findings = [{
        "finding_type": "supplier_mismatch",
        "severity": "critical",
        "field": "supplier_name",
        "message": "Supplier mismatch",
        "expected_value": "Supplier A",
        "actual_value": "Supplier B"
    }]
    result = engine.calculate_risk_score(
        findings=findings,
        duplicate_results={"has_duplicates": False, "exact_duplicate": None, "business_duplicate": None},
        invoice_fields={"extraction_successful": True, "invoice_number": "INV-001", "amount": 5000.0}
    )
    assert result["risk_score"] >= 35
    assert result["risk_level"] in ["MEDIUM", "HIGH"]
    assert result["financing_recommendation"] in ["MANUAL_REVIEW_REQUIRED", "REJECT"]


def test_risk_engine_exact_duplicate():
    """Exact duplicate should produce high risk score."""
    engine = RiskEngine()
    duplicate_results = {
        "has_duplicates": True,
        "exact_duplicate": {
            "duplicate_found": True,
            "duplicate_type": "exact_file_match",
            "original_document_id": "abc-123",
            "original_uploaded_at": "2026-10-01T00:00:00",
            "duplicate_count": 1,
            "message": "Exact file duplicate detected"
        },
        "business_duplicate": None
    }
    result = engine.calculate_risk_score(
        findings=[],
        duplicate_results=duplicate_results,
        invoice_fields={"extraction_successful": True, "invoice_number": "INV-001", "amount": 5000.0}
    )
    assert result["risk_score"] >= 50
    assert result["risk_level"] == "HIGH"
    assert result["financing_recommendation"] == "REJECT"


def test_risk_engine_score_capped_at_100():
    """Risk score should never exceed 100."""
    engine = RiskEngine()
    # Stack many findings
    findings = [
        {"finding_type": "supplier_mismatch", "severity": "critical", "field": "supplier_name",
         "message": "Supplier mismatch", "expected_value": "A", "actual_value": "B"},
        {"finding_type": "quantity_overcharge", "severity": "critical", "field": "quantity",
         "message": "Overcharge", "expected_value": 100, "actual_value": 200},
        {"finding_type": "amount_mismatch", "severity": "critical", "field": "amount",
         "message": "Amount mismatch", "expected_value": 5000, "actual_value": 9000},
        {"finding_type": "po_mismatch", "severity": "critical", "field": "po_reference",
         "message": "PO mismatch", "expected_value": "PO-1", "actual_value": "PO-2"},
    ]
    duplicate_results = {
        "has_duplicates": True,
        "exact_duplicate": {
            "duplicate_found": True, "duplicate_type": "exact_file_match",
            "original_document_id": "abc", "original_uploaded_at": "2026-01-01",
            "duplicate_count": 1, "message": "Duplicate"
        },
        "business_duplicate": None
    }
    result = engine.calculate_risk_score(
        findings=findings,
        duplicate_results=duplicate_results,
        invoice_fields={"extraction_successful": True, "invoice_number": "INV-001", "amount": 5000.0}
    )
    assert result["risk_score"] <= 100


# ===================== INTEGRATION TESTS =====================

def test_verify_includes_risk_assessment():
    """Verification response should include risk assessment."""
    inv_pdf = make_pdf("Invoice Number: INV-001 Supplier: ABC Corp Buyer: XYZ Ltd Total: $5000")
    inv_id = upload(inv_pdf, "invoice.pdf", "invoice")
    result = verify(inv_id)

    assert "risk_assessment" in result
    assert result["risk_assessment"] is not None
    assert "risk_score" in result["risk_assessment"]
    assert "risk_level" in result["risk_assessment"]
    assert "financing_recommendation" in result["risk_assessment"]


def test_verify_includes_duplicate_check():
    """Verification response should include duplicate check results."""
    inv_pdf = make_pdf("Invoice Number: INV-002 Supplier: ABC Corp Total: $5000")
    inv_id = upload(inv_pdf, "invoice.pdf", "invoice")
    result = verify(inv_id)

    assert "duplicate_check" in result
    assert result["duplicate_check"] is not None
    assert "has_duplicates" in result["duplicate_check"]


def test_exact_duplicate_detection():
    """Uploading the same PDF twice should trigger exact duplicate detection."""
    pdf_bytes = make_pdf("Invoice Number: INV-DUP-001 Supplier: ABC Corp Total: $5000")

    # First upload + verify
    inv_id1 = upload(pdf_bytes, "invoice.pdf", "invoice")
    verify(inv_id1)

    # Second upload (same bytes, same hash)
    inv_id2 = upload(pdf_bytes, "invoice_copy.pdf", "invoice")
    result2 = verify(inv_id2)

    dup_check = result2["duplicate_check"]
    assert dup_check["has_duplicates"] is True
    assert dup_check["exact_duplicate"] is not None
    assert dup_check["exact_duplicate"]["duplicate_type"] == "exact_file_match"


def test_risk_endpoint():
    """GET /invoices/{invoice_id}/risk should return full risk breakdown."""
    inv_pdf = make_pdf("Invoice Number: INV-003 Supplier: ABC Corp Buyer: XYZ Ltd Total: $5000")
    inv_id = upload(inv_pdf, "invoice.pdf", "invoice")
    verify(inv_id)

    resp = client.get(f"/invoices/{inv_id}/risk")
    assert resp.status_code == 200
    data = resp.json()

    assert "risk_score" in data
    assert "risk_level" in data
    assert "financing_recommendation" in data
    assert "recommendation_reason" in data
    assert "recommendation_action" in data
    assert "risk_factors" in data
    assert "duplicate_check" in data


def test_risk_endpoint_not_found():
    """Risk endpoint for unknown invoice should return 404."""
    resp = client.get("/invoices/00000000-0000-0000-0000-000000000000/risk")
    assert resp.status_code == 404


def test_risk_factors_are_explainable():
    """Each risk factor must have description and details."""
    # Create an invoice with a PO mismatch to generate a risk factor
    inv_pdf = make_pdf(
        "Invoice Number: INV-004 Supplier: Fake Supplier Buyer: XYZ Ltd "
        "PO Reference: PO-999 Total: $9000"
    )
    po_pdf = make_pdf(
        "Purchase Order Number: PO-001 Vendor: Real Supplier "
        "Buyer: XYZ Ltd Total: $5000"
    )
    inv_id = upload(inv_pdf, "invoice.pdf", "invoice")
    po_id = upload(po_pdf, "po.pdf", "purchase_order")
    verify(inv_id, po_id=po_id)

    resp = client.get(f"/invoices/{inv_id}/risk")
    data = resp.json()

    assert data["risk_factor_count"] > 0
    for factor in data["risk_factors"]:
        assert "factor" in factor
        assert "score" in factor
        assert "description" in factor
        assert "details" in factor
        assert factor["score"] > 0

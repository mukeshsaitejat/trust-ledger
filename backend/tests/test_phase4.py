"""
Phase 4 Tests: Audit Trail and Document Integrity
"""
import pytest
from fastapi.testclient import TestClient
import io
import json

from app.main import app
from app.db.database import Base, engine
from app.db.models import AuditEvent
from app.services.audit_service import AuditService

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_pdf(content: str) -> bytes:
    """Create a minimal PDF."""
    content_stream = f"BT /F1 10 Tf 50 700 Td ({content}) Tj ET".encode("latin-1")
    length = len(content_stream)
    return (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
        b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
        b"/MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(length).encode() + b" >>\nstream\n"
        + content_stream + b"\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n0000000300 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
    )


# ============ AUDIT SERVICE UNIT TESTS ============

def test_audit_hash_calculation():
    """Audit service should calculate deterministic hashes."""
    service = AuditService()
    
    hash1 = service.calculate_event_hash(
        "test_event",
        "entity-123",
        "document",
        {"key": "value"},
        "2026-01-01T00:00:00",
        None
    )
    
    hash2 = service.calculate_event_hash(
        "test_event",
        "entity-123",
        "document",
        {"key": "value"},
        "2026-01-01T00:00:00",
        None
    )
    
    # Same inputs = same hash
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex


def test_audit_hash_changes_with_data():
    """Changing any data should change the hash."""
    service = AuditService()
    
    hash1 = service.calculate_event_hash(
        "test_event", "entity-123", "document",
        {"key": "value"}, "2026-01-01T00:00:00", None
    )
    
    hash2 = service.calculate_event_hash(
        "test_event", "entity-123", "document",
        {"key": "different"},  # Changed data
        "2026-01-01T00:00:00", None
    )
    
    assert hash1 != hash2


# ============ INTEGRATION TESTS ============

def test_document_upload_creates_audit_event():
    """Uploading a document should create an audit event."""
    pdf = make_pdf("Test Invoice")
    resp = client.post(
        "/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"document_type": "invoice"}
    )
    assert resp.status_code == 201
    doc_id = resp.json()["document_id"]
    
    # Check audit trail
    audit_resp = client.get(f"/audit/trail/{doc_id}")
    assert audit_resp.status_code == 200
    
    data = audit_resp.json()
    assert data["entity_id"] == doc_id
    assert data["event_count"] >= 1
    assert any(e["event_type"] == "document_uploaded" for e in data["events"])


def test_verification_creates_audit_event():
    """Verification should create an audit event."""
    pdf = make_pdf("Invoice Number: INV-001 Supplier: ABC Total: $5000")
    inv_id = client.post(
        "/documents/upload",
        files={"file": ("inv.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"document_type": "invoice"}
    ).json()["document_id"]
    
    verify_resp = client.post("/invoices/verify", json={"invoice_id": inv_id})
    assert verify_resp.status_code == 201
    verification_id = verify_resp.json()["verification_id"]
    
    # Check audit trail for verification
    audit_resp = client.get(f"/audit/trail/{verification_id}")
    assert audit_resp.status_code == 200
    
    data = audit_resp.json()
    assert any(e["event_type"] == "verification_completed" for e in data["events"])


def test_audit_trail_is_hash_linked():
    """Audit events should form a hash-linked chain."""
    # Upload multiple documents to create chain
    for i in range(3):
        pdf = make_pdf(f"Document {i}")
        client.post(
            "/documents/upload",
            files={"file": (f"doc{i}.pdf", io.BytesIO(pdf), "application/pdf")},
            data={"document_type": "invoice"}
        )
    
    # Verify chain
    chain_resp = client.post("/audit/verify-chain")
    assert chain_resp.status_code == 200
    
    result = chain_resp.json()["verification_result"]
    assert result["valid"] is True
    assert result["event_count"] >= 3
    assert len(result["discrepancies"]) == 0


def test_audit_trail_endpoint():
    """GET /audit/trail/{entity_id} should return audit events."""
    pdf = make_pdf("Test")
    doc_id = client.post(
        "/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"document_type": "invoice"}
    ).json()["document_id"]
    
    resp = client.get(f"/audit/trail/{doc_id}")
    assert resp.status_code == 200
    
    data = resp.json()
    assert "entity_id" in data
    assert "events" in data
    assert "chain_info" in data
    assert data["chain_info"]["is_chained"] is True


def test_audit_trail_not_found():
    """Audit trail for unknown entity should return 404."""
    resp = client.get("/audit/trail/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_verify_chain_endpoint():
    """POST /audit/verify-chain should verify audit integrity."""
    # Create some audit events
    pdf = make_pdf("Test")
    client.post(
        "/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"document_type": "invoice"}
    )
    
    resp = client.post("/audit/verify-chain")
    assert resp.status_code == 200
    
    result = resp.json()["verification_result"]
    assert "valid" in result
    assert "event_count" in result
    assert "discrepancies" in result


def test_document_integrity_verification():
    """POST /audit/verify-document/{id} should verify file integrity."""
    pdf = make_pdf("Test Document")
    doc_id = client.post(
        "/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"document_type": "invoice"}
    ).json()["document_id"]
    
    resp = client.post(f"/audit/verify-document/{doc_id}")
    assert resp.status_code == 200
    
    data = resp.json()
    assert data["document_id"] == doc_id
    assert data["document_found"] is True
    assert data["integrity_verified"] is True


def test_document_integrity_not_found():
    """Document integrity check for unknown document should return 404."""
    resp = client.post("/audit/verify-document/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_audit_stats_endpoint():
    """GET /audit/stats should return statistics."""
    # Create some events
    for i in range(2):
        pdf = make_pdf(f"Doc {i}")
        client.post(
            "/documents/upload",
            files={"file": (f"doc{i}.pdf", io.BytesIO(pdf), "application/pdf")},
            data={"document_type": "invoice"}
        )
    
    resp = client.get("/audit/stats")
    assert resp.status_code == 200
    
    data = resp.json()
    assert "total_events" in data
    assert "events_by_type" in data
    assert "chain_length" in data
    assert data["total_events"] >= 2


def test_audit_event_contains_required_fields():
    """Each audit event should contain required fields."""
    pdf = make_pdf("Test")
    doc_id = client.post(
        "/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"document_type": "invoice"}
    ).json()["document_id"]
    
    resp = client.get(f"/audit/trail/{doc_id}")
    events = resp.json()["events"]
    
    for event in events:
        assert "id" in event
        assert "event_type" in event
        assert "entity_type" in event
        assert "event_data" in event
        assert "actor" in event
        assert "timestamp" in event
        assert "event_hash" in event
        # First event has no previous
        if event["id"] > 1:
            assert "previous_hash" in event

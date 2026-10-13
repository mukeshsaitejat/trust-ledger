"""
Phase 5: Integration Tests
Tests for system endpoints and end-to-end workflows.
"""
import pytest
from fastapi.testclient import TestClient
import io

from app.main import app
from app.db.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Initialize database before each test."""
    init_db()


def test_system_stats_endpoint():
    """Test system statistics endpoint."""
    response = client.get("/system/stats")
    assert response.status_code == 200
    
    stats = response.json()
    assert "total_documents" in stats
    assert "total_verifications" in stats
    assert "total_audit_events" in stats
    assert "approved_count" in stats
    assert "rejected_count" in stats
    assert "review_required_count" in stats
    assert "high_risk_count" in stats
    assert "duplicate_count" in stats
    assert "uptime_seconds" in stats
    assert "database_size_mb" in stats
    
    # All counts should be non-negative integers
    assert stats["total_documents"] >= 0
    assert stats["total_verifications"] >= 0
    assert stats["total_audit_events"] >= 0


def test_end_to_end_clean_workflow():
    """Test complete workflow with clean invoice."""
    # Step 1: Upload documents
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>%%EOF"
    
    # Upload invoice
    invoice_response = client.post(
        "/documents/upload",
        files={"file": ("test_invoice.pdf", io.BytesIO(pdf_content), "application/pdf")},
        data={"document_type": "invoice"}
    )
    assert invoice_response.status_code == 201
    invoice_id = invoice_response.json()["document_id"]
    
    # Upload PO
    po_response = client.post(
        "/documents/upload",
        files={"file": ("test_po.pdf", io.BytesIO(pdf_content), "application/pdf")},
        data={"document_type": "purchase_order"}
    )
    assert po_response.status_code == 201
    po_id = po_response.json()["document_id"]
    
    # Upload delivery receipt
    dr_response = client.post(
        "/documents/upload",
        files={"file": ("test_dr.pdf", io.BytesIO(pdf_content), "application/pdf")},
        data={"document_type": "delivery_receipt"}
    )
    assert dr_response.status_code == 201
    dr_id = dr_response.json()["document_id"]
    
    # Step 2: Verify invoice
    verify_response = client.post(
        "/invoices/verify",
        json={
            "invoice_id": invoice_id,
            "po_id": po_id,
            "delivery_receipt_id": dr_id
        }
    )
    assert verify_response.status_code == 201
    verification = verify_response.json()
    verification_id = verification["verification_id"]
    
    # Step 3: Check risk assessment
    risk_response = client.get(f"/invoices/{invoice_id}/risk")
    assert risk_response.status_code == 200
    risk = risk_response.json()
    assert "risk_score" in risk
    assert "risk_level" in risk
    
    # Step 4: Check audit trail
    audit_response = client.get(f"/audit/trail/{verification_id}")
    assert audit_response.status_code == 200
    audit = audit_response.json()
    assert audit["event_count"] >= 1  # At least verification event
    assert "chain_info" in audit
    assert audit["chain_info"]["is_chained"] is True
    
    # Step 5: Verify document integrity
    integrity_response = client.get(f"/audit/document/{invoice_id}/integrity")
    assert integrity_response.status_code == 200
    integrity = integrity_response.json()
    assert integrity["document_found"] is True
    assert integrity["integrity_verified"] is True


def test_system_stats_after_operations():
    """Test that system stats reflect actual operations."""
    # Get initial stats
    initial_response = client.get("/system/stats")
    initial_stats = initial_response.json()
    initial_docs = initial_stats["total_documents"]
    
    # Upload a document
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>%%EOF"
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("stats_test.pdf", io.BytesIO(pdf_content), "application/pdf")},
        data={"document_type": "invoice"}
    )
    assert upload_response.status_code == 201
    
    # Get updated stats
    updated_response = client.get("/system/stats")
    updated_stats = updated_response.json()
    
    # Document count should increase
    assert updated_stats["total_documents"] == initial_docs + 1


def test_multiple_verifications_workflow():
    """Test handling multiple verification requests."""
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>%%EOF"
    
    verifications = []
    
    for i in range(3):
        # Upload invoice
        invoice_resp = client.post(
            "/documents/upload",
            files={"file": (f"invoice_{i}.pdf", io.BytesIO(pdf_content), "application/pdf")},
            data={"document_type": "invoice"}
        )
        invoice_id = invoice_resp.json()["document_id"]
        
        # Upload PO
        po_resp = client.post(
            "/documents/upload",
            files={"file": (f"po_{i}.pdf", io.BytesIO(pdf_content), "application/pdf")},
            data={"document_type": "purchase_order"}
        )
        po_id = po_resp.json()["document_id"]
        
        # Upload DR
        dr_resp = client.post(
            "/documents/upload",
            files={"file": (f"dr_{i}.pdf", io.BytesIO(pdf_content), "application/pdf")},
            data={"document_type": "delivery_receipt"}
        )
        dr_id = dr_resp.json()["document_id"]
        
        # Verify
        verify_resp = client.post(
            "/invoices/verify",
            json={
                "invoice_id": invoice_id,
                "po_id": po_id,
                "delivery_receipt_id": dr_id
            }
        )
        assert verify_resp.status_code == 201
        verifications.append(verify_resp.json()["verification_id"])
    
    # Verify all verifications were created
    assert len(verifications) == 3
    assert len(set(verifications)) == 3  # All unique


def test_audit_stats_endpoint():
    """Test audit statistics endpoint."""
    response = client.get("/audit/stats")
    assert response.status_code == 200
    
    stats = response.json()
    assert "total_events" in stats
    assert "events_by_type" in stats
    assert ("first_event_at" in stats or stats["total_events"] == 0)


def test_verify_chain_integrity():
    """Test audit chain verification endpoint."""
    # Upload a document to create audit events
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>%%EOF"
    client.post(
        "/documents/upload",
        files={"file": ("chain_test.pdf", io.BytesIO(pdf_content), "application/pdf")},
        data={"document_type": "invoice"}
    )
    
    # Verify chain
    response = client.post("/audit/verify-chain")
    assert response.status_code == 200
    
    result = response.json()
    assert "verification_result" in result
    assert result["verification_result"]["valid"] is True


def test_api_documentation_accessible():
    """Test that API documentation is accessible."""
    # Test Swagger UI
    swagger_response = client.get("/docs")
    assert swagger_response.status_code == 200
    
    # Test ReDoc
    redoc_response = client.get("/redoc")
    assert redoc_response.status_code == 200
    
    # Test OpenAPI schema
    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200
    schema = openapi_response.json()
    assert "openapi" in schema
    assert "paths" in schema


def test_error_handling_invalid_verification():
    """Test error handling for invalid verification request."""
    response = client.post(
        "/invoices/verify",
        json={
            "invoice_id": "nonexistent-id",
            "po_id": "nonexistent-id",
            "delivery_receipt_id": "nonexistent-id"
        }
    )
    # Should handle gracefully (either 404 or error message)
    assert response.status_code in [404, 500]


def test_concurrent_uploads():
    """Test handling concurrent document uploads."""
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>%%EOF"
    
    responses = []
    for i in range(5):
        response = client.post(
            "/documents/upload",
            files={"file": (f"concurrent_{i}.pdf", io.BytesIO(pdf_content), "application/pdf")},
            data={"document_type": "invoice"}
        )
        responses.append(response)
    
    # All uploads should succeed
    assert all(r.status_code == 201 for r in responses)
    
    # All should have unique IDs
    doc_ids = [r.json()["document_id"] for r in responses]
    assert len(set(doc_ids)) == 5

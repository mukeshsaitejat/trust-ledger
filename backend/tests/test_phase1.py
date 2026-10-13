"""
Phase 1 Tests: Backend Foundation and Document Intake
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from app.main import app
from app.db.database import Base, engine

# Test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def create_test_pdf() -> bytes:
    """Create a minimal valid PDF for testing."""
    # Minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Test Invoice) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
409
%%EOF
"""
    return pdf_content


def test_root_endpoint():
    """Test the root welcome endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Welcome to InvoiceShield API"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "InvoiceShield"
    assert "timestamp" in data


def test_upload_document_success():
    """Test successful document upload."""
    pdf_content = create_test_pdf()
    
    files = {
        "file": ("test_invoice.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data = {
        "document_type": "invoice"
    }
    
    response = client.post("/documents/upload", files=files, data=data)
    assert response.status_code == 201
    
    result = response.json()
    assert "document_id" in result
    assert result["filename"] == "test_invoice.pdf"
    assert result["document_type"] == "invoice"
    assert result["file_size"] == len(pdf_content)
    assert "sha256_hash" in result
    assert len(result["sha256_hash"]) == 64  # SHA-256 hex length


def test_upload_invalid_document_type():
    """Test upload with invalid document type."""
    pdf_content = create_test_pdf()
    
    files = {
        "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data = {
        "document_type": "invalid_type"
    }
    
    response = client.post("/documents/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid document_type" in response.json()["detail"]


def test_upload_non_pdf_file():
    """Test upload with non-PDF file."""
    text_content = b"This is not a PDF"
    
    files = {
        "file": ("test.txt", io.BytesIO(text_content), "text/plain")
    }
    data = {
        "document_type": "invoice"
    }
    
    response = client.post("/documents/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


def test_upload_empty_file():
    """Test upload with empty file."""
    files = {
        "file": ("empty.pdf", io.BytesIO(b""), "application/pdf")
    }
    data = {
        "document_type": "invoice"
    }
    
    response = client.post("/documents/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Empty file" in response.json()["detail"]


def test_get_document_metadata():
    """Test retrieving document metadata."""
    # First upload a document
    pdf_content = create_test_pdf()
    files = {
        "file": ("test_invoice.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data = {"document_type": "invoice"}
    
    upload_response = client.post("/documents/upload", files=files, data=data)
    assert upload_response.status_code == 201
    document_id = upload_response.json()["document_id"]
    
    # Retrieve the document
    response = client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    
    result = response.json()
    assert result["id"] == document_id
    assert result["filename"] == "test_invoice.pdf"
    assert result["document_type"] == "invoice"


def test_get_nonexistent_document():
    """Test retrieving non-existent document."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/documents/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_duplicate_hash_detection():
    """Test that identical files produce the same hash."""
    pdf_content = create_test_pdf()
    
    # Upload first document
    files1 = {
        "file": ("invoice1.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data1 = {"document_type": "invoice"}
    response1 = client.post("/documents/upload", files=files1, data=data1)
    hash1 = response1.json()["sha256_hash"]
    
    # Upload identical document with different name
    files2 = {
        "file": ("invoice2.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data2 = {"document_type": "invoice"}
    response2 = client.post("/documents/upload", files=files2, data=data2)
    hash2 = response2.json()["sha256_hash"]
    
    # Hashes should match
    assert hash1 == hash2
    
    # But document IDs should differ
    assert response1.json()["document_id"] != response2.json()["document_id"]

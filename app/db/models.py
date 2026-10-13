"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Text, Float, Float
from datetime import datetime
import json

from app.db.database import Base


class Document(Base):
    """
    Stores metadata for uploaded documents.
    The actual PDF files are stored in the filesystem.
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    filename = Column(String, nullable=False)  # Original filename
    document_type = Column(String, nullable=False)  # invoice, purchase_order, delivery_receipt
    file_path = Column(String, nullable=False)  # Storage path
    file_size = Column(BigInteger, nullable=False)  # Bytes
    sha256_hash = Column(String(64), nullable=False, index=True)  # Document fingerprint
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Document {self.id} type={self.document_type}>"


class Verification(Base):
    """
    Stores invoice verification results.
    """
    __tablename__ = "verifications"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    invoice_id = Column(String, nullable=False, index=True)
    po_id = Column(String, nullable=True)
    delivery_receipt_id = Column(String, nullable=True)
    
    # Extracted fields (stored as JSON)
    invoice_fields = Column(Text, nullable=False)
    po_fields = Column(Text, nullable=True)
    delivery_fields = Column(Text, nullable=True)
    
    # Comparison results
    verification_status = Column(String, nullable=False)  # approved, review_required, rejected
    findings = Column(Text, nullable=False)  # JSON array of findings
    findings_count = Column(Integer, nullable=False, default=0)
    critical_count = Column(Integer, nullable=False, default=0)
    
    # Risk assessment (Phase 3)
    risk_score = Column(Float, nullable=True)  # 0-100
    risk_level = Column(String, nullable=True)  # MINIMAL, LOW, MEDIUM, HIGH
    financing_recommendation = Column(String, nullable=True)  # APPROVED, MANUAL_REVIEW, REJECT
    has_duplicates = Column(Integer, nullable=False, default=0)  # Boolean as integer
    duplicate_info = Column(Text, nullable=True)  # JSON duplicate details
    
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Verification {self.id} status={self.verification_status}>"
    
    def get_invoice_fields(self):
        """Parse invoice fields JSON."""
        return json.loads(self.invoice_fields) if self.invoice_fields else {}
    
    def get_findings(self):
        """Parse findings JSON."""
        return json.loads(self.findings) if self.findings else []

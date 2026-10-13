"""
Pydantic schemas for verification requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class VerificationRequest(BaseModel):
    """Request to verify an invoice with supporting documents."""
    invoice_id: str = Field(..., description="Document ID of uploaded invoice")
    po_id: Optional[str] = Field(None, description="Document ID of purchase order")
    delivery_receipt_id: Optional[str] = Field(None, description="Document ID of delivery receipt")


class ExtractedFields(BaseModel):
    """Extracted fields from a document."""
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    supplier_name: Optional[str] = None
    buyer_name: Optional[str] = None
    po_reference: Optional[str] = None
    amount: Optional[float] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    extraction_successful: bool
    extraction_errors: List[str] = []


class Finding(BaseModel):
    """Verification finding."""
    finding_type: str = Field(..., description="Type of finding")
    severity: str = Field(..., description="Severity: critical, high, medium, low, info")
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Human-readable explanation")
    expected_value: Optional[Any] = Field(None, description="Expected value")
    actual_value: Optional[Any] = Field(None, description="Actual value")


class ComparisonResult(BaseModel):
    """Document comparison results."""
    status: str = Field(..., description="Status: approved, review_required, rejected")
    findings: List[Finding]
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int


class VerificationResponse(BaseModel):
    """Response from invoice verification."""
    verification_id: str = Field(..., description="Unique verification ID")
    invoice_id: str
    po_id: Optional[str] = None
    delivery_receipt_id: Optional[str] = None
    invoice_fields: ExtractedFields
    po_fields: Optional[ExtractedFields] = None
    delivery_fields: Optional[ExtractedFields] = None
    comparison_result: ComparisonResult
    verified_at: datetime
    
    class Config:
        from_attributes = True

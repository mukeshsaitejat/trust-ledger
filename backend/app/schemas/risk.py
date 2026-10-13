"""
Pydantic schemas for risk assessment.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RiskFactor(BaseModel):
    """Individual risk factor."""
    factor: str = Field(..., description="Risk factor type")
    score: float = Field(..., description="Risk score contribution")
    description: str = Field(..., description="Human-readable description")
    details: str = Field(..., description="Additional details")


class DuplicateInfo(BaseModel):
    """Duplicate detection information."""
    duplicate_found: bool
    duplicate_type: str
    confidence: Optional[str] = None
    original_document_id: Optional[str] = None
    original_verification_id: Optional[str] = None
    original_uploaded_at: Optional[str] = None
    original_verified_at: Optional[str] = None
    duplicate_count: int
    message: str
    matching_fields: Optional[Dict[str, Any]] = None


class DuplicateResults(BaseModel):
    """Complete duplicate detection results."""
    exact_duplicate: Optional[DuplicateInfo] = None
    business_duplicate: Optional[DuplicateInfo] = None
    has_duplicates: bool


class RiskAssessment(BaseModel):
    """Complete risk assessment."""
    risk_score: float = Field(..., description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: MINIMAL, LOW, MEDIUM, HIGH")
    risk_factors: List[RiskFactor] = Field(..., description="Individual risk factors")
    risk_factor_count: int = Field(..., description="Number of risk factors")
    financing_recommendation: str = Field(..., description="Financing recommendation")
    recommendation_reason: str = Field(..., description="Reason for recommendation")
    recommendation_action: str = Field(..., description="Recommended action")


class InvoiceRiskResponse(BaseModel):
    """Response for invoice risk assessment endpoint."""
    invoice_id: str
    verification_id: Optional[str] = None
    duplicate_check: DuplicateResults
    risk_assessment: RiskAssessment
    assessed_at: str
    
    class Config:
        from_attributes = True

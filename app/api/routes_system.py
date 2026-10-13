"""
System-level endpoints for Phase 5.
Provides platform statistics and batch operations.
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import Document, Verification, AuditEvent
from pydantic import BaseModel

router = APIRouter(prefix="/system", tags=["system"])


class SystemStats(BaseModel):
    """System statistics response."""
    total_documents: int
    total_verifications: int
    total_audit_events: int
    approved_count: int
    rejected_count: int
    review_required_count: int
    high_risk_count: int
    duplicate_count: int
    uptime_seconds: float
    database_size_mb: float


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get platform usage statistics."""
    db: Session = next(get_db())
    
    try:
        # Count documents
        total_documents = db.query(Document).count()
        
        # Count verifications by status
        total_verifications = db.query(Verification).count()
        approved_count = db.query(Verification).filter(
            Verification.verification_status == "approved"
        ).count()
        rejected_count = db.query(Verification).filter(
            Verification.verification_status == "rejected"
        ).count()
        review_required_count = db.query(Verification).filter(
            Verification.verification_status == "review_required"
        ).count()
        
        # Count high risk verifications
        high_risk_count = db.query(Verification).filter(
            Verification.risk_level == "HIGH"
        ).count()
        
        # Count duplicates
        duplicate_count = db.query(Verification).filter(
            Verification.has_duplicates == 1
        ).count()
        
        # Count audit events
        total_audit_events = db.query(AuditEvent).count()
        
        # Simple uptime calculation (since last db init)
        import os
        db_path = "invoiceshield.db"
        if os.path.exists(db_path):
            uptime_seconds = (datetime.utcnow() - datetime.fromtimestamp(
                os.path.getctime(db_path)
            )).total_seconds()
            database_size_mb = os.path.getsize(db_path) / (1024 * 1024)
        else:
            uptime_seconds = 0
            database_size_mb = 0
        
        return SystemStats(
            total_documents=total_documents,
            total_verifications=total_verifications,
            total_audit_events=total_audit_events,
            approved_count=approved_count,
            rejected_count=rejected_count,
            review_required_count=review_required_count,
            high_risk_count=high_risk_count,
            duplicate_count=duplicate_count,
            uptime_seconds=uptime_seconds,
            database_size_mb=round(database_size_mb, 2)
        )
    finally:
        db.close()

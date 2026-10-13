"""
Invoice verification API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import json
from pathlib import Path

from app.db.database import get_db
from app.db.models import Document, Verification
from app.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
    ExtractedFields,
    ComparisonResult
)
from app.schemas.risk import DuplicateResults, RiskAssessment
from app.services.pdf_extractor import pdf_extractor
from app.services.document_comparator import document_comparator
from app.services.duplicate_detector import duplicate_detector
from app.services.risk_engine import risk_engine
from app.services.audit_service import audit_service

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/verify", response_model=VerificationResponse, status_code=201)
async def verify_invoice(
    request: VerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify an invoice against purchase order and delivery receipt.
    
    Extracts data from PDFs, compares documents, and returns
    structured verification findings.
    
    Args:
        request: Verification request with document IDs
        
    Returns:
        Verification results with findings and risk assessment
    """
    # Retrieve invoice document
    invoice_doc = db.query(Document).filter(
        Document.id == request.invoice_id
    ).first()
    
    if not invoice_doc:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice document {request.invoice_id} not found"
        )
    
    if invoice_doc.document_type != "invoice":
        raise HTTPException(
            status_code=400,
            detail=f"Document {request.invoice_id} is not an invoice"
        )
    
    # Extract invoice fields
    try:
        invoice_text = pdf_extractor.extract_text(invoice_doc.file_path)
        invoice_fields = pdf_extractor.extract_invoice_fields(invoice_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract invoice data: {str(e)}"
        )
    
    # Extract PO fields if provided
    po_fields = None
    if request.po_id:
        po_doc = db.query(Document).filter(
            Document.id == request.po_id
        ).first()
        
        if not po_doc:
            raise HTTPException(
                status_code=404,
                detail=f"PO document {request.po_id} not found"
            )
        
        if po_doc.document_type != "purchase_order":
            raise HTTPException(
                status_code=400,
                detail=f"Document {request.po_id} is not a purchase order"
            )
        
        try:
            po_text = pdf_extractor.extract_text(po_doc.file_path)
            po_fields = pdf_extractor.extract_po_fields(po_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract PO data: {str(e)}"
            )
    
    # Extract delivery receipt fields if provided
    delivery_fields = None
    if request.delivery_receipt_id:
        delivery_doc = db.query(Document).filter(
            Document.id == request.delivery_receipt_id
        ).first()
        
        if not delivery_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Delivery receipt {request.delivery_receipt_id} not found"
            )
        
        if delivery_doc.document_type != "delivery_receipt":
            raise HTTPException(
                status_code=400,
                detail=f"Document {request.delivery_receipt_id} is not a delivery receipt"
            )
        
        try:
            delivery_text = pdf_extractor.extract_text(delivery_doc.file_path)
            delivery_fields = pdf_extractor.extract_delivery_receipt_fields(delivery_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract delivery receipt data: {str(e)}"
            )
    
    # Compare documents
    comparison_result = document_comparator.compare_documents(
        invoice_fields,
        po_fields,
        delivery_fields
    )
    
    # Check for duplicates
    duplicate_results = duplicate_detector.check_duplicates(
        invoice_doc.sha256_hash,
        invoice_fields.get("invoice_number"),
        invoice_fields.get("supplier_name"),
        invoice_fields.get("amount"),
        db
    )
    
    # Calculate risk score
    risk_assessment = risk_engine.calculate_risk_score(
        comparison_result["findings"],
        duplicate_results,
        invoice_fields,
        po_fields,
        delivery_fields
    )
    
    # Create verification record
    verification_id = str(uuid.uuid4())
    
    verification = Verification(
        id=verification_id,
        invoice_id=request.invoice_id,
        po_id=request.po_id,
        delivery_receipt_id=request.delivery_receipt_id,
        invoice_fields=json.dumps(invoice_fields),
        po_fields=json.dumps(po_fields) if po_fields else None,
        delivery_fields=json.dumps(delivery_fields) if delivery_fields else None,
        verification_status=comparison_result["status"],
        findings=json.dumps(comparison_result["findings"]),
        findings_count=comparison_result["findings_count"],
        critical_count=comparison_result["critical_count"],
        risk_score=risk_assessment["risk_score"],
        risk_level=risk_assessment["risk_level"],
        financing_recommendation=risk_assessment["financing_recommendation"],
        has_duplicates=duplicate_results["has_duplicates"],
        duplicate_info=json.dumps(duplicate_results)
    )
    
    try:
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        # Record audit event
        audit_service.record_event(
            event_type="verification_completed",
            entity_id=verification.id,
            entity_type="verification",
            event_data={
                "invoice_id": verification.invoice_id,
                "po_id": verification.po_id,
                "delivery_receipt_id": verification.delivery_receipt_id,
                "verification_status": verification.verification_status,
                "risk_score": verification.risk_score,
                "risk_level": verification.risk_level,
                "financing_recommendation": verification.financing_recommendation,
                "has_duplicates": bool(verification.has_duplicates),
                "findings_count": verification.findings_count,
                "critical_count": verification.critical_count
            },
            actor="system",
            db=db
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save verification: {str(e)}"
        )
    
    # Build response
    return VerificationResponse(
        verification_id=verification.id,
        invoice_id=verification.invoice_id,
        po_id=verification.po_id,
        delivery_receipt_id=verification.delivery_receipt_id,
        invoice_fields=ExtractedFields(**invoice_fields),
        po_fields=ExtractedFields(**po_fields) if po_fields else None,
        delivery_fields=ExtractedFields(**delivery_fields) if delivery_fields else None,
        comparison_result=ComparisonResult(**comparison_result),
        duplicate_check=duplicate_results,
        risk_assessment=risk_assessment,
        verified_at=verification.verified_at
    )


@router.get("/{invoice_id}/verification", response_model=VerificationResponse)
async def get_verification(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the most recent verification result for an invoice.
    
    Args:
        invoice_id: Invoice document ID
        
    Returns:
        Verification results
    """
    # Get most recent verification for this invoice
    verification = db.query(Verification).filter(
        Verification.invoice_id == invoice_id
    ).order_by(Verification.verified_at.desc()).first()
    
    if not verification:
        raise HTTPException(
            status_code=404,
            detail=f"No verification found for invoice {invoice_id}"
        )
    
    # Parse stored JSON data
    invoice_fields = json.loads(verification.invoice_fields)
    po_fields = json.loads(verification.po_fields) if verification.po_fields else None
    delivery_fields = json.loads(verification.delivery_fields) if verification.delivery_fields else None
    findings = json.loads(verification.findings)
    
    comparison_result = {
        "status": verification.verification_status,
        "findings": findings,
        "findings_count": verification.findings_count,
        "critical_count": verification.critical_count,
        "high_count": sum(1 for f in findings if f.get("severity") == "high"),
        "medium_count": sum(1 for f in findings if f.get("severity") == "medium")
    }
    
    # Parse risk and duplicate info if available
    risk_data = None
    if verification.risk_score is not None:
        risk_data = {
            "risk_score": verification.risk_score,
            "risk_level": verification.risk_level,
            "financing_recommendation": verification.financing_recommendation
        }
    
    duplicate_data = None
    if verification.duplicate_info:
        duplicate_data = json.loads(verification.duplicate_info)
    
    return VerificationResponse(
        verification_id=verification.id,
        invoice_id=verification.invoice_id,
        po_id=verification.po_id,
        delivery_receipt_id=verification.delivery_receipt_id,
        invoice_fields=ExtractedFields(**invoice_fields),
        po_fields=ExtractedFields(**po_fields) if po_fields else None,
        delivery_fields=ExtractedFields(**delivery_fields) if delivery_fields else None,
        comparison_result=ComparisonResult(**comparison_result),
        duplicate_check=duplicate_data,
        risk_assessment=risk_data,
        verified_at=verification.verified_at
    )


@router.get("/{invoice_id}/risk")
async def get_invoice_risk(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the full risk assessment for an invoice.
    Returns risk score, level, all risk factors, and financing recommendation.
    """
    verification = db.query(Verification).filter(
        Verification.invoice_id == invoice_id
    ).order_by(Verification.verified_at.desc()).first()

    if not verification:
        raise HTTPException(
            status_code=404,
            detail=f"No verification found for invoice {invoice_id}"
        )

    invoice_fields = verification.get_invoice_fields()
    findings = verification.get_findings()
    duplicate_info = json.loads(verification.duplicate_info) if verification.duplicate_info else {
        "has_duplicates": False, "exact_duplicate": None, "business_duplicate": None
    }

    # Recalculate full risk assessment for complete factor list
    po_fields = json.loads(verification.po_fields) if verification.po_fields else None
    delivery_fields = json.loads(verification.delivery_fields) if verification.delivery_fields else None

    full_risk = risk_engine.calculate_risk_score(
        findings,
        duplicate_info,
        invoice_fields,
        po_fields,
        delivery_fields
    )

    from datetime import datetime
    return {
        "invoice_id": invoice_id,
        "verification_id": verification.id,
        "risk_score": full_risk["risk_score"],
        "risk_level": full_risk["risk_level"],
        "financing_recommendation": full_risk["financing_recommendation"],
        "recommendation_reason": full_risk["recommendation_reason"],
        "recommendation_action": full_risk["recommendation_action"],
        "risk_factors": full_risk["risk_factors"],
        "risk_factor_count": full_risk["risk_factor_count"],
        "duplicate_check": duplicate_info,
        "assessed_at": verification.verified_at.isoformat()
    }

"""
Audit trail API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.db.models import Document
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
async def list_all_audit_events(
    db: Session = Depends(get_db),
    limit: int = 200,
) -> Dict[str, Any]:
    """
    Return all audit events across every entity, newest first.
    Used by the global Audit Trail page.
    """
    from app.db.models import AuditEvent
    import json as _json

    rows = (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
        .all()
    )

    events = []
    for row in rows:
        try:
            data = _json.loads(row.event_data) if row.event_data else {}
        except Exception:
            data = {}

        events.append({
            "id": row.id,
            "event_type": row.event_type,
            "entity_id": row.entity_id,
            "entity_type": row.entity_type,
            "actor": row.actor,
            "timestamp": row.timestamp,
            "event_hash": row.event_hash,
            "previous_hash": row.previous_hash,
            "event_data": data,
            "created_at": row.created_at.isoformat(),
        })

    return {"events": events, "total": len(events)}


@router.get("/trail/{entity_id}")
async def get_audit_trail(
    entity_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get complete audit trail for an entity (document or verification).
    
    Returns all audit events related to the entity in chronological order,
    showing the hash-linked chain of events.
    
    Args:
        entity_id: Document ID or Verification ID
        
    Returns:
        Audit trail with all events
    """
    events = audit_service.get_audit_trail(entity_id, db)
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"No audit trail found for entity {entity_id}"
        )
    
    return {
        "entity_id": entity_id,
        "event_count": len(events),
        "events": events,
        "chain_info": {
            "first_event_hash": events[0]["event_hash"],
            "last_event_hash": events[-1]["event_hash"],
            "is_chained": all(
                events[i]["event_hash"] == events[i+1].get("previous_hash")
                for i in range(len(events)-1)
            ) if len(events) > 1 else True
        }
    }


@router.post("/verify-chain")
async def verify_audit_chain(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify the entire audit chain integrity.
    
    Recalculates all event hashes and verifies the chain hasn't been
    tampered with. Detects:
    - Modified event data
    - Broken hash links
    - Missing events
    
    Returns:
        Verification result with any discrepancies found
    """
    result = audit_service.verify_chain_integrity(db)
    
    return {
        "verification_result": result,
        "timestamp": audit_service.calculate_event_hash.__globals__['datetime'].utcnow().isoformat()
    }


@router.get("/document/{document_id}/integrity")
async def get_document_integrity(
    document_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify a stored document hasn't been tampered with.
    
    Recalculates the document's SHA-256 hash and compares it to
    the hash stored at upload time. Any modification to the file
    will be detected.
    
    Args:
        document_id: Document ID
        
    Returns:
        Integrity verification result
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    result = audit_service.verify_document_integrity(
        document.id,
        document.file_path,
        document.sha256_hash
    )
    
    return {
        "document_id": document_id,
        "filename": document.filename,
        "document_type": document.document_type,
        "uploaded_at": document.uploaded_at.isoformat(),
        "document_found": True,
        "integrity_verified": result["valid"],
        "message": result["message"]
    }


@router.post("/verify-document/{document_id}")
async def verify_document_integrity_post(
    document_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    POST version of document integrity verification (for backward compatibility).
    """
    return await get_document_integrity(document_id, db)


@router.get("/stats")
async def get_audit_stats(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get audit trail statistics.
    
    Returns:
        Statistics about the audit trail
    """
    from app.db.models import AuditEvent
    from sqlalchemy import func
    
    total_events = db.query(func.count(AuditEvent.id)).scalar()
    
    events_by_type = db.query(
        AuditEvent.event_type,
        func.count(AuditEvent.id)
    ).group_by(AuditEvent.event_type).all()
    
    first_event = db.query(AuditEvent).order_by(AuditEvent.created_at.asc()).first()
    last_event = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).first()
    
    return {
        "total_events": total_events,
        "events_by_type": {event_type: count for event_type, count in events_by_type},
        "first_event_at": first_event.created_at.isoformat() if first_event else None,
        "last_event_at": last_event.created_at.isoformat() if last_event else None,
        "chain_length": total_events
    }

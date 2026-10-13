"""
Audit trail service.
Creates tamper-evident hash-linked audit events.
"""
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models import AuditEvent


class AuditService:
    """
    Creates and manages hash-linked audit trail.
    
    Each audit event contains:
    - Event details (type, actor, data)
    - Hash of current event data
    - Hash of previous event (creating a chain)
    
    This makes it possible to detect if any event in the chain
    has been modified after creation.
    """
    
    def calculate_event_hash(
        self,
        event_type: str,
        entity_id: str,
        entity_type: str,
        event_data: Dict[str, Any],
        timestamp: str,
        previous_hash: Optional[str]
    ) -> str:
        """
        Calculate deterministic hash of an audit event.
        
        Args:
            event_type: Type of event (e.g., "document_uploaded")
            entity_id: ID of the entity (document, verification, etc.)
            entity_type: Type of entity (document, verification)
            event_data: Additional event data
            timestamp: ISO format timestamp
            previous_hash: Hash of previous event in chain
            
        Returns:
            SHA-256 hash as hex string
        """
        # Create deterministic representation
        event_dict = {
            "event_type": event_type,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "event_data": event_data,
            "timestamp": timestamp,
            "previous_hash": previous_hash or "GENESIS"
        }
        
        # Use sorted keys for deterministic JSON
        canonical = json.dumps(event_dict, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    
    def get_last_event(self, db: Session) -> Optional[AuditEvent]:
        """Get the most recent audit event."""
        return db.query(AuditEvent).order_by(
            AuditEvent.created_at.desc()
        ).first()
    
    def record_event(
        self,
        event_type: str,
        entity_id: str,
        entity_type: str,
        event_data: Dict[str, Any],
        actor: str = "system",
        db: Session = None
    ) -> AuditEvent:
        """
        Record a new audit event in the hash-linked chain.
        
        Args:
            event_type: Event type (document_uploaded, verification_completed, etc.)
            entity_id: ID of affected entity
            entity_type: Type of entity (document, verification)
            event_data: Additional event data
            actor: Who performed the action
            db: Database session
            
        Returns:
            Created AuditEvent
        """
        # Get previous event for chaining
        previous_event = self.get_last_event(db)
        previous_hash = previous_event.event_hash if previous_event else None
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate event hash
        event_hash = self.calculate_event_hash(
            event_type,
            entity_id,
            entity_type,
            event_data,
            timestamp,
            previous_hash
        )
        
        # Create audit event
        audit_event = AuditEvent(
            event_type=event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            event_data=json.dumps(event_data),
            actor=actor,
            previous_hash=previous_hash,
            event_hash=event_hash,
            timestamp=timestamp
        )
        
        if db:
            db.add(audit_event)
            db.commit()
            db.refresh(audit_event)
        
        return audit_event
    
    def get_audit_trail(
        self,
        entity_id: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Get all audit events for a specific entity.
        
        Args:
            entity_id: Entity ID to query
            db: Database session
            
        Returns:
            List of audit events
        """
        events = db.query(AuditEvent).filter(
            AuditEvent.entity_id == entity_id
        ).order_by(AuditEvent.created_at.asc()).all()
        
        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "entity_type": event.entity_type,
                "event_data": json.loads(event.event_data),
                "actor": event.actor,
                "timestamp": event.timestamp,
                "event_hash": event.event_hash,
                "previous_hash": event.previous_hash
            }
            for event in events
        ]
    
    def verify_chain_integrity(self, db: Session) -> Dict[str, Any]:
        """
        Verify the entire audit chain hasn't been tampered with.
        
        Recalculates each event's hash and verifies it matches
        the stored hash. Also checks that each event's previous_hash
        matches the actual previous event's hash.
        
        Args:
            db: Database session
            
        Returns:
            Verification result with any discrepancies found
        """
        events = db.query(AuditEvent).order_by(AuditEvent.created_at.asc()).all()
        
        if not events:
            return {
                "valid": True,
                "event_count": 0,
                "message": "No audit events to verify"
            }
        
        discrepancies = []
        previous_hash = None
        
        for idx, event in enumerate(events):
            # Verify previous_hash points to actual previous event
            if previous_hash != event.previous_hash:
                discrepancies.append({
                    "event_id": event.id,
                    "event_index": idx,
                    "issue": "previous_hash_mismatch",
                    "expected": previous_hash,
                    "actual": event.previous_hash
                })
            
            # Recalculate event hash
            event_data = json.loads(event.event_data)
            calculated_hash = self.calculate_event_hash(
                event.event_type,
                event.entity_id,
                event.entity_type,
                event_data,
                event.timestamp,
                event.previous_hash
            )
            
            # Verify stored hash matches calculated hash
            if calculated_hash != event.event_hash:
                discrepancies.append({
                    "event_id": event.id,
                    "event_index": idx,
                    "issue": "event_hash_mismatch",
                    "expected": calculated_hash,
                    "actual": event.event_hash
                })
            
            previous_hash = event.event_hash
        
        return {
            "valid": len(discrepancies) == 0,
            "event_count": len(events),
            "discrepancies": discrepancies,
            "message": "Audit chain is valid" if not discrepancies else f"Found {len(discrepancies)} discrepancies"
        }
    
    def verify_document_integrity(
        self,
        document_id: str,
        document_path: str,
        expected_hash: str
    ) -> Dict[str, Any]:
        """
        Verify a stored document hasn't been modified.
        
        Args:
            document_id: Document ID
            document_path: Path to stored file
            expected_hash: Expected SHA-256 hash
            
        Returns:
            Verification result
        """
        from pathlib import Path
        
        file_path = Path(document_path)
        
        if not file_path.exists():
            return {
                "valid": False,
                "document_id": document_id,
                "issue": "file_not_found",
                "message": f"Document file not found at {document_path}"
            }
        
        # Calculate current hash
        file_content = file_path.read_bytes()
        current_hash = hashlib.sha256(file_content).hexdigest()
        
        # Compare hashes
        if current_hash == expected_hash:
            return {
                "valid": True,
                "document_id": document_id,
                "message": "Document integrity verified",
                "hash": current_hash
            }
        else:
            return {
                "valid": False,
                "document_id": document_id,
                "issue": "hash_mismatch",
                "expected_hash": expected_hash,
                "actual_hash": current_hash,
                "message": "Document has been modified after upload"
            }


# Global instance
audit_service = AuditService()

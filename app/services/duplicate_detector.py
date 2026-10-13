"""
Duplicate detection service.
Detects duplicate invoices using SHA-256 hashes and business identifiers.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.models import Document, Verification
from app.services.field_normalizer import field_normalizer


class DuplicateDetector:
    """Detects duplicate invoice submissions."""
    
    def detect_duplicate_by_hash(
        self,
        document_hash: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Detect exact duplicate by SHA-256 hash.
        
        Args:
            document_hash: SHA-256 hash of the document
            db: Database session
            
        Returns:
            Duplicate document info if found, None otherwise
        """
        # Find documents with matching hash
        duplicates = db.query(Document).filter(
            Document.sha256_hash == document_hash
        ).all()
        
        if len(duplicates) > 1:
            # Sort by upload time
            duplicates.sort(key=lambda d: d.uploaded_at)
            original = duplicates[0]
            
            return {
                "duplicate_found": True,
                "duplicate_type": "exact_file_match",
                "original_document_id": original.id,
                "original_uploaded_at": original.uploaded_at.isoformat(),
                "duplicate_count": len(duplicates) - 1,
                "message": f"Exact file duplicate detected. Original uploaded on {original.uploaded_at.date()}"
            }
        
        return None
    
    def detect_duplicate_by_business_id(
        self,
        invoice_number: Optional[str],
        supplier_name: Optional[str],
        amount: Optional[float],
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Detect duplicate by business identifiers.
        
        Checks for invoices with same:
        - Invoice number + supplier (most reliable)
        - Invoice number + supplier + amount (strongest signal)
        
        Args:
            invoice_number: Invoice number
            supplier_name: Supplier name
            amount: Invoice amount
            db: Database session
            
        Returns:
            Duplicate info if found, None otherwise
        """
        if not invoice_number or not supplier_name:
            return None
        
        # Normalize for comparison
        norm_invoice_num = field_normalizer.normalize_identifier(invoice_number)
        norm_supplier = field_normalizer.normalize_company_name(supplier_name)
        
        if not norm_invoice_num or not norm_supplier:
            return None
        
        # Find previous verifications with similar business identifiers
        verifications = db.query(Verification).all()
        
        matches = []
        for verification in verifications:
            # Parse stored JSON
            inv_fields = verification.get_invoice_fields()
            
            stored_inv_num = field_normalizer.normalize_identifier(
                inv_fields.get("invoice_number")
            )
            stored_supplier = field_normalizer.normalize_company_name(
                inv_fields.get("supplier_name")
            )
            stored_amount = field_normalizer.normalize_amount(
                inv_fields.get("amount")
            )
            
            # Check for match
            if stored_inv_num == norm_invoice_num and stored_supplier == norm_supplier:
                match_info = {
                    "verification_id": verification.id,
                    "invoice_id": verification.invoice_id,
                    "verified_at": verification.verified_at.isoformat(),
                    "invoice_number": inv_fields.get("invoice_number"),
                    "supplier": inv_fields.get("supplier_name"),
                    "amount": stored_amount
                }
                
                # Check if amount also matches
                if amount and stored_amount:
                    norm_amount = field_normalizer.normalize_amount(amount)
                    if abs(norm_amount - stored_amount) < 0.01:
                        match_info["amount_match"] = True
                
                matches.append(match_info)
        
        if matches:
            # Sort by verification time
            matches.sort(key=lambda m: m["verified_at"])
            original = matches[0]
            
            amount_matched = original.get("amount_match", False)
            
            return {
                "duplicate_found": True,
                "duplicate_type": "business_identifier_match",
                "confidence": "high" if amount_matched else "medium",
                "original_verification_id": original["verification_id"],
                "original_invoice_id": original["invoice_id"],
                "original_verified_at": original["verified_at"],
                "matching_fields": {
                    "invoice_number": original["invoice_number"],
                    "supplier": original["supplier"],
                    "amount_match": amount_matched
                },
                "duplicate_count": len(matches),
                "message": f"Potential duplicate invoice. Same invoice number and supplier found in previous submission on {original['verified_at'][:10]}"
            }
        
        return None
    
    def check_duplicates(
        self,
        document_hash: str,
        invoice_number: Optional[str],
        supplier_name: Optional[str],
        amount: Optional[float],
        db: Session
    ) -> Dict[str, Any]:
        """
        Check for duplicates using both hash and business identifiers.
        
        Args:
            document_hash: SHA-256 hash
            invoice_number: Invoice number
            supplier_name: Supplier name
            amount: Invoice amount
            db: Database session
            
        Returns:
            Duplicate detection results
        """
        results = {
            "exact_duplicate": None,
            "business_duplicate": None,
            "has_duplicates": False
        }
        
        # Check exact file duplicate
        exact_dup = self.detect_duplicate_by_hash(document_hash, db)
        if exact_dup:
            results["exact_duplicate"] = exact_dup
            results["has_duplicates"] = True
        
        # Check business identifier duplicate
        business_dup = self.detect_duplicate_by_business_id(
            invoice_number,
            supplier_name,
            amount,
            db
        )
        if business_dup:
            results["business_duplicate"] = business_dup
            results["has_duplicates"] = True
        
        return results


# Global instance
duplicate_detector = DuplicateDetector()

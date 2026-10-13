"""
Document comparison service.
Compares extracted fields from invoice, PO, and delivery receipt.
"""
from typing import Dict, List, Any, Optional
from app.services.field_normalizer import field_normalizer


class Finding:
    """Represents a verification finding."""
    
    def __init__(
        self,
        finding_type: str,
        severity: str,
        field: str,
        message: str,
        expected_value: Any = None,
        actual_value: Any = None
    ):
        self.finding_type = finding_type
        self.severity = severity  # "critical", "high", "medium", "low", "info"
        self.field = field
        self.message = message
        self.expected_value = expected_value
        self.actual_value = actual_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "finding_type": self.finding_type,
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value
        }


class DocumentComparator:
    """Compares documents to detect discrepancies."""
    
    def compare_documents(
        self,
        invoice_fields: Dict[str, Any],
        po_fields: Optional[Dict[str, Any]] = None,
        delivery_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare invoice against PO and delivery receipt.
        
        Args:
            invoice_fields: Extracted invoice fields
            po_fields: Extracted PO fields (optional)
            delivery_fields: Extracted delivery receipt fields (optional)
            
        Returns:
            Comparison results with findings
        """
        findings: List[Finding] = []
        
        # Check for missing mandatory invoice fields
        findings.extend(self._check_mandatory_fields(invoice_fields))
        
        # Compare invoice with PO if available
        if po_fields:
            findings.extend(self._compare_invoice_with_po(invoice_fields, po_fields))
        
        # Compare invoice with delivery receipt if available
        if delivery_fields:
            findings.extend(self._compare_invoice_with_delivery(invoice_fields, delivery_fields))
        
        # Cross-check quantities if all documents available
        if po_fields and delivery_fields:
            findings.extend(
                self._compare_quantities(invoice_fields, po_fields, delivery_fields)
            )
        
        # Determine overall verification status
        status = self._determine_status(findings)
        
        return {
            "status": status,
            "findings": [f.to_dict() for f in findings],
            "findings_count": len(findings),
            "critical_count": sum(1 for f in findings if f.severity == "critical"),
            "high_count": sum(1 for f in findings if f.severity == "high"),
            "medium_count": sum(1 for f in findings if f.severity == "medium")
        }
    
    def _check_mandatory_fields(self, invoice_fields: Dict[str, Any]) -> List[Finding]:
        """Check for missing mandatory invoice fields."""
        findings = []
        
        mandatory = {
            "invoice_number": "Invoice Number",
            "supplier_name": "Supplier Name",
            "buyer_name": "Buyer Name",
            "amount": "Invoice Amount"
        }
        
        for field, display_name in mandatory.items():
            if not invoice_fields.get(field):
                findings.append(Finding(
                    finding_type="missing_field",
                    severity="high",
                    field=field,
                    message=f"Missing mandatory field: {display_name}",
                    expected_value="Required",
                    actual_value=None
                ))
        
        return findings
    
    def _compare_invoice_with_po(
        self,
        invoice_fields: Dict[str, Any],
        po_fields: Dict[str, Any]
    ) -> List[Finding]:
        """Compare invoice against purchase order."""
        findings = []
        
        # Check PO reference match
        invoice_po_ref = field_normalizer.normalize_identifier(
            invoice_fields.get("po_reference")
        )
        po_number = field_normalizer.normalize_identifier(
            po_fields.get("po_number")
        )
        
        if invoice_po_ref and po_number and invoice_po_ref != po_number:
            findings.append(Finding(
                finding_type="po_mismatch",
                severity="critical",
                field="po_reference",
                message="Invoice PO reference does not match PO number",
                expected_value=po_number,
                actual_value=invoice_po_ref
            ))
        
        # Check supplier consistency
        invoice_supplier = field_normalizer.normalize_company_name(
            invoice_fields.get("supplier_name")
        )
        po_supplier = field_normalizer.normalize_company_name(
            po_fields.get("supplier_name")
        )
        
        if invoice_supplier and po_supplier and invoice_supplier != po_supplier:
            findings.append(Finding(
                finding_type="supplier_mismatch",
                severity="critical",
                field="supplier_name",
                message="Supplier name mismatch between invoice and PO",
                expected_value=po_supplier,
                actual_value=invoice_supplier
            ))
        
        # Check buyer consistency
        invoice_buyer = field_normalizer.normalize_company_name(
            invoice_fields.get("buyer_name")
        )
        po_buyer = field_normalizer.normalize_company_name(
            po_fields.get("buyer_name")
        )
        
        if invoice_buyer and po_buyer and invoice_buyer != po_buyer:
            findings.append(Finding(
                finding_type="buyer_mismatch",
                severity="high",
                field="buyer_name",
                message="Buyer name mismatch between invoice and PO",
                expected_value=po_buyer,
                actual_value=invoice_buyer
            ))
        
        # Check amount consistency
        invoice_amount = field_normalizer.normalize_amount(
            invoice_fields.get("amount")
        )
        po_amount = field_normalizer.normalize_amount(
            po_fields.get("amount")
        )
        
        if invoice_amount and po_amount:
            # Allow small rounding differences
            if abs(invoice_amount - po_amount) > 0.01:
                difference = abs(invoice_amount - po_amount)
                percentage = (difference / po_amount) * 100 if po_amount > 0 else 0
                
                severity = "critical" if percentage > 10 else "high"
                
                findings.append(Finding(
                    finding_type="amount_mismatch",
                    severity=severity,
                    field="amount",
                    message=f"Invoice amount differs from PO by ${difference:.2f} ({percentage:.1f}%)",
                    expected_value=po_amount,
                    actual_value=invoice_amount
                ))
        
        return findings
    
    def _compare_invoice_with_delivery(
        self,
        invoice_fields: Dict[str, Any],
        delivery_fields: Dict[str, Any]
    ) -> List[Finding]:
        """Compare invoice against delivery receipt."""
        findings = []
        
        # Check PO reference consistency
        invoice_po_ref = field_normalizer.normalize_identifier(
            invoice_fields.get("po_reference")
        )
        delivery_po_ref = field_normalizer.normalize_identifier(
            delivery_fields.get("po_reference")
        )
        
        if invoice_po_ref and delivery_po_ref and invoice_po_ref != delivery_po_ref:
            findings.append(Finding(
                finding_type="po_reference_mismatch",
                severity="high",
                field="po_reference",
                message="PO reference mismatch between invoice and delivery receipt",
                expected_value=delivery_po_ref,
                actual_value=invoice_po_ref
            ))
        
        # Check supplier consistency
        invoice_supplier = field_normalizer.normalize_company_name(
            invoice_fields.get("supplier_name")
        )
        delivery_supplier = field_normalizer.normalize_company_name(
            delivery_fields.get("supplier_name")
        )
        
        if invoice_supplier and delivery_supplier and invoice_supplier != delivery_supplier:
            findings.append(Finding(
                finding_type="supplier_mismatch",
                severity="critical",
                field="supplier_name",
                message="Supplier name mismatch between invoice and delivery receipt",
                expected_value=delivery_supplier,
                actual_value=invoice_supplier
            ))
        
        return findings
    
    def _compare_quantities(
        self,
        invoice_fields: Dict[str, Any],
        po_fields: Dict[str, Any],
        delivery_fields: Dict[str, Any]
    ) -> List[Finding]:
        """Compare quantities across all three documents."""
        findings = []
        
        invoice_qty = field_normalizer.normalize_quantity(
            invoice_fields.get("quantity")
        )
        po_qty = field_normalizer.normalize_quantity(
            po_fields.get("quantity")
        )
        delivered_qty = field_normalizer.normalize_quantity(
            delivery_fields.get("delivered_quantity")
        )
        
        # Check if invoiced quantity exceeds delivered quantity
        if invoice_qty and delivered_qty and invoice_qty > delivered_qty:
            findings.append(Finding(
                finding_type="quantity_overcharge",
                severity="critical",
                field="quantity",
                message=f"Invoice quantity ({invoice_qty}) exceeds delivered quantity ({delivered_qty})",
                expected_value=delivered_qty,
                actual_value=invoice_qty
            ))
        
        # Check if delivered quantity exceeds PO quantity
        if delivered_qty and po_qty and delivered_qty > po_qty:
            findings.append(Finding(
                finding_type="over_delivery",
                severity="medium",
                field="quantity",
                message=f"Delivered quantity ({delivered_qty}) exceeds PO quantity ({po_qty})",
                expected_value=po_qty,
                actual_value=delivered_qty
            ))
        
        return findings
    
    def _determine_status(self, findings: List[Finding]) -> str:
        """
        Determine overall verification status based on findings.
        
        Returns:
            One of: "approved", "review_required", "rejected"
        """
        if not findings:
            return "approved"
        
        # Any critical findings require rejection or manual review
        critical_count = sum(1 for f in findings if f.severity == "critical")
        if critical_count > 0:
            return "rejected"
        
        # High severity findings require review
        high_count = sum(1 for f in findings if f.severity == "high")
        if high_count > 0:
            return "review_required"
        
        # Medium or low findings still require review
        return "review_required"


# Global instance
document_comparator = DocumentComparator()

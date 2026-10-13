"""
Risk scoring engine.
Calculates explainable risk scores for invoice financing decisions.
"""
from typing import List, Dict, Any


class RiskEngine:
    """
    Calculates risk scores based on verification findings and duplicates.
    
    Risk scoring is configurable and explainable. Each risk factor
    has a weight and contributes to the overall score.
    """
    
    def __init__(self):
        """Initialize with default risk weights."""
        self.risk_weights = {
            # Duplicate-related risks
            "exact_duplicate": 50,
            "business_duplicate_high": 40,
            "business_duplicate_medium": 25,
            
            # Critical findings
            "supplier_mismatch": 35,
            "po_mismatch": 30,
            "quantity_overcharge": 35,
            
            # High severity findings
            "amount_mismatch_critical": 30,  # >10% difference
            "amount_mismatch_high": 20,      # ≤10% difference
            "buyer_mismatch": 20,
            "po_reference_mismatch": 15,
            
            # Missing field risks
            "missing_critical_field": 15,
            "missing_field": 10,
            
            # Medium severity
            "over_delivery": 10,
            
            # Extraction issues
            "extraction_failed": 25,
            "partial_extraction": 10
        }
    
    def calculate_risk_score(
        self,
        findings: List[Dict[str, Any]],
        duplicate_results: Dict[str, Any],
        invoice_fields: Dict[str, Any],
        po_fields: Dict[str, Any] = None,
        delivery_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score.
        
        Args:
            findings: List of verification findings
            duplicate_results: Duplicate detection results
            invoice_fields: Extracted invoice fields
            po_fields: Extracted PO fields
            delivery_fields: Extracted delivery receipt fields
            
        Returns:
            Risk assessment with score, level, and explanation
        """
        risk_factors = []
        total_score = 0
        
        # Check for duplicates
        if duplicate_results.get("has_duplicates"):
            if duplicate_results.get("exact_duplicate"):
                score = self.risk_weights["exact_duplicate"]
                total_score += score
                risk_factors.append({
                    "factor": "exact_duplicate",
                    "score": score,
                    "description": "Exact duplicate file detected",
                    "details": duplicate_results["exact_duplicate"]["message"]
                })
            
            if duplicate_results.get("business_duplicate"):
                bus_dup = duplicate_results["business_duplicate"]
                confidence = bus_dup.get("confidence", "medium")
                
                if confidence == "high":
                    score = self.risk_weights["business_duplicate_high"]
                else:
                    score = self.risk_weights["business_duplicate_medium"]
                
                total_score += score
                risk_factors.append({
                    "factor": f"business_duplicate_{confidence}",
                    "score": score,
                    "description": "Potential duplicate invoice submission",
                    "details": bus_dup["message"]
                })
        
        # Process verification findings
        for finding in findings:
            finding_type = finding["finding_type"]
            severity = finding["severity"]
            
            # Map findings to risk factors
            score = 0
            
            if finding_type == "supplier_mismatch":
                score = self.risk_weights["supplier_mismatch"]
            elif finding_type == "po_mismatch":
                score = self.risk_weights["po_mismatch"]
            elif finding_type == "quantity_overcharge":
                score = self.risk_weights["quantity_overcharge"]
            elif finding_type == "amount_mismatch":
                # Check percentage difference
                if severity == "critical":
                    score = self.risk_weights["amount_mismatch_critical"]
                else:
                    score = self.risk_weights["amount_mismatch_high"]
            elif finding_type == "buyer_mismatch":
                score = self.risk_weights["buyer_mismatch"]
            elif finding_type == "po_reference_mismatch":
                score = self.risk_weights["po_reference_mismatch"]
            elif finding_type == "missing_field":
                # Critical fields get higher weight
                if finding["field"] in ["invoice_number", "supplier_name", "amount"]:
                    score = self.risk_weights["missing_critical_field"]
                else:
                    score = self.risk_weights["missing_field"]
            elif finding_type == "over_delivery":
                score = self.risk_weights["over_delivery"]
            
            if score > 0:
                total_score += score
                risk_factors.append({
                    "factor": finding_type,
                    "score": score,
                    "description": finding["message"],
                    "details": f"Field: {finding['field']}, Severity: {severity}"
                })
        
        # Check extraction quality
        if not invoice_fields.get("extraction_successful"):
            score = self.risk_weights["extraction_failed"]
            total_score += score
            risk_factors.append({
                "factor": "extraction_failed",
                "score": score,
                "description": "Failed to extract invoice data",
                "details": "Unable to parse invoice fields reliably"
            })
        elif not invoice_fields.get("amount") or not invoice_fields.get("invoice_number"):
            score = self.risk_weights["partial_extraction"]
            total_score += score
            risk_factors.append({
                "factor": "partial_extraction",
                "score": score,
                "description": "Incomplete data extraction",
                "details": "Some critical fields could not be extracted"
            })
        
        # Cap score at 100
        total_score = min(total_score, 100)
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        # Generate financing recommendation
        recommendation = self._generate_recommendation(
            total_score,
            risk_level,
            risk_factors
        )
        
        return {
            "risk_score": round(total_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "risk_factor_count": len(risk_factors),
            "financing_recommendation": recommendation["recommendation"],
            "recommendation_reason": recommendation["reason"],
            "recommendation_action": recommendation["action"]
        }
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score."""
        if score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        elif score >= 10:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_recommendation(
        self,
        score: float,
        risk_level: str,
        risk_factors: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate financing recommendation."""
        
        # Check for critical factors
        has_duplicate = any(
            "duplicate" in f["factor"]
            for f in risk_factors
        )
        has_critical_mismatch = any(
            f["factor"] in ["supplier_mismatch", "quantity_overcharge", "po_mismatch"]
            for f in risk_factors
        )
        
        if score >= 50 or has_duplicate:
            return {
                "recommendation": "REJECT",
                "reason": "High risk score or duplicate submission detected",
                "action": "Do not proceed with financing. Conduct thorough investigation."
            }
        elif score >= 35 or has_critical_mismatch:
            return {
                "recommendation": "MANUAL_REVIEW_REQUIRED",
                "reason": "Significant discrepancies or moderate risk level",
                "action": "Requires detailed manual review before financing decision."
            }
        elif score >= 15:
            return {
                "recommendation": "REVIEW_WITH_CAUTION",
                "reason": "Some minor issues detected",
                "action": "May proceed with additional verification steps and documentation."
            }
        else:
            return {
                "recommendation": "APPROVED_FOR_CONSIDERATION",
                "reason": "Low risk factors detected",
                "action": "Eligible for standard financing review process."
            }


# Global instance
risk_engine = RiskEngine()

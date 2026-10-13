"""
Field normalization service.
Standardizes extracted data for consistent comparison.
"""
import re
from typing import Optional


class FieldNormalizer:
    """Normalizes extracted fields for comparison."""
    
    def normalize_identifier(self, identifier: Optional[str]) -> Optional[str]:
        """
        Normalize identifiers (invoice numbers, PO numbers, etc.).
        
        Args:
            identifier: Raw identifier string
            
        Returns:
            Normalized identifier (uppercase, no spaces/dashes)
        """
        if not identifier:
            return None
        
        # Convert to uppercase, remove spaces and dashes
        normalized = identifier.upper().replace(" ", "").replace("-", "")
        return normalized if normalized else None
    
    def normalize_company_name(self, name: Optional[str]) -> Optional[str]:
        """
        Normalize company names for comparison.
        
        Args:
            name: Raw company name
            
        Returns:
            Normalized company name
        """
        if not name:
            return None
        
        # Convert to uppercase, remove extra spaces
        normalized = " ".join(name.upper().split())
        
        # Remove common suffixes for better matching
        suffixes = [" INC", " INC.", " LLC", " LLC.", " LTD", " LTD.", " CORP", " CORP."]
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        return normalized if normalized else None
    
    def normalize_amount(self, amount: Optional[float]) -> Optional[float]:
        """
        Normalize monetary amounts.
        
        Args:
            amount: Raw amount
            
        Returns:
            Normalized amount (rounded to 2 decimal places)
        """
        if amount is None:
            return None
        
        try:
            return round(float(amount), 2)
        except (ValueError, TypeError):
            return None
    
    def normalize_quantity(self, quantity: Optional[int]) -> Optional[int]:
        """
        Normalize quantities.
        
        Args:
            quantity: Raw quantity
            
        Returns:
            Normalized quantity (integer)
        """
        if quantity is None:
            return None
        
        try:
            return int(quantity)
        except (ValueError, TypeError):
            return None
    
    def normalize_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Normalize date strings to YYYY-MM-DD format.
        Simple implementation for demonstration.
        
        Args:
            date_str: Raw date string
            
        Returns:
            Normalized date string
        """
        if not date_str:
            return None
        
        # This is a simple implementation
        # Production would use proper date parsing libraries
        # Just return as-is for now
        return date_str.strip()


# Global instance
field_normalizer = FieldNormalizer()

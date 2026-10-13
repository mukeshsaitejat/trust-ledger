"""
PDF text extraction service.
Extracts structured data from invoice, PO, and delivery receipt PDFs.
"""
import re
from pathlib import Path
from typing import Optional, Dict, Any
import fitz  # PyMuPDF


class PDFExtractor:
    """Extracts text and structured data from PDF documents."""
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If PDF cannot be read
        """
        try:
            doc = fitz.open(file_path)
            text_content = []
            
            for page in doc:
                text_content.append(page.get_text())
            
            doc.close()
            return "\n".join(text_content)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_invoice_fields(self, text: str) -> Dict[str, Any]:
        """
        Parse invoice-specific fields from extracted text.
        
        This is a simple pattern-based parser for demonstration.
        Production systems would use more sophisticated OCR/NLP.
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {
            "invoice_number": None,
            "invoice_date": None,
            "supplier_name": None,
            "buyer_name": None,
            "po_reference": None,
            "amount": None,
            "quantity": None,
            "unit_price": None,
            "extraction_successful": False,
            "extraction_errors": []
        }
        
        try:
            # Invoice number patterns - improved to skip label words
            invoice_patterns = [
                r"Invoice\s+Number\s*:?\s+([A-Z0-9\-]+)",
                r"Invoice\s*#\s*:?\s*([A-Z0-9\-]+)",
                r"INV\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"Invoice\s+No\.?\s*:?\s*([A-Z0-9\-]+)"
            ]
            for pattern in invoice_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    inv_num = match.group(1).strip()
                    # Skip if we just captured the label word itself
                    if inv_num.upper() not in ['NUMBER', 'NO', 'INVOICE']:
                        fields["invoice_number"] = inv_num
                        break
            
            # Invoice date patterns
            date_patterns = [
                r"Invoice\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields["invoice_date"] = match.group(1).strip()
                    break
            
            # Supplier patterns - improved for table and inline formats
            supplier_patterns = [
                r"Supplier\s+([A-Za-z0-9\s&,\.'\-]+?)(?:\n|Buyer|PO|Amount|Quantity)",  # Table format
                r"(?:From|Supplier|Vendor)\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)",
                r"Supplier\s+Name\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)"
            ]
            for pattern in supplier_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    supplier = match.group(1).strip()
                    # Filter out obviously wrong captures
                    if len(supplier) > 3 and supplier.upper() not in ['NAME', 'VALUE', 'FIELD']:
                        fields["supplier_name"] = supplier
                        break
            
            # Buyer patterns - improved for table and inline formats
            buyer_patterns = [
                r"Buyer\s+([A-Za-z0-9\s&,\.'\-]+?)(?:\n|PO|Amount|Quantity|Supplier|Notes)",  # Table format
                r"(?:To|Buyer|Customer)\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)",
                r"Bill\s+To\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)"
            ]
            for pattern in buyer_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    buyer = match.group(1).strip()
                    # Filter out obviously wrong captures
                    if len(buyer) > 3 and buyer.upper() not in ['NAME', 'VALUE', 'FIELD']:
                        fields["buyer_name"] = buyer
                        break
            
            # PO reference patterns - improved
            po_patterns = [
                r"PO\s+Reference\s*:?\s+([A-Z0-9\-]+)",
                r"PO\s*#\s*:?\s*([A-Z0-9\-]+)",
                r"Purchase\s+Order\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"P\.?O\.?\s+Number\s*:?\s*([A-Z0-9\-]+)",
                r"PO\s*:?\s+([A-Z0-9\-]+)"
            ]
            for pattern in po_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    po_ref = match.group(1).strip()
                    # Skip if we just captured label words
                    if po_ref.upper() not in ['REFERENCE', 'NUMBER', 'ORDER']:
                        fields["po_reference"] = po_ref
                        break
            
            # Amount patterns - support multiple currencies (USD, INR, EUR, etc.)
            amount_patterns = [
                r"(?:Total|Amount|Grand\s+Total)\s*:?\s*[$₹€£¥I]\s*([\d,]+\.?\d*)",
                r"Amount\s*:?\s*\n?\s*[$₹€£¥I]\s*([\d,]+\.?\d*)",
                r"(?:Total|Amount)\s*[$₹€£¥I]?\s*([\d,]+\.?\d*)",
                r"[$₹€£¥I]\s*([\d,]+\.?\d*)\s*(?:Total|USD|INR|EUR)"
            ]
            for pattern in amount_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(",", "")
                    try:
                        fields["amount"] = float(amount_str)
                        break
                    except ValueError:
                        pass
            
            # Quantity patterns
            quantity_patterns = [
                r"(?:Quantity|Qty)\s*:?\s*(\d+)",
                r"(\d+)\s+(?:units?|items?|pcs?)"
            ]
            for pattern in quantity_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        fields["quantity"] = int(match.group(1))
                    except ValueError:
                        pass
                    break
            
            # Unit price patterns
            unit_price_patterns = [
                r"(?:Unit\s+Price|Price\s+per\s+Unit)\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                r"\$\s*([\d,]+\.?\d*)\s*/\s*(?:unit|item|pc)"
            ]
            for pattern in unit_price_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(",", "")
                    try:
                        fields["unit_price"] = float(price_str)
                    except ValueError:
                        pass
                    break
            
            # Mark extraction as successful if we got key fields
            if fields["invoice_number"] or fields["amount"]:
                fields["extraction_successful"] = True
            else:
                fields["extraction_errors"].append("Could not extract key invoice fields")
            
        except Exception as e:
            fields["extraction_errors"].append(f"Extraction error: {str(e)}")
        
        return fields
    
    def extract_po_fields(self, text: str) -> Dict[str, Any]:
        """
        Parse purchase order fields from extracted text.
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {
            "po_number": None,
            "po_date": None,
            "supplier_name": None,
            "buyer_name": None,
            "amount": None,
            "quantity": None,
            "extraction_successful": False,
            "extraction_errors": []
        }
        
        try:
            # PO number patterns - improved
            po_patterns = [
                r"Purchase\s+Order\s+Number\s*:?\s+([A-Z0-9\-]+)",
                r"(?:Purchase\s+Order|PO)\s*#\s*:?\s*([A-Z0-9\-]+)",
                r"Order\s+Number\s*:?\s*([A-Z0-9\-]+)",
                r"PO\s*:?\s+([A-Z0-9\-]+)"
            ]
            for pattern in po_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    po_num = match.group(1).strip()
                    if po_num.upper() not in ['NUMBER', 'ORDER', 'DOCUMENT']:
                        fields["po_number"] = po_num
                        break
            
            # Date patterns
            date_patterns = [
                r"(?:PO\s+Date|Order\s+Date|Date)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields["po_date"] = match.group(1).strip()
                    break
            
            # Supplier patterns - improved for table format
            supplier_patterns = [
                r"Supplier\s+([A-Za-z0-9\s&,\.'\-]+?)(?:\n|Buyer|Amount|Quantity|PO)",  # Table format
                r"(?:Vendor|Supplier)\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)"
            ]
            for pattern in supplier_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    supplier = match.group(1).strip()
                    if len(supplier) > 3 and supplier.upper() not in ['NAME', 'VALUE', 'FIELD']:
                        fields["supplier_name"] = supplier
                        break
            
            # Buyer patterns - improved for table format
            buyer_patterns = [
                r"Buyer\s+([A-Za-z0-9\s&,\.'\-]+?)(?:\n|Supplier|Amount|Quantity|PO|Notes)",  # Table format
                r"(?:Buyer|Customer|Ordered\s+By)\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)"
            ]
            for pattern in buyer_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    buyer = match.group(1).strip()
                    if len(buyer) > 3 and buyer.upper() not in ['NAME', 'VALUE', 'FIELD']:
                        fields["buyer_name"] = buyer
                        break
            
            # Amount patterns - support multiple currencies
            amount_patterns = [
                r"(?:Total|Amount)\s*:?\s*[$₹€£¥I]\s*([\d,]+\.?\d*)",
                r"Amount\s*:?\s*\n?\s*[$₹€£¥I]\s*([\d,]+\.?\d*)",
                r"[$₹€£¥I]\s*([\d,]+\.?\d*)\s*(?:Total|USD|INR|EUR)"
            ]
            for pattern in amount_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(",", "")
                    try:
                        fields["amount"] = float(amount_str)
                        break
                    except ValueError:
                        pass
            
            # Quantity patterns
            quantity_patterns = [
                r"(?:Quantity|Qty)\s*:?\s*(\d+)"
            ]
            for pattern in quantity_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        fields["quantity"] = int(match.group(1))
                    except ValueError:
                        pass
                    break
            
            if fields["po_number"]:
                fields["extraction_successful"] = True
            else:
                fields["extraction_errors"].append("Could not extract PO number")
            
        except Exception as e:
            fields["extraction_errors"].append(f"Extraction error: {str(e)}")
        
        return fields
    
    def extract_delivery_receipt_fields(self, text: str) -> Dict[str, Any]:
        """
        Parse delivery receipt fields from extracted text.
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {
            "receipt_number": None,
            "delivery_date": None,
            "supplier_name": None,
            "buyer_name": None,
            "po_reference": None,
            "delivered_quantity": None,
            "extraction_successful": False,
            "extraction_errors": []
        }
        
        try:
            # Receipt number patterns
            receipt_patterns = [
                r"(?:Receipt|Delivery)\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"Delivery\s+Note\s*#?\s*:?\s*([A-Z0-9\-]+)"
            ]
            for pattern in receipt_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields["receipt_number"] = match.group(1).strip()
                    break
            
            # Delivery date patterns
            date_patterns = [
                r"(?:Delivery\s+Date|Date\s+Delivered|Date)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields["delivery_date"] = match.group(1).strip()
                    break
            
            # Supplier patterns - improved for table format
            supplier_patterns = [
                r"Supplier\s+([A-Za-z0-9\s&,\.'\-]+?)(?:\n|Buyer|Delivered|Quantity|PO)",  # Table format
                r"(?:From|Supplier|Vendor)\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)"
            ]
            for pattern in supplier_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    supplier = match.group(1).strip()
                    if len(supplier) > 3 and supplier.upper() not in ['NAME', 'VALUE', 'FIELD']:
                        fields["supplier_name"] = supplier
                        break
            
            # Buyer patterns - improved for table format
            buyer_patterns = [
                r"(?:Delivered\s+To|Buyer)\s+([A-Za-z0-9\s&,\.'\-]+?)(?:\n|Supplier|Quantity|PO|Notes)",  # Table format
                r"(?:To|Delivered\s+To|Customer)\s*:?\s*([A-Za-z0-9\s&,\.'\-]+?)(?:\n|$)"
            ]
            for pattern in buyer_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    buyer = match.group(1).strip()
                    if len(buyer) > 3 and buyer.upper() not in ['NAME', 'VALUE', 'FIELD']:
                        fields["buyer_name"] = buyer
                        break
                    break
            
            # PO reference patterns - improved
            po_patterns = [
                r"PO\s+Reference\s*:?\s+([A-Z0-9\-]+)",
                r"PO\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"Purchase\s+Order\s*:?\s*([A-Z0-9\-]+)",
                r"PO\s*:?\s+([A-Z0-9\-]+)"
            ]
            for pattern in po_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    po_ref = match.group(1).strip()
                    if po_ref.upper() not in ['REFERENCE', 'NUMBER', 'ORDER']:
                        fields["po_reference"] = po_ref
                        break
            
            # Delivered quantity patterns
            quantity_patterns = [
                r"(?:Delivered|Quantity\s+Delivered|Qty)\s*:?\s*(\d+)",
                r"(\d+)\s+(?:units?\s+delivered|items?\s+delivered)"
            ]
            for pattern in quantity_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        fields["delivered_quantity"] = int(match.group(1))
                    except ValueError:
                        pass
                    break
            
            if fields["receipt_number"] or fields["delivered_quantity"] is not None:
                fields["extraction_successful"] = True
            else:
                fields["extraction_errors"].append("Could not extract delivery receipt fields")
            
        except Exception as e:
            fields["extraction_errors"].append(f"Extraction error: {str(e)}")
        
        return fields


# Global instance
pdf_extractor = PDFExtractor()

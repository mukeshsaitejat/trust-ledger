InvoiceShield Synthetic PDF Test Pack
======================================

All files are fictional synthetic test documents. They are NOT valid commercial, tax, payment, or financing documents.

Cases:
1. case1_clean: invoice, purchase order, delivery receipt should match on supplier, buyer, PO reference, amount, and quantity.
2. case2_amount_mismatch: invoice amount is ₹95,000 while PO/delivery amount is ₹90,000.
3. case3_quantity_mismatch: invoice says 100 units but delivery receipt says 80 units.
4. case4_supplier_mismatch: invoice supplier name differs from PO and delivery receipt supplier.
5. case5_duplicate_invoice: invoice_duplicate.pdf is byte-for-byte copy of case1_clean/invoice.pdf; use it to test exact-file hash duplicate detection.

Important:
- These PDFs are designed for testing a parser and demo workflow, but their fields are simple and structured. OCR/text extraction and currency parsing may need normalization.
- Duplicate invoice identity checks should also use invoice number + supplier + amount; file hashes only catch byte-identical files.
- A mismatch should be treated as a review flag, not definitive proof of fraud.

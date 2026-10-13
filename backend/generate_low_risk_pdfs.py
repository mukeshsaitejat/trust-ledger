"""
Generate a perfectly-matched set of 3 PDFs that score MINIMAL risk
when verified through the InvoiceShield backend.

Key rules:
  - Amount uses $  prefix (no space before digits) — PyMuPDF Helvetica renders $ fine
  - PO reference matches exactly across invoice & delivery receipt
  - Supplier name matches exactly across all 3 docs
  - Quantity invoiced == delivered quantity

Output: InvoiceShield_Synthetic_Test_PDFs/low_risk_demo/
"""

import fitz
import time
from pathlib import Path

OUTPUT_DIR = Path("InvoiceShield_Synthetic_Test_PDFs/low_risk_demo")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Shared constants ──────────────────────────────────────────────────────────
# Use a timestamp-based suffix so it's unique every run (avoids duplicate detection)
_SUFFIX        = str(int(time.time()))[-4:]
INVOICE_NUMBER = f"INV-2026-{_SUFFIX}"
PO_NUMBER      = f"PO-2026-{_SUFFIX}"
SUPPLIER       = "Apex Supplies Ltd"
BUYER          = "GlobalTech Corp"
AMOUNT_NUM     = "50000.00"
AMOUNT         = f"${AMOUNT_NUM}"    # $ immediately before digits (ASCII, font-safe)
QUANTITY       = "100"
UNIT_PRICE     = "$500.00"
INVOICE_DATE   = "10/01/2026"
PO_DATE        = "09/25/2026"
DELIVERY_DATE  = "10/05/2026"
DESCRIPTION    = "Industrial Grade Steel Pipes"
DR_NUMBER      = f"DR-2026-{_SUFFIX}"


def make_pdf(path: Path, lines: list) -> None:
    doc  = fitz.open()
    page = doc.new_page(width=595, height=842)
    y    = 60

    for line in lines:
        if line == "---":
            page.draw_line(fitz.Point(40, y), fitz.Point(555, y),
                           color=(0.6, 0.6, 0.6), width=0.5)
            y += 12
        elif line.startswith("##"):
            page.insert_text(fitz.Point(40, y), line[2:].strip(),
                             fontsize=18, fontname="helv",
                             color=(0.06, 0.27, 0.55))
            y += 30
        elif line.startswith("#"):
            page.insert_text(fitz.Point(40, y), line[1:].strip(),
                             fontsize=11, fontname="hebo",
                             color=(0.1, 0.1, 0.1))
            y += 20
        elif line == "":
            y += 8
        else:
            page.insert_text(fitz.Point(40, y), line,
                             fontsize=10, fontname="helv",
                             color=(0.2, 0.2, 0.2))
            y += 15

    doc.save(str(path))
    doc.close()
    print(f"  Created: {path}")


# ── 1. INVOICE ────────────────────────────────────────────────────────────────
invoice_lines = [
    "## INVOICE",
    "---",
    f"# Invoice Number : {INVOICE_NUMBER}",
    f"  Invoice Date   : {INVOICE_DATE}",
    "",
    "---",
    "# Supplier Details",
    f"  Supplier Name  : {SUPPLIER}",
    f"  Address        : 12 Commerce Street, Mumbai 400001",
    "",
    "# Buyer Details",
    f"  Buyer Name     : {BUYER}",
    f"  Address        : 8 Innovation Park, Bengaluru 560001",
    "",
    "---",
    "# Order Details",
    f"  PO Reference   : {PO_NUMBER}",
    f"  Description    : {DESCRIPTION}",
    f"  Quantity       : {QUANTITY} units",
    f"  Unit Price     : {UNIT_PRICE} per unit",
    "",
    "---",
    f"# Total Amount : {AMOUNT}",
    "",
    "  Payment Terms  : Net 30 days",
    "  Bank Account   : HDFC Bank, IFSC HDFC0001234",
    "",
    "  Authorized Signatory: ___________________",
]
make_pdf(OUTPUT_DIR / "invoice.pdf", invoice_lines)


# ── 2. PURCHASE ORDER ─────────────────────────────────────────────────────────
po_lines = [
    "## PURCHASE ORDER",
    "---",
    f"# Purchase Order Number : {PO_NUMBER}",
    f"  PO Date               : {PO_DATE}",
    "",
    "---",
    "# Supplier",
    f"  Supplier Name  : {SUPPLIER}",
    f"  Address        : 12 Commerce Street, Mumbai 400001",
    "",
    "# Buyer",
    f"  Buyer Name     : {BUYER}",
    f"  Address        : 8 Innovation Park, Bengaluru 560001",
    "",
    "---",
    "# Item Details",
    f"  Description    : {DESCRIPTION}",
    f"  Quantity       : {QUANTITY} units",
    f"  Unit Price     : {UNIT_PRICE} per unit",
    "",
    "---",
    f"# Total Amount : {AMOUNT}",
    "",
    "  Delivery By    : 10/07/2026",
    "  Terms          : FOB Destination",
    "",
    "  Authorized By: ___________________",
]
make_pdf(OUTPUT_DIR / "purchase_order.pdf", po_lines)


# ── 3. DELIVERY RECEIPT ───────────────────────────────────────────────────────
dr_lines = [
    "## DELIVERY RECEIPT",
    "---",
    f"# Receipt Number  : {DR_NUMBER}",
    f"  Delivery Date   : {DELIVERY_DATE}",
    "",
    "---",
    "# Supplier",
    f"  Supplier Name   : {SUPPLIER}",
    "",
    "# Delivered To",
    f"  Buyer Name      : {BUYER}",
    f"  Address         : 8 Innovation Park, Bengaluru 560001",
    "",
    "---",
    "# Order Reference",
    f"  PO Reference    : {PO_NUMBER}",
    f"  Description     : {DESCRIPTION}",
    "",
    "---",
    f"  Delivered : {QUANTITY} units",
    "",
    "  Condition      : Good - no damage observed",
    "  Received By    : ___________________",
    "  Driver Sign    : ___________________",
]
make_pdf(OUTPUT_DIR / "delivery_receipt.pdf", dr_lines)


print()
print("=" * 55)
print("  PDFs ready in:", OUTPUT_DIR)
print("=" * 55)

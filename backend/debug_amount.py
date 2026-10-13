import fitz, re

doc = fitz.open('InvoiceShield_Synthetic_Test_PDFs/low_risk_demo/invoice.pdf')
text = doc[0].get_text()
doc.close()

print("--- RAW TEXT ---")
print(repr(text))
print()

# Exact patterns from pdf_extractor.py
patterns = [
    r"(?:Total|Amount|Grand\s+Total)\s*:?\s*[$₹€£¥I]\s*([\d,]+\.?\d*)",
    r"Amount\s*:?\s*\n?\s*[$₹€£¥I]\s*([\d,]+\.?\d*)",
    r"(?:Total|Amount)\s*[$₹€£¥I]?\s*([\d,]+\.?\d*)",
    r"[$₹€£¥I]\s*([\d,]+\.?\d*)\s*(?:Total|USD|INR|EUR)"
]

for i, p in enumerate(patterns):
    m = re.search(p, text, re.IGNORECASE)
    result = m.group(0) if m else "NO MATCH"
    print(f"Pattern {i}: {result}")

# Also check what ₹ looks like as bytes
print()
print("₹ ord:", ord('₹'), hex(ord('₹')))
for char in text:
    if ord(char) > 127:
        print(f"  non-ascii char: {repr(char)}  ord={ord(char)}  hex={hex(ord(char))}")

"""
Test script: Upload the low-risk PDF set and verify the risk score.
Run: python test_low_risk.py
"""
import requests
from pathlib import Path

BASE = "http://localhost:8000"
DIR  = Path("InvoiceShield_Synthetic_Test_PDFs/low_risk_demo")

def upload(filepath: Path, doc_type: str) -> str:
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE}/documents/upload",
            files={"file": (filepath.name, f, "application/pdf")},
            data={"document_type": doc_type},
        )
    resp.raise_for_status()
    doc_id = resp.json()["document_id"]
    print(f"  Uploaded {filepath.name}  →  {doc_id}")
    return doc_id

print("── Uploading documents ───────────────────────────")
inv_id = upload(DIR / "invoice.pdf",          "invoice")
po_id  = upload(DIR / "purchase_order.pdf",   "purchase_order")
dr_id  = upload(DIR / "delivery_receipt.pdf", "delivery_receipt")

print("\n── Running verification ──────────────────────────")
resp = requests.post(f"{BASE}/invoices/verify", json={
    "invoice_id": inv_id,
    "po_id":      po_id,
    "delivery_receipt_id": dr_id,
})
resp.raise_for_status()
v = resp.json()
print(f"  Status     : {v['comparison_result']['status']}")
print(f"  Findings   : {v['comparison_result']['findings_count']}")
print(f"  Critical   : {v['comparison_result']['critical_count']}")
if v["comparison_result"]["findings"]:
    for f in v["comparison_result"]["findings"]:
        print(f"    ⚠  [{f['severity']}] {f['finding_type']}: {f['message']}")

print("\n── Risk assessment ───────────────────────────────")
risk = requests.get(f"{BASE}/invoices/{inv_id}/risk").json()
print(f"  Risk Score      : {risk['risk_score']}")
print(f"  Risk Level      : {risk['risk_level']}")
print(f"  Recommendation  : {risk['financing_recommendation']}")
print(f"  Reason          : {risk['recommendation_reason']}")

print()
if risk["risk_level"] in ("MINIMAL", "LOW"):
    print("✅  SUCCESS — LOW / MINIMAL RISK achieved!")
else:
    print(f"⚠   Risk level is {risk['risk_level']} — check findings above.")

print(f"\n  Invoice ID for frontend: {inv_id}")
print(f"  Open: http://localhost:5173/invoices/{inv_id}")

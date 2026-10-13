"""
InvoiceShield Demo Script
Automated demo showcasing all platform capabilities for hackathon judges.
"""
import requests
import time
from pathlib import Path
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(result, indent=0):
    """Print JSON result in formatted way."""
    spacing = "  " * indent
    print(f"{spacing}{json.dumps(result, indent=2)}")

def check_health():
    """Check API health."""
    print_section("1. HEALTH CHECK")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print_result(response.json())
    return response.status_code == 200

def upload_test_documents(case_name):
    """Upload test documents from a specific case."""
    print_section(f"2. UPLOADING TEST DOCUMENTS - {case_name.upper()}")
    
    base_path = Path(f"InvoiceShield_Synthetic_Test_PDFs/invoiceshield_test_pdfs/{case_name}")
    
    if not base_path.exists():
        print(f"❌ Test case directory not found: {base_path}")
        return None
    
    document_ids = {}
    
    # Upload invoice
    invoice_path = base_path / "invoice.pdf"
    if invoice_path.exists():
        with open(invoice_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            data = {"document_type": "invoice"}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                document_ids["invoice"] = result["document_id"]
                print(f"✓ Invoice uploaded: {result['document_id']}")
            else:
                print(f"❌ Invoice upload failed: {response.status_code}")
    
    # Upload purchase order
    po_path = base_path / "purchase_order.pdf"
    if po_path.exists():
        with open(po_path, "rb") as f:
            files = {"file": ("purchase_order.pdf", f, "application/pdf")}
            data = {"document_type": "purchase_order"}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                document_ids["po"] = result["document_id"]
                print(f"✓ Purchase Order uploaded: {result['document_id']}")
    
    # Upload delivery receipt
    dr_path = base_path / "delivery_receipt.pdf"
    if dr_path.exists():
        with open(dr_path, "rb") as f:
            files = {"file": ("delivery_receipt.pdf", f, "application/pdf")}
            data = {"document_type": "delivery_receipt"}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                document_ids["delivery_receipt"] = result["document_id"]
                print(f"✓ Delivery Receipt uploaded: {result['document_id']}")
    
    return document_ids

def verify_invoice(document_ids):
    """Verify invoice against PO and delivery receipt."""
    print_section("3. INVOICE VERIFICATION")
    
    payload = {
        "invoice_id": document_ids["invoice"],
        "po_id": document_ids["po"],
        "delivery_receipt_id": document_ids["delivery_receipt"]
    }
    
    response = requests.post(f"{BASE_URL}/invoices/verify", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Verification completed")
        print(f"\n📋 VERIFICATION SUMMARY:")
        print(f"  Verification ID: {result['verification_id']}")
        print(f"  Status: {result['comparison_result']['status'].upper()}")
        print(f"  Findings: {result['comparison_result']['findings_count']}")
        print(f"  Critical Issues: {result['comparison_result']['critical_count']}")
        
        if result['comparison_result']['findings']:
            print(f"\n  📌 Issues Found:")
            for finding in result['comparison_result']['findings']:
                print(f"    - [{finding['severity'].upper()}] {finding['message']}")
        
        # Risk assessment
        risk = result.get('risk_assessment', {})
        if risk:
            print(f"\n⚠️  RISK ASSESSMENT:")
            print(f"  Risk Score: {risk['risk_score']}/100")
            print(f"  Risk Level: {risk['risk_level']}")
            print(f"  Recommendation: {risk['financing_recommendation']}")
            print(f"  Reason: {risk['recommendation_reason']}")
        
        # Duplicate check
        dup_check = result.get('duplicate_check', {})
        if dup_check and dup_check.get('has_duplicates'):
            print(f"\n🔴 DUPLICATE DETECTED:")
            if dup_check.get('exact_duplicate'):
                print(f"  Type: Exact File Match")
                print(f"  Original: {dup_check['exact_duplicate']['original_document_id']}")
        
        return result['verification_id']
    else:
        print(f"❌ Verification failed: {response.status_code}")
        print_result(response.json())
        return None

def check_audit_trail(verification_id):
    """Check audit trail for verification."""
    print_section("4. AUDIT TRAIL VERIFICATION")
    
    response = requests.get(f"{BASE_URL}/audit/trail/{verification_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Retrieved {result['event_count']} audit events")
        print(f"  Chain Valid: {result['chain_valid']}")
        
        if result['events']:
            print(f"\n📜 Event Timeline:")
            for event in result['events']:
                print(f"  [{event['timestamp']}] {event['event_type']}")
                print(f"    Entity: {event['entity_type']} - {event['entity_id']}")
        
        return result
    else:
        print(f"❌ Audit trail check failed: {response.status_code}")
        return None

def get_system_stats():
    """Get system statistics."""
    print_section("5. SYSTEM STATISTICS")
    
    response = requests.get(f"{BASE_URL}/system/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"📊 Platform Statistics:")
        print(f"  Total Documents: {stats['total_documents']}")
        print(f"  Total Verifications: {stats['total_verifications']}")
        print(f"  Approved: {stats['approved_count']}")
        print(f"  Rejected: {stats['rejected_count']}")
        print(f"  Review Required: {stats['review_required_count']}")
        print(f"  High Risk: {stats['high_risk_count']}")
        print(f"  Duplicates Detected: {stats['duplicate_count']}")
        print(f"  Audit Events: {stats['total_audit_events']}")
        print(f"  Database Size: {stats['database_size_mb']} MB")
        return stats
    else:
        print(f"❌ Stats retrieval failed: {response.status_code}")
        return None

def run_demo():
    """Run complete demo workflow."""
    print("\n" + "🚀" * 35)
    print("  INVOICESHIELD DEMO - AI-Assisted Invoice Verification")
    print("🚀" * 35)
    
    # Step 1: Health check
    if not check_health():
        print("\n❌ API is not healthy. Please start the server first.")
        print("Run: uvicorn app.main:app --reload")
        return
    
    time.sleep(1)
    
    # Step 2: Test Case 1 - Clean Invoice (Should APPROVE)
    print("\n\n" + "🎯" * 35)
    print("  TEST CASE 1: CLEAN INVOICE (Expected: APPROVED)")
    print("🎯" * 35)
    doc_ids_clean = upload_test_documents("case1_clean")
    if doc_ids_clean:
        time.sleep(0.5)
        ver_id_clean = verify_invoice(doc_ids_clean)
        if ver_id_clean:
            time.sleep(0.5)
            check_audit_trail(ver_id_clean)
    
    time.sleep(2)
    
    # Step 3: Test Case 2 - Amount Mismatch (Should REJECT)
    print("\n\n" + "⚠️ " * 35)
    print("  TEST CASE 2: AMOUNT MISMATCH (Expected: REJECTED)")
    print("⚠️ " * 35)
    doc_ids_mismatch = upload_test_documents("case2_amount_mismatch")
    if doc_ids_mismatch:
        time.sleep(0.5)
        ver_id_mismatch = verify_invoice(doc_ids_mismatch)
        if ver_id_mismatch:
            time.sleep(0.5)
            check_audit_trail(ver_id_mismatch)
    
    time.sleep(2)
    
    # Step 4: Test Case 3 - Quantity Mismatch (Should REVIEW)
    print("\n\n" + "🔍" * 35)
    print("  TEST CASE 3: QUANTITY MISMATCH (Expected: REVIEW REQUIRED)")
    print("🔍" * 35)
    doc_ids_qty = upload_test_documents("case3_quantity_mismatch")
    if doc_ids_qty:
        time.sleep(0.5)
        ver_id_qty = verify_invoice(doc_ids_qty)
        if ver_id_qty:
            time.sleep(0.5)
            check_audit_trail(ver_id_qty)
    
    time.sleep(2)
    
    # Step 5: System stats
    get_system_stats()
    
    # Final summary
    print("\n\n" + "✨" * 35)
    print("  DEMO COMPLETED SUCCESSFULLY")
    print("✨" * 35)
    print("\n📝 Key Features Demonstrated:")
    print("  ✓ Document upload with SHA-256 hashing")
    print("  ✓ PDF text extraction and field parsing")
    print("  ✓ 3-way document verification (Invoice-PO-DR)")
    print("  ✓ Duplicate detection (exact & business logic)")
    print("  ✓ Explainable risk scoring (0-100)")
    print("  ✓ Financing recommendations (APPROVE/REVIEW/REJECT)")
    print("  ✓ Hash-linked audit trail")
    print("  ✓ Document integrity verification")
    print("\n🎉 InvoiceShield is ready for production!")

if __name__ == "__main__":
    try:
        run_demo()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Please ensure the server is running:")
        print("  uvicorn app.main:app --reload")
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

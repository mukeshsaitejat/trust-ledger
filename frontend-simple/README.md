# InvoiceShield Frontend

Simple, modern web interface for testing the InvoiceShield API.

## Features

✅ **Document Upload** - Upload invoice, PO, and delivery receipt PDFs  
✅ **Real-time Verification** - Instant invoice verification results  
✅ **Risk Visualization** - Colorful risk score meter and breakdown  
✅ **Live Statistics** - Real-time platform metrics  
✅ **Detailed Results** - View extracted fields and findings  
✅ **Duplicate Detection** - Visual warnings for duplicates  
✅ **Responsive Design** - Works on desktop and mobile  

## Quick Start

### Method 1: Using Python Server (Recommended)

1. **Start the backend** (in project root):
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Start the frontend** (in separate terminal):
   ```bash
   cd frontend
   python serve.py
   ```

3. **Browser opens automatically** at `http://localhost:3000`

### Method 2: Direct File Open

1. Start the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open `index.html` directly in your browser

**Note:** CORS is already configured in the backend to allow all origins.

## How to Use

### Step 1: Upload Documents
1. Click "Choose Invoice PDF" and select an invoice
2. Click "Choose PO PDF" and select a purchase order
3. Click "Choose Delivery Receipt PDF" and select a delivery receipt
4. Click "Upload All Documents"
5. Wait for success message with document IDs

### Step 2: Verify Invoice
1. After successful upload, the "Verify Invoice" button becomes active
2. Click "Verify Invoice"
3. Wait for verification results

### Step 3: Review Results
- **Status Badge**: Shows APPROVED, REJECTED, or REVIEW REQUIRED
- **Risk Score**: Visual meter showing 0-100 risk score
- **Risk Factors**: Breakdown of what contributed to the risk score
- **Duplicate Warnings**: Alerts if duplicate detected
- **Detailed Findings**: All issues found during verification
- **Extracted Data**: All fields extracted from each document

## Understanding Results

### Verification Status
- **APPROVED** (Green): Invoice is clean, safe to finance
- **REVIEW REQUIRED** (Yellow): Minor issues, manual review needed
- **REJECTED** (Red): Critical issues, do not finance

### Risk Levels
- **MINIMAL** (0-25): Low risk, safe to proceed
- **LOW** (26-50): Minor concerns, generally safe
- **MEDIUM** (51-75): Moderate risk, review recommended
- **HIGH** (76-100): High risk, reject or investigate

### Risk Factors
Each factor shows:
- **Factor name**: Type of issue detected
- **Score**: Points added to total risk score
- **Description**: What was found

## Test with Sample PDFs

Use the included test PDFs in `InvoiceShield_Synthetic_Test_PDFs/`:

```
InvoiceShield_Synthetic_Test_PDFs/
├── case1_clean/              # Should APPROVE
│   ├── invoice.pdf
│   ├── purchase_order.pdf
│   └── delivery_receipt.pdf
│
├── case2_amount_mismatch/    # Should REJECT
│   ├── invoice.pdf
│   ├── purchase_order.pdf
│   └── delivery_receipt.pdf
│
├── case3_quantity_mismatch/  # Should REVIEW
│   ├── invoice.pdf
│   ├── purchase_order.pdf
│   └── delivery_receipt.pdf
│
└── case4_supplier_mismatch/  # Should REJECT
    ├── invoice.pdf
    ├── purchase_order.pdf
    └── delivery_receipt.pdf
```

## Troubleshooting

### Backend Connection Error
- Make sure backend is running: `uvicorn app.main:app --reload`
- Backend should be at `http://localhost:8000`
- Check console for error messages

### CORS Issues
- If using direct file open, try the Python server method
- Backend has CORS enabled for all origins by default

### Upload Fails
- Make sure files are PDFs
- Check file size (should be reasonable)
- Check backend logs for errors

### Statistics Not Loading
- Backend might not be running
- Check browser console for errors
- Refresh the page

## Technology Stack

- **Pure HTML/CSS/JavaScript** - No frameworks needed
- **Fetch API** - For backend communication
- **CSS Grid** - Responsive layout
- **Modern CSS** - Gradients, animations, shadows

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## API Endpoints Used

- `GET /system/stats` - Live statistics
- `POST /documents/upload` - Upload documents
- `POST /invoices/verify` - Verify invoice
- `GET /invoices/{id}/risk` - Get risk assessment

## Development

To modify the frontend:
1. Edit `index.html`
2. Refresh browser to see changes
3. No build process needed!

## Tips for Demo

1. **Start with clean invoice** (case1) - Show it works perfectly
2. **Show amount mismatch** (case2) - Demonstrates validation
3. **Upload duplicate** - Show duplicate detection
4. **Watch live stats update** - Shows real-time tracking
5. **Explain risk factors** - Transparency in decision-making

## Screenshots

### Main Interface
- Split view: Upload on left, Verification on right
- Stats bar at top showing platform metrics
- Clean, modern design with purple gradient

### Results Display
- Color-coded status badges
- Visual risk meter with gradient colors
- Expandable detailed results
- Clear, readable findings

## Next Steps

For production deployment:
1. Add user authentication
2. Implement file previews
3. Add batch upload support
4. Create admin dashboard
5. Add export to PDF/Excel
6. Implement real-time notifications

## Support

For issues or questions:
1. Check backend logs
2. Check browser console
3. Verify backend is running on port 8000
4. Ensure PDFs are valid format

---

**Built for Synesis 26 FinTech Hackathon**  
*Simple, Fast, Effective* 🚀

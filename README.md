# FlowParse — Invoice Intelligence

A local Streamlit invoice-review workspace with a dark navy, electric-blue and purple dashboard inspired by the selected reference design.

## Run on Windows

1. Extract this ZIP to a folder such as `C:\FlowParse-New`.
2. Open PowerShell/VS Code terminal in that folder.
3. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Or double-click `run_app.bat` after installing requirements.

## Pages included

- Overview dashboard (live metrics from SQLite, date filter, processing chart, risk donut, workflow status bars, recent invoice table)
- Upload Invoice (PDF selectable-text extraction and rule-based validation)
- Documents (search/export)
- Validation Rules
- Exceptions (status updates and reviewer notes)
- Data Extraction
- History & Audit
- Batch Processing (CSV validation/export)
- API & Integration (current architecture notes)
- Settings (non-destructive financial what-if simulator)

## Data integrity and limitations

- `flowparse.db` is created beside `app.py`; the app does not seed fake invoice records.
- Dashboard KPIs and charts use saved database values. It does not claim ML confidence or validation-accuracy scores because those are not calculated in this starter.
- PDF extraction reads selectable text only; OCR for scanned PDFs is not included.
- Invoice checks are rule-based and do not independently verify GST tax rules, duplicate invoices, supplier master data, or payment authorization.
- This starter is for local testing; authentication and production security controls are not implemented.

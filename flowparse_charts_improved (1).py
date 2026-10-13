from __future__ import annotations



import json

import re

import sqlite3

import html

from datetime import datetime, date, timedelta

from decimal import Decimal, InvalidOperation

from pathlib import Path



import fitz

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

import streamlit as st



APP_DIR = Path(__file__).resolve().parent

DB_PATH = APP_DIR / "flowparse.db"



st.set_page_config(

    page_title="FlowParse | Invoice Intelligence",

    page_icon="🧾",

    layout="wide",

    initial_sidebar_state="expanded",

)



# --------------------------- THEME ---------------------------

st.markdown(r"""

<style>

@import url('https\://fonts.googleapis.com/css2?family=Inter:wght\@400;500;600;700;800&display=swap');

:root{--bg:#f5f8fc;--sidebar:#ffffff;--panel:#ffffff;--panel2:#f8faff;--border:#e2e8f0;--text:#14213d;--muted:#64748b;--blue:#416bff;--purple:#8063f6;--teal:#0d9488;--green:#059669;--yellow:#d97706;--red:#dc2626;}

html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif;}

.stApp{background:radial-gradient(ellipse at 68% 0%,rgba(35,70,133,.12),transparent 42%),var(--bg);color:var(--text)}

[data-testid="stHeader"]{display:none!important}

[data-testid="stToolbar"]{display:none!important}

#MainMenu{visibility:hidden}

footer{visibility:hidden}

[data-testid="stSidebar"]{background:var(--sidebar);border-right:1px solid #1a2940;min-width:252px!important;max-width:252px!important;width:252px!important}

[data-testid="stSidebarContent"]{width:252px!important}

[data-testid="stSidebar"] *{color:var(--text)}

[data-testid="stSidebar"] .block-container{padding:18px 14px 22px!important}

.block-container{max-width:1600px;padding-top:.55rem;padding-bottom:1rem;padding-left:1.65rem;padding-right:1.65rem}

h1,h2,h3,h4{color:var(--text);letter-spacing:-.45px}

h1{font-size:27px!important;line-height:1.18!important;font-weight:750!important}

h2{font-size:22px!important}

h3{font-size:16px!important}

p,label,[data-testid="stCaptionContainer"]{color:var(--muted)}

p{font-size:13px}

[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--border);border-radius:13px;padding:18px 20px}

[data-testid="stMetricLabel"]{color:var(--muted)}

[data-testid="stMetricValue"]{color:var(--text);font-weight:750}

[data-testid="stMetricDelta"]{font-size:12px}

.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:8px;border:1px solid #263957;background:#0d1c32;color:var(--text);font-weight:600;min-height:38px;font-size:13px}

.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button[kind="primary"]{background:linear-gradient(135deg,#426fff,#315ce7);border:1px solid #426fff;color:#fff}

.stButton>button:hover,.stDownloadButton>button:hover{border-color:#638aff;color:#fff}

[data-testid="stFileUploader"]{background:#09172a;border:1px dashed #344969;border-radius:12px;padding:12px}

[data-testid="stExpander"]{background:#09172a;border:1px solid var(--border);border-radius:12px}

[data-testid="stDataFrame"]{border:1px solid var(--border);border-radius:10px}

[data-testid="stTabs"] button{color:var(--muted)}

[data-testid="stAlert"]{border-radius:10px}

hr{border-color:var(--border)}

/* Sidebar navigation: blue active selection, no bright default radio dot. */

[data-testid="stSidebar"] [role="radiogroup"]{gap:5px}

[data-testid="stSidebar"] [role="radiogroup"] label{padding:8px 10px;border:1px solid transparent;border-radius:8px;background:transparent;min-height:36px;transition:background .12s ease}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#182f5b;border-color:#223f77;color:#8fb0ff}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:#91b2ff!important}

[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#101f38}

[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{display:none}

[data-testid="stSidebar"] [role="radiogroup"] label p{font-size:13px;font-weight:550}

.fp-brand{font-size:23px;font-weight:800;color:#f4f7ff;letter-spacing:-.8px;display:flex;align-items:center;gap:9px}

.fp-brand .logo{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1.5px solid #9ab4ff;border-radius:9px;color:#9ab4ff;font-size:17px;background:linear-gradient(145deg,#142a50,#0a172b)}

.fp-brand span{color:#8ba8ff}

.fp-sidebar-plan{background:linear-gradient(150deg,#0d1f38,#09172a);border:1px solid #1e304b;border-radius:12px;padding:14px;margin:18px 0 12px}

.fp-sidebar-user{border-top:1px solid #1a2940;padding-top:14px;margin-top:16px;display:flex;align-items:center;gap:9px}

.fp-avatar{width:34px;height:34px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:linear-gradient(140deg,#2d55d4,#172c64);color:white;font-weight:700;font-size:12px}

.fp-topbar{height:40px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #192941;padding-bottom:9px;margin-bottom:16px}

.fp-topmeta{color:#9baac5;background:#0a172a;border:1px solid #1b2b45;border-radius:8px;padding:9px 12px;font-size:12px;text-align:center;white-space:nowrap}

.fp-page-title{font-size:26px;line-height:1.16;font-weight:750;letter-spacing:-.75px;color:#f0f4ff;margin:1px 0 4px}

.fp-overline{font-size:12px;color:#a3b2cd;margin-bottom:4px}

.fp-subtitle{font-size:13px;color:#9baac5;line-height:1.45;margin:0}

.fp-kpi-card{height:122px;background:linear-gradient(145deg,#0c1b30,#091629);border:1px solid #1b2c46;border-radius:11px;padding:17px 18px;box-sizing:border-box;overflow:hidden}

.fp-kpi-top{display:flex;align-items:center;gap:12px;min-height:32px}

.fp-icon{display:inline-flex;align-items:center;justify-content:center;width:43px;height:43px;min-width:43px;border-radius:50%;font-size:21px;font-weight:700;color:#fff;background:rgba(64,105,255,.23);border:1px solid rgba(90,130,255,.17)}

.fp-icon.teal{background:rgba(17,197,176,.18);color:#39dcca}

.fp-icon.purple{background:rgba(128,99,246,.2);color:#ad98ff}

.fp-icon.red{background:rgba(255,117,134,.17);color:#ff97a5}

.fp-icon.gold{background:rgba(244,198,94,.17);color:#f4cd76}

.fp-kpi-label{font-size:12px;color:#a9b9d3;line-height:1.25;font-weight:500}

.fp-kpi-value{font-size:27px;font-weight:750;line-height:1.18;color:#f4f7ff;letter-spacing:-.7px;margin:7px 0 0 55px;white-space:nowrap}

.fp-kpi-foot{font-size:11px;color:#95a8c6;margin:5px 0 0 55px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.fp-kpi-foot .positive{color:#49d9ac}

.fp-panel{background:linear-gradient(150deg,#0a182b,#091629);border:1px solid #1c2d47;border-radius:11px;padding:17px 16px 13px;min-height:247px;box-sizing:border-box}

.fp-section{font-size:15px;font-weight:700;color:#f1f5ff;letter-spacing:-.25px;margin:0 0 4px}

.fp-subtle{font-size:11px;color:#93a7c7;line-height:1.4;margin-bottom:8px}

.fp-legend{font-size:11px;color:#aebdd5;line-height:1.7}

.fp-bars-label{display:flex;justify-content:space-between;gap:7px;margin:14px 0 6px;font-size:11px;color:#becae0}

.fp-track{height:9px;border-radius:99px;background:#142742;overflow:hidden;flex:1}

.fp-fill{height:100%;border-radius:99px}

.fp-table-panel{background:linear-gradient(150deg,#0a182b,#091629);border:1px solid #1c2d47;border-radius:11px;padding:16px 15px 10px;box-sizing:border-box}

.fp-table{width:100%;border-collapse:collapse;font-size:11px;color:#dce6f8;margin-top:9px}

.fp-table th{text-align:left;text-transform:uppercase;font-size:9px;letter-spacing:.55px;font-weight:600;color:#8fa4c4;background:#101f36;padding:12px 9px;border-bottom:1px solid #263955;white-space:nowrap}

.fp-table td{padding:12px 9px;border-bottom:1px solid #1b2b43;white-space:nowrap;vertical-align:middle}

.fp-table tr:last-child td{border-bottom:0}

.fp-table tbody tr:hover{background:#0e2039}

.fp-file{color:#8eaaff;font-size:16px;padding-right:5px}

.fp-status{display:inline-block;padding:4px 7px;border-radius:5px;font-size:10px;font-weight:650;white-space:nowrap}

.fp-status.resolved{background:rgba(17,197,176,.13);color:#4fddc8}

.fp-status.pending{background:rgba(66,111,255,.16);color:#9cb2ff}

.fp-status.escalated{background:rgba(255,117,134,.15);color:#ff9aa8}

.fp-risk.low{color:#45d7a8}.fp-risk.medium{color:#f4c65e}.fp-risk.high{color:#ff8494}.fp-risk.unknown{color:#9baac5}

.fp-table-link{font-size:12px;color:#7ea0ff;font-weight:600}

.fp-banner{background:linear-gradient(100deg,#eff6ff,#f8faff);border:1px solid #dbeafe;border-radius:11px;padding:15px 17px;display:flex;align-items:center;gap:12px;min-height:60px;box-sizing:border-box}

.fp-banner-icon{width:37px;height:37px;border-radius:50%;background:#dbeafe;border:1px solid #bfdbfe;display:flex;align-items:center;justify-content:center;font-size:18px;color:#2563eb;flex-shrink:0}

.fp-banner-title{font-size:13px;font-weight:700;color:#14213d}

.fp-banner-copy{font-size:11px;color:#64748b;margin-top:4px}

[data-testid="stProgressBar"] > div > div{background:linear-gradient(90deg,#426fff,#8063f6)}

input,textarea{color:var(--text)!important}

@media(max-width:1100px){.block-container{padding-left:1rem;padding-right:1rem}.fp-kpi-card{padding:13px;height:124px}.fp-kpi-value{font-size:22px;margin-left:0}.fp-kpi-foot{margin-left:0}.fp-icon{width:35px;height:35px;min-width:35px;font-size:18px}.fp-table{font-size:10px}.fp-table th,.fp-table td{padding:9px 6px}}



/* Professional light business theme overrides */

.stApp{background:#f5f8fc!important;color:#14213d!important}

[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #e2e8f0!important}

[data-testid="stSidebar"] *{color:#14213d!important}

h1,h2,h3,h4,.fp-page-title,.fp-section{color:#14213d!important}

p,label,[data-testid="stCaptionContainer"],.fp-subtitle,.fp-overline,.fp-subtle,.fp-kpi-label,.fp-kpi-foot,.fp-legend,.fp-bars-label{color:#64748b!important}

[data-testid="stMetric"],.fp-kpi-card,.fp-panel,.fp-table-panel,[data-testid="stExpander"],[data-testid="stFileUploader"]{background:#fff!important;border:1px solid #e2e8f0!important;box-shadow:0 2px 8px rgba(15,23,42,.035)!important}

.fp-kpi-value{color:#14213d!important}

.fp-brand,.fp-brand span{color:#14213d!important}

.fp-brand .logo{background:#eff6ff!important;color:#416bff!important;border-color:#bfdbfe!important}

.fp-sidebar-plan{background:#f8faff!important;border:1px solid #e2e8f0!important}

.fp-sidebar-user{border-top-color:#e2e8f0!important}

.fp-topbar{border-bottom-color:#e2e8f0!important}

.fp-topmeta{background:#f8fafc!important;border-color:#e2e8f0!important;color:#475569!important}

.fp-avatar{background:#e0e7ff!important;color:#3730a3!important}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#eff6ff!important;border-color:#dbeafe!important}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:#1d4ed8!important}

[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#f8fafc!important}

.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{background:#fff!important;border-color:#dbe3ef!important;color:#1e293b!important}

.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button[kind="primary"]{background:#416bff!important;color:#fff!important;border-color:#416bff!important}

hr{border-color:#e2e8f0!important}

.fp-track{background:#e9eef7!important}

.fp-table{color:#334155!important}

.fp-table th{background:#f8fafc!important;color:#475569!important}

.fp-table td{border-bottom-color:#edf2f7!important;color:#334155!important}


/* Final FlowParse light-theme refinements */
.fp-kpi-card,.fp-panel,.fp-table-panel{background:#fff!important;border:1px solid #e2e8f0!important;box-shadow:0 2px 8px rgba(15,23,42,.035)!important}
.fp-section{color:#14213d!important}
.fp-subtle,.fp-kpi-label,.fp-kpi-foot,.fp-legend,.fp-bars-label{color:#64748b!important}
.fp-table th{background:#f8fafc!important;color:#475569!important}
.fp-table td{color:#334155!important;border-bottom-color:#edf2f7!important}
.fp-table tbody tr:hover{background:#f8fafc!important}
.fp-track{background:#e9eef7!important}
.fp-banner-title{color:#14213d!important}
.fp-banner-copy{color:#64748b!important}
[data-testid="stFileUploader"] section{background:#fff!important}
@media(max-width:800px){.block-container{padding-left:.75rem!important;padding-right:.75rem!important}.fp-kpi-card{height:auto;min-height:112px}.fp-table{font-size:10px}}

</style>

""", unsafe_allow_html=True)



# --------------------------- DATABASE ---------------------------

def connect() -> sqlite3.Connection:

    conn = sqlite3.connect(DB_PATH, timeout=15)

    conn.row_factory = sqlite3.Row

    return conn





def init_db() -> None:

    with connect() as conn:

        conn.execute("""CREATE TABLE IF NOT EXISTS invoices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            created_at TEXT NOT NULL,

            invoice_number TEXT,

            supplier TEXT,

            invoice_total REAL NOT NULL DEFAULT 0,

            expected_total REAL NOT NULL DEFAULT 0,

            difference REAL NOT NULL DEFAULT 0,

            severity TEXT NOT NULL DEFAULT 'Low',

            status TEXT NOT NULL DEFAULT 'Pending review',

            exceptions TEXT NOT NULL DEFAULT '[]',

            extracted_text TEXT NOT NULL DEFAULT ''

        )""")

        conn.execute("""CREATE TABLE IF NOT EXISTS audit_log (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            created_at TEXT NOT NULL,

            invoice_id INTEGER,

            action TEXT NOT NULL,

            details TEXT DEFAULT '',

            reviewer_note TEXT DEFAULT ''

        )""")

        # Add missing fields to older FlowParse databases without deleting user data.

        existing = {r[1] for r in conn.execute("PRAGMA table_info(invoices)").fetchall()}

        migrations = {

            "created_at": "TEXT", "invoice_number": "TEXT", "supplier": "TEXT",

            "invoice_total": "REAL DEFAULT 0", "expected_total": "REAL DEFAULT 0",

            "difference": "REAL DEFAULT 0", "severity": "TEXT DEFAULT 'Low'",

            "status": "TEXT DEFAULT 'Pending review'", "exceptions": "TEXT DEFAULT '[]'",

            "extracted_text": "TEXT DEFAULT ''",

        }

        for col, ddl in migrations.items():

            if col not in existing:

                conn.execute(f'ALTER TABLE invoices ADD COLUMN "{col}" {ddl}')

        existing_audit = {r[1] for r in conn.execute("PRAGMA table_info(audit_log)").fetchall()}

        for col, ddl in {

            "created_at": "TEXT", "invoice_id": "INTEGER", "action": "TEXT",

            "details": "TEXT DEFAULT ''", "reviewer_note": "TEXT DEFAULT ''",

        }.items():

            if col not in existing_audit:

                conn.execute(f'ALTER TABLE audit_log ADD COLUMN "{col}" {ddl}')





def audit(invoice_id: int | None, action: str, details: str = "", note: str = "") -> None:

    with connect() as conn:

        cols = {r[1] for r in conn.execute("PRAGMA table_info(audit_log)").fetchall()}

        values = {

            "created_at": datetime.now().isoformat(timespec="seconds"),

            "invoice_id": invoice_id, "action": action, "details": details,

            "reviewer_note": note,

        }

        selected = {k: v for k, v in values.items() if k in cols}

        names = list(selected)

        conn.execute(

            f"INSERT INTO audit_log ({','.join(names)}) VALUES ({','.join('?' for _ in names)})",

            tuple(selected[n] for n in names),

        )





def load_invoices() -> pd.DataFrame:

    with connect() as conn:

        return pd.read_sql_query("SELECT * FROM invoices ORDER BY id DESC", conn)





def load_audit() -> pd.DataFrame:

    with connect() as conn:

        return pd.read_sql_query("SELECT * FROM audit_log ORDER BY id DESC", conn)





init_db()



# --------------------------- HELPERS ---------------------------

def money(value) -> str:

    try:

        return f"₹{float(value):,.2f}"

    except (TypeError, ValueError):

        return "₹0.00"





def dec(value) -> Decimal:

    try:

        cleaned = str(value if value is not None else "0").replace(",", "").replace("₹", "").strip()

        return Decimal(cleaned or "0")

    except (InvalidOperation, ValueError, TypeError):

        return Decimal("0")





def extract_pdf_text(upload) -> str:

    try:

        with fitz.open(stream=upload.getvalue(), filetype="pdf") as pdf:

            return "\n".join(page.get_text("text") for page in pdf).strip()

    except Exception as exc:

        st.error(f"Could not read PDF: {exc}")

        return ""





def extract_invoice_fields(text: str) -> dict[str, str]:

    
    patterns = {
        "invoice_number": [
            r"Invoice\s*(?:No\.?|Number|#)\s*[:#\-]?\s*([A-Za-z0-9/\-]+)",
            r"Bill\s*(?:No\.?|Number|#)\s*[:#\-]?\s*([A-Za-z0-9/\-]+)",
        ],
        "supplier": [
            r"Supplier\s*[:\-]\s*([^\n]+)",
            r"Vendor\s*[:\-]\s*([^\n]+)",
        ],
        "invoice_total": [
            r"(?:Grand\s+Total|Invoice\s+Total|Total\s+Amount|Net\s+Payable|Amount\s+Due)\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d{1,2})?)"
        ],
        "quantity": [
            r"Quantity\s*[:\-]?\s*([\d,]+(?:\.\d+)?)",
            r"Qty\s*[:\-]?\s*([\d,]+(?:\.\d+)?)",
        ],
        "rate": [
            r"(?:Unit\s+Price|Unit\s+Rate|Rate)\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d{1,2})?)"
        ],
        "gst": [
            r"GST(?:\s+Amount)?\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d{1,2})?)"
        ],
    }


    out = {key: "" for key in patterns}

    for key, candidates in patterns.items():

        for pattern in candidates:

            match = re.search(pattern, text, flags=re.IGNORECASE)

            if match:

                value = match.group(1).strip()

                out[key] = value[:100] if key == "supplier" else value

                break

    return out





def compare_invoice(invoice_quantity, invoice_rate, invoice_gst, invoice_total, po_quantity, po_rate) -> dict:

    iq, ir, gst, total, pq, pr = map(dec, [invoice_quantity, invoice_rate, invoice_gst, invoice_total, po_quantity, po_rate])

    expected = pq * pr + gst

    difference = total - expected

    exceptions = []

    checks = [

        ("Quantity mismatch", iq != pq, iq, pq, "Invoice quantity differs from purchase order quantity."),

        ("Unit rate mismatch", ir != pr, ir, pr, "Invoice unit rate differs from purchase order unit rate."),

        ("Invoice total mismatch", total > 0 and abs(difference) >= Decimal("0.01"), total, expected, "Invoice total differs from quantity × PO rate + entered GST."),

    ]

    for rule, failed, actual, expected_value, explanation in checks:

        if failed:

            delta = actual - expected_value

            exceptions.append({

                "rule": rule,

                "severity": "High" if rule in ("Quantity mismatch", "Unit rate mismatch") or (rule == "Invoice total mismatch" and abs(difference) >= Decimal("10000")) else "Medium",

                "invoice_value": str(actual), "expected_value": str(expected_value), "difference": str(delta),

                "explanation": f"{explanation} Actual: {actual}; expected: {expected_value}; difference: {delta}.",

            })

    severity = "High" if any(e["severity"] == "High" for e in exceptions) else ("Medium" if exceptions else "Low")

    return {"expected_total": float(expected), "difference": float(difference), "severity": severity, "exceptions": exceptions}





def save_invoice(invoice_number, supplier, invoice_total, result, extracted_text) -> int:

    with connect() as conn:

        cur = conn.execute("""INSERT INTO invoices

            (created_at, invoice_number, supplier, invoice_total, expected_total, difference, severity, status, exceptions, extracted_text)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",

            (datetime.now().isoformat(timespec="seconds"), invoice_number.strip(), supplier.strip(),

             float(invoice_total), result["expected_total"], result["difference"], result["severity"],

             "Pending review" if result["exceptions"] else "Resolved",

             json.dumps(result["exceptions"], ensure_ascii=False), extracted_text))

        record_id = int(cur.lastrowid)

    audit(record_id, "Invoice validated", f"Risk: {result['severity']}; exceptions: {len(result['exceptions'])}")

    return record_id





def safe_json(value) -> list:

    try:

        parsed = json.loads(value or "[]")

        return parsed if isinstance(parsed, list) else []

    except (json.JSONDecodeError, TypeError):

        return []





def page_title(title: str, subtitle: str) -> None:

    st.markdown(f"<h1 style='margin-bottom:.15rem'>{title}</h1><p style='margin-top:0'>{subtitle}</p>", unsafe_allow_html=True)





def make_plotly_dark(fig, height=300):

    fig.update_layout(

        height=height, paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",

        margin=dict(l=8, r=8, t=18, b=8), font=dict(family="Inter, sans-serif", color="#64748b", size=11),

        legend=dict(font=dict(color="#475569")),

    )

    return fig



# --------------------------- SIDEBAR ---------------------------

with st.sidebar:

    st.markdown("<div class='fp-brand'><span class='logo'>◈</span><span style='color:#f3f6ff'>Flow<span>Parse</span></span></div><div style='font-size:11px;color:#93a7c7;margin:5px 0 18px 41px;letter-spacing:.2px'>INVOICE INTELLIGENCE</div>", unsafe_allow_html=True)

    st.divider()

    pages = [

        "Overview", "Upload Invoice", "Documents", "Validation Rules", "Exceptions",

        "Data Extraction", "History & Audit", "Batch Processing", "API & Integration", "Settings",

    ]

    icons = {"Overview":"▦", "Upload Invoice":"↥", "Documents":"▤", "Validation Rules":"☷", "Exceptions":"⚠", "Data Extraction":"⌘", "History & Audit":"◷", "Batch Processing":"▱", "API & Integration":"⚿", "Settings":"⚙"}

    if "pending_page" in st.session_state:

        pending = st.session_state.pop("pending_page")

        if pending in pages:

            st.session_state["main_navigation"] = pending

    current_page = st.session_state.get("main_navigation", "Overview")

    if current_page not in pages:

        current_page = "Overview"

    page = st.radio("WORKSPACE", pages, index=pages.index(current_page), format_func=lambda p: f"{icons[p]}    {p}", label_visibility="collapsed", key="main_navigation")

    st.markdown("<div style='height:15px'></div><div class='fp-sidebar-plan'><div class='fp-kicker'>WORKSPACE</div><div style='font-size:14px;font-weight:700;color:#f0f4ff'>Local instance</div><div class='fp-foot'>SQLite storage · PDF extraction</div><div style='font-size:10px;color:#8095b5;margin-top:12px'>PRIVATE LOCAL WORKSPACE</div></div><div class='fp-sidebar-user'><span class='fp-avatar'>AD</span><div><div style='font-size:12px;font-weight:650;color:#ecf2ff'>Admin User</div><div style='font-size:10px;color:#93a7c7;margin-top:2px'>Local administrator</div></div></div>", unsafe_allow_html=True)



# --------------------------- OVERVIEW ---------------------------

if page == "Overview":

    df_all = load_invoices()



    # Reference-style top bar. Counts always come from SQLite; no demo metrics are fabricated.

    top_label, top_count, top_upload, top_admin = st.columns([5.7, 1.15, 1.05, .42], vertical_alignment="center", gap="small")

    with top_label:

        st.markdown("<div style='font-size:11px;color:#8095b7;letter-spacing:.45px;padding-top:8px'>FLOWPARSE <span style='color:#4b6fff'>/</span> WORKSPACE</div>", unsafe_allow_html=True)

    with top_count:

        st.markdown(f"<div class='fp-topmeta'>▣ &nbsp; {len(df_all):,} invoices</div>", unsafe_allow_html=True)

    with top_upload:

        if st.button("＋  Upload", type="primary", use_container_width=True, key="top_upload_invoice"):

            st.session_state["pending_page"] = "Upload Invoice"

            st.rerun()

    with top_admin:

        st.markdown("<div class='fp-avatar' style='margin:auto'>AD</div>", unsafe_allow_html=True)



    title_l, title_r = st.columns([3.7, 1.1], vertical_alignment="center")

    with title_l:

        st.markdown("<div class='fp-page-title'>Invoice Intelligence Dashboard</div><p class='fp-subtitle'>Monitor invoice processing, review workload and financial discrepancies.</p>", unsafe_allow_html=True)

    with title_r:

        period = st.selectbox("Date range", ["All time", "Last 30 days", "Last 7 days"], index=0, label_visibility="collapsed", key="overview_period")



    df = df_all.copy()

    if not df.empty and period != "All time":

        days = 30 if period == "Last 30 days" else 7

        timestamps = pd.to_datetime(df["created_at"], errors="coerce")

        cutoff = pd.Timestamp(datetime.now() - timedelta(days=days))

        df = df[timestamps >= cutoff].copy()



    total = len(df)

    if total:

        status_s = df["status"].fillna("Pending review")

        severity_s = df["severity"].fillna("Unknown")

        resolved = int((status_s == "Resolved").sum())

        open_count = int((status_s != "Resolved").sum())

        low_risk = int((severity_s == "Low").sum())

        high_count = int((severity_s == "High").sum())

        exposure = float(df.loc[status_s != "Resolved", "difference"].fillna(0).abs().sum())

        resolution_rate = resolved / total * 100

    else:

        status_s = pd.Series(dtype=str); severity_s = pd.Series(dtype=str)

        resolved = open_count = low_risk = high_count = 0

        exposure = resolution_rate = 0.0



    kcols = st.columns(4, gap="small")

    pending_count = int((status_s == "Pending review").sum()) if total else 0
    metric_cards = [
        ("Invoices Processed", f"{total:,}", "In selected period", "▤", "blue"),
        ("Resolved Invoices", f"{resolved:,}", f"{resolution_rate:.1f}% resolution rate", "✓", "teal"),
        ("Pending Review", f"{pending_count:,}", "Awaiting review", "◷", "purple"),
        ("Exceptions", f"{open_count:,}", f"Exposure: {money(exposure)}", "⚠", "red"),
    ]

    for col, (label, value, foot, icon, color) in zip(kcols, metric_cards):
        with col:
            st.markdown(f"<div class='fp-kpi-card'><div class='fp-kpi-top'><span class='fp-icon {color}'>{icon}</span><span class='fp-kpi-label'>{label}</span></div><div class='fp-kpi-value'>{value}</div><div class='fp-kpi-foot'>{foot}</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    chart_a, chart_b, chart_c = st.columns([1.12, 1, 1], gap="small")

    with chart_a:
        with st.container(border=True):
            st.markdown("<div class='fp-section'>Invoice Processing Trend</div><div class='fp-subtle'>Invoices saved by date</div>", unsafe_allow_html=True)
            if df.empty:
                st.info("No data available yet. Upload and save an invoice to see the trend.")
            else:
                tmp = df.copy()
                tmp["Date"] = pd.to_datetime(tmp["created_at"], errors="coerce").dt.date
                daily = tmp.dropna(subset=["Date"]).groupby("Date").size().reset_index(name="Invoices").sort_values("Date").tail(14)
                if daily.empty:
                    st.info("No valid processing dates are available in this period.")
                else:
                    fig = px.line(daily, x="Date", y="Invoices", markers=True, color_discrete_sequence=["#416fff"])
                    fig.update_traces(line=dict(width=3), marker=dict(size=8), hovertemplate="<b>%{x|%d %b %Y}</b><br>Invoices: %{y}<extra></extra>")
                    fig.update_xaxes(title=None, showgrid=False, tickformat="%b %d", color="#64748b", fixedrange=True, nticks=5)
                    fig.update_yaxes(title=None, rangemode="tozero", gridcolor="#edf2f7", color="#64748b", fixedrange=True, dtick=1 if daily["Invoices"].max() <= 10 else None)
                    fig.update_layout(margin=dict(l=4, r=8, t=12, b=4), showlegend=False)
                    st.plotly_chart(make_plotly_dark(fig, 250), use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with chart_b:
        with st.container(border=True):
            st.markdown("<div class='fp-section'>Validation Status</div><div class='fp-subtle'>Current invoice workflow</div>", unsafe_allow_html=True)
            if df.empty:
                st.info("No data available yet.")
            else:
                status_order = ["Resolved", "Pending review", "Escalated"]
                status_counts = df["status"].fillna("Pending review").value_counts()
                status_df = pd.DataFrame({"Status": status_order, "Invoices": [int(status_counts.get(x, 0)) for x in status_order]})
                status_df = status_df[status_df["Invoices"] > 0]
                status_colors = {"Resolved": "#13b8a6", "Pending review": "#8063f6", "Escalated": "#f06475"}
                fig = px.bar(status_df, x="Invoices", y="Status", orientation="h", text="Invoices", color="Status", color_discrete_map=status_colors, category_orders={"Status": status_order})
                fig.update_traces(textposition="outside", hovertemplate="%{y}: %{x} invoice(s)<extra></extra>")
                fig.update_xaxes(title=None, showgrid=True, gridcolor="#edf2f7", color="#64748b", rangemode="tozero", fixedrange=True)
                fig.update_yaxes(title=None, showgrid=False, color="#64748b", fixedrange=True, autorange="reversed")
                fig.update_layout(showlegend=False, margin=dict(l=4, r=12, t=10, b=4, pad=0), bargap=0.42)
                st.plotly_chart(make_plotly_dark(fig, 250), use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with chart_c:
        with st.container(border=True):
            st.markdown("<div class='fp-section'>Risk Distribution</div><div class='fp-subtle'>Invoices by rule-based risk level</div>", unsafe_allow_html=True)
            if df.empty:
                st.info("No data available yet. Risk distribution will appear after validation.")
            else:
                risk_counts = df["severity"].fillna("Unknown").value_counts()
                order = ["Low", "Medium", "High", "Unknown"]
                plot_df = pd.DataFrame({"Risk": order, "Invoices": [int(risk_counts.get(x, 0)) for x in order]})
                plot_df = plot_df[plot_df["Invoices"] > 0]
                colors = {"Low": "#13b8a6", "Medium": "#8063f6", "High": "#f06475", "Unknown": "#7486a6"}
                fig = px.bar(plot_df, x="Risk", y="Invoices", text="Invoices", color="Risk", color_discrete_map=colors, category_orders={"Risk": order})
                fig.update_traces(textposition="outside", hovertemplate="%{x}: %{y} invoice(s)<extra></extra>")
                fig.update_xaxes(title=None, showgrid=False, color="#64748b", fixedrange=True)
                fig.update_yaxes(title=None, rangemode="tozero", gridcolor="#edf2f7", color="#64748b", fixedrange=True, dtick=1 if plot_df["Invoices"].max() <= 10 else None)
                fig.update_layout(showlegend=False, margin=dict(l=4, r=8, t=10, b=4), bargap=0.38)
                st.plotly_chart(make_plotly_dark(fig, 250), use_container_width=True, config={"displayModeBar": False, "responsive": True})
                st.caption("Risk levels are based on configured validation rules, not machine-learning predictions.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    table_title, table_action = st.columns([4, 1], vertical_alignment="center")

    with table_title:

        st.markdown("<div class='fp-section' style='font-size:16px'>Recent Documents</div><div class='fp-subtle'>Latest invoice records saved in your FlowParse workspace</div>", unsafe_allow_html=True)

    with table_action:

        if st.button("View all documents  →", key="view_all_docs", use_container_width=True):

            st.session_state["pending_page"] = "Documents"; st.rerun()



    with st.container(border=True):

        if df.empty:

            st.info("No invoices in this date range. Upload a PDF to start building your invoice workspace.")

        else:

            recent = df.head(5).copy()

            headers = ["INVOICE NUMBER", "SUPPLIER", "INVOICE DATE", "TOTAL AMOUNT", "STATUS", "RISK", "DIFFERENCE", ""]

            html_rows = []

            for _, row in recent.iterrows():

                inv = html.escape(str(row.get("invoice_number") or f"INV-{int(row['id']):06d}"))

                supplier = html.escape(str(row.get("supplier") or "Unknown supplier"))

                stamp = pd.to_datetime(row.get("created_at"), errors="coerce")

                inv_date = stamp.strftime("%b %d, %Y") if pd.notna(stamp) else "—"

                amount = money(row.get("invoice_total"))

                diff = money(row.get("difference"))

                status = str(row.get("status") or "Pending review")

                status_cls = "resolved" if status == "Resolved" else ("escalated" if status == "Escalated" else "pending")

                severity = str(row.get("severity") or "Unknown")

                risk_cls = severity.lower() if severity.lower() in ("low", "medium", "high") else "unknown"

                action_icon = "◎"

                html_rows.append(f"<tr><td><span class='fp-file'>▤</span> {inv}</td><td>{supplier}</td><td>{inv_date}</td><td>{amount}</td><td><span class='fp-status {status_cls}'>{html.escape(status)}</span></td><td><span class='fp-risk {risk_cls}'>● &nbsp;{html.escape(severity)}</span></td><td>{diff}</td><td style='text-align:center;color:#7398ff;font-size:15px'>{action_icon}</td></tr>")

            header_html = "".join(f"<th>{h}</th>" for h in headers)

            table_html = f"<div style='overflow-x:auto'><table class='fp-table'><thead><tr>{header_html}</tr></thead><tbody>{''.join(html_rows)}</tbody></table></div>"

            st.markdown(table_html, unsafe_allow_html=True)



    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    banner_l, banner_r = st.columns([4.5, 1.05], vertical_alignment="center", gap="small")

    with banner_l:

        st.markdown("<div class='fp-banner'><div class='fp-banner-icon'>⬡</div><div><div class='fp-banner-title'>Smart validation, trusted results</div><div class='fp-banner-copy'>FlowParse highlights invoice discrepancies and keeps a review trail so you can verify records before payment decisions.</div></div></div>", unsafe_allow_html=True)

    with banner_r:

        if st.button("Configure Validation Rules  ›", key="configure_rules", type="primary", use_container_width=True):

            st.session_state["pending_page"] = "Validation Rules"; st.rerun()



# --------------------------- UPLOAD / VALIDATE ---------------------------

elif page == "Upload Invoice":

    page_title("Upload Invoice", "Extract invoice text, check key values and review potential discrepancies.")

    uploaded = st.file_uploader("Choose an invoice PDF", type=["pdf"], key="invoice_upload")

    if uploaded:

        text = extract_pdf_text(uploaded)

        if text:

            fields = extract_invoice_fields(text)

            st.success("Selectable PDF text extracted. Please verify extracted fields before validation.")

            with st.expander("Preview extracted PDF text"):

                st.text(text[:12000])

            with st.form("validate_invoice_form"):

                st.subheader("Invoice details")

                left, right = st.columns(2)

                with left:

                    invoice_number = st.text_input("Invoice number", value=fields["invoice_number"])

                    supplier = st.text_input("Supplier / Vendor", value=fields["supplier"])

                    invoice_quantity = st.number_input("Invoice quantity", min_value=0.0, value=float(dec(fields["quantity"])), step=1.0)

                    invoice_rate = st.number_input("Invoice unit rate (₹)", min_value=0.0, value=float(dec(fields["rate"])), step=100.0)

                with right:

                    invoice_total = st.number_input("Invoice total (₹)", min_value=0.0, value=float(dec(fields["invoice_total"])), step=100.0)

                    invoice_gst = st.number_input("GST amount (₹)", min_value=0.0, value=float(dec(fields["gst"])), step=10.0)

                    po_quantity = st.number_input("Purchase order quantity", min_value=0.0, value=float(dec(fields["quantity"])), step=1.0)

                    po_rate = st.number_input("Purchase order unit rate (₹)", min_value=0.0, value=float(dec(fields["rate"])), step=100.0)

                submitted = st.form_submit_button("Validate and save invoice", type="primary", use_container_width=True)

            if submitted:

                if invoice_total <= 0:

                    st.error("Enter an invoice total greater than zero.")

                else:

                    result = compare_invoice(invoice_quantity,invoice_rate,invoice_gst,invoice_total,po_quantity,po_rate)

                    invoice_id = save_invoice(invoice_number,supplier,invoice_total,result,text)

                    st.session_state["last_result"] = {"id":invoice_id,"result":result,"number":invoice_number}

                    st.success(f"Invoice validated and saved. Record ID: {invoice_id}")

            saved = st.session_state.get("last_result")

            if saved:

                result = saved["result"]

                st.subheader(f"Latest validation result · {saved['number'] or 'Invoice'}")

                c1,c2,c3 = st.columns(3)

                c1.metric("Expected total",money(result["expected_total"]))

                c2.metric("Invoice difference",money(result["difference"]))

                c3.metric("Risk level",result["severity"])

                if result["exceptions"]:

                    st.warning(f"{len(result['exceptions'])} exception(s) were found.")

                    for item in result["exceptions"]:

                        with st.expander(item["rule"]):

                            st.write(item["explanation"])

                else:

                    st.success("No discrepancies were detected by the current checks.")

                report={"invoice_id":saved["id"],"invoice_number":saved["number"],"validation":result,"generated_at":datetime.now().isoformat()}

                st.download_button("Download validation report (JSON)",json.dumps(report,indent=2,ensure_ascii=False),file_name=f"flowparse_report_{saved['id']}.json",mime="application/json")

        else:

            st.warning("No selectable text was found. Scanned PDFs need OCR, which is not included in this starter version.")



# --------------------------- DOCUMENTS ---------------------------

elif page == "Documents":

    page_title("Documents", "Search, inspect and export saved invoice records.")

    df=load_invoices()

    if df.empty: st.info("No saved documents yet. Upload an invoice PDF to begin.")

    else:

        q=st.text_input("Search by invoice number or supplier")

        filtered=df.copy()

        if q.strip():

            filtered=filtered[filtered["invoice_number"].fillna("").str.contains(q,case=False,na=False,regex=False)|filtered["supplier"].fillna("").str.contains(q,case=False,na=False,regex=False)]

        st.caption(f"{len(filtered)} document(s)")

        st.dataframe(filtered.drop(columns=["extracted_text","exceptions"],errors="ignore"),use_container_width=True,hide_index=True)

        st.download_button("Export documents (CSV)",filtered.to_csv(index=False).encode("utf-8"),file_name="flowparse_documents.csv",mime="text/csv")



# --------------------------- VALIDATION RULES ---------------------------

elif page == "Validation Rules":

    page_title("Validation Rules", "Understand the deterministic checks currently applied to invoice values.")

    rules=pd.DataFrame([

        {"Rule":"Quantity mismatch","Purpose":"Compares invoice quantity with PO quantity.","Behavior":"Flags unequal quantities as High risk."},

        {"Rule":"Unit rate mismatch","Purpose":"Compares invoice unit rate with PO unit rate.","Behavior":"Flags unequal unit rates as High risk."},

        {"Rule":"Invoice total mismatch","Purpose":"Compares total with PO quantity × PO rate + entered GST.","Behavior":"Flags differences of ₹0.01 or more; difference ≥ ₹10,000 is High risk."},

    ])

    st.dataframe(rules,use_container_width=True,hide_index=True)

    st.warning("These are rule-based checks, not proof of invoice correctness. GST rates, tax calculation, duplicate invoices and vendor master data are not independently verified.")



# --------------------------- EXCEPTIONS ---------------------------

elif page == "Exceptions":

    page_title("Exception Review", "Review flagged invoices, update workflow status and record notes.")

    df=load_invoices()

    if df.empty: st.info("No invoices are available for review.")

    else:

        unresolved=df[df["status"].fillna("Pending review")!="Resolved"]

        st.metric("Invoices requiring attention",len(unresolved))

        if unresolved.empty: st.success("No open invoice reviews.")

        for _,row in unresolved.iterrows():

            title=row["invoice_number"] or f"Invoice #{row['id']}"

            with st.expander(f"{title} · {row['severity']} risk · {money(row['difference'])}"):

                a,b,c=st.columns(3); a.metric("Supplier",row["supplier"] or "Not identified"); b.metric("Invoice total",money(row["invoice_total"])); c.metric("Difference",money(row["difference"]))

                for item in safe_json(row["exceptions"]):

                    st.markdown(f"**{item.get('rule','Exception')}** — {item.get('explanation','')}")

                statuses=["Pending review","Resolved","Escalated"]

                current=row["status"] if row["status"] in statuses else "Pending review"

                with st.form(f"review_form_{row['id']}"):

                    new_status=st.selectbox("Review status",statuses,index=statuses.index(current))

                    note=st.text_area("Reviewer note",placeholder="Record the reason or next action...")

                    save=st.form_submit_button("Save review",type="primary")

                if save:

                    with connect() as conn: conn.execute("UPDATE invoices SET status=? WHERE id=?",(new_status,int(row["id"])))

                    audit(int(row["id"]),"Review updated",f"Status changed to {new_status}",note)

                    st.success("Review saved."); st.rerun()



# --------------------------- DATA EXTRACTION ---------------------------

elif page == "Data Extraction":

    page_title("Data Extraction", "Preview fields found in selectable text from PDF invoices.")

    upload=st.file_uploader("Upload a PDF for extraction preview",type=["pdf"],key="extract_only")

    if upload:

        text=extract_pdf_text(upload)

        if text:

            st.subheader("Detected fields"); st.json(extract_invoice_fields(text))

            st.subheader("Extracted text"); st.text_area("PDF text",text,height=300)

            st.download_button("Download extracted text",text,file_name="extracted_invoice.txt",mime="text/plain")

        else: st.warning("No selectable text found in this PDF.")



# --------------------------- HISTORY & AUDIT ---------------------------

elif page == "History & Audit":

    page_title("History & Audit", "Explore invoice records and review actions tracked by FlowParse.")

    tab1,tab2=st.tabs(["Invoice History","Audit Events"])

    with tab1:

        df=load_invoices()

        if df.empty: st.info("No invoice history yet.")

        else:

            st.dataframe(df.drop(columns=["extracted_text"],errors="ignore"),use_container_width=True,hide_index=True)

            st.download_button("Download invoice history",df.to_csv(index=False).encode("utf-8"),file_name="flowparse_history.csv",mime="text/csv")

    with tab2:

        logs=load_audit()

        if logs.empty: st.info("No audit events recorded yet.")

        else:

            st.dataframe(logs,use_container_width=True,hide_index=True)

            st.download_button("Download audit log",logs.to_csv(index=False).encode("utf-8"),file_name="flowparse_audit.csv",mime="text/csv")



# --------------------------- BATCH PROCESSING ---------------------------

elif page == "Batch Processing":

    page_title("Batch Processing", "Run rule-based validation on a CSV of invoice values.")

    st.info("Required columns: invoice_quantity, invoice_rate, invoice_gst, invoice_total, po_quantity, po_rate. Batch outputs are downloadable and are not automatically added to invoice history.")

    batch_file=st.file_uploader("Choose invoice batch CSV",type=["csv"],key="batch_file")

    if batch_file:

        try:

            batch=pd.read_csv(batch_file); st.subheader("Input preview"); st.dataframe(batch.head(20),use_container_width=True,hide_index=True)

            required=["invoice_quantity","invoice_rate","invoice_gst","invoice_total","po_quantity","po_rate"]

            missing=[x for x in required if x not in batch.columns]

            if missing: st.error("Missing columns: "+", ".join(missing))

            elif st.button("Validate batch",type="primary"):

                rows=[]

                for i,row in batch.iterrows():

                    result=compare_invoice(*(row[x] for x in required))

                    rows.append({"row_number":int(i)+1,"invoice_total":row["invoice_total"],"expected_total":result["expected_total"],"difference":result["difference"],"severity":result["severity"],"exception_count":len(result["exceptions"]),"exceptions":json.dumps(result["exceptions"],ensure_ascii=False)})

                out=pd.DataFrame(rows); st.subheader("Validation results"); st.dataframe(out.drop(columns=["exceptions"]),use_container_width=True,hide_index=True)

                st.download_button("Download batch results (CSV)",out.to_csv(index=False).encode("utf-8"),file_name="flowparse_batch_results.csv",mime="text/csv")

        except Exception as exc: st.error(f"Unable to process CSV: {exc}")



# --------------------------- API & INTEGRATION ---------------------------

elif page == "API & Integration":

    page_title("API & Integration", "Current implementation and a safe path for future integrations.")

    st.subheader("Current architecture")

    st.code("Streamlit user interface\n        ↓\nPDF text extraction\n        ↓\nRule-based invoice validation\n        ↓\nSQLite invoice records + audit log",language="text")

    st.info("This starter runs locally in Streamlit. A production REST API, user authentication and payment automation are not implemented.")

    st.subheader("Example input")

    st.code('''invoice_data = {

    "invoice_quantity": 10,

    "invoice_rate": 500,

    "invoice_gst": 900,

    "invoice_total": 5900,

    "po_quantity": 10,

    "po_rate": 500,

}''',language="python")



# --------------------------- SETTINGS ---------------------------

elif page == "Settings":

    page_title("Settings", "Workspace configuration and a non-destructive financial scenario simulator.")

    left,right=st.columns(2)

    with left:

        st.markdown("<div class='fp-card'><div class='fp-kicker'>STORAGE</div><div style='font-size:18px;font-weight:700'>Local SQLite database</div><div class='fp-foot'>flowparse.db</div></div>",unsafe_allow_html=True)

    with right:

        st.markdown("<div class='fp-card'><div class='fp-kicker'>PROCESSING</div><div style='font-size:18px;font-weight:700'>PDF text + validation rules</div><div class='fp-foot'>Scanned PDF OCR is not included yet</div></div>",unsafe_allow_html=True)

    st.markdown("### Financial what-if simulator")

    st.caption("This simulation does not alter saved invoice records.")

    df=load_invoices()

    if df.empty:

        base_total,base_qty,base_rate,base_gst=0.0,1.0,0.0,0.0

        st.info("Save at least one invoice to load an example into this simulator.")

    else:

        ids=df["id"].tolist()

        chosen=st.selectbox("Choose a saved invoice",ids,format_func=lambda x:f"ID {x} · {df.loc[df['id']==x,'invoice_number'].iloc[0] or 'No invoice number'}")

        selected=df[df["id"]==chosen].iloc[0]

        base_total=float(selected["invoice_total"] or 0); base_qty=1.0; base_rate=base_total; base_gst=0.0

        detected=extract_invoice_fields(selected["extracted_text"] or "")

        base_qty=max(float(dec(detected["quantity"])),1.0); base_rate=float(dec(detected["rate"])); base_gst=float(dec(detected["gst"]))

    with st.form("sim_form"):

        a,b=st.columns(2)

        with a: q=st.number_input("Simulated quantity",min_value=0.0,value=float(base_qty),step=1.0); rate=st.number_input("Simulated unit rate (₹)",min_value=0.0,value=float(base_rate),step=100.0)

        with b: gst=st.number_input("Simulated GST (₹)",min_value=0.0,value=float(base_gst),step=10.0); total=st.number_input("Comparison invoice total (₹)",min_value=0.0,value=float(base_total),step=100.0)

        run=st.form_submit_button("Calculate scenario",type="primary")

    if run:

        expected=Decimal(str(q))*Decimal(str(rate))+Decimal(str(gst)); diff=Decimal(str(total))-expected

        a,b,c=st.columns(3); a.metric("Expected total",money(expected)); b.metric("Comparison total",money(total)); c.metric("Difference",money(diff))

        if abs(diff)>=Decimal("10000"): st.error("High-value difference in this scenario.")

        elif abs(diff)>=Decimal("0.01"): st.warning("A difference exists in this scenario.")

        else: st.success("No difference in this scenario.")

    st.markdown("### Operational safeguards")

    st.markdown("- Verify extracted values against the invoice.\n- Review exceptions before financial decisions.\n- Back up the local database.\n- Add authentication and role-based access before deploying to real users.\n- Consider OCR for scanned documents and a secured API for external integrations.")

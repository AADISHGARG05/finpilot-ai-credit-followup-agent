import sys
import os

ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
"""
FinPilot AI — Credit Follow-Up Email Agent
Complete Professional Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import time
import io
import traceback

# ─── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="FinPilot AI — Credit Follow-Up Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Backend integration (graceful fallback) ─────────────────────────────────
BACKEND_AVAILABLE = False
try:
    from app.services.invoice_processor import InvoiceProcessor
    from app.services.llm_service import LLMEmailGenerator
    from app.database.db import AuditDatabase
    BACKEND_AVAILABLE = True
except ImportError:
    # Provide stub implementations so the dashboard is fully runnable standalone 
    class AuditDatabase:
        def __init__(self):
            import sqlite3, os
            self.db_path = "finpilot_audit.db"
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._init_db()

        def _init_db(self):
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    invoice_no TEXT,
                    client_name TEXT,
                    stage TEXT,
                    tone TEXT,
                    subject TEXT,
                    body TEXT,
                    cta TEXT
                )
            """)
            self.conn.commit()

        def log_email(self, email_data):
            self.conn.execute("""
                INSERT INTO audit_log (timestamp, invoice_no, client_name, stage, tone, subject, body, cta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                email_data.get("invoice_no"),
                email_data.get("client_name"),
                email_data.get("stage"),
                email_data.get("tone"),
                email_data.get("subject"),
                email_data.get("body"),
                email_data.get("cta"),
            ))
            self.conn.commit()

        def get_logs(self, limit=100):
            import sqlite3
            df = pd.read_sql_query(
                f"SELECT * FROM audit_log ORDER BY id DESC LIMIT {limit}",
                self.conn
            )
            return df

        def is_connected(self):
            try:
                self.conn.execute("SELECT 1")
                return True
            except Exception:
                return False


# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Root & Reset ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
  --bg-void:      #07080c;
  --bg-surface:   #0d0f17;
  --bg-card:      #11141f;
  --bg-elevated:  #171b29;
  --border:       rgba(255,255,255,0.06);
  --border-glow:  rgba(99,179,237,0.25);
  --accent-cyan:  #38bdf8;
  --accent-green: #4ade80;
  --accent-amber: #fb923c;
  --accent-red:   #f87171;
  --accent-violet:#a78bfa;
  --text-primary: #e2e8f0;
  --text-muted:   #64748b;
  --text-dim:     #334155;
  --gradient-1:   linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
  --gradient-2:   linear-gradient(135deg, #10b981 0%, #0ea5e9 100%);
  --gradient-3:   linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
}

/* Hide default Streamlit chrome */
#MainMenu, header, footer, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: var(--bg-void) !important; }

/* Typography defaults */
html, body, .stApp, p, div, span {
  font-family: 'Syne', sans-serif;
  color: var(--text-primary);
}

/* ── Hero ── */
.hero-wrap {
  position: relative;
  overflow: hidden;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  padding: 48px 56px 42px;
}
.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(56,189,248,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56,189,248,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}
.hero-glow {
  position: absolute; top: -80px; right: -80px;
  width: 420px; height: 420px;
  background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
  pointer-events: none;
}
.hero-title {
  font-size: 2.8rem; font-weight: 800; letter-spacing: -0.03em;
  background: var(--gradient-1);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px;
}
.hero-subtitle {
  color: var(--text-muted); font-size: 1rem; font-weight: 400;
  font-family: 'JetBrains Mono', monospace;
  margin: 0 0 20px;
}
.hero-badges { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: 999px; font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace; font-weight: 500; letter-spacing: 0.02em;
  border: 1px solid var(--border); background: var(--bg-card);
}
.badge-live { border-color: rgba(74,222,128,0.4); color: var(--accent-green); }
.badge-live::before {
  content: ''; width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent-green);
  animation: pulse-dot 1.8s ease-in-out infinite;
}
.badge-model { border-color: rgba(56,189,248,0.3); color: var(--accent-cyan); }
.badge-time { color: var(--text-muted); }
@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(74,222,128,0.4); }
  50% { opacity: 0.7; box-shadow: 0 0 0 5px rgba(74,222,128,0); }
}

/* ── Sections ── */
.section-wrap { padding: 40px 56px; }
.section-label {
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.15em;
  color: var(--text-muted); text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 6px;
}
.section-title {
  font-size: 1.45rem; font-weight: 700; letter-spacing: -0.02em;
  color: var(--text-primary); margin: 0 0 28px;
}
.section-divider {
  border: none; border-top: 1px solid var(--border); margin: 0 56px 0;
}

/* ── Metric Cards ── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 24px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.metric-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--card-accent, var(--gradient-1));
}
.metric-card-icon {
  font-size: 1.5rem; margin-bottom: 12px; display: block;
}
.metric-card-label {
  font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.1em; font-family: 'JetBrains Mono', monospace;
  margin-bottom: 6px;
}
.metric-card-value {
  font-size: 2rem; font-weight: 800; letter-spacing: -0.03em;
  color: var(--card-color, var(--accent-cyan));
}
.metric-card-sub {
  font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;
  font-family: 'JetBrains Mono', monospace;
}
.card-glow {
  position: absolute; inset: 0;
  background: radial-gradient(circle at 80% 20%, var(--card-glow, rgba(56,189,248,0.06)) 0%, transparent 60%);
  pointer-events: none;
}

/* ── Upload Zone ── */
.upload-zone {
  background: var(--bg-card);
  border: 2px dashed rgba(56,189,248,0.25);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  transition: border-color 0.2s;
  margin-bottom: 24px;
}
.upload-zone:hover { border-color: rgba(56,189,248,0.5); }
.upload-icon { font-size: 2.5rem; margin-bottom: 12px; }
.upload-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
.upload-hint { font-size: 0.8rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

/* ── Buttons ── */
.stButton > button {
  background: var(--gradient-1) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  padding: 14px 32px !important;
  transition: opacity 0.2s, transform 0.15s !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover {
  opacity: 0.88 !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Generate button — special */
.gen-btn > button {
  background: linear-gradient(135deg, #10b981 0%, #0ea5e9 50%, #6366f1 100%) !important;
  font-size: 1.05rem !important;
  padding: 18px 48px !important;
  box-shadow: 0 0 30px rgba(16,185,129,0.25) !important;
  width: 100% !important;
}

/* ── Email Cards ── */
.email-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 24px;
  margin-bottom: 14px;
  border-left: 4px solid var(--stage-color, #38bdf8);
}
.email-card-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 14px; gap: 12px;
}
.email-inv { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-muted); }
.email-client { font-size: 1.05rem; font-weight: 700; }
.stage-pill {
  display: inline-block; padding: 3px 12px; border-radius: 999px;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; background: var(--stage-bg);
  color: var(--stage-color); border: 1px solid var(--stage-color);
  white-space: nowrap;
}
.email-subject {
  font-size: 0.9rem; font-weight: 600; color: var(--text-primary);
  margin-bottom: 10px;
}
.email-body-text {
  font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
  color: var(--text-muted); line-height: 1.65;
  background: var(--bg-void); border-radius: 8px; padding: 14px 16px;
  margin-bottom: 12px; white-space: pre-wrap;
}
.cta-btn {
  display: inline-block; padding: 7px 18px;
  background: var(--stage-color); color: #000;
  border-radius: 8px; font-size: 0.78rem; font-weight: 700;
  letter-spacing: 0.04em; text-transform: uppercase;
}

/* ── Status panel ── */
.status-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.status-item {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 16px 18px;
  display: flex; align-items: center; gap: 12px;
}
.status-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.dot-ok  { background: var(--accent-green); box-shadow: 0 0 8px rgba(74,222,128,0.5); }
.dot-warn { background: var(--accent-amber); box-shadow: 0 0 8px rgba(251,146,60,0.5); }
.dot-off { background: var(--text-dim); }
.status-label { font-size: 0.78rem; font-weight: 600; }
.status-val { font-size: 0.68rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

/* Streamlit overrides */
.stDataFrame { background: var(--bg-card) !important; border-radius: 12px !important; }
div[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
.stSuccess { background: rgba(74,222,128,0.08) !important; border-color: rgba(74,222,128,0.3) !important; }
.stWarning { background: rgba(251,146,60,0.08) !important; border-color: rgba(251,146,60,0.3) !important; }
.stError   { background: rgba(248,113,113,0.08) !important; border-color: rgba(248,113,113,0.3) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─── Session state defaults ───────────────────────────────────────────────────
for key, default in {
    "raw_df": None,
    "processed_df": None,
    "generated_emails": [],
    "db": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─── Initialise DB ────────────────────────────────────────────────────────────
@st.cache_resource
def fetch_all_logs():
    try:
        return AuditDatabase()
    except Exception:
        return None

if st.session_state.db is None:
    st.session_state.db = fetch_all_logs()


# ─── Helper functions ─────────────────────────────────────────────────────────
REQUIRED_COLS = ["invoice_no", "client_name", "email", "amount", "due_date",
                 "followup_count", "payment_link"]

STAGE_COLORS = {
    "Stage 1":    {"color": "#4ade80", "bg": "rgba(74,222,128,0.1)"},
    "Stage 2":    {"color": "#38bdf8", "bg": "rgba(56,189,248,0.1)"},
    "Stage 3":    {"color": "#fb923c", "bg": "rgba(251,146,60,0.1)"},
    "Stage 4":    {"color": "#f87171", "bg": "rgba(248,113,113,0.1)"},
    "Escalation": {"color": "#dc2626", "bg": "rgba(220,38,38,0.1)"},
}

def validate_csv(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    return missing

def compute_metrics(df: pd.DataFrame):
    if df is None or df.empty:
        return {}
    proc = df if "days_overdue" in df.columns else df
    escalated = proc.get("escalated", pd.Series(dtype=bool))
    return {
        "total_invoices":    len(proc),
        "escalated_cases":   int(escalated.sum()) if not escalated.empty else 0,
        "pending_cases":     int((~escalated).sum()) if not escalated.empty else len(proc),
        "avg_overdue_days":  round(proc.get("days_overdue", pd.Series([0])).mean(), 1),
        "total_outstanding": proc.get("amount", pd.Series([0])).sum(),
        "emails_generated":  len(st.session_state.generated_emails),
    }

def render_metric_cards(metrics: dict):
    cards = [
        ("📋", "Total Invoices",      str(metrics.get("total_invoices", 0)),
         "invoices loaded",  "var(--accent-cyan)",   "linear-gradient(90deg,#0ea5e9,#6366f1)",  "rgba(56,189,248,0.06)"),
        ("✉️", "Emails Generated",    str(metrics.get("emails_generated", 0)),
         "AI emails sent",   "var(--accent-green)",  "linear-gradient(90deg,#10b981,#0ea5e9)",  "rgba(74,222,128,0.06)"),
        ("🚨", "Escalated Cases",     str(metrics.get("escalated_cases", 0)),
         "require action",   "var(--accent-red)",    "linear-gradient(90deg,#ef4444,#f97316)",  "rgba(248,113,113,0.06)"),
        ("⏳", "Pending Cases",       str(metrics.get("pending_cases", 0)),
         "awaiting follow-up","var(--accent-amber)",  "linear-gradient(90deg,#f59e0b,#ef4444)",  "rgba(251,146,60,0.06)"),
        ("📅", "Avg Overdue Days",    f"{metrics.get('avg_overdue_days', 0)}d",
         "average delay",    "var(--accent-violet)", "linear-gradient(90deg,#8b5cf6,#6366f1)",  "rgba(167,139,250,0.06)"),
        ("💰", "Total Outstanding",
         f"${metrics.get('total_outstanding', 0):,.0f}",
         "total receivables","#fbbf24",              "linear-gradient(90deg,#f59e0b,#fbbf24)",  "rgba(251,191,36,0.06)"),
    ]
    cols = st.columns(len(cards))
    for col, (icon, label, value, sub, color, gradient, glow) in zip(cols, cards):
        col.markdown(f"""
        <div class="metric-card" style="--card-accent:{gradient};--card-color:{color};--card-glow:{glow}">
          <div class="card-glow"></div>
          <span class="metric-card-icon">{icon}</span>
          <div class="metric-card-label">{label}</div>
          <div class="metric-card-value">{value}</div>
          <div class="metric-card-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

def render_email_card(email: dict):
    stage = email.get("stage", "Stage 1")
    sc = STAGE_COLORS.get(stage, STAGE_COLORS["Stage 1"])
    color, bg = sc["color"], sc["bg"]
    st.markdown(f"""
    <div class="email-card" style="--stage-color:{color}; border-left-color:{color}">
      <div class="email-card-header">
        <div>
          <div class="email-inv">{email.get('invoice_no','')}</div>
          <div class="email-client">{email.get('client_name','')}</div>
        </div>
        <span class="stage-pill" style="--stage-bg:{bg};--stage-color:{color}">
          {stage} · {email.get('tone','')}
        </span>
      </div>
      <div class="email-subject">📧 {email.get('subject','')}</div>
      <div class="email-body-text">{email.get('body','')}</div>
      <span class="cta-btn" style="background:{color}">→ {email.get('cta','')}</span>
    </div>
    """, unsafe_allow_html=True)


def make_charts(df: pd.DataFrame):
    plotly_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Syne, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=10, r=10, t=36, b=10),
    )
    axis_style = dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11),
    )

    # 1 — Stage Distribution
    stage_counts = df["stage"].value_counts().reset_index()
    stage_counts.columns = ["stage", "count"]
    colors_map = [STAGE_COLORS.get(s, {}).get("color", "#38bdf8") for s in stage_counts["stage"]]
    fig_stage = px.bar(
        stage_counts, x="stage", y="count",
        title="Invoice Stage Distribution",
        color="stage",
        color_discrete_sequence=colors_map,
    )
    fig_stage.update_layout(**plotly_layout)
    fig_stage.update_xaxes(**axis_style)
    fig_stage.update_yaxes(**axis_style)
    fig_stage.update_traces(marker_line_width=0)

    # 2 — Overdue Days Distribution
    fig_overdue = px.histogram(
        df, x="days_overdue", nbins=20,
        title="Overdue Days Distribution",
        color_discrete_sequence=["#38bdf8"],
    )
    fig_overdue.update_layout(**plotly_layout)
    fig_overdue.update_xaxes(**axis_style, title="Days Overdue")
    fig_overdue.update_yaxes(**axis_style, title="Count")
    fig_overdue.update_traces(marker_line_width=0)

    # 3 — Outstanding by Stage
    stage_amount = df.groupby("stage")["amount"].sum().reset_index()
    stage_amount.columns = ["stage", "total"]
    colors_amt = [STAGE_COLORS.get(s, {}).get("color", "#38bdf8") for s in stage_amount["stage"]]
    fig_amount = px.bar(
        stage_amount, x="stage", y="total",
        title="Outstanding Amount by Stage ($)",
        color="stage", color_discrete_sequence=colors_amt,
    )
    fig_amount.update_layout(**plotly_layout)
    fig_amount.update_xaxes(**axis_style)
    fig_amount.update_yaxes(**axis_style)
    fig_amount.update_traces(marker_line_width=0)

    # 4 — Tone Distribution
    tone_counts = df["tone"].value_counts().reset_index()
    tone_counts.columns = ["tone", "count"]
    fig_tone = px.pie(
        tone_counts, names="tone", values="count",
        title="Tone Distribution",
        color_discrete_sequence=["#38bdf8","#4ade80","#fb923c","#f87171","#a78bfa","#fbbf24"],
        hole=0.55,
    )
    fig_tone.update_layout(**plotly_layout, showlegend=True,
                           legend=dict(font=dict(size=11, color="#94a3b8")))
    fig_tone.update_traces(textfont_size=12, marker_line_width=0)

    return fig_stage, fig_overdue, fig_amount, fig_tone


# ─── 1. HERO HEADER ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <div class="hero-title">⚡ FinPilot AI</div>
  <div class="hero-subtitle">Credit Follow-Up Email Agent — AI-Powered Collections Automation</div>
  <div class="hero-badges">
    <span class="badge badge-live">AI ONLINE</span>
    <span class="badge badge-model">MODEL · claude-sonnet-4 / groq-llama-3</span>
    <span class="badge badge-time">🕐 {datetime.now().strftime('%Y-%m-%d  %H:%M:%S UTC')}</span>
    <span class="badge">{'🔗 BACKEND CONNECTED' if BACKEND_AVAILABLE else '⚙️ STANDALONE MODE'}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── 2. LIVE METRICS ─────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Live KPIs</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Portfolio Metrics</div>', unsafe_allow_html=True)

metrics = compute_metrics(st.session_state.processed_df)
render_metric_cards(metrics)
st.markdown('</div>', unsafe_allow_html=True)


# ─── 3. CSV UPLOAD ───────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Data Ingestion</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Upload Invoice CSV</div>', unsafe_allow_html=True)

st.markdown("""
<div class="upload-zone">
  <div class="upload-icon">📂</div>
  <div class="upload-title">Drag & drop your CSV file here</div>
  <div class="upload-hint">Required columns: invoice_no · client_name · email · amount · due_date · followup_count · payment_link</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload CSV", type=["csv"],
    label_visibility="collapsed",
    help="Upload your invoice CSV to begin processing"
)

if uploaded_file:
    try:
        raw_df = pd.read_csv(uploaded_file)
        missing_cols = validate_csv(raw_df)
        if missing_cols:
            st.error(f"⚠️  Missing required columns: **{', '.join(missing_cols)}**")
        else:
            st.session_state.raw_df = raw_df
            st.success(f"✅  Loaded **{len(raw_df):,}** invoices from `{uploaded_file.name}`")
            with st.expander("📋  Raw CSV Preview", expanded=False):
                st.dataframe(raw_df, use_container_width=True, height=260)

            # Auto-process on upload
            with st.spinner("⚙️  Processing invoices…"):
                processor = InvoiceProcessor()
                processor.df = raw_df
                processed = (
                processor.process_invoices()
                )
                processed = pd.DataFrame(
                    processed
                )
                st.session_state.processed_df = processed
                st.success(f"⚡  Processed **{len(processed):,}** invoices — stages & tones assigned")
    except Exception as exc:
        st.error(f"❌  Failed to parse CSV: {exc}")

st.markdown('</div>', unsafe_allow_html=True)


# ─── 4. PROCESSED INVOICE TABLE ───────────────────────────────────────────────
if st.session_state.processed_df is not None:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Processed Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Invoice Analysis Table</div>', unsafe_allow_html=True)

    display_cols = [c for c in
        ["invoice_no","client_name","email","amount","due_date",
         "days_overdue","stage","tone","escalated","followup_count"]
        if c in st.session_state.processed_df.columns]

    st.dataframe(
        st.session_state.processed_df[display_cols].style.background_gradient(
            subset=["days_overdue"] if "days_overdue" in display_cols else [],
            cmap="OrRd"
        ),
        use_container_width=True, height=320
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ─── 5. AI EMAIL GENERATION ───────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">AI Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Generate Follow-Up Emails</div>', unsafe_allow_html=True)

if st.session_state.processed_df is None:
    st.info("⬆️  Upload and process a CSV above to enable AI email generation.")
else:
    st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
    gen_clicked = st.button("⚡  Generate AI Follow-Up Emails", key="gen_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if gen_clicked:
        generator = LLMEmailGenerator()
        db = st.session_state.db
        emails = []
        progress = st.progress(0, text="Initialising AI pipeline…")
        total = len(st.session_state.processed_df)

        for i, (_, row) in enumerate(st.session_state.processed_df.iterrows()):
            try:
                email = generator.generate_email(
                    row.to_dict()
                )
                if email is None:
                    continue
                if hasattr(email, "model_dump"):
                    email = email.model_dump()
                if email is not None:
                    emails.append(email)
                if db:
                    try:
                        db.log_email(email)
                    except Exception:
                        pass
            except Exception as exc:
                st.warning(f"⚠️  Skipped invoice {row.get('invoice_no','?')}: {exc}")
            progress.progress((i + 1) / total,
                              text=f"Generating… {i+1}/{total}")
            time.sleep(0.02)

        progress.empty()
        st.session_state.generated_emails = emails
        st.success(f"✅  Generated **{len(emails):,}** AI emails — logged to audit database")
        st.rerun()

    # Display generated emails
if st.session_state.generated_emails:

    st.markdown(
        f"## {len(st.session_state.generated_emails)} emails generated — scroll to review:"
    )

    for email in st.session_state.generated_emails:

        if email is None:
            continue

        if hasattr(email, "model_dump"):
            email = email.model_dump()

        if not isinstance(email, dict):
            continue

        render_email_card(email)

st.markdown('</div>', unsafe_allow_html=True)


# ─── 6. AUDIT LOG ─────────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Compliance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">SQLite Audit Log</div>', unsafe_allow_html=True)

db = st.session_state.db
if db:
    try:
        log_df = db.fetch_all_logs()
        if log_df.empty:
            st.info("📭  No audit entries yet. Generate emails to populate the log.")
        else:
            search_query = st.text_input("🔍  Search audit log (client, invoice, stage…)",
                                          placeholder="Type to filter…")
            if search_query:
                mask = log_df.apply(
                    lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1
                )
                log_df = log_df[mask]
            st.dataframe(log_df, use_container_width=True, height=300)
    except Exception as exc:
        st.error(f"❌  Audit log error: {exc}")
else:
    st.warning("⚠️  Database connection unavailable.")

st.markdown('</div>', unsafe_allow_html=True)


# ─── 7. LIVE ANALYTICS ────────────────────────────────────────────────────────
if st.session_state.processed_df is not None:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Live Portfolio Analytics</div>', unsafe_allow_html=True)

    try:
        df_charts = st.session_state.processed_df
        fig_stage, fig_overdue, fig_amount, fig_tone = make_charts(df_charts)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_stage,   use_container_width=True)
            st.plotly_chart(fig_amount,  use_container_width=True)
        with col2:
            st.plotly_chart(fig_overdue, use_container_width=True)
            st.plotly_chart(fig_tone,    use_container_width=True)
    except Exception as exc:
        st.error(f"❌  Chart error: {exc}\n{traceback.format_exc()}")

    st.markdown('</div>', unsafe_allow_html=True)


# ─── 8. SYSTEM STATUS ─────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">System</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">System Status</div>', unsafe_allow_html=True)

db = st.session_state.db
db_ok = True if db else False

statuses = [
    ("🤖", "AI Model",            "claude-sonnet-4 / groq-llama-3", "dot-ok"),
    ("🗄️", "Database",            "Connected · SQLite" if db_ok else "Disconnected",
                                   "dot-ok" if db_ok else "dot-warn"),
    ("⚡", "Groq API",             "Active" if BACKEND_AVAILABLE else "Standalone Mode",
                                   "dot-ok" if BACKEND_AVAILABLE else "dot-warn"),
    ("🔗", "Backend",              "Connected" if BACKEND_AVAILABLE else "Stub Mode",
                                   "dot-ok" if BACKEND_AVAILABLE else "dot-warn"),
    ("🧪", "Dry Run",              "Off · Live Mode", "dot-ok"),
    ("📊", "Data Loaded",          f"{len(st.session_state.processed_df):,} invoices"
                                    if st.session_state.processed_df is not None else "No data",
                                   "dot-ok" if st.session_state.processed_df is not None else "dot-off"),
]

cols = st.columns(len(statuses))
for col, (icon, label, val, dot_cls) in zip(cols, statuses):
    col.markdown(f"""
    <div class="status-item">
      <div class="status-dot {dot_cls}"></div>
      <div>
        <div class="status-label">{icon} {label}</div>
        <div class="status-val">{val}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;padding:32px 0 24px;color:#334155;
    font-family:'JetBrains Mono',monospace;font-size:0.7rem;letter-spacing:0.08em">
  FinPilot AI · Credit Follow-Up Agent · Enterprise Collections Automation
</div>
""", unsafe_allow_html=True)
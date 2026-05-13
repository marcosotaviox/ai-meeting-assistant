"""
ui/styles.py
=============
Custom CSS — Glassmorphic command centre aesthetic.
Neon cyan accents, deep navy background, translucent panels.
"""

import streamlit as st


def inject_custom_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

    /* ── Base ─────────────────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0a0f1e !important;
    }

    .main {
        background: radial-gradient(ellipse at 60% 20%, #0d1f3c 0%, #0a0f1e 60%, #000000 100%) !important;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    /* ── Sidebar ──────────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(0, 229, 255, 0.15) !important;
    }

    /* ── Glassmorphic panels ──────────────────────────────────────────────── */
    div[data-testid="metric-container"] {
        background: rgba(0, 229, 255, 0.05) !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.08),
                    inset 0 1px 0 rgba(255,255,255,0.05) !important;
        padding: 1rem !important;
    }

    div[data-testid="metric-container"] label {
        color: #00B0FF !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }

    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #00E5FF !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* ── Title ────────────────────────────────────────────────────────────── */
    .meetingmind-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.08em;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .meetingmind-title span {
        color: #00E5FF;
        text-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
    }

    .meetingmind-subtitle {
        text-align: center;
        color: #00B0FF;
        font-size: 0.82rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    /* ── Upload area ──────────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: rgba(0, 229, 255, 0.03) !important;
        border: 1px dashed rgba(0, 229, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    /* ── Action item card ─────────────────────────────────────────────────── */
    .action-card {
        background: rgba(0, 176, 255, 0.06);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-left: 3px solid #00E5FF;
        border-radius: 0 10px 10px 0;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.7rem;
        backdrop-filter: blur(8px);
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.05);
    }

    .action-owner {
        color: #00E5FF;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .action-deadline {
        color: #475569;
        font-size: 0.72rem;
        float: right;
    }

    .action-task {
        color: #CBD5E1;
        font-size: 0.88rem;
        margin-top: 0.3rem;
        line-height: 1.5;
    }

    /* ── Pills ────────────────────────────────────────────────────────────── */
    .pill-decision {
        display: block;
        background: rgba(0, 229, 255, 0.08);
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        color: #00E5FF;
        font-size: 0.83rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.06);
    }

    .pill-question {
        display: block;
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        color: #F59E0B;
        font-size: 0.83rem;
        margin-bottom: 0.5rem;
    }

    /* ── Section headers ──────────────────────────────────────────────────── */
    .section-header {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #00B0FF;
        margin-bottom: 0.8rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.15);
    }

    /* ── Summary box ──────────────────────────────────────────────────────── */
    .summary-box {
        background: rgba(0, 229, 255, 0.04);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        color: #CBD5E1;
        font-size: 0.9rem;
        line-height: 1.7;
        backdrop-filter: blur(8px);
    }

    /* ── Transcript box ───────────────────────────────────────────────────── */
    .transcript-box {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 229, 255, 0.1);
        border-radius: 10px;
        padding: 1.2rem;
        color: #64748B;
        font-family: 'Courier New', monospace;
        font-size: 0.80rem;
        line-height: 1.7;
        max-height: 280px;
        overflow-y: auto;
        white-space: pre-wrap;
    }

    /* ── Buttons ──────────────────────────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00E5FF, #00B0FF) !important;
        color: #0a0f1e !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.1em !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button {
        font-family: 'Rajdhani', sans-serif !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        color: #00E5FF !important;
        background: transparent !important;
    }

    /* ── Divider ──────────────────────────────────────────────────────────── */
    hr {
        border-color: rgba(0, 229, 255, 0.1) !important;
    }

    /* ── Scrollbar ────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(0, 229, 255, 0.2); border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)
"""
ui/styles.py
------------
Custom CSS injected into Streamlit for a polished game-tool aesthetic.
Theme: Dark tactical UI — inspired by esports analytics dashboards.
"""

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Google Font import ──────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500&display=swap');

        /* ── Root variables ─────────────────────────────────────────── */
        :root {
            --bg-primary:    #0b0e1a;
            --bg-secondary:  #0f1220;
            --bg-card:       #141828;
            --bg-input:      #1a1f2e;
            --border:        rgba(255,255,255,0.07);
            --border-accent: rgba(99,186,255,0.25);
            --text-primary:  #e0e6f0;
            --text-muted:    #7a8499;
            --accent-blue:   #63baff;
            --accent-teal:   #00e5c8;
            --accent-red:    #ff4d4d;
            --accent-gold:   #ffd700;
        }

        /* ── Global overrides ───────────────────────────────────────── */
        html, body, .stApp {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* ── Hide Streamlit chrome ──────────────────────────────────── */
        #MainMenu, footer, header { visibility: hidden; }
        .stDeployButton { display: none; }

        /* ── Header ─────────────────────────────────────────────────── */
        .app-header {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 18px 0 12px 0;
            border-bottom: 1px solid var(--border-accent);
            margin-bottom: 20px;
        }
        .app-logo { font-size: 2rem; }
        .app-title {
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--accent-blue);
            line-height: 1;
            text-transform: uppercase;
        }
        .app-subtitle {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            color: var(--text-muted);
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-top: 3px;
        }

        /* ── Sidebar ─────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: var(--bg-secondary) !important;
            border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: var(--accent-blue) !important;
            font-family: 'Rajdhani', sans-serif !important;
            letter-spacing: 0.06em;
        }
        .sidebar-section {
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 18px 0 6px 0;
            padding-bottom: 4px;
            border-bottom: 1px solid var(--border);
        }

        /* ── Select / input widgets ──────────────────────────────────── */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            background: var(--bg-input) !important;
            border: 1px solid var(--border-accent) !important;
            color: var(--text-primary) !important;
            border-radius: 4px !important;
        }
        .stSelectbox label, .stMultiSelect label,
        .stSlider label, .stCheckbox label,
        .stRadio label, .stFileUploader label {
            color: var(--text-primary) !important;
            font-size: 0.82rem !important;
        }

        /* ── Metric cards ────────────────────────────────────────────── */
        .metric-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 18px;
            min-width: 100px;
            flex: 1;
        }
        .metric-value {
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.7rem;
            font-weight: 700;
            color: var(--accent-blue);
            line-height: 1;
        }
        .metric-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.62rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-top: 2px;
        }

        /* ── Canvas card ─────────────────────────────────────────────── */
        .canvas-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 4px;
            overflow: hidden;
        }

        /* ── Section headings ────────────────────────────────────────── */
        .section-label {
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 6px;
        }

        /* ── Info / warning banners ──────────────────────────────────── */
        .stAlert {
            background: var(--bg-input) !important;
            border: 1px solid var(--border-accent) !important;
            color: var(--text-primary) !important;
            border-radius: 4px !important;
        }

        /* ── Slider ──────────────────────────────────────────────────── */
        .stSlider [data-baseweb="slider"] {
            margin-top: 4px;
        }
        div[data-testid="stSlider"] > div > div > div {
            background: var(--accent-teal) !important;
        }

        /* ── Tabs ────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-input) !important;
            border-radius: 6px 6px 0 0;
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Rajdhani', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em !important;
            color: var(--text-muted) !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            color: var(--accent-blue) !important;
            border-bottom: 2px solid var(--accent-blue) !important;
        }

        /* ── Plotly container ────────────────────────────────────────── */
        .js-plotly-plot .plotly .modebar {
            background: rgba(15,18,30,0.8) !important;
        }
        .js-plotly-plot .plotly .modebar-btn svg path {
            fill: var(--text-muted) !important;
        }

        /* ── Empty state ─────────────────────────────────────────────── */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 500px;
            color: var(--text-muted);
            font-family: 'Rajdhani', sans-serif;
            font-size: 1rem;
            letter-spacing: 0.06em;
            gap: 12px;
        }
        .empty-state-icon { font-size: 3rem; opacity: 0.4; }
        .empty-state-text { text-align: center; opacity: 0.6; }

        /* ── File uploader ───────────────────────────────────────────── */
        [data-testid="stFileUploader"] {
            border: 1px dashed var(--border-accent) !important;
            border-radius: 6px !important;
            background: var(--bg-input) !important;
        }

        /* ── Toggle / checkbox ───────────────────────────────────────── */
        .stCheckbox [data-testid="stMarkdownContainer"] p {
            font-size: 0.84rem !important;
            color: var(--text-primary) !important;
        }

        /* ── Divider ─────────────────────────────────────────────────── */
        hr { border-color: var(--border) !important; }

        /* ── Scrollbar ───────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb {
            background: var(--border-accent);
            border-radius: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

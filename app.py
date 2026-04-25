"""
Player Journey Visualization Tool — Lila Games
A Streamlit app for level designers to explore match telemetry.
"""

import streamlit as st
from pathlib import Path

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Player Journey · Lila Games",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.sidebar import render_sidebar
from ui.main_canvas import render_main_canvas
from ui.styles import inject_css


def main() -> None:
    inject_css()

    st.markdown(
        """
        <div class="app-header">
            <span class="app-logo">🎯</span>
            <div>
                <div class="app-title">Player Journey</div>
                <div class="app-subtitle">Match Telemetry Visualizer · Lila Games</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filters = render_sidebar()
    render_main_canvas(filters)


if __name__ == "__main__":
    main()

"""
ui/sidebar.py
-------------
Renders the left-hand sidebar with all filters and controls.
Returns a FilterState dict consumed by the main canvas.
"""

from __future__ import annotations
from typing import TypedDict, Optional

import streamlit as st
import pandas as pd

from core.data_loader import (
    get_available_dates,
    load_date_folder,
    load_uploaded_files,
    get_matches,
    get_maps,
)
from core.coords import known_maps


class FilterState(TypedDict):
    df: pd.DataFrame
    map_id: Optional[str]
    match_id: Optional[str]
    show_humans: bool
    show_bots: bool
    active_events: list[str]
    show_paths: bool
    heatmap_mode: str
    ts_max: Optional[float]
    ts_min: float


ALL_EVENT_TYPES = ["Kill", "BotKill", "Killed", "BotKilled", "KilledByStorm", "Loot"]


def render_sidebar() -> FilterState:
    with st.sidebar:
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:1.2rem;"
            "font-weight:700;color:#63baff;letter-spacing:0.08em;margin-bottom:4px;'>"
            "🗺 FILTERS</div>",
            unsafe_allow_html=True,
        )

        # ── Data source ───────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Data Source</div>", unsafe_allow_html=True)

        source_mode = st.radio(
            "Load from",
            ["📁 Folder (date)", "⬆ Upload files"],
            label_visibility="collapsed",
            horizontal=True,
        )

        df = pd.DataFrame()

        if "📁" in source_mode:
            dates = get_available_dates()
            if dates:
                selected_date = st.selectbox(
                    "Session date",
                    dates,
                    index=0,
                )
                with st.spinner("Loading telemetry…"):
                    df = load_date_folder(selected_date)
                if df.empty:
                    st.warning("No data found for this date.")
            else:
                st.info(
                    "No date folders found.\n\n"
                    "Place Parquet files in:\n```\ndata/YYYY-MM-DD/*.parquet\n```"
                )
        else:
            uploaded = st.file_uploader(
                "Upload .parquet files",
                type=["parquet"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )
            if uploaded:
                with st.spinner("Parsing files…"):
                    df = load_uploaded_files(uploaded)
                if df.empty:
                    st.warning("Could not parse uploaded files.")

        # ── Map filter ────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Map</div>", unsafe_allow_html=True)

        available_maps = get_maps(df)
        if not available_maps:
            available_maps = known_maps()

        map_id = st.selectbox(
            "Map",
            available_maps,
            index=0,
            label_visibility="collapsed",
        )

        # Filter df to selected map early (so matches list is relevant)
        map_df = df[df["map_id"] == map_id] if not df.empty and map_id else df

        # ── Match filter ──────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Match</div>", unsafe_allow_html=True)

        matches = get_matches(map_df)
        if matches:
            match_id = st.selectbox(
                "Match ID",
                matches,
                format_func=lambda x: x[:16] + "…" if len(x) > 16 else x,
                label_visibility="collapsed",
            )
        else:
            st.caption("No matches available.")
            match_id = None

        # Filter to match
        if match_id and not map_df.empty:
            match_df = map_df[map_df["match_id"] == match_id].copy()
        else:
            match_df = map_df.copy()

        # ── Players ───────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Players</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            show_humans = st.checkbox("Humans", value=True)
        with col2:
            show_bots = st.checkbox("Bots", value=True)

        # ── Events ────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Events</div>", unsafe_allow_html=True)

        active_events = st.multiselect(
            "Event types",
            ALL_EVENT_TYPES,
            default=ALL_EVENT_TYPES,
            label_visibility="collapsed",
        )

        # ── Visualisation ─────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Visualisation</div>", unsafe_allow_html=True)

        show_paths = st.checkbox("Show movement paths", value=True)

        heatmap_mode = st.selectbox(
            "Heatmap overlay",
            ["None", "movement", "kills"],
            format_func=lambda x: x.capitalize(),
        )

        # ── Timeline ──────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Timeline</div>", unsafe_allow_html=True)

        ts_min = 0.0
        ts_max_val = None

        if not match_df.empty:
            ts_values = match_df["ts_sec"].dropna()
            if len(ts_values) >= 2:
                ts_min = float(ts_values.min())
                ts_global_max = float(ts_values.max())
                total_sec = ts_global_max - ts_min

                if total_sec > 0:
                    slider_val = st.slider(
                        "Replay to (seconds)",
                        min_value=0,
                        max_value=int(total_sec),
                        value=int(total_sec),
                        step=max(1, int(total_sec // 100)),
                        format="%ds",
                        label_visibility="visible",
                    )
                    ts_max_val = ts_min + slider_val
                    mins = slider_val // 60
                    secs = slider_val % 60
                    st.caption(f"⏱ {mins:02d}:{secs:02d} / {int(total_sec//60):02d}:{int(total_sec%60):02d}")
                else:
                    ts_max_val = ts_global_max
            else:
                st.caption("Not enough time data for slider.")
        else:
            st.caption("No data loaded yet.")

        # ── Legend ────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-section'>Legend</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='font-size:0.75rem;line-height:2;'>
            <span style='color:#FF3B3B'>✕</span> Kill &nbsp;
            <span style='color:#FF8C00'>✕</span> Bot Kill<br>
            <span style='color:#111;background:#aaa;border-radius:50%;padding:1px 4px;font-size:0.6rem'>●</span> Death &nbsp;
            <span style='color:#9B59B6'>◆</span> Storm Death<br>
            <span style='color:#FFD700'>★</span> Loot
            </div>
            """,
            unsafe_allow_html=True,
        )

    return FilterState(
        df=match_df,
        map_id=map_id,
        match_id=match_id,
        show_humans=show_humans,
        show_bots=show_bots,
        active_events=active_events,
        show_paths=show_paths,
        heatmap_mode=heatmap_mode if heatmap_mode != "None" else None,
        ts_max=ts_max_val,
        ts_min=ts_min,
    )

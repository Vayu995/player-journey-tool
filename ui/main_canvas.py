"""
ui/main_canvas.py
-----------------
Renders the main content area: metrics row, map canvas, and event table.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.data_loader import filter_df
from core.chart_builder import build_journey_figure, compute_match_stats
from ui.sidebar import FilterState


def render_main_canvas(filters: FilterState) -> None:
    df = filters["df"]
    map_id = filters.get("map_id") or "AmbroseValley"

    # Apply all filters
    filtered = filter_df(
        df,
        map_id=None,          # already filtered in sidebar
        match_id=None,        # already filtered in sidebar
        show_humans=filters["show_humans"],
        show_bots=filters["show_bots"],
        event_types=filters["active_events"],
        ts_max=filters["ts_max"],
    )

    # ── Metrics row ────────────────────────────────────────────────────────
    stats = compute_match_stats(filtered)
    _render_metrics(stats, filters)

    # ── Tabs: Map | Data table ─────────────────────────────────────────────
    tab_map, tab_table, tab_help = st.tabs(["🗺 Map View", "📋 Event Log", "ℹ️ Help"])

    with tab_map:
        _render_map(filtered, filters, map_id)

    with tab_table:
        _render_event_table(filtered)

    with tab_help:
        _render_help()


# ── Private renderers ─────────────────────────────────────────────────────────

def _render_metrics(stats: dict, filters: FilterState) -> None:
    dur_min = stats["duration"] // 60
    dur_sec = stats["duration"] % 60

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value">{stats['players']}</div>
                <div class="metric-label">Players</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#63baff">{stats['humans']}</div>
                <div class="metric-label">Humans</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#8899bb">{stats['bots']}</div>
                <div class="metric-label">Bots</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#ff4d4d">{stats['kills']}</div>
                <div class="metric-label">Kills</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#ffd700">{stats['loots']}</div>
                <div class="metric-label">Loots</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#00e5c8">{dur_min:02d}:{dur_sec:02d}</div>
                <div class="metric-label">Duration</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_map(filtered: pd.DataFrame, filters: FilterState, map_id: str) -> None:
    if filtered.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🗺</div>
                <div class="empty-state-text">
                    No data to display.<br>
                    Load a date folder or upload Parquet files using the sidebar.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    with st.spinner("Rendering map…"):
        fig = build_journey_figure(
            df=filtered,
            map_id=map_id,
            show_paths=filters["show_paths"],
            show_events=bool(filters["active_events"]),
            active_events=filters["active_events"],
            heatmap_mode=filters.get("heatmap_mode"),
            ts_max=filters.get("ts_max"),
        )

    st.markdown("<div class='canvas-card'>", unsafe_allow_html=True)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
            "modeBarButtonsToAdd": ["toggleSpikelines"],
            "displaylogo": False,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"journey_{map_id}",
                "height": 1024,
                "width": 1024,
                "scale": 1,
            },
        },
        height=850,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Quick tip
    st.markdown(
        "<div style='font-size:0.7rem;color:#4a5568;margin-top:4px;text-align:right;'>"
        "Scroll to zoom · Drag to pan · Double-click to reset · Click legend to toggle layers"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_event_table(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        st.info("No events to display. Load data and select a match.")
        return

    POSITION_EVENTS = {"Position", "BotPosition"}
    event_df = filtered[~filtered["event"].isin(POSITION_EVENTS)].copy()

    if event_df.empty:
        st.info("No non-position events in the current selection.")
        return

    # Format for display
    display_cols = ["ts_sec", "event", "user_id", "is_human", "x", "z", "map_id"]
    available = [c for c in display_cols if c in event_df.columns]
    table = event_df[available].copy()

    table["ts_sec"] = table["ts_sec"].apply(
        lambda v: f"{int(v)//60:02d}:{int(v)%60:02d}" if pd.notna(v) else "—"
    )
    table["is_human"] = table["is_human"].apply(lambda v: "Human" if v else "Bot")
    table["x"] = table["x"].apply(lambda v: f"{v:.1f}" if pd.notna(v) else "—")
    table["z"] = table["z"].apply(lambda v: f"{v:.1f}" if pd.notna(v) else "—")

    table = table.rename(columns={
        "ts_sec": "Time",
        "event": "Event",
        "user_id": "Player ID",
        "is_human": "Type",
        "x": "X",
        "z": "Z",
        "map_id": "Map",
    })

    st.markdown(
        f"<div class='section-label'>Showing {len(table):,} events</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        table,
        use_container_width=True,
        height=500,
        hide_index=True,
    )

    # Download button
    csv = event_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Export CSV",
        data=csv,
        file_name="events_export.csv",
        mime="text/csv",
    )


def _render_help() -> None:
    st.markdown(
        """
        ### Getting Started

        **1. Load data**
        - Place Parquet files in `data/YYYY-MM-DD/*.parquet` (one file per player per match)
        - Or upload files directly via the sidebar

        **2. Select a match**
        - Choose a map, then pick a match ID from the dropdown
        - All players in that match will be shown

        **3. Explore the map**
        - Human paths are shown as solid lines, bots as dashed
        - Zoom with scroll, pan by dragging
        - Click legend entries to show/hide individual players or event types

        **4. Use the timeline**
        - Drag the sidebar slider to replay the match up to any point in time

        **5. Heatmaps**
        - Toggle movement or kill density heatmaps from the sidebar

        ---
        ### Expected Data Format

        | Column | Type | Notes |
        |--------|------|-------|
        | `user_id` | string | UUID = human, numeric = bot |
        | `match_id` | string | Groups players into matches |
        | `map_id` | string | AmbroseValley / GrandRift / Lockdown |
        | `x`, `y`, `z` | float | World coordinates |
        | `ts` | numeric/timedelta | Match-relative time |
        | `event` | bytes or string | Position, Kill, Loot… |

        ---
        ### Minimap Images

        Place 1024×1024 PNG files in `assets/minimaps/`:
        ```
        assets/minimaps/AmbroseValley.png
        assets/minimaps/GrandRift.png
        assets/minimaps/Lockdown.png
        ```
        The tool shows a placeholder grid when images are missing.
        """,
        unsafe_allow_html=True,
    )

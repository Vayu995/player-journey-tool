"""
core/chart_builder.py
---------------------
Builds Plotly figures from filtered telemetry data.
All rendering is done in minimap-pixel space (0–1024).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import base64

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from core.coords import add_pixel_coords, get_map_config

# ── Visual config ─────────────────────────────────────────────────────────────

MINIMAP_SIZE = 1024  # pixels

EVENT_STYLES: dict[str, dict] = {
    "Kill":          {"color": "#FF3B3B", "symbol": "x",          "size": 12, "label": "Kill"},
    "BotKill":       {"color": "#FF8C00", "symbol": "x",          "size": 10, "label": "Bot Kill"},
    "Killed":        {"color": "#111111", "symbol": "circle",     "size": 12, "label": "Death"},
    "BotKilled":     {"color": "#555555", "symbol": "circle",     "size": 10, "label": "Bot Death"},
    "KilledByStorm": {"color": "#9B59B6", "symbol": "diamond",    "size": 12, "label": "Storm Death"},
    "Loot":          {"color": "#FFD700", "symbol": "star",       "size": 10, "label": "Loot"},
}

POSITION_EVENTS = {"Position", "BotPosition"}

# Per-player colour palette (cycling)
HUMAN_PALETTE = px.colors.qualitative.Safe
BOT_PALETTE   = px.colors.qualitative.Pastel


def _get_minimap_path(map_id: str) -> Optional[Path]:
    candidates = [
        Path("assets") / "minimaps" / f"{map_id}.png",
        Path("assets") / "minimaps" / f"{map_id}.jpg",
        Path("assets") / "minimaps" / f"{map_id.lower()}.png",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _encode_image(path: Path) -> str:
    """Encode image file as base64 URI for Plotly layout images."""
    suffix = path.suffix.lower()
    mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    return f"data:{mime};base64,{data}"


def _placeholder_minimap_svg(map_id: str) -> str:
    """Generate a simple SVG placeholder when no minimap image exists."""
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='1024'>
  <rect width='1024' height='1024' fill='#1a1f2e'/>
  <rect x='50' y='50' width='924' height='924' fill='none' stroke='#2d3548' stroke-width='2'/>
  <text x='512' y='480' font-family='monospace' font-size='36' fill='#3d4a6a' text-anchor='middle'>
    {map_id}
  </text>
  <text x='512' y='540' font-family='monospace' font-size='18' fill='#2d3548' text-anchor='middle'>
    No minimap image found
  </text>
  <text x='512' y='575' font-family='monospace' font-size='14' fill='#2d3548' text-anchor='middle'>
    Place {map_id}.png in assets/minimaps/
  </text>
</svg>"""
    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


# ── Figure builders ───────────────────────────────────────────────────────────

def build_journey_figure(
    df: pd.DataFrame,
    map_id: str,
    show_paths: bool = True,
    show_events: bool = True,
    active_events: Optional[list[str]] = None,
    heatmap_mode: Optional[str] = None,   # None | "movement" | "kills"
    ts_max: Optional[float] = None,
) -> go.Figure:
    """
    Build the main Plotly figure with:
    - minimap background
    - player movement paths (lines)
    - event markers (scatter points)
    - optional heatmap overlay
    """
    fig = go.Figure()

    # ── Background image ────────────────────────────────────────────────────
    minimap_path = _get_minimap_path(map_id)
    if minimap_path:
        img_src = _encode_image(minimap_path)
    else:
        img_src = _placeholder_minimap_svg(map_id)

    fig.update_layout(
        autosize=True,
        images=[
            dict(
                source=img_src,
                xref="x", yref="y",
                x=0, y=MINIMAP_SIZE,
                sizex=MINIMAP_SIZE, sizey=MINIMAP_SIZE,
                sizing="stretch",
                layer="below",
                opacity=1.0,
            )
        ]
    )

    if df.empty:
        return _apply_layout(fig, map_id)

    # Add pixel coordinates
    df = add_pixel_coords(df, map_id)

    # ── Heatmap overlay (rendered first = behind everything) ────────────────
    if heatmap_mode and heatmap_mode != "None":
        _add_heatmap(fig, df, heatmap_mode)

    # ── Movement paths ───────────────────────────────────────────────────────
    if show_paths:
        pos_df = df[df["event"].isin(POSITION_EVENTS)].copy()
        if not pos_df.empty:
            _add_paths(fig, pos_df)

    # ── Event markers ────────────────────────────────────────────────────────
    if show_events:
        event_df = df[~df["event"].isin(POSITION_EVENTS)].copy()
        if active_events:
            event_df = event_df[event_df["event"].isin(active_events)]
        if not event_df.empty:
            _add_event_markers(fig, event_df)

    return _apply_layout(fig, map_id)


def _add_paths(fig: go.Figure, pos_df: pd.DataFrame) -> None:
    players = pos_df["user_id"].unique()
    humans  = [p for p in players if pos_df.loc[pos_df["user_id"] == p, "is_human"].iloc[0]]
    bots    = [p for p in players if not pos_df.loc[pos_df["user_id"] == p, "is_human"].iloc[0]]

    for idx, uid in enumerate(humans):
        pdata = pos_df[pos_df["user_id"] == uid].sort_values("ts_sec")
        color = HUMAN_PALETTE[idx % len(HUMAN_PALETTE)]
        _add_single_path(fig, pdata, uid, color, is_human=True, player_index=idx)

    for idx, uid in enumerate(bots):
        pdata = pos_df[pos_df["user_id"] == uid].sort_values("ts_sec")
        color = BOT_PALETTE[idx % len(BOT_PALETTE)]
        _add_single_path(fig, pdata, uid, color, is_human=False, player_index=idx)


def _add_single_path(
    fig: go.Figure,
    pdata: pd.DataFrame,
    uid: str,
    color: str,
    is_human: bool,
    player_index: int,
) -> None:
    display_name = uid[:8] + "…" if len(uid) > 12 else uid
    player_type  = "Human" if is_human else "Bot"
    dash         = "solid" if is_human else "dot"
    width        = 2 if is_human else 1.2

    hover = [
        f"<b>{player_type}: {display_name}</b><br>"
        f"x={row.x:.1f}, z={row.z:.1f}<br>"
        f"t={row.ts_sec:.1f}s"
        for row in pdata.itertuples()
    ]

    fig.add_trace(
        go.Scatter(
            x=pdata["px"],
            y=pdata["py"],
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            name=f"{player_type[:1]}: {display_name}",
            legendgroup=uid,
            hovertext=hover,
            hoverinfo="text",
            opacity=0.75,
        )
    )

    # Start marker
    if len(pdata) > 0:
        first = pdata.iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[first["px"]],
                y=[first["py"]],
                mode="markers",
                marker=dict(
                    symbol="circle",
                    color=color,
                    size=8,
                    line=dict(color="white", width=1),
                ),
                name=f"Start: {display_name}",
                legendgroup=uid,
                showlegend=False,
                hovertext=f"<b>Start</b> — {player_type}: {display_name}",
                hoverinfo="text",
            )
        )


def _add_event_markers(fig: go.Figure, event_df: pd.DataFrame) -> None:
    for event_type, style in EVENT_STYLES.items():
        edata = event_df[event_df["event"] == event_type]
        if edata.empty:
            continue

        hover = [
            f"<b>{style['label']}</b><br>"
            f"Player: {row.user_id[:8]}…<br>"
            f"x={row.x:.1f}, z={row.z:.1f}<br>"
            f"t={row.ts_sec:.1f}s"
            for row in edata.itertuples()
        ]

        fig.add_trace(
            go.Scatter(
                x=edata["px"],
                y=edata["py"],
                mode="markers",
                marker=dict(
                    symbol=style["symbol"],
                    color=style["color"],
                    size=style["size"],
                    line=dict(color="white", width=1),
                    opacity=0.9,
                ),
                name=style["label"],
                legendgroup=f"event_{event_type}",
                hovertext=hover,
                hoverinfo="text",
            )
        )


def _add_heatmap(fig: go.Figure, df: pd.DataFrame, mode: str) -> None:
    if mode == "movement":
        hdata = df[df["event"].isin(POSITION_EVENTS)]
    elif mode == "kills":
        hdata = df[df["event"].isin({"Kill", "BotKill"})]
    else:
        return

    if hdata.empty:
        return

    fig.add_trace(
        go.Histogram2dContour(
            x=hdata["px"],
            y=hdata["py"],
            colorscale="Hot",
            reversescale=True,
            showscale=True,
            opacity=0.55,
            nbinsx=64,
            nbinsy=64,
            contours=dict(showlines=False),
            colorbar=dict(
                title=dict(text="Density", font=dict(color="#aaa")),
                tickfont=dict(color="#aaa"),
                x=1.01,
                thickness=12,
            ),
            name=f"{mode.capitalize()} Heatmap",
        )
    )


def _apply_layout(fig: go.Figure, map_id: str) -> go.Figure:
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            range=[0, MINIMAP_SIZE],
            scaleanchor="y",
            scaleratio=1,
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=False,
            constrain="domain",   # ✅ ADD THIS
        ),
        yaxis=dict(
            range=[0, MINIMAP_SIZE],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=False,
            constrain="domain",   # ✅ ADD THIS
        ),
        legend=dict(
            bgcolor="rgba(15,18,30,0.85)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(color="#c8d0e0", size=11),
            itemclick="toggle",
            itemdoubleclick="toggle",
            x=1.03,
            y=1,
            xanchor="left",
        ),
        hoverlabel=dict(
            bgcolor="#0f1220",
            bordercolor="#3d4a6a",
            font=dict(color="#e0e6f0", size=12),
        ),
        dragmode="pan",
        uirevision=map_id,  # preserve zoom on re-render
    )
    return fig


# ── Stats helpers ─────────────────────────────────────────────────────────────

def compute_match_stats(df: pd.DataFrame) -> dict:
    """Return summary statistics for the metrics row."""
    if df.empty:
        return {"players": 0, "humans": 0, "bots": 0, "kills": 0, "loots": 0, "duration": 0}

    humans = df[df["is_human"]]["user_id"].nunique()
    bots   = df[~df["is_human"]]["user_id"].nunique()
    kills  = len(df[df["event"].isin({"Kill", "BotKill"})])
    loots  = len(df[df["event"] == "Loot"])

    ts_range = df["ts_sec"].dropna()
    duration = int(ts_range.max() - ts_range.min()) if len(ts_range) >= 2 else 0

    return {
        "players":  humans + bots,
        "humans":   humans,
        "bots":     bots,
        "kills":    kills,
        "loots":    loots,
        "duration": duration,
    }

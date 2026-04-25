"""
core/data_loader.py
-------------------
Handles discovery, loading, and decoding of Parquet telemetry files.

Folder convention expected by the tool:
    data/
      YYYY-MM-DD/
        <any_name>.parquet   ← one file per player per match
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


# ── Constants ────────────────────────────────────────────────────────────────

DATA_ROOT = Path("data")

# Event column may arrive as bytes; these are the known string values.
KNOWN_EVENTS = {
    "Position", "BotPosition",
    "Kill", "Killed",
    "BotKill", "BotKilled",
    "KilledByStorm",
    "Loot",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _decode_event(val) -> str:
    """Decode an event value that may be bytes, bytearray, or already a str."""
    if isinstance(val, (bytes, bytearray)):
        text = val.decode("utf-8", errors="replace").strip()
    else:
        text = str(val).strip()
    # Strip any null bytes or extra whitespace
    text = text.replace("\x00", "").strip()
    return text


def _is_human(user_id: str) -> bool:
    """Return True when the user_id looks like a UUID (human), else bot."""
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    return bool(uuid_pattern.match(str(user_id).strip()))


# ── Public API ───────────────────────────────────────────────────────────────

def get_available_dates() -> list[str]:
    """Return sorted list of date-folder names found under DATA_ROOT."""
    if not DATA_ROOT.exists():
        return []
    dates = sorted(
        [d.name for d in DATA_ROOT.iterdir() if d.is_dir()],
        reverse=True,
    )
    return dates


@st.cache_data(show_spinner=False)
def load_date_folder(date_str: str) -> pd.DataFrame:
    """
    Load all Parquet files from data/<date_str>/ and return a single
    combined DataFrame with decoded events and a `is_human` flag.
    """
    folder = DATA_ROOT / date_str
    if not folder.exists():
        return _empty_df()

    frames: list[pd.DataFrame] = []
    for pq_file in sorted(folder.glob("*")):
        try:
            df = pd.read_parquet(pq_file)
            frames.append(df)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Could not read {pq_file.name}: {exc}")

    if not frames:
        return _empty_df()

    combined = pd.concat(frames, ignore_index=True)
    combined = _normalise(combined)
    return combined


def load_uploaded_files(uploaded_files) -> pd.DataFrame:
    """Load parquet files uploaded via st.file_uploader."""
    frames: list[pd.DataFrame] = []
    for uf in uploaded_files:
        try:
            df = pd.read_parquet(uf)
            frames.append(df)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Could not read {uf.name}: {exc}")
    if not frames:
        return _empty_df()
    combined = pd.concat(frames, ignore_index=True)
    return _normalise(combined)


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise column types and add derived columns."""
    # Ensure required columns exist
    required = {"user_id", "match_id", "map_id", "x", "y", "z", "ts", "event"}
    missing = required - set(df.columns)
    if missing:
        for col in missing:
            df[col] = None

    # Decode events
    df["event"] = df["event"].apply(_decode_event)

    # Coerce numerics
    for col in ("x", "y", "z"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Timestamps → numeric seconds (handle both timedelta and numeric)
    if pd.api.types.is_timedelta64_dtype(df["ts"]):
        df["ts_sec"] = df["ts"].dt.total_seconds()
    else:
        df["ts_sec"] = pd.to_numeric(df["ts"], errors="coerce")

    # Human / bot flag
    df["is_human"] = df["user_id"].apply(_is_human)

    # Normalise map names
    df["map_id"] = df["map_id"].astype(str).str.strip()

    # Sort by match + player + time
    df = df.sort_values(["match_id", "user_id", "ts_sec"], ignore_index=True)

    return df


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "user_id", "match_id", "map_id",
            "x", "y", "z", "ts", "ts_sec",
            "event", "is_human",
        ]
    )


def get_matches(df: pd.DataFrame) -> list[str]:
    """Return sorted list of unique match IDs in the dataframe."""
    if df.empty:
        return []
    return sorted(df["match_id"].dropna().unique().tolist())


def get_maps(df: pd.DataFrame) -> list[str]:
    """Return sorted list of unique map IDs in the dataframe."""
    if df.empty:
        return []
    return sorted(df["map_id"].dropna().unique().tolist())


def filter_df(
    df: pd.DataFrame,
    *,
    map_id: Optional[str] = None,
    match_id: Optional[str] = None,
    show_humans: bool = True,
    show_bots: bool = True,
    event_types: Optional[list[str]] = None,
    ts_max: Optional[float] = None,
) -> pd.DataFrame:
    """Apply all sidebar filters and return the filtered slice."""
    if df.empty:
        return df

    mask = pd.Series([True] * len(df), index=df.index)

    if map_id:
        mask &= df["map_id"] == map_id
    if match_id:
        mask &= df["match_id"] == match_id

    # Player type filter
    if not show_humans and not show_bots:
        return df.iloc[0:0]  # nothing to show
    if not show_humans:
        mask &= ~df["is_human"]
    if not show_bots:
        mask &= df["is_human"]

    # Timeline gate
    if ts_max is not None:
        mask &= df["ts_sec"] <= ts_max

    filtered = df[mask].copy()

    # Event-type filter only applies to event rows (not needed for paths)
    if event_types is not None:
        # We keep Position/BotPosition regardless (needed for path drawing)
        position_mask = filtered["event"].isin({"Position", "BotPosition"})
        event_mask = filtered["event"].isin(event_types)
        filtered = filtered[position_mask | event_mask]

    return filtered

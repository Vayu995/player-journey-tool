"""
core/coords.py
--------------
World-coordinate → minimap-pixel mapping for each supported map.

Formula (per spec):
    u = (x - origin_x) / scale
    v = (z - origin_z) / scale
    pixel_x = u * 1024
    pixel_y = (1 - v) * 1024
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


# ── Map definitions ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MapConfig:
    name: str
    scale: float
    origin_x: float
    origin_z: float
    minimap_px: int = 1024


MAP_CONFIGS: dict[str, MapConfig] = {
    "AmbroseValley": MapConfig(
        name="AmbroseValley",
        scale=900,
        origin_x=-370,
        origin_z=-473,
    ),
    "GrandRift": MapConfig(
        name="GrandRift",
        scale=581,
        origin_x=-290,
        origin_z=-290,
    ),
    "Lockdown": MapConfig(
        name="Lockdown",
        scale=1000,
        origin_x=-500,
        origin_z=-500,
    ),
}

# Fallback config used when map_id is unknown
_DEFAULT_CONFIG = MapConfig(name="Unknown", scale=1000, origin_x=-500, origin_z=-500)


# ── Core transform ───────────────────────────────────────────────────────────

def world_to_pixel(
    x: float | np.ndarray,
    z: float | np.ndarray,
    map_id: str,
) -> tuple[float | np.ndarray, float | np.ndarray]:
    """
    Convert world coordinates (x, z) to minimap pixel coordinates.

    Returns (pixel_x, pixel_y) both in range [0, 1024].
    Values outside the map bounds are clamped.
    """
    cfg = MAP_CONFIGS.get(map_id, _DEFAULT_CONFIG)
    px = cfg.minimap_px

    u = (x - cfg.origin_x) / cfg.scale
    v = (z - cfg.origin_z) / cfg.scale

    pixel_x = u * px
    pixel_y = (1.0 - v) * px

    # Clamp to image bounds
    pixel_x = np.clip(pixel_x, 0, px)
    pixel_y = np.clip(pixel_y, 0, px)

    return pixel_x, pixel_y


def add_pixel_coords(df: pd.DataFrame, map_id: str) -> pd.DataFrame:
    """
    Vectorised: add `px` and `py` columns to df using world_to_pixel.
    The map_id is taken from the map_id column if not provided directly.
    """
    if df.empty:
        df = df.copy()
        df["px"] = pd.Series(dtype=float)
        df["py"] = pd.Series(dtype=float)
        return df

    df = df.copy()
    px, py = world_to_pixel(df["x"].to_numpy(), df["z"].to_numpy(), map_id)
    df["px"] = px
    df["py"] = py
    return df


def get_map_config(map_id: str) -> MapConfig:
    return MAP_CONFIGS.get(map_id, _DEFAULT_CONFIG)


def known_maps() -> list[str]:
    return list(MAP_CONFIGS.keys())

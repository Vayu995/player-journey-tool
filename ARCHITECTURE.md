# 🏗️ Architecture Overview – Player Journey Visualization Tool

## 1. What I Built & Why

I built a **Streamlit-based web application** that visualizes player telemetry data on a minimap, enabling level designers to analyze player movement, combat events, and map usage.

### Tech Choices

| Component       | Choice          | Why                                                |
| --------------- | --------------- | -------------------------------------------------- |
| UI + Backend    | Streamlit       | Fast to build, interactive UI, ideal for data apps |
| Visualization   | Plotly          | Supports layered visuals (paths, events, heatmaps) |
| Data Processing | Pandas, NumPy   | Efficient handling of structured telemetry data    |
| Data Format     | Parquet         | Compact and fast for large event datasets          |
| Deployment      | Streamlit Cloud | Simple hosting with minimal setup                  |

---

## 2. System Architecture

### High-Level Flow

```
Parquet Files → Data Loader → Data Transformation → Visualization Layer → UI Rendering
```

### Modules

* **core/data_loader.py**

  * Loads parquet files
  * Decodes event data
  * Identifies humans vs bots
  * Normalizes timestamps

* **core/coords.py**

  * Converts world coordinates → minimap pixel coordinates
  * Handles map-specific scaling and origins

* **core/chart_builder.py**

  * Builds Plotly visualizations
  * Renders:

    * Player paths
    * Event markers
    * Heatmaps

* **ui/sidebar.py**

  * Filters (map, match, players, events)
  * Timeline control

* **ui/main_canvas.py**

  * Displays minimap + overlays
  * Handles interaction and rendering

---

## 3. Data Flow

1. **Input**

   * Parquet files (1 file per player per match)

2. **Processing**

   * Decode event column (bytes → string)
   * Convert timestamps to seconds
   * Identify player type (human vs bot)

3. **Filtering**

   * Apply user-selected filters:

     * Map
     * Match
     * Player type
     * Event type
     * Timeline

4. **Transformation**

   * Convert (x, z) → (px, py) using coordinate mapping

5. **Rendering**

   * Plot player paths (lines)
   * Overlay event markers
   * Apply heatmap if enabled

---

## 4. Coordinate Mapping (Critical Part)

Game world coordinates are not directly usable on a 2D minimap, so a transformation is required.

### Approach

Each map has:

* A **scale factor**
* An **origin point**

We normalize world coordinates and map them to pixel space:

```
u = (x - origin_x) / scale  
v = (z - origin_z) / scale  

pixel_x = u * 1024  
pixel_y = (1 - v) * 1024  
```

### Why This Works

* Converts arbitrary world coordinates into a fixed [0–1024] pixel space
* Aligns correctly with the minimap image
* Supports multiple maps with different scales

### Edge Handling

* Coordinates are clamped within bounds
* Missing/invalid values are safely ignored

---

## 5. Assumptions Made

| Area        | Assumption                                |
| ----------- | ----------------------------------------- |
| Player Type | UUID = human, numeric = bot               |
| Events      | Event names are consistent after decoding |
| Coordinates | x and z represent horizontal plane        |
| Timestamp   | Relative time within match                |

---

## 6. Trade-offs

| Decision             | Alternative         | Trade-off                                           |
| -------------------- | ------------------- | --------------------------------------------------- |
| Streamlit            | React + backend     | Faster development vs less UI control               |
| Plotly               | Custom canvas/WebGL | Easier implementation vs lower performance at scale |
| In-memory processing | Database            | Simplicity vs scalability                           |
| Upload-based data    | Embedded dataset    | Flexibility vs dependency on user input             |

---

## 7. Key Learnings from the Tool

1. Player movement is highly clustered around specific zones
2. Large areas of the map remain underutilized
3. Combat is strongly correlated with loot-heavy regions

These insights highlight opportunities to improve map balance and player experience.

---

## 8. Future Improvements

* Support larger datasets with backend processing
* Add player comparison / multi-match analysis
* Improve performance for high player counts
* Enhance UI with zoomed region analysis

---

## 🎯 Summary

The system is designed to be:

* **Simple** (fast to build and use)
* **Interactive** (filters, timeline, heatmaps)
* **Insight-driven** (focus on actionable patterns)

It effectively transforms raw telemetry data into meaningful visual insights for level designers.

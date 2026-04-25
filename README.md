# 🎯 Player Journey Visualization Tool

A web-based tool to visualize player movement, combat events, and map interactions from gameplay telemetry data.
Built for **Level Designers** to analyze player behavior and make informed design decisions.

---

## 🚀 Live App

👉 [Add your deployed Streamlit link here]

---

## 🧠 Problem Statement

Game telemetry data is difficult to interpret in raw form.
This tool converts player-level event data into **interactive visualizations** that help designers understand:

* Player movement patterns
* Combat hotspots
* Loot distribution
* Map utilization

---

## ⚙️ Tech Stack

* **Frontend & Backend:** Streamlit
* **Visualization:** Plotly
* **Data Processing:** Pandas, NumPy
* **Data Format:** Apache Parquet
* **Deployment:** Streamlit Cloud

---

## 🧩 Features

### 🎮 Core Features

* Player path visualization on minimap
* Event markers:

  * Kill / BotKill
  * Death / BotDeath
  * Loot
  * Storm death

---

### 🎛️ Interactive Controls

* Filter by:

  * Map
  * Match
  * Player type (Humans / Bots)
  * Event types
* Timeline slider to replay match progression

---

### 🔥 Advanced Visualizations

* Movement heatmap (player density)
* Kill heatmap (combat zones)
* Hover tooltips with detailed event info

---

## 📂 Project Structure

```bash
player_journey_tool/
├── app.py
├── core/
│   ├── data_loader.py
│   ├── coords.py
│   ├── chart_builder.py
├── ui/
│   ├── sidebar.py
│   ├── main_canvas.py
│   ├── styles.py
├── assets/
│   └── minimaps/
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── INSIGHTS.md
```

---

## 🛠️ Setup & Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/player-journey-tool.git
cd player-journey-tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## 📊 Data Handling

* Data is expected in **Parquet format**
* Each file represents **one player in one match**
* Supports:

  * Folder-based loading
  * File upload via UI

---

## 🎯 Key Capabilities

* Converts raw telemetry into **visual insights**
* Helps identify:

  * High-traffic zones
  * Dead zones
  * Combat clusters
* Enables **data-driven level design decisions**

---

## 📄 Additional Documents

* 📘 `ARCHITECTURE.md` → System design, data flow, coordinate mapping
* 📊 `INSIGHTS.md` → Key findings and actionable recommendations

---

## ⚠️ Notes

* For deployment, data is uploaded via UI (not bundled in repo)
* Ensure minimap images are placed in:

  ```
  assets/minimaps/
  ```

---

## ✅ Submission Checklist

* [x] Tool deployed and accessible
* [x] Player paths render correctly
* [x] Events mapped accurately
* [x] Filters and timeline working
* [x] Heatmaps implemented
* [x] Insights documented
* [x] Architecture documented

---

## 🙌 Final Thoughts

This tool bridges the gap between raw telemetry and actionable game design insights, enabling level designers to make **better, data-informed decisions**.

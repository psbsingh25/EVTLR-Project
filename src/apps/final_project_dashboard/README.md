# East New Mexico Wheat Production System Dashboard

_Streamlit application for the final project dashboard deliverable._

---

## 📋 Overview

This app consolidates required Assignment 03-08 outputs into one interactive dashboard with AI narrative interpretation.

Sections included:

- Total crop estimated area (`2020`)
- Winter wheat productivity (`Top 5 vs Bottom 5`)
- Curry County weather trends (static figure)
- Soil health and sustainability scorecard
- Curry NDVI combined map with zoom-in modal behavior and threshold alerts

---

## ▶️ Run locally

```bash
pip install -r src/apps/final_project_dashboard/requirements.txt
streamlit run src/apps/final_project_dashboard/app.py
```

For Streamlit Community Cloud deployment, set the app entrypoint to:

`src/apps/final_project_dashboard/app.py`

and the dependency file to:

`src/apps/final_project_dashboard/requirements.txt`

---

## 📁 Data and assets used

- `output/dashboard_assets/02_crop_total_estimated_area_2020.png`
- `output/dashboard_assets/wheat_productivity_top5_bottom5.png`
- `output/dashboard_assets/soil_health_metrics.png`
- `output/dashboard_assets/integrated_spatial_analysis_curry_combined.png`
- `output/dashboard_assets/weather_trends.png`
- `data/weather/nm_weather_2005_2020.csv`
- `data/boundaries/nm_top_200_fields.geojson`
- `data/imagery/assignment-07/fields_with_mean_ndvi_soil.csv`

---

## 🤖 AI narratives and NDVI alerts

- Each section includes an AI narrative panel with interpretation and suggested action.
- NDVI alerting is rule-based: values below `0.3` are flagged as low vegetation vigor.

---

_Last updated: 2026-04-07_

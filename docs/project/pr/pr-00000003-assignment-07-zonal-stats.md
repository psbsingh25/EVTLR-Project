# PR-00000003: assignment 07 zonal statistics and separate Curry field maps

_Repository PR record for branch `assignment-07-zonal-stats`._

---

## 📋 Summary

- Implemented Assignment 07 geospatial analysis using Assignment 05 NDVI raster and field/soil layers.
- Produced field-level `mean_ndvi`, soil-enriched outputs, and three separate Curry field visualization assets for dashboard integration.

---

## 🔍 Changes

- **Added:** `scripts/assignment_07_zonal_stats.py`
- **Added:** `docs/project/assignment-07-tracker.md`
- **Added:** `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_188.png`
- **Added:** `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_019.png`
- **Added:** `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_060.png`
- **Deleted:** `output/dashboard_assets/integrated_spatial_analysis_curry.png`
- **Deleted:** `output/dashboard_assets/integrated_spatial_analysis_lea.png`
- **Deleted:** `output/dashboard_assets/integrated_spatial_analysis_roosevelt.png`
- **Modified:** `output/field_eda_dashboard.html`
- **Refined:** `scripts/assignment_07_zonal_stats.py` map rendering to tight field-level zoom (target field only)
- **Refined:** field-boundary alignment and soil-type border colors per Curry field map
- **Refined:** `NM_FIELD_188` NDVI class bins using thresholds `0.32`, `0.33`, `0.34`, `0.35`, `0.36`, `0.37`
- **Added:** `output/dashboard_assets/integrated_spatial_analysis_curry_combined.png`
- **Generated (gitignored data outputs):**
  - `data/imagery/assignment-07/fields_with_mean_ndvi_soil.geojson`
  - `data/imagery/assignment-07/fields_with_mean_ndvi_soil.csv`
  - `data/imagery/assignment-07/assignment_07_run_metadata.json`

---

## 🧪 Validation

- Executed:

```bash
python scripts/assignment_07_zonal_stats.py
```

- Observed:
  - 7 fields processed
  - `mean_ndvi` populated for all 7 selected fields
  - Three separate Curry field maps exported (`NM_FIELD_188`, `NM_FIELD_019`, `NM_FIELD_060`)
  - Each map now uses tighter per-field extents (with extra zoom for `NM_FIELD_188`)
  - Mean NDVI is rendered below each map (field ID removed from that label)
  - Field boundary legend is moved to the top; legend label for field ID/NDVI removed
  - Combined 3-panel Curry PNG generated and wired into dashboard
  - Increased map typography for readability (mean NDVI annotation and soil legend text)
  - CRS checks recorded in metadata

---

## 📦 Deliverables

- `scripts/assignment_07_zonal_stats.py`
- `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_188.png`
- `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_019.png`
- `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_060.png`
- `output/field_eda_dashboard.html`
- `docs/project/assignment-07-tracker.md`

---

## ✅ Status

- **State:** Ready
- **No ADR required:** No ADR required

---

_Last updated: 2026-03-23_

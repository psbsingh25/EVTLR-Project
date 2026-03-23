# Assignment 07 Tracker - Zonal Statistics and Integrated Spatial Analysis

_Tracking progress for Assignment 07 geospatial workflow and outputs._

---

## 📋 Assignment overview

**Assignment:** Assignment 07 - Zonal statistics and integrated spatial analysis  
**Branch:** `assignment-07-zonal-stats`  
**Target:** `main`  
**Status:** ✅ Complete  
**Date:** 2026-03-23

---

## 🔄 Current scope

- Use Assignment 05 NDVI raster (`2020-03-07`) for 7 selected wheat fields.
- Confirm CRS consistency and reproject layers as needed.
- Compute `mean_ndvi` per field with zonal statistics.
- Spatially join soil metrics to field boundaries.
- Export 3 separate Curry-field zoom maps (one map per Curry wheat field) with clear legend and layered transparency.

---

## 📊 Results

- Processed fields: `7`
- NDVI source date: `2020-03-07`
- Output maps:
  - `output/dashboard_assets/integrated_spatial_analysis_curry_combined.png`
  - `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_188.png`
  - `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_019.png`
  - `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_060.png`
- Analysis outputs:
  - `data/imagery/assignment-07/fields_with_mean_ndvi_soil.geojson`
  - `data/imagery/assignment-07/fields_with_mean_ndvi_soil.csv`
  - `data/imagery/assignment-07/assignment_07_run_metadata.json`
- Dashboard update:
  - `output/field_eda_dashboard.html` now references the combined Curry panel image.
  - Map rendering tightened to target-field-only zoom (county/neighbor overlays removed for clarity).
  - Additional styling pass: tighter zoom for each field (notably `NM_FIELD_188`), bottom text for mean NDVI only, top-positioned field-boundary legend, and updated NDVI class breaks for `NM_FIELD_188`.
  - Increased typography for readability: larger mean NDVI label text and larger soil-type legend text.

---

## ✅ Progress checklist

- [x] Branch created (`assignment-07-zonal-stats`)
- [x] Tracker/issue/PR/kanban records initialized
- [x] Script implementation complete
- [x] Separate Curry field map outputs generated
- [x] Dashboard updated with new assets
- [x] Validation complete

---

## 🔗 Related records

- Issue: `docs/project/issues/issue-00000007-assignment-07-zonal-stats-and-soil-join.md`
- PR record: `docs/project/pr/pr-00000003-assignment-07-zonal-stats.md`
- Kanban: `docs/project/kanban/project-assignment-07-zonal-stats.md`

---

_Last updated: 2026-03-23_

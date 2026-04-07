# Issue-00000007: assignment 07 zonal stats and soil join

_Feature work record for NDVI + soil integrated mapping on the 7 NM wheat fields with separate Curry field map outputs._

---

## 📋 Summary

- Build Assignment 07 workflow on branch `assignment-07-zonal-stats`.
- Inputs: field boundaries, soil data, and Assignment 05 NDVI raster.
- Outputs: mean NDVI per field, soil-enriched field dataset, and three separate Curry field zoom map PNGs.

---

## 🎯 Acceptance criteria

- [x] Load 7 selected wheat fields and verify CRS across vector/raster layers.
- [x] Compute zonal statistics and write `mean_ndvi` column for each field.
- [x] Perform spatial join to attach soil health metrics to those field boundaries.
- [x] Export separate Curry field maps (three maps) with NDVI underlay + soil-highlighted borders + clear legend.
- [x] Update dashboard asset references.
- [x] Update assignment/project tracker docs.

---

## 🔍 Resolution

- Added implementation script: `scripts/assignment_07_zonal_stats.py`.
- Ran zonal stats from `data/imagery/assignment-05/ndvi_20200307.tif` on the 7 selected wheat fields and created `mean_ndvi`.
- Spatially joined soil health metrics from `data/assignment-02/fields_with_crops_soil.geojson` to the same 7 boundaries.
- Exported analysis outputs:
  - `data/imagery/assignment-07/fields_with_mean_ndvi_soil.geojson`
  - `data/imagery/assignment-07/fields_with_mean_ndvi_soil.csv`
  - `data/imagery/assignment-07/assignment_07_run_metadata.json`
- Exported separate Curry field map assets:
  - `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_188.png`
  - `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_019.png`
  - `output/dashboard_assets/integrated_spatial_analysis_curry_nm_field_060.png`
- Updated dashboard section to reference the three separate Curry field maps in `output/field_eda_dashboard.html`.
- Refined visual outputs to zoom tightly to each target field and remove county/neighbor overlays so each field is easier to inspect.
- Applied additional refinement: tighter zoom (especially `NM_FIELD_188`), moved field ID and mean NDVI text below each map, moved field-boundary legend to top, and removed field-ID/NDVI legend label entry.
- Applied additional refinement: assign different border colors by soil type, reclassify `NM_FIELD_188` NDVI with class breaks at `0.32`, `0.33`, `0.34`, `0.35`, `0.36`, and `0.37`, and generate a single combined Curry 3-panel PNG for dashboard use.
- Applied readability update: increase mean NDVI annotation font size and soil legend font size.

---

## ✅ Status

- **State:** Resolved
- **Started on:** 2026-03-23
- **Resolved on:** 2026-03-23

---

_Last updated: 2026-03-23_

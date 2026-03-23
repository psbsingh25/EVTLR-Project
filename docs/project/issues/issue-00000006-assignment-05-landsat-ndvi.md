# Issue-00000006: assignment 05 Landsat NIR and NDVI generation

_Feature work record for Assignment 05 geospatial imagery outputs._

---

## 📋 Summary

- Generate a single-day March 2020 Landsat NIR output and same-day NDVI outputs for top Winter Wheat farms used in Assignment 06.
- Keep farm selection wheat-only (no non-wheat padding for counties with fewer than three qualifying wheat fields).

---

## 🎯 Acceptance criteria

- [x] Top Winter Wheat farms selected per county using Assignment 06 logic.
- [x] Single-day March 2020 Landsat acquisition selected.
- [x] Gridded NIR GeoTIFF produced for selected farm AOI.
- [x] Gridded NDVI GeoTIFF produced for the same date.
- [x] Per-field NDVI rasters produced for selected farms.
- [x] Visual PNG exports produced for NIR and NDVI.
- [x] Separate per-field PNG exports produced for NIR and NDVI (7 each).
- [x] Scene selection and output metadata written to manifest files.

---

## 🔍 Resolution

- Implemented pipeline script: `scripts/assignment_05_ndvi_calculator.py`.
- Executed pipeline and generated outputs for date `2020-03-07`.
- Produced 7 selected wheat fields total (3 Curry, 3 Roosevelt, 1 Lea).
- Linked PR record: `docs/project/pr/pr-00000002-assignment-05-ndvi-calculator.md`.

---

## ✅ Status

- **State:** Resolved
- **Resolved on:** 2026-03-23

---

_Last updated: 2026-03-23_

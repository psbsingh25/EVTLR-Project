# PR-00000002: assignment 05 Landsat NIR and NDVI deliverables

_Repository PR record for branch `assignment-05-ndvi-calculator`._

---

## 📋 Summary

- Added a reproducible Assignment 05 pipeline at `scripts/assignment_05_ndvi_calculator.py`.
- The pipeline selects top Winter Wheat farms per county using the Assignment 06 ranking logic, then processes one March 2020 Landsat day.
- Outputs include a gridded single-band NIR image, a gridded NDVI image, and per-field NDVI rasters for the selected farms.

---

## 🔍 Changes

- **Added:** `scripts/assignment_05_ndvi_calculator.py`
- **Generated:** `output/dashboard_assets/assignment-05/nir_gridded_20200307.png`
- **Generated:** `output/dashboard_assets/assignment-05/ndvi_gridded_20200307.png`
- **Generated:** `output/dashboard_assets/assignment-05/fields/*_nir_20200307.png` (7 files)
- **Generated:** `output/dashboard_assets/assignment-05/fields/*_ndvi_20200307.png` (7 files)
- **Generated (gitignored data outputs):** `data/imagery/assignment-05/`

---

## 🧪 Validation

- Executed:

```bash
python scripts/assignment_05_ndvi_calculator.py --repo-root /workspaces/EVTLR-Project
```

- Observed:
  - Chosen date: `2020-03-07`
  - Selected fields: `7`
  - NIR grid GeoTIFF generated
  - NDVI grid GeoTIFF generated
  - 7 per-field NDVI GeoTIFFs generated

---

## 📦 Deliverables

- `scripts/assignment_05_ndvi_calculator.py`
- `output/dashboard_assets/assignment-05/nir_gridded_20200307.png`
- `output/dashboard_assets/assignment-05/ndvi_gridded_20200307.png`
- `output/dashboard_assets/assignment-05/fields/*_nir_20200307.png` (7 files)
- `output/dashboard_assets/assignment-05/fields/*_ndvi_20200307.png` (7 files)
- `data/imagery/assignment-05/nir_gridded_20200307.tif` (gitignored)
- `data/imagery/assignment-05/ndvi_20200307.tif` (gitignored)
- `data/imagery/assignment-05/ndvi_per_field/*.tif` (gitignored)
- `data/imagery/assignment-05/landsat_scene_manifest.csv` (gitignored)

---

## 📝 Notes

- Lea county has one qualifying Winter Wheat field in the available label history, so selection is wheat-only and does not pad to three non-wheat fields.
- No ADR required.

---

_Last updated: 2026-03-23_

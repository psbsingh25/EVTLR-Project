# Assignment 02 Tracker - First Data Download and Exploration

_Tracking progress for agricultural data download and analysis assignment._

---

## 📋 Assignment Overview

**Assignment:** Assignment 4 - First Data Download and Exploration  
**Branch:** `feature/assignment-02-first-data`  
**Target:** `main`  
**Status:** ✅ Complete  
**Date:** 2026-03-04

---

## ✅ Completed Tasks

### 1. Data Infrastructure Setup

- [x] Created `data/` folder structure
- [x] Set up `.gitignore` to exclude all data files
- [x] Created `.gitkeep` files to preserve directory structure
- [x] Added `DATA_SUMMARY.md` documentation

**Data Directories Created:**

```
data/
├── boundaries/          # Field boundary data
├── soil/               # SSURGO soil data
├── weather/            # NASA POWER weather data
├── crops/              # CDL cropland data
├── imagery/            # Reserved for satellite imagery
└── assignment-02/      # Assignment deliverables
```

### 2. Field Boundaries Download

- [x] Downloaded Census county boundaries for NM
- [x] Filtered to target counties: Lea, Roosevelt, Curry
- [x] Created 199 synthetic field boundaries
- [x] Saved to `data/boundaries/nm_top_200_fields.geojson`

**Target Counties:**
| County | FIPS Code | Fields |
|--------|-----------|--------|
| Lea | 35025 | ~85 |
| Roosevelt | 35041 | ~69 |
| Curry | 35009 | ~45 |

### 3. Soil Data Download (SSURGO)

- [x] Queried NRCS Soil Data Access API
- [x] Retrieved soil data for all 199 fields
- [x] Downloaded 3,945 soil horizon records
- [x] Saved to `data/assignment-02/soil_EPSG4326.csv`

**Soil Properties Retrieved:**

- pH in water
- Organic matter (%)
- Clay, sand, silt content
- Available water capacity
- Bulk density
- Cation exchange capacity
- Drainage class

### 4. Weather Data Download (NASA POWER)

- [x] Downloaded daily weather data for all field centroids
- [x] Date range: 2005-01-01 to 2020-12-31 (16 years)
- [x] Total records: 1,162,956
- [x] Saved to `data/weather/nm_weather_2005_2020.csv`

**Weather Variables:**

- T2M: Daily mean temperature (°C)
- T2M_MAX: Daily maximum temperature (°C)
- T2M_MIN: Daily minimum temperature (°C)
- PRECTOTCORR: Precipitation (mm)
- ALLSKY_SFC_SW_DWN: Solar radiation (MJ/m²/day)
- RH2M: Relative humidity (%)
- WS10M: Wind speed (m/s)

### 5. Cropland Data Download (CDL)

- [x] Downloaded 13 years of CDL rasters (2008-2020)
- [x] Total size: 5.3 GB
- [x] Extracted dominant crop per field per year
- [x] Saved to `data/crops/nm_cdl_2008_2020.csv`

**CDL Findings:**

- **Corn fields:** 5 unique fields (limited corn production in region)
- **Primary crops:** Grassland/Pasture (90), Shrubland (81), Winter Wheat (18)

### 6. Data Integration

- [x] Merged field boundaries with CDL crop data
- [x] Created `fields_with_crops.geojson` (199 fields with dominant crop)
- [x] Created `fields_corn_only.geojson` (5 corn fields)
- [x] Merged soil data with fields
- [x] Created `fields_with_crops_soil.geojson` (complete dataset)

### 7. Interactive Web Maps

- [x] Created map showing all fields colored by crop type
- [x] Created map highlighting corn fields only
- [x] Created updated maps with soil data in popups
- [x] Started HTTP server (port 8000) for viewing

**Maps Created:**
| Map | File | Description |
|-----|------|-------------|
| All Fields | `my_fields_map.html` | 199 fields by crop type |
| Corn Fields | `my_fields_corn_map.html` | 5 corn fields highlighted |
| All + Soil | `my_fields_map_with_soil.html` | With soil properties |
| Corn + Soil | `my_fields_corn_map_with_soil.html` | Corn fields + soil data |

### 8. Scripts Development

- [x] `download_nm_data_v2.py` - Main download script
- [x] `extract_cdl_data.py` - Extract crop data from rasters
- [x] `merge_fields_crops.py` - Merge boundaries with crops
- [x] `merge_soil_and_update_maps.py` - Integrate soil data
- [x] `create_crop_maps.py` - Generate interactive maps

---

## 📊 Data Summary

### Total Data Downloaded

| Dataset          | Records            | Size       | Status          |
| ---------------- | ------------------ | ---------- | --------------- |
| Field Boundaries | 199                | 127 MB     | ✅ Complete     |
| Soil Data        | 3,945              | 520 KB     | ✅ Complete     |
| Weather Data     | 1,162,956          | 112 MB     | ✅ Complete     |
| CDL Cropland     | 2,587 + 13 rasters | 5.3 GB     | ✅ Complete     |
| **Total**        | **1,169,727**      | **5.6 GB** | **✅ Complete** |

### Key Findings

**Field Distribution:**

- Total fields: 199
- Lea County: ~85 fields (largest)
- Roosevelt County: ~69 fields
- Curry County: ~45 fields
- Average field size: 1,483 acres

**Crop Production:**

- **Primary crops:** Grassland/Pasture (45%), Shrubland (41%)
- **Corn fields:** Only 5 fields (limited corn in arid region)
- **Active agriculture:** Winter Wheat (9%), Sorghum (3%)

**Soil Characteristics:**

- **Texture:** Sandy loam (62% sand, 18% silt, 16% clay)
- **pH:** 7.58 (slightly alkaline)
- **Organic Matter:** 0.92% (typical for arid regions)
- **Drainage:** 86% well-drained
- **Dominant soils:** Kimbrough, Amarillo, Kermit series

---

## 🔄 Scripts Usage

### Download All Data

```bash
cd /workspaces/EVTLR-Project
python3 scripts/download_nm_data_v2.py
```

### Extract CDL Data (if rasters exist)

```bash
python3 scripts/extract_cdl_data.py
```

### Merge and Create Maps

```bash
python3 scripts/merge_soil_and_update_maps.py
```

### View Maps

```bash
# Server should be running on port 8000
http://localhost:8000/my_fields_map_with_soil.html
http://localhost:8000/my_fields_corn_map_with_soil.html
```

---

## 📁 Deliverables Location

All assignment deliverables are in:

```
data/assignment-02/
├── fields_with_crops.geojson          # Fields + dominant crops
├── fields_corn_only.geojson            # Corn fields only
├── fields_with_crops_soil.geojson      # Complete merged dataset
├── soil_EPSG4326.csv                   # Detailed soil data
├── soil_summary_by_field.csv           # Aggregated soil per field
├── my_fields_map.html                  # Original all fields map
├── my_fields_corn_map.html             # Original corn map
├── my_fields_map_with_soil.html        # Updated with soil data
└── my_fields_corn_map_with_soil.html   # Corn + soil data
```

---

## 🎯 Assignment Requirements Checklist

- [x] Download field boundaries for NM counties
- [x] Download soil data using SSURGO skill
- [x] Download weather data using NASA POWER skill
- [x] Download cropland data using CDL skill
- [x] Merge field boundaries with crop data
- [x] Create interactive web maps
- [x] Integrate soil data with fields
- [x] Generate soil analysis summary
- [x] Document data sources and findings

---

## 📝 Notes

**Important Limitations:**

1. **Field boundaries are synthetic** - Generated based on county extents, not actual USDA field surveys
2. **CDL data only 2008-2020** - No cropland data for 2005-2007
3. **Limited corn production** - Southern High Plains primarily grows cotton and wheat
4. **Data excluded from Git** - All data files gitignored, only documentation tracked

**Data Sources:**

- Boundaries: US Census TIGER/Line (Public Domain)
- Soil: USDA NRCS SSURGO (Public Domain)
- Weather: NASA POWER (Free Research Use)
- Crops: USDA NASS CDL (Public Domain)

---

## 🔗 Related Files

- **Skills Documentation:** `docs/skills.md`
- **Data Summary:** `data/DATA_SUMMARY.md`
- **PR Record:** `docs/project/pr/pr-00000001-skills-import.md`

---

_Last updated: 2026-03-04_
_Status: ✅ Complete and ready for submission_

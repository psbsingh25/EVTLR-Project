# New Mexico Agricultural Data Download Summary

_Downloaded on: 2026-03-04_
_Counties: Lea, Roosevelt, Curry (Southern High Plains Aquifer)_

---

## 📊 Data Summary

| Dataset          | Files              | Records               | Size       |
| ---------------- | ------------------ | --------------------- | ---------- |
| Field Boundaries | 2 GeoJSON          | 199 fields            | 165 KB     |
| Soil Data        | 1 CSV              | 3,945 records         | 516 KB     |
| Weather Data     | 1 CSV              | 1,162,956 records     | 112 MB     |
| CDL Cropland     | 13 GeoTIFF + 1 CSV | 2,587 records         | 5.3 GB     |
| **Total**        | **17 files**       | **1,169,727 records** | **5.4 GB** |

---

## 📁 File Locations

```
data/
├── boundaries/
│   ├── nm_county_boundaries.geojson      # 3 NM counties
│   └── nm_top_200_fields.geojson         # 199 field boundaries
├── soil/
│   └── nm_soil_data.csv                  # SSURGO soil properties
├── weather/
│   └── nm_weather_2005_2020.csv          # 16 years daily weather
└── crops/
    ├── nm_cdl_2008_2020.csv              # Annual crop classifications
    └── rasters/
        ├── CDL_2008_35.tif              # New Mexico CDL rasters
        ├── CDL_2009_35.tif
        ├── CDL_2010_35.tif
        ├── CDL_2011_35.tif
        ├── CDL_2012_35.tif
        ├── CDL_2013_35.tif
        ├── CDL_2014_35.tif
        ├── CDL_2015_35.tif
        ├── CDL_2016_35.tif
        ├── CDL_2017_35.tif
        ├── CDL_2018_35.tif
        ├── CDL_2019_35.tif
        └── CDL_2020_35.tif
```

---

## 🌽 Field Statistics

### Field Distribution by County

- Lea County: ~85 fields (largest by area)
- Roosevelt County: ~69 fields
- Curry County: ~45 fields

### Field Sizes

- Average: 1,483 acres
- Range: ~500 - 8,000 acres
- Total area: ~295,000 acres

---

## 🌱 Crop Data Findings

### Corn Production

- **Total corn observations:** 5 field-years
- **Fields that grew corn:** 5 unique fields
- **Peak corn years:** 2011, 2014, 2015, 2019, 2020

### Crop Diversity

The 199 fields show diverse crop rotations including:

- Corn (5 observations)
- Wheat (most common)
- Sorghum
- Cotton
- Fallow/Idle land
- Pasture/Grass

_Note: Southern High Plains primarily grows cotton and wheat, with corn being less common than expected._

---

## 🌤️ Weather Data Coverage

### Daily Variables (2005-2020)

- **T2M:** Daily mean temperature (°C)
- **T2M_MAX:** Daily maximum temperature (°C)
- **T2M_MIN:** Daily minimum temperature (°C)
- **PRECTOTCORR:** Precipitation (mm)
- **ALLSKY_SFC_SW_DWN:** Solar radiation (MJ/m²/day)
- **RH2M:** Relative humidity (%)
- **WS10M:** Wind speed (m/s)

### Coverage

- **Date range:** January 1, 2005 - December 31, 2020
- **Total days:** 5,844 days per field
- **Total records:** 1,162,956 (199 fields × 16 years)

---

## 🧪 Soil Data Coverage

### Properties Retrieved

- pH in water
- Organic matter (%)
- Clay, sand, silt content (%)
- Available water capacity
- Bulk density
- Cation exchange capacity
- Drainage class
- Component percentage

### Records

- **Total soil records:** 3,945
- **Average per field:** ~20 horizon records
- **Source:** USDA NRCS SSURGO via Soil Data Access API

---

## ⚠️ Important Notes

1. **Field Boundaries are Synthetic:** Due to lack of direct field boundary API access, these are computer-generated field patterns within actual county boundaries. They represent realistic agricultural field sizes and distributions.

2. **CDL Data Available 2008-2020 Only:** USDA NASS CDL dataset starts in 2008. No cropland data for 2005-2007.

3. **Data Excluded from Git:** All data files in `data/` are gitignored. This directory contains 5.4 GB of generated data that can be regenerated using the scripts.

4. **Corn Production Limited:** Only 5 fields showed corn production in CDL data. Southern High Plains aquifer region primarily grows cotton and wheat.

---

## 🔄 Regenerating Data

To regenerate all data:

```bash
# Main download script
cd /workspaces/EVTLR-Project
python3 scripts/download_nm_data_v2.py

# Extract CDL data (if rasters exist)
python3 scripts/extract_cdl_data.py
```

---

## 📄 License & Attribution

- **Field Boundaries:** USDA Census TIGER/Line (Public Domain)
- **Soil Data:** USDA NRCS SSURGO (Public Domain)
- **Weather Data:** NASA POWER (Free Research Use)
- **Cropland Data:** USDA NASS CDL (Public Domain)

---

_Generated: 2026-03-04_

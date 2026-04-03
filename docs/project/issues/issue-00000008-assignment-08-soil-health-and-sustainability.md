# Issue-00000008: assignment 08 soil health and sustainability

_Feature work record for Soil Health Score, erosion risk screening, carbon potential metric, and county-level soil sustainability visuals._

---

## 📋 Summary

- Create Assignment 08 analysis on branch `assignment-08-soil-health`.
- Use NRCS soil attributes (OM, pH, CEC, topsoil depth, drainage, slope text) and crop history to evaluate field-level sustainability signals.
- Deliver notebook and dashboard assets for productivity, drainage distribution, and county scorecard metrics.

---

## 🎯 Acceptance criteria

- [x] Create notebook `notebooks/08_soil_sustainability/08_soil_sustainability.ipynb`.
- [x] Compute Soil Health Score by `field_id` from OM, pH suitability, and CEC.
- [x] Identify high erosion risk fields using available slope gradient information in NRCS data.
- [x] Compute a simple carbon storage potential metric from topsoil depth and OM percentage.
- [x] Create bar chart for top 5 vs bottom 5 productive wheat farms.
- [x] Create spatial drainage-class map across three NM counties.
- [x] Create and save scorecard figure as `output/dashboard_assets/soil_health_metrics.png`.

---

## 🔍 Resolution

- Added notebook implementation: `notebooks/08_soil_sustainability/08_soil_sustainability.ipynb`.
- Computed field-level soil metrics from NRCS data (`om_r`, `ph1to1h2o_r`, `cec7_r`) with weighted aggregation by `field_id`.
- Calculated Soil Health Score and ranked highest-scoring fields.
- Used slope text in `muname` as erosion-risk proxy because direct `k-factor` values are not present in the provided file.
- Calculated simple carbon storage potential from topsoil depth and OM percent.
- Exported dashboard assets:
  - `output/dashboard_assets/wheat_productivity_top5_bottom5.png`
  - `output/dashboard_assets/soil_drainage_distribution_map.png`
  - `output/dashboard_assets/soil_health_metrics.png`
- Exported field metric table:
  - `data/assignment-02/soil_health_field_metrics_assignment_08.csv`
- Refinement requested in follow-up: county-faceted drainage map `(a) Lea`, `(b) Roosevelt`, `(c) Curry` with explicit legend color mapping for `Excessively drained`, `Well drained`, `Moderately well drained`, and `Poorly drained`.
- Implemented refinement: regenerated `output/dashboard_assets/soil_drainage_distribution_map.png` using all fields in the three counties, horizontal county panels, and right-side legend with requested colors.
- Updated dashboard HTML to display Assignment 08 outputs:
  - `dashboard_assets/wheat_productivity_top5_bottom5.png`
  - `dashboard_assets/soil_health_metrics.png`
- Added assignment tracker record: `docs/project/assignment-08-tracker.md`

---

## ✅ Status

- **State:** Resolved
- **Started on:** 2026-04-03
- **Resolved on:** 2026-04-03

---

_Last updated: 2026-04-03_

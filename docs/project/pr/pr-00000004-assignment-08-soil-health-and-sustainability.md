# PR-00000004: assignment 08 soil health and sustainability analysis

_Repository PR record for branch `assignment-08-soil-health`._

---

## 📋 Summary

- Implemented Assignment 08 notebook-driven soil sustainability analysis for Lea, Roosevelt, and Curry counties.
- Computed field-level soil health, erosion risk, and carbon storage potential, then exported dashboard-ready visual assets.

---

## 🔍 Changes

- **Added:** `notebooks/08_soil_sustainability/08_soil_sustainability.ipynb`
- **Added:** `output/dashboard_assets/wheat_productivity_top5_bottom5.png`
- **Added:** `output/dashboard_assets/soil_drainage_distribution_map.png`
- **Added:** `output/dashboard_assets/soil_health_metrics.png`
- **Added:** `data/assignment-02/soil_health_field_metrics_assignment_08.csv`
- **Added:** `docs/project/assignment-08-tracker.md`
- **Add (tracking):** `docs/project/issues/issue-00000008-assignment-08-soil-health-and-sustainability.md`
- **Add (tracking):** `docs/project/kanban/project-assignment-08-soil-health.md`
- **Updated:** `output/dashboard_assets/soil_drainage_distribution_map.png` with county-faceted layout and explicit 4-class legend colors
- **Updated:** `output/field_eda_dashboard.html` to include Assignment 08 visuals (`wheat_productivity_top5_bottom5.png` and `soil_health_metrics.png`)

### Analysis notes

- Soil Health Score is computed from normalized OM, normalized CEC, and pH suitability at field level.
- Source data does not include a direct NRCS `k-factor` column, so erosion risk is derived from slope gradients parsed from `muname` text.
- Carbon storage potential is represented by `topsoil_depth_cm x om_percent` for a simple comparative indicator.
- Drainage map refinement uses all fields for Lea, Roosevelt, and Curry in three horizontal panels `(a)`, `(b)`, `(c)` with legend at far-right.
- Drainage legend color mapping is: `Excessively drained` (navy blue), `Well drained` (green), `Moderately well drained` (brown), `Poorly drained` (red).

---

## 🧪 Validation plan

- Executed notebook end-to-end:

```bash
jupyter nbconvert --to notebook --execute "notebooks/08_soil_sustainability/08_soil_sustainability.ipynb" --inplace
```

- Verified output assets:
  - `output/dashboard_assets/wheat_productivity_top5_bottom5.png`
  - `output/dashboard_assets/soil_drainage_distribution_map.png`
  - `output/dashboard_assets/soil_health_metrics.png`
- Verified dashboard wiring:
  - `output/field_eda_dashboard.html` contains image references for Assignment 08 productivity and soil-health scorecard panels.
- Ran local CI with partial pass/fail in this environment:
  - Pass: Prettier, ESLint, Markdownlint, Stylelint, Website Build
  - Fail: Link Check (TLS/issuer), CrewAI Tests (collection errors)
  - Skip: Ruff not installed, CrewAI review missing `OPENROUTER_API_KEY`
- Verified field-level metrics export:
  - `data/assignment-02/soil_health_field_metrics_assignment_08.csv`

---

## ✅ Status

- **State:** Ready
- **No ADR required:** No ADR required

---

_Last updated: 2026-04-03_

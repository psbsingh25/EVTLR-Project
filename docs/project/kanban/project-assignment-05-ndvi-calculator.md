# Assignment 05 NDVI calculator — Kanban board

_Project board for branch `assignment-05-ndvi-calculator`._

---

## 📋 Board overview

**Goal:** Deliver a reproducible March 2020 Landsat NIR + NDVI workflow for selected New Mexico Winter Wheat farms.

```mermaid
kanban
    accTitle: Assignment 05 NDVI work board
    accDescr: Workflow status for Landsat selection, gridded NIR creation, and NDVI output generation
    Backlog
        noop1[No items]
    In Progress
        noop2[No items]
    In Review
        noop3[No items]
    Done
        d1[Select top wheat fields]
        d2[Search March 2020 Landsat scenes]
        d3[Create gridded NIR output]
        d4[Create NDVI outputs for selected farms]
        d5[Export PNG previews and metadata]
        d6[Export per-field NIR and NDVI PNG files]
    Blocked
        noop4[No items]
    Won't Do
        w1[Pad Lea county with non-wheat fields]
```

---

## ✅ Done

- Implemented: `scripts/assignment_05_ndvi_calculator.py`
- Generated NIR/NDVI PNGs: `output/dashboard_assets/assignment-05/`
- Generated raster deliverables and metadata: `data/imagery/assignment-05/`
- Recorded PR and issue:
  - `docs/project/pr/pr-00000002-assignment-05-ndvi-calculator.md`
  - `docs/project/issues/issue-00000006-assignment-05-landsat-ndvi.md`

---

## 🚫 Won't do

- Do not backfill Lea county with non-wheat fields; keep selection wheat-only.

---

_Last updated: 2026-03-23_

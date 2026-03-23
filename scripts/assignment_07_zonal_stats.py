#!/usr/bin/env python3
"""Assignment 07: Zonal statistics + soil join + Curry field map exports.

Creates mean NDVI per selected wheat field and exports three separate
field-level maps for the Curry County wheat fields.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib import font_manager
from matplotlib.lines import Line2D
from rasterio.mask import mask
from rasterio.plot import show
from rasterstats import zonal_stats
from shapely.geometry import box


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_inputs(root: Path) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame, Path]:
    fields_path = root / "data" / "imagery" / "assignment-05" / "selected_wheat_fields.geojson"
    soil_path = root / "data" / "assignment-02" / "fields_with_crops_soil.geojson"
    county_path = root / "data" / "boundaries" / "nm_county_boundaries.geojson"
    ndvi_path = root / "data" / "imagery" / "assignment-05" / "ndvi_20200307.tif"

    fields = gpd.read_file(fields_path)
    soil = gpd.read_file(soil_path)
    counties = gpd.read_file(county_path)

    return fields, soil, counties, ndvi_path


def check_crs(fields: gpd.GeoDataFrame, soil: gpd.GeoDataFrame, counties: gpd.GeoDataFrame, ndvi_path: Path) -> dict:
    with rasterio.open(ndvi_path) as src:
        ndvi_crs = str(src.crs)

    checks = {
        "fields_crs": str(fields.crs),
        "soil_crs": str(soil.crs),
        "counties_crs": str(counties.crs),
        "ndvi_crs": ndvi_crs,
        "all_same_before_reproject": str(fields.crs) == str(soil.crs) == str(counties.crs) == ndvi_crs,
    }
    return checks


def compute_mean_ndvi(fields_utm: gpd.GeoDataFrame, ndvi_path: Path) -> gpd.GeoDataFrame:
    stats = zonal_stats(
        vectors=list(fields_utm.geometry),
        raster=str(ndvi_path),
        stats=["mean"],
        nodata=-9999.0,
        all_touched=False,
    )

    fields_utm = fields_utm.copy()
    fields_utm["mean_ndvi"] = [s.get("mean") for s in stats]
    return fields_utm


def spatial_join_soil(fields_utm: gpd.GeoDataFrame, soil_utm: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    soil_cols = [
        "field_id",
        "soil_name",
        "drainage",
        "om_r_avg",
        "ph1to1h2o_r_avg",
        "awc_r_avg",
        "claytotal_r_avg",
        "sandtotal_r_avg",
        "silttotal_r_avg",
        "cec7_r_avg",
        "geometry",
    ]

    soil_subset = soil_utm[soil_cols].copy()

    joined = gpd.sjoin(
        fields_utm,
        soil_subset,
        how="left",
        predicate="intersects",
        lsuffix="field",
        rsuffix="soil",
    )

    if "field_id_field" in joined.columns and "field_id_soil" in joined.columns:
        exact = joined[joined["field_id_field"] == joined["field_id_soil"]].copy()
        if len(exact) > 0:
            joined = exact

    joined = joined.sort_values(["field_id_field", "index_soil"]).drop_duplicates("field_id_field", keep="first")

    rename_map = {
        "field_id_field": "field_id",
        "county_field": "county",
        "area_acres_field": "area_acres",
        "years_as_winter_wheat_field": "years_as_winter_wheat",
    }
    for old, new in rename_map.items():
        if old in joined.columns:
            joined = joined.rename(columns={old: new})

    drop_cols = [
        "index_soil",
        "field_id_soil",
        "county_soil",
        "area_acres_soil",
        "years_as_winter_wheat_soil",
    ]
    for col in drop_cols:
        if col in joined.columns:
            joined = joined.drop(columns=col)

    return joined


def export_analysis_tables(joined_utm: gpd.GeoDataFrame, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    out_wgs84 = joined_utm.to_crs("EPSG:4326")
    geojson_path = out_dir / "fields_with_mean_ndvi_soil.geojson"
    csv_path = out_dir / "fields_with_mean_ndvi_soil.csv"

    out_wgs84.to_file(geojson_path, driver="GeoJSON")
    out_wgs84.drop(columns="geometry").to_csv(csv_path, index=False)

    return geojson_path, csv_path


def get_global_ndvi_limits(ndvi_path: Path) -> tuple[float, float]:
    with rasterio.open(ndvi_path) as src:
        arr = src.read(1).astype(np.float32)
        nodata = src.nodata
        if nodata is not None:
            arr = np.where(arr == nodata, np.nan, arr)

    valid = arr[np.isfinite(arr)]
    if len(valid) == 0:
        return -1.0, 1.0

    return float(np.nanpercentile(valid, 2)), float(np.nanpercentile(valid, 98))


def make_field_map(
    field_row,
    all_curry_fields_utm: gpd.GeoDataFrame,
    ndvi_path: Path,
    out_png: Path,
    ndvi_limits: tuple[float, float],
    soil_colors: dict[str, str],
) -> dict:
    available_fonts = {f.name for f in font_manager.fontManager.ttflist}
    annotation_font = "Arial" if "Arial" in available_fonts else "DejaVu Sans"

    field_id = field_row.field_id
    field_soil = field_row.soil_name if pd.notna(field_row.soil_name) else "Unknown"
    field_mean_ndvi = float(field_row.mean_ndvi) if pd.notna(field_row.mean_ndvi) else np.nan
    border_color = soil_colors.get(field_soil, "#ef4444")

    target_field = all_curry_fields_utm[all_curry_fields_utm["field_id"] == field_id].copy()
    if target_field.empty:
        return {"field_id": field_id, "map_path": str(out_png), "highlight_soil": field_soil}

    with rasterio.open(ndvi_path) as src:
        minx, miny, maxx, maxy = target_field.total_bounds
        width = maxx - minx
        height = maxy - miny
        pad_m = max(width, height) * 0.06
        pad_m = max(40.0, min(pad_m, 280.0))
        if field_id == "NM_FIELD_188":
            pad_m = max(25.0, min(pad_m * 0.45, 140.0))
        bbox = box(minx - pad_m, miny - pad_m, maxx + pad_m, maxy + pad_m)
        ndvi_clip, transform = mask(src, [bbox], crop=True, nodata=src.nodata)
        arr = ndvi_clip[0].astype(np.float32)
        if src.nodata is not None:
            arr = np.where(arr == src.nodata, np.nan, arr)

    fig, ax = plt.subplots(figsize=(10, 8))

    if field_id == "NM_FIELD_188":
        # Requested NDVI reclassification bins for NM_FIELD_188.
        ndvi_bins = [0.32, 0.33, 0.34, 0.35, 0.36, 0.37]
        ndvi_cmap = ListedColormap(["#fff3b0", "#ffd60a", "#b7e4c7", "#52b788", "#1b5e20"])
        ndvi_norm = BoundaryNorm(ndvi_bins, ndvi_cmap.N, clip=True)
        im = show(
            arr,
            transform=transform,
            ax=ax,
            cmap=ndvi_cmap,
            norm=ndvi_norm,
            alpha=0.78,
            interpolation="nearest",
            zorder=1,
        )
    else:
        im = show(
            arr,
            transform=transform,
            ax=ax,
            cmap="RdYlGn",
            vmin=ndvi_limits[0],
            vmax=ndvi_limits[1],
            alpha=0.78,
            interpolation="nearest",
            zorder=1,
        )

    target_field.boundary.plot(ax=ax, linewidth=3.2, color=border_color, alpha=1.0, zorder=3)
    ax.set_aspect("equal")

    ax.set_title(f"Curry field {field_id}: Zoomed NDVI (2020-03-07)")
    ax.set_axis_off()

    raster_artist = ax.images[-1]
    cbar = fig.colorbar(raster_artist, ax=ax, fraction=0.035, pad=0.02)
    if field_id == "NM_FIELD_188":
        cbar.set_ticks([0.32, 0.33, 0.34, 0.35, 0.36, 0.37])
        cbar.set_label("NDVI classes (NM_FIELD_188)")
    else:
        cbar.set_label("NDVI")

    legend_handles = [
        Line2D([0], [0], color=border_color, lw=3, label=f"Target field border ({field_soil})"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        framealpha=0.94,
        fontsize=12,
    )

    fig.text(
        0.5,
        0.062,
        f"Mean NDVI: {field_mean_ndvi:.3f}",
        ha="center",
        va="center",
        fontsize=20,
        fontfamily=annotation_font,
        color="#111827",
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0.02, 0.10, 0.98, 0.98))
    fig.savefig(out_png, dpi=300)
    plt.close(fig)

    return {
        "field_id": field_id,
        "soil_name": field_soil,
        "mean_ndvi": float(field_row.mean_ndvi),
        "map_path": str(out_png),
    }


def create_combined_curry_map(map_info: list[dict], out_png: Path) -> Path:
    ordered = sorted(map_info, key=lambda x: x["field_id"])
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, item in zip(axes, ordered, strict=False):
        img = plt.imread(item["map_path"])
        ax.imshow(img)
        ax.set_title(item["field_id"], fontsize=14)
        ax.axis("off")

    fig.suptitle("Curry Wheat Fields NDVI Maps (2020-03-07)", fontsize=16)
    fig.tight_layout(rect=(0.01, 0.04, 0.99, 0.94))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=300)
    plt.close(fig)
    return out_png


def update_run_metadata(metadata_path: Path, crs_checks: dict, curry_field_maps: list[dict], outputs: dict) -> None:
    payload = {
        "assignment": "assignment-07-zonal-stats",
        "analysis_date": "2026-03-23",
        "crs_checks": crs_checks,
        "curry_field_maps": curry_field_maps,
        "outputs": outputs,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    root = repo_root()
    fields, soil, counties, ndvi_path = load_inputs(root)

    crs_checks = check_crs(fields, soil, counties, ndvi_path)

    with rasterio.open(ndvi_path) as src:
        ndvi_crs = src.crs

    fields_utm = fields.to_crs(ndvi_crs)
    soil_utm = soil.to_crs(ndvi_crs)
    counties_utm = counties.to_crs(ndvi_crs)

    fields_utm = compute_mean_ndvi(fields_utm, ndvi_path)
    joined_utm = spatial_join_soil(fields_utm, soil_utm)

    data_out_dir = root / "data" / "imagery" / "assignment-07"
    geojson_path, csv_path = export_analysis_tables(joined_utm, data_out_dir)

    vmin, vmax = get_global_ndvi_limits(ndvi_path)

    asset_dir = root / "output" / "dashboard_assets"
    curry_fields = joined_utm[joined_utm["county"] == "Curry"].copy()
    curry_fields = curry_fields.sort_values(["years_as_winter_wheat", "field_id"], ascending=[False, True])

    unique_soils = [s for s in curry_fields["soil_name"].fillna("Unknown").unique()]
    soil_palette = ["#2563eb", "#16a34a", "#dc2626", "#7c3aed", "#ea580c"]
    soil_colors = {soil: soil_palette[i % len(soil_palette)] for i, soil in enumerate(sorted(unique_soils))}

    map_info: list[dict] = []
    for row in curry_fields.itertuples():
        out_png = asset_dir / f"integrated_spatial_analysis_curry_{row.field_id.lower()}.png"
        info = make_field_map(
            field_row=row,
            all_curry_fields_utm=curry_fields,
            ndvi_path=ndvi_path,
            out_png=out_png,
            ndvi_limits=(vmin, vmax),
            soil_colors=soil_colors,
        )
        map_info.append(info)

    combined_png = create_combined_curry_map(map_info, asset_dir / "integrated_spatial_analysis_curry_combined.png")

    metadata_path = data_out_dir / "assignment_07_run_metadata.json"
    update_run_metadata(
        metadata_path,
        crs_checks=crs_checks,
        curry_field_maps=map_info,
        outputs={
            "fields_with_mean_ndvi_geojson": str(geojson_path),
            "fields_with_mean_ndvi_csv": str(csv_path),
            "curry_field_maps": [m["map_path"] for m in map_info],
            "curry_combined_map": str(combined_png),
        },
    )

    print("Assignment 07 processing complete.")
    print(f"Fields processed: {len(joined_utm)}")
    print(f"Output GeoJSON: {geojson_path}")
    print(f"Output CSV: {csv_path}")
    for m in map_info:
        print(f"{m['field_id']}: {m['map_path']} (soil: {m['soil_name']})")


if __name__ == "__main__":
    main()

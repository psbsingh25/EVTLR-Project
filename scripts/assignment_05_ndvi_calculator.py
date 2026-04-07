#!/usr/bin/env python3
"""Generate March 2020 Landsat NIR and NDVI outputs for Assignment 05.

Workflow:
- Select top Winter Wheat fields per county using Assignment 06 logic
- Query Landsat Collection 2 Level-2 scenes from USGS STAC
- Choose a single March 2020 date with best field coverage / cloud score
- Build gridded NIR and RED mosaics clipped to selected fields
- Compute NDVI for that same day and export per-field NDVI rasters
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import requests
from rasterio.mask import mask
from rasterio.merge import merge
from shapely.geometry import shape

STAC_SEARCH_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
STAC_SIGN_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/sign"


@dataclass
class Config:
    repo_root: Path
    data_dir: Path
    output_dir: Path
    fields_path: Path
    crops_path: Path
    start_dt: str
    end_dt: str
    max_cloud_cover: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Landsat NIR and NDVI outputs")
    parser.add_argument("--start", default="2020-03-01T00:00:00Z")
    parser.add_argument("--end", default="2020-03-31T23:59:59Z")
    parser.add_argument("--max-cloud", type=float, default=40.0)
    parser.add_argument("--repo-root", default=".")
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> Config:
    repo_root = Path(args.repo_root).resolve()
    data_dir = repo_root / "data" / "imagery" / "assignment-05"
    output_dir = repo_root / "output" / "dashboard_assets" / "assignment-05"
    return Config(
        repo_root=repo_root,
        data_dir=data_dir,
        output_dir=output_dir,
        fields_path=repo_root / "data" / "boundaries" / "nm_top_200_fields.geojson",
        crops_path=repo_root / "data" / "crops" / "nm_cdl_2008_2020.csv",
        start_dt=args.start,
        end_dt=args.end,
        max_cloud_cover=args.max_cloud,
    )


def select_top_wheat_fields(cfg: Config) -> gpd.GeoDataFrame:
    fields = gpd.read_file(cfg.fields_path)
    crops = pd.read_csv(cfg.crops_path)

    county_map = dict(zip(fields["field_id"], fields["county"], strict=False))

    wheat = crops[crops["crop_name"].eq("Winter Wheat")].copy()
    wheat["county"] = wheat["field_id"].map(county_map)

    ranked = (
        wheat.groupby(["county", "field_id"], as_index=False)
        .size()
        .rename(columns={"size": "years_as_winter_wheat"})
        .sort_values(["county", "years_as_winter_wheat", "field_id"], ascending=[True, False, True])
    )

    selected = ranked.groupby("county", group_keys=False).head(3).copy()
    selected_ids = set(selected["field_id"])

    selected_fields = fields[fields["field_id"].isin(selected_ids)].copy()
    selected_fields = selected_fields.merge(selected, on=["county", "field_id"], how="left")
    selected_fields = selected_fields.sort_values(
        ["county", "years_as_winter_wheat", "field_id"], ascending=[True, False, True]
    )

    return selected_fields


def search_landsat_items(bbox: tuple[float, float, float, float], cfg: Config) -> list[dict]:
    payload = {
        "collections": ["landsat-c2-l2"],
        "bbox": list(bbox),
        "datetime": f"{cfg.start_dt}/{cfg.end_dt}",
        "limit": 500,
        "query": {
            "eo:cloud_cover": {"lte": cfg.max_cloud_cover},
        },
    }

    response = requests.post(STAC_SEARCH_URL, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    items = data.get("features", [])
    allowed_platforms = {"landsat-8", "landsat-9", "LANDSAT_8", "LANDSAT_9"}
    items = [i for i in items if i.get("properties", {}).get("platform") in allowed_platforms]
    return items


def sign_asset_href(href: str) -> str:
    response = requests.get(STAC_SIGN_URL, params={"href": href}, timeout=60)
    response.raise_for_status()
    return response.json()["href"]


def choose_best_single_day(
    items: list[dict], selected_fields: gpd.GeoDataFrame
) -> tuple[str, list[dict], dict]:
    field_geoms = {row.field_id: row.geometry for row in selected_fields.itertuples()}

    by_date: dict[str, list[dict]] = {}
    for item in items:
        date_key = item["properties"]["datetime"][:10]
        by_date.setdefault(date_key, []).append(item)

    scored_days = []
    for day, day_items in by_date.items():
        scene_geoms = [shape(item["geometry"]) for item in day_items]
        covered_fields = set()
        for field_id, geom in field_geoms.items():
            if any(scene_geom.intersects(geom) for scene_geom in scene_geoms):
                covered_fields.add(field_id)

        cloud_vals = [item["properties"].get("eo:cloud_cover", 100.0) for item in day_items]
        avg_cloud = float(np.mean(cloud_vals)) if cloud_vals else 100.0
        scored_days.append(
            {
                "date": day,
                "coverage_count": len(covered_fields),
                "avg_cloud": avg_cloud,
                "scene_count": len(day_items),
                "covered_fields": sorted(covered_fields),
            }
        )

    if not scored_days:
        raise RuntimeError("No candidate March 2020 Landsat-8/9 scenes found for AOI.")

    scored_days.sort(key=lambda d: (-d["coverage_count"], d["avg_cloud"], d["date"]))
    best = scored_days[0]
    return best["date"], by_date[best["date"]], best


def clip_remote_asset(
    item: dict, asset_key: str, out_path: Path, clip_geom, dst_crs: str = "EPSG:4326"
) -> Path:
    href = sign_asset_href(item["assets"][asset_key]["href"])

    with rasterio.open(href) as src:
        geom_series = gpd.GeoSeries([clip_geom], crs="EPSG:4326").to_crs(src.crs)
        out_image, out_transform = mask(src, [geom_series.iloc[0]], crop=True, nodata=0)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "compress": "lzw",
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(out_image)

    if dst_crs:
        with rasterio.open(out_path) as src:
            if str(src.crs) != dst_crs:
                # Keep native Landsat grid. No reprojection by design.
                pass

    return out_path


def build_clipped_mosaic(
    input_paths: list[Path], clip_geom, out_path: Path, nodata_value: float
) -> Path:
    srcs = [rasterio.open(str(p)) for p in input_paths]
    try:
        mosaic, transform = merge(srcs)
        meta = srcs[0].meta.copy()
        meta.update(
            {
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": transform,
                "count": 1,
                "compress": "lzw",
                "nodata": nodata_value,
            }
        )

        temp_path = out_path.with_name(f"{out_path.stem}_tmp{out_path.suffix}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(temp_path, "w", **meta) as tmp:
            tmp.write(mosaic)

        with rasterio.open(temp_path) as src:
            clip_series = gpd.GeoSeries([clip_geom], crs="EPSG:4326").to_crs(src.crs)
            clipped, clipped_transform = mask(
                src, [clip_series.iloc[0]], crop=True, nodata=nodata_value
            )
            clipped_meta = src.meta.copy()
            clipped_meta.update(
                {
                    "height": clipped.shape[1],
                    "width": clipped.shape[2],
                    "transform": clipped_transform,
                    "nodata": nodata_value,
                }
            )

        with rasterio.open(out_path, "w", **clipped_meta) as dst:
            dst.write(clipped)

        temp_path.unlink(missing_ok=True)
        return out_path
    finally:
        for src in srcs:
            src.close()


def compute_ndvi(red_path: Path, nir_path: Path, ndvi_path: Path) -> Path:
    ndvi_nodata = np.float32(-9999.0)
    with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
        red = red_src.read(1).astype(np.float32)
        nir = nir_src.read(1).astype(np.float32)

        red_nodata = red_src.nodata if red_src.nodata is not None else 0
        nir_nodata = nir_src.nodata if nir_src.nodata is not None else 0

        denom = nir + red
        valid = (red != red_nodata) & (nir != nir_nodata) & (denom != 0)

        ndvi = np.full(red.shape, ndvi_nodata, dtype=np.float32)
        ndvi[valid] = (nir[valid] - red[valid]) / denom[valid]

        profile = red_src.profile.copy()
        profile.update(dtype="float32", count=1, compress="lzw", nodata=ndvi_nodata)

    ndvi_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(ndvi_path, "w", **profile) as dst:
        dst.write(ndvi, 1)

    return ndvi_path


def export_per_field_ndvi(
    ndvi_path: Path, selected_fields: gpd.GeoDataFrame, output_dir: Path, date_key: str
) -> list[Path]:
    outputs: list[Path] = []
    with rasterio.open(ndvi_path) as src:
        for row in selected_fields.itertuples():
            geom_series = gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_crs(src.crs)
            clipped, transform = mask(src, [geom_series.iloc[0]], crop=True, nodata=src.nodata)
            profile = src.profile.copy()
            profile.update(
                {
                    "height": clipped.shape[1],
                    "width": clipped.shape[2],
                    "transform": transform,
                }
            )

            out_path = (
                output_dir / "ndvi_per_field" / f"{row.county}_{row.field_id}_ndvi_{date_key}.tif"
            )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with rasterio.open(out_path, "w", **profile) as dst:
                dst.write(clipped)
            outputs.append(out_path)

    return outputs


def save_preview_png(
    raster_path: Path, png_path: Path, title: str, cmap: str, vmin=None, vmax=None
) -> Path:
    with rasterio.open(raster_path) as src:
        arr = src.read(1).astype(np.float32)
        nodata = src.nodata
        if nodata is not None:
            arr = np.where(arr == nodata, np.nan, arr)

    plt.figure(figsize=(12, 8))
    plt.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.title(title)
    plt.colorbar(shrink=0.8)
    plt.axis("off")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path


def export_per_field_pngs(
    raster_path: Path,
    selected_fields: gpd.GeoDataFrame,
    output_dir: Path,
    date_key: str,
    product_name: str,
    cmap: str,
    fixed_range: tuple[float, float] | None = None,
) -> list[Path]:
    png_outputs: list[Path] = []

    with rasterio.open(raster_path) as src:
        nodata = src.nodata

        for row in selected_fields.itertuples():
            geom_series = gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_crs(src.crs)
            clipped, _ = mask(src, [geom_series.iloc[0]], crop=True, nodata=nodata)
            arr = clipped[0].astype(np.float32)

            if nodata is not None:
                arr = np.where(arr == nodata, np.nan, arr)

            valid = np.isfinite(arr)
            if not valid.any():
                continue

            if fixed_range is None:
                vmin = float(np.nanpercentile(arr, 2))
                vmax = float(np.nanpercentile(arr, 98))
                if np.isclose(vmin, vmax):
                    vmin = float(np.nanmin(arr))
                    vmax = float(np.nanmax(arr))
            else:
                vmin, vmax = fixed_range

            out_path = (
                output_dir / "fields" / f"{row.county}_{row.field_id}_{product_name}_{date_key}.png"
            )
            out_path.parent.mkdir(parents=True, exist_ok=True)

            fig, ax = plt.subplots(figsize=(6, 6))
            im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
            ax.set_title(f"{product_name.upper()} {row.county} {row.field_id} ({date_key})")
            ax.axis("off")
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            fig.tight_layout()
            fig.savefig(out_path, dpi=300)
            plt.close(fig)

            png_outputs.append(out_path)

    return png_outputs


def main() -> None:
    args = parse_args()
    cfg = build_config(args)

    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    selected_fields = select_top_wheat_fields(cfg)
    if selected_fields.empty:
        raise RuntimeError("No Winter Wheat fields were selected from input data.")

    selected_fields_path = cfg.data_dir / "selected_wheat_fields.geojson"
    selected_fields_csv = cfg.data_dir / "selected_wheat_fields.csv"
    selected_fields.to_file(selected_fields_path, driver="GeoJSON")
    selected_fields.drop(columns="geometry").to_csv(selected_fields_csv, index=False)

    if hasattr(selected_fields.geometry, "union_all"):
        union_geom = selected_fields.geometry.union_all()
    else:
        union_geom = selected_fields.unary_union
    bbox = selected_fields.total_bounds

    items = search_landsat_items(tuple(bbox), cfg)
    if not items:
        raise RuntimeError("No Landsat-8/9 items found for March 2020 AOI and cloud filter.")

    chosen_day, day_items, day_score = choose_best_single_day(items, selected_fields)
    date_key = chosen_day.replace("-", "")

    staged_dir = cfg.data_dir / "staged_clips"
    nir_clips: list[Path] = []
    red_clips: list[Path] = []
    manifest_rows = []

    for item in day_items:
        scene_id = item["id"]
        platform = item["properties"].get("platform")
        cloud_cover = item["properties"].get("eo:cloud_cover")

        nir_clip = staged_dir / f"{scene_id}_nir08_clip.tif"
        red_clip = staged_dir / f"{scene_id}_red_clip.tif"

        clip_remote_asset(item, "nir08", nir_clip, union_geom)
        clip_remote_asset(item, "red", red_clip, union_geom)

        nir_clips.append(nir_clip)
        red_clips.append(red_clip)

        manifest_rows.append(
            {
                "scene_id": scene_id,
                "date": chosen_day,
                "platform": platform,
                "cloud_cover": cloud_cover,
                "nir_asset": item["assets"]["nir08"]["href"],
                "red_asset": item["assets"]["red"]["href"],
                "nir_clip_path": str(nir_clip),
                "red_clip_path": str(red_clip),
            }
        )

    nir_grid = cfg.data_dir / f"nir_gridded_{date_key}.tif"
    red_grid = cfg.data_dir / f"red_gridded_{date_key}.tif"
    ndvi_grid = cfg.data_dir / f"ndvi_{date_key}.tif"

    build_clipped_mosaic(nir_clips, union_geom, nir_grid, nodata_value=0)
    build_clipped_mosaic(red_clips, union_geom, red_grid, nodata_value=0)
    compute_ndvi(red_grid, nir_grid, ndvi_grid)

    per_field_ndvi = export_per_field_ndvi(ndvi_grid, selected_fields, cfg.data_dir, date_key)

    per_field_nir_pngs = export_per_field_pngs(
        nir_grid,
        selected_fields,
        cfg.output_dir,
        date_key,
        product_name="nir",
        cmap="YlGn",
    )
    per_field_ndvi_pngs = export_per_field_pngs(
        ndvi_grid,
        selected_fields,
        cfg.output_dir,
        date_key,
        product_name="ndvi",
        cmap="RdYlGn",
        fixed_range=(-1.0, 1.0),
    )

    nir_png = cfg.output_dir / f"nir_gridded_{date_key}.png"
    ndvi_png = cfg.output_dir / f"ndvi_gridded_{date_key}.png"
    save_preview_png(nir_grid, nir_png, f"Gridded Landsat NIR ({chosen_day})", cmap="YlGn")
    save_preview_png(
        ndvi_grid,
        ndvi_png,
        f"NDVI for Selected NM Wheat Fields ({chosen_day})",
        cmap="RdYlGn",
        vmin=-1,
        vmax=1,
    )

    manifest_path = cfg.data_dir / "landsat_scene_manifest.csv"
    pd.DataFrame(manifest_rows).to_csv(manifest_path, index=False)

    selection_meta = {
        "chosen_date": chosen_day,
        "selection_score": day_score,
        "selected_field_count": int(len(selected_fields)),
        "selected_fields": selected_fields[["county", "field_id", "years_as_winter_wheat"]]
        .sort_values(["county", "years_as_winter_wheat", "field_id"], ascending=[True, False, True])
        .to_dict(orient="records"),
        "outputs": {
            "nir_grid_tif": str(nir_grid),
            "red_grid_tif": str(red_grid),
            "ndvi_grid_tif": str(ndvi_grid),
            "nir_png": str(nir_png),
            "ndvi_png": str(ndvi_png),
            "per_field_ndvi_count": len(per_field_ndvi),
            "per_field_nir_png_count": len(per_field_nir_pngs),
            "per_field_ndvi_png_count": len(per_field_ndvi_pngs),
            "manifest_csv": str(manifest_path),
            "selected_fields_geojson": str(selected_fields_path),
            "selected_fields_csv": str(selected_fields_csv),
        },
    }

    meta_path = cfg.data_dir / "run_metadata.json"
    meta_path.write_text(json.dumps(selection_meta, indent=2), encoding="utf-8")

    print("Assignment 05 NDVI pipeline completed.")
    print(f"Chosen date: {chosen_day}")
    print(f"Selected fields: {len(selected_fields)}")
    print(f"NIR grid: {nir_grid}")
    print(f"NDVI grid: {ndvi_grid}")
    print(f"Per-field NDVI rasters: {len(per_field_ndvi)}")
    print(f"Per-field NIR PNGs: {len(per_field_nir_pngs)}")
    print(f"Per-field NDVI PNGs: {len(per_field_ndvi_pngs)}")


if __name__ == "__main__":
    main()

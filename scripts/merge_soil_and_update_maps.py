#!/usr/bin/env python3
"""Merge soil data with fields and create updated interactive maps."""

from pathlib import Path

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "assignment-02"

# Crop color mapping
CROP_COLORS = {
    "Corn": "#FFD700",
    "Soybeans": "#90EE90",
    "Winter Wheat": "#DAA520",
    "Spring Wheat": "#F0E68C",
    "Cotton": "#F5F5DC",
    "Sorghum": "#CD853F",
    "Grassland/Pasture": "#228B22",
    "Shrubland": "#8FBC8F",
    "Alfalfa": "#32CD32",
    "Fallow/Idle Cropland": "#DEB887",
    "Developed/Low Intensity": "#A9A9A9",
    "Developed/Medium Intensity": "#696969",
    "Water": "#1E90FF",
    "Unknown": "#808080",
}


def get_dominant_soil_per_field(soil_df):
    """Get dominant soil component per field."""
    print("Aggregating soil data per field...")

    # Group by field_id and get the component with highest comppct_r
    dominant_idx = soil_df.groupby("field_id")["comppct_r"].idxmax()
    dominant_soil = soil_df.loc[dominant_idx].copy()

    # Calculate weighted averages for numeric columns
    numeric_cols = [
        "om_r",
        "ph1to1h2o_r",
        "awc_r",
        "claytotal_r",
        "sandtotal_r",
        "silttotal_r",
        "dbthirdbar_r",
        "cec7_r",
    ]

    field_soil_summary = []

    for field_id in soil_df["field_id"].unique():
        field_data = soil_df[soil_df["field_id"] == field_id]

        # Get dominant component
        dominant = field_data.loc[field_data["comppct_r"].idxmax()]

        # Calculate weighted averages
        weights = field_data["comppct_r"].values
        weights = weights / weights.sum()  # Normalize

        summary = {
            "field_id": field_id,
            "soil_name": dominant["compname"],
            "soil_pct": dominant["comppct_r"],
            "drainage": dominant["drainagecl"],
            "mukey": dominant["mukey"],
        }

        # Add weighted averages
        for col in numeric_cols:
            if col in field_data.columns:
                values = field_data[col].values
                if not pd.isna(values).all():
                    summary[f"{col}_avg"] = np.average(values, weights=weights)
                else:
                    summary[f"{col}_avg"] = np.nan

        field_soil_summary.append(summary)

    return pd.DataFrame(field_soil_summary)


def merge_soil_with_fields():
    """Merge soil data with field boundaries."""
    print("=" * 70)
    print("MERGING SOIL DATA WITH FIELDS")
    print("=" * 70)

    # Load data
    print("\nLoading field boundaries...")
    fields = gpd.read_file(OUTPUT_DIR / "fields_with_crops.geojson")
    print(f"Loaded {len(fields)} fields")

    print("Loading soil data...")
    soil = pd.read_csv(OUTPUT_DIR / "soil_EPSG4326.csv")
    print(f"Loaded {len(soil)} soil records")

    # Get dominant soil per field
    soil_summary = get_dominant_soil_per_field(soil)
    print(f"Created soil summary for {len(soil_summary)} fields")

    # Merge with fields
    merged = fields.merge(soil_summary, on="field_id", how="left")
    print(f"Merged data: {len(merged)} fields")

    # Save merged data
    merged.to_file(OUTPUT_DIR / "fields_with_crops_soil.geojson", driver="GeoJSON")
    print("✓ Saved: fields_with_crops_soil.geojson")

    # Also save soil summary as CSV
    soil_summary.to_csv(OUTPUT_DIR / "soil_summary_by_field.csv", index=False)
    print("✓ Saved: soil_summary_by_field.csv")

    return merged


def create_map_with_soil(fields_gdf, output_name, title, corn_only=False):
    """Create interactive map with soil and crop data."""
    print(f"\nCreating map: {title}...")

    # Calculate center
    center = fields_gdf.geometry.union_all().centroid

    # Create base map
    m = folium.Map(
        location=[center.y, center.x], zoom_start=9 if not corn_only else 10, tiles="OpenStreetMap"
    )

    # Add satellite layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add fields with detailed popups
    for idx, row in fields_gdf.iterrows():
        crop = row["dominant_crop"]
        color = CROP_COLORS.get(crop, "#808080")

        # Create detailed popup
        popup_content = f"""
        <b>Field ID:</b> {row["field_id"]}<br>
        <b>County:</b> {row["county"]}<br>
        <b>Area:</b> {row["area_acres"]:.1f} acres<br>
        <b>Crop:</b> {crop}<br>
        <b>Coverage:</b> {row["dominant_pct"]:.1f}%<br>
        <hr>
        <b>Soil:</b> {row.get("soil_name", "N/A")}<br>
        <b>Drainage:</b> {row.get("drainage", "N/A")}<br>
        <b>pH:</b> {row.get("ph1to1h2o_r_avg", "N/A"):.2f}<br>
        <b>Organic Matter:</b> {row.get("om_r_avg", "N/A"):.2f}%<br>
        <b>Clay:</b> {row.get("claytotal_r_avg", "N/A"):.1f}%<br>
        <b>Sand:</b> {row.get("sandtotal_r_avg", "N/A"):.1f}%<br>
        <b>AWC:</b> {row.get("awc_r_avg", "N/A"):.3f}<br>
        """

        style = {
            "fillColor": color,
            "color": "black",
            "weight": 2 if corn_only else 1,
            "fillOpacity": 0.7,
        }

        folium.GeoJson(
            row.geometry,
            style_function=lambda x, style=style: style,
            popup=folium.Popup(popup_content, max_width=350),
        ).add_to(m)

    # Add marker cluster for corn fields
    if corn_only:
        marker_cluster = MarkerCluster(name="Corn Fields").add_to(m)
        for idx, row in fields_gdf.iterrows():
            centroid = row.geometry.centroid
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"{row['field_id']}<br>pH: {row.get('ph1to1h2o_r_avg', 'N/A'):.2f}",
                icon=folium.Icon(color="orange", icon="leaf", prefix="fa"),
            ).add_to(marker_cluster)

    # Add legend
    if not corn_only:
        legend_html = """
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 200px;
                    border:2px solid grey; z-index:9999; 
                    background-color:white; padding: 10px;
                    font-size:12px;
                    max-height: 400px;
                    overflow-y: auto;">
        <b>Crop Types</b><br>
        """

        for crop in fields_gdf["dominant_crop"].unique():
            if crop and crop != "Unknown":
                count = len(fields_gdf[fields_gdf["dominant_crop"] == crop])
                color = CROP_COLORS.get(crop, "#808080")
                legend_html += f'<i style="background:{color};width:10px;height:10px;display:inline-block;margin-right:5px;"></i>{crop} ({count})<br>'

        legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(legend_html))

    # Add title
    title_html = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 350px;
                background-color: white; padding: 10px;
                border: 2px solid grey; z-index:9999;
                font-size: 14px; font-weight: bold;">
    {title}<br>
    <span style="font-size: 11px; font-weight: normal;">
    Click fields for soil data • {len(fields_gdf)} fields
    </span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save
    output_path = OUTPUT_DIR / output_name
    m.save(output_path)
    print(f"✓ Saved: {output_path}")
    print(f"  Fields: {len(fields_gdf)}")


def create_soil_analysis_summary(soil_summary):
    """Create a summary of soil characteristics."""
    print("\n" + "=" * 70)
    print("SOIL ANALYSIS SUMMARY")
    print("=" * 70)

    print(f"\nTotal fields analyzed: {len(soil_summary)}")

    print("\nSoil Texture Distribution:")
    print(f"  Avg Clay: {soil_summary['claytotal_r_avg'].mean():.1f}%")
    print(f"  Avg Sand: {soil_summary['sandtotal_r_avg'].mean():.1f}%")
    print(f"  Avg Silt: {soil_summary['silttotal_r_avg'].mean():.1f}%")

    print("\nChemical Properties:")
    print(f"  Avg pH: {soil_summary['ph1to1h2o_r_avg'].mean():.2f}")
    print(f"  Avg Organic Matter: {soil_summary['om_r_avg'].mean():.2f}%")
    print(f"  Avg CEC: {soil_summary['cec7_r_avg'].mean():.1f}")

    print("\nDrainage Classes:")
    print(soil_summary["drainage"].value_counts())

    print("\nDominant Soil Series (Top 10):")
    print(soil_summary["soil_name"].value_counts().head(10))


def main():
    """Main execution."""
    print("#" * 70)
    print("# MERGING SOIL DATA AND UPDATING MAPS")
    print("# Southern High Plains Aquifer - NM Counties")
    print("#" * 70)
    print()

    # Merge soil with fields
    merged = merge_soil_with_fields()

    # Create soil analysis
    soil_summary = pd.read_csv(OUTPUT_DIR / "soil_summary_by_field.csv")
    create_soil_analysis_summary(soil_summary)

    # Create updated map for all fields
    print("\n" + "=" * 70)
    print("CREATING UPDATED MAPS")
    print("=" * 70)

    create_map_with_soil(
        merged,
        "my_fields_map_with_soil.html",
        "🌾 Agricultural Fields with Soil Data",
        corn_only=False,
    )

    # Create map for corn fields
    corn_fields = merged[
        merged["field_id"].isin(pd.read_csv(OUTPUT_DIR / "soil_summary_by_field.csv")["field_id"])
        & merged["field_id"].isin(
            ["NM_FIELD_188", "NM_FIELD_025", "NM_FIELD_130", "NM_FIELD_078", "NM_FIELD_065"]
        )
    ]

    if len(corn_fields) > 0:
        # Get the corn fields from the merged data
        corn_gdf = merged[
            merged["field_id"].isin(
                ["NM_FIELD_188", "NM_FIELD_025", "NM_FIELD_130", "NM_FIELD_078", "NM_FIELD_065"]
            )
        ]

        create_map_with_soil(
            corn_gdf,
            "my_fields_corn_map_with_soil.html",
            "🌽 Corn Fields with Soil Characteristics",
            corn_only=True,
        )

    # Summary
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"\nFiles created in {OUTPUT_DIR}:")
    print("  ✓ soil_EPSG4326.csv (detailed soil data)")
    print("  ✓ soil_summary_by_field.csv (aggregated by field)")
    print("  ✓ fields_with_crops_soil.geojson (merged data)")
    print("  ✓ my_fields_map_with_soil.html (all fields + soil)")
    print("  ✓ my_fields_corn_map_with_soil.html (corn fields + soil)")

    print("\nTo view the maps:")
    print("  1. Open http://localhost:8000/my_fields_map_with_soil.html")
    print("  2. Open http://localhost:8000/my_fields_corn_map_with_soil.html")


if __name__ == "__main__":
    main()

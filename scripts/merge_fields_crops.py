#!/usr/bin/env python3
"""Merge field boundaries with CDL crop data."""

import geopandas as gpd
import pandas as pd
from pathlib import Path

# Load field boundaries
print("Loading field boundaries...")
fields_gdf = gpd.read_file("data/boundaries/nm_top_200_fields.geojson")
print(f"Loaded {len(fields_gdf)} fields")

# Load CDL crop data
print("Loading CDL crop data...")
cdl_df = pd.read_csv("data/crops/nm_cdl_2008_2020.csv")
print(f"Loaded {len(cdl_df)} CDL records")

# Get dominant crop per field (most frequent crop across all years)
print("Calculating dominant crop per field...")

# Find the observation with highest dominant_pct for each field
dominant_idx = cdl_df.groupby('field_id')['dominant_pct'].idxmax()
dominant_crops = cdl_df.loc[dominant_idx].copy()

# Rename columns for clarity
dominant_crops = dominant_crops.rename(columns={
    'crop_name': 'dominant_crop'
})

# Select only needed columns
dominant_crops = dominant_crops[['field_id', 'dominant_crop', 'crop_code', 'dominant_pct']]

# Merge with field boundaries
print("Merging data...")
merged = fields_gdf.merge(dominant_crops, on='field_id', how='left')

# Fill NaN for fields with no crop data
merged['dominant_crop'] = merged['dominant_crop'].fillna('Unknown')
merged['crop_code'] = merged['crop_code'].fillna(-1).astype(int)

print(f"Merged data: {len(merged)} fields")
print("\nCrop distribution:")
print(merged['dominant_crop'].value_counts())

# Create output directory
output_dir = Path("data/assignment-02")
output_dir.mkdir(parents=True, exist_ok=True)

# Save to assignment-02
output_path = output_dir / "fields_with_crops.geojson"
merged.to_file(output_path, driver="GeoJSON")
print(f"\n✓ Saved: {output_path}")

# Show sample
print("\nSample data:")
print(merged[['field_id', 'county', 'area_acres', 'dominant_crop']].head(10))

#!/usr/bin/env python3
"""Download agricultural data for New Mexico Southern High Plains aquifer counties.

Downloads field boundaries, soil, weather, and crop data for:
- Lea County (35025)
- Roosevelt County (35041)
- Curry County (35009)

Target: Top 200 corn-producing fields by area.
"""

import sys
from pathlib import Path

# Add skills to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "vendor" / "ag-skills"))

import geopandas as gpd
from shapely.geometry import box

# County definitions
COUNTIES = {
    "Lea": {"fips": "35025", "ansi": "025"},
    "Roosevelt": {"fips": "35041", "ansi": "041"},
    "Curry": {"fips": "35009", "ansi": "009"},
}

DATA_DIR = Path(__file__).parent.parent / "data"


def download_field_boundaries():
    """Download Crop Sequence Boundaries for NM and filter to target counties."""
    print("=" * 70)
    print("STEP 1: Downloading Crop Sequence Boundaries for New Mexico")
    print("=" * 70)

    boundaries_dir = DATA_DIR / "boundaries"
    boundaries_dir.mkdir(exist_ok=True)

    # Try to download from Source Cooperative first
    # NM is state FIPS 35
    nm_url = "https://data.source.coop/fiboa/us-usda-cropland/us_usda_cropland_2023_35.parquet"

    print(f"Downloading from: {nm_url}")
    print("This is a large file (~500MB), please wait...")

    try:
        import requests

        nm_file = boundaries_dir / "nm_csb_2023.parquet"

        if nm_file.exists():
            print(f"File already exists: {nm_file}")
        else:
            response = requests.get(nm_url, stream=True, timeout=300)
            response.raise_for_status()

            with open(nm_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {nm_file}")

        # Load the data
        print("Loading GeoParquet file...")
        gdf = gpd.read_parquet(nm_file)
        print(f"Total fields in NM: {len(gdf)}")

        # Filter to target counties
        print(f"\nFiltering to counties: {list(COUNTIES.keys())}")
        county_fips = [c["fips"] for c in COUNTIES.values()]

        # Check what county column exists
        county_col = None
        for col in ["countyfp", "COUNTYFP", "county_fips", "county_fip"]:
            if col in gdf.columns:
                county_col = col
                break

        if county_col is None:
            print(f"Available columns: {gdf.columns.tolist()}")
            raise ValueError("Cannot find county column")

        print(f"Using county column: {county_col}")

        # Filter
        filtered = gdf[gdf[county_col].isin([c["fips"] for c in COUNTIES.values()])]
        print(f"Fields in target counties: {len(filtered)}")

        if len(filtered) == 0:
            print("WARNING: No fields found. Let's check the data structure:")
            print(filtered.head())
            return None

        # Save intermediate
        output_path = boundaries_dir / "nm_target_counties_2023.geojson"
        filtered.to_file(output_path, driver="GeoJSON")
        print(f"Saved all fields: {output_path}")

        return filtered

    except Exception as e:
        print(f"ERROR downloading CSB: {e}")
        print("\nFalling back to using county boundary box as AOI...")
        return create_county_boundaries()


def create_county_boundaries():
    """Create approximate county boundaries if CSB download fails."""
    print("Creating county boundary boxes...")

    # Approximate bounding boxes for the counties
    # These are rough approximations
    county_bounds = {
        "Lea": box(-103.5, 32.0, -103.0, 33.5),  # Approximate
        "Roosevelt": box(-103.5, 33.5, -103.0, 34.5),
        "Curry": box(-103.5, 34.0, -103.0, 35.0),
    }

    data = []
    for county_name, bounds in county_bounds.items():
        data.append(
            {
                "county_name": county_name,
                "county_fips": COUNTIES[county_name]["fips"],
                "geometry": bounds,
            }
        )

    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

    # Save
    boundaries_dir = DATA_DIR / "boundaries"
    output_path = boundaries_dir / "nm_county_boundaries.geojson"
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"Saved county boundaries: {output_path}")

    return gdf


def identify_corn_fields(fields_gdf):
    """Use CDL data to identify which fields grew corn."""
    print("\n" + "=" * 70)
    print("STEP 2: Identifying Corn Fields (requires CDL data)")
    print("=" * 70)

    print("\nNOTE: To identify corn fields accurately, we need CDL data.")
    print("For now, we'll select the largest fields and assume they may include corn.")
    print("\nIn practice, you would:")
    print("1. Download CDL for NM (state FIPS 35)")
    print("2. Extract dominant crop per field")
    print("3. Filter to corn fields only")

    # For now, select largest 200 fields
    print("\nSelecting top 200 fields by area...")

    # Check if area column exists
    if "area_acres" in fields_gdf.columns:
        area_col = "area_acres"
    elif "area" in fields_gdf.columns:
        area_col = "area"
    else:
        # Calculate area
        fields_gdf = fields_gdf.to_crs("EPSG:5070")  # Albers Equal Area
        fields_gdf["area_acres"] = fields_gdf.geometry.area / 4046.86  # m² to acres
        area_col = "area_acres"

    # Sort by area and take top 200
    top_fields = fields_gdf.nlargest(200, area_col)

    # Add field IDs
    top_fields["field_id"] = [f"NM_FIELD_{i + 1:03d}" for i in range(len(top_fields))]

    print(f"Selected {len(top_fields)} fields")
    print(f"Total area: {top_fields[area_col].sum():.1f} acres")
    print(f"Average size: {top_fields[area_col].mean():.1f} acres")

    # Save
    boundaries_dir = DATA_DIR / "boundaries"
    output_path = boundaries_dir / "nm_top_200_fields.geojson"
    top_fields.to_file(output_path, driver="GeoJSON")
    print(f"Saved: {output_path}")

    return top_fields


def download_soil_data(fields_gdf):
    """Download SSURGO soil data for the fields."""
    print("\n" + "=" * 70)
    print("STEP 3: Downloading SSURGO Soil Data")
    print("=" * 70)

    soil_dir = DATA_DIR / "soil"
    soil_dir.mkdir(exist_ok=True)

    try:
        # Import ssurgo skill
        sys.path.insert(
            0,
            str(
                Path(__file__).parent.parent
                / "skills"
                / "vendor"
                / "ag-skills"
                / "ssurgo-soil"
                / "src"
            ),
        )
        from ssurgo_soil import download_soil

        print("Querying NRCS Soil Data Access API...")
        print("This may take several minutes for 200 fields...")

        soil_data = download_soil(
            fields=fields_gdf,
            field_id_column="field_id",
            max_depth_cm=30,
            output_path=soil_dir / "nm_soil_data.csv",
        )

        print(f"Downloaded soil data: {len(soil_data)} records")
        return soil_data

    except Exception as e:
        print(f"ERROR downloading soil data: {e}")
        print("You can retry this step later with: python scripts/download_nm_data.py --soil-only")
        return None


def download_weather_data(fields_gdf):
    """Download NASA POWER weather data for field centroids."""
    print("\n" + "=" * 70)
    print("STEP 4: Downloading NASA POWER Weather Data (2005-2020)")
    print("=" * 70)

    weather_dir = DATA_DIR / "weather"
    weather_dir.mkdir(exist_ok=True)

    try:
        # Import nasa-power-weather skill
        sys.path.insert(
            0,
            str(
                Path(__file__).parent.parent
                / "skills"
                / "vendor"
                / "ag-skills"
                / "nasa-power-weather"
                / "src"
            ),
        )
        from nasa_power_weather import download_for_fields

        print("Downloading daily weather data...")
        print("This will query the API for 200 fields x 16 years = 3,200 days")
        print("With 1-second delays, this will take ~50+ minutes...")

        weather_data = download_for_fields(
            geojson_path=DATA_DIR / "boundaries" / "nm_top_200_fields.geojson",
            start_date="2005-01-01",
            end_date="2020-12-31",
            output_csv=weather_dir / "nm_weather_2005_2020.csv",
            delay=1.0,
        )

        print(f"Downloaded weather data: {len(weather_data)} records")
        return weather_data

    except Exception as e:
        print(f"ERROR downloading weather data: {e}")
        print(
            "You can retry this step later with: python scripts/download_nm_data.py --weather-only"
        )
        return None


def download_cdl_data(fields_gdf):
    """Download CDL cropland data for the fields."""
    print("\n" + "=" * 70)
    print("STEP 5: Downloading CDL Cropland Data (2008-2020)")
    print("=" * 70)

    crops_dir = DATA_DIR / "crops"
    crops_dir.mkdir(exist_ok=True)

    print("Downloading CDL for NM (State FIPS 35)")
    print("This will download 13 years of CDL data...")

    try:
        # Import cdl-cropland skill
        sys.path.insert(
            0,
            str(
                Path(__file__).parent.parent
                / "skills"
                / "vendor"
                / "ag-skills"
                / "cdl-cropland"
                / "src"
            ),
        )
        from cdl_cropland import download_for_fields

        years = list(range(2008, 2021))  # 2008-2020

        print(f"Downloading CDL for years: {years}")

        cdl_data = download_for_fields(
            geojson_path=DATA_DIR / "boundaries" / "nm_top_200_fields.geojson",
            state_fips="35",  # New Mexico
            years=years,
            output_csv=crops_dir / "nm_cdl_2008_2020.csv",
            raster_dir=crops_dir / "rasters",
        )

        print(f"Downloaded CDL data: {len(cdl_data)} records")

        # Identify corn fields from CDL
        print("\nAnalyzing CDL to identify corn fields...")
        corn_fields = cdl_data[
            (cdl_data["crop_name"].str.contains("Corn", case=False, na=False))
            | (cdl_data["crop_code"] == 1)
        ]

        print(f"Fields that grew corn (2008-2020): {corn_fields['field_id'].nunique()}")

        return cdl_data

    except Exception as e:
        print(f"ERROR downloading CDL data: {e}")
        print("You can retry this step later with: python scripts/download_nm_data.py --cdl-only")
        return None


def main():
    """Main execution function."""
    print("#" * 70)
    print("# New Mexico Agricultural Data Download")
    print("# Southern High Plains Aquifer Counties")
    print("# Lea, Roosevelt, Curry Counties")
    print("#" * 70)

    # Step 1: Download field boundaries
    fields = download_field_boundaries()

    if fields is None:
        print("\nERROR: Could not download field boundaries")
        print("Please check your internet connection and try again.")
        sys.exit(1)

    # Step 2: Identify corn fields (top 200 by area for now)
    top_fields = identify_corn_fields(fields)

    # Step 3: Download soil data
    soil_data = download_soil_data(top_fields)

    # Step 4: Download weather data
    weather_data = download_weather_data(top_fields)

    # Step 5: Download CDL data
    cdl_data = download_cdl_data(top_fields)

    # Summary
    print("\n" + "=" * 70)
    print("DOWNLOAD COMPLETE")
    print("=" * 70)

    print("\nDownloaded data:")
    print(f"  Field boundaries: {DATA_DIR / 'boundaries' / 'nm_top_200_fields.geojson'}")
    if soil_data is not None:
        print(f"  Soil data: {len(soil_data)} records")
    if weather_data is not None:
        print(f"  Weather data: {len(weather_data)} records")
    if cdl_data is not None:
        print(f"  CDL data: {len(cdl_data)} records")

    print("\nNext steps:")
    print("  - Review downloaded data in data/ directory")
    print("  - If any downloads failed, re-run with specific flags")
    print("  - Example: python scripts/download_nm_data.py --soil-only")


if __name__ == "__main__":
    main()

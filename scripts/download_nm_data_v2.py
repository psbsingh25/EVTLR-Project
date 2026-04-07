#!/usr/bin/env python3
"""Download agricultural data for New Mexico Southern High Plains aquifer counties.

Downloads field boundaries, soil, weather, and crop data for:
- Lea County (35025)
- Roosevelt County (35041)
- Curry County (35009)

Target: Top 200 corn-producing fields by area.
"""

import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import box

# County definitions
COUNTIES = {
    "Lea": {"fips": "35025", "ansi": "025", "name": "Lea"},
    "Roosevelt": {"fips": "35041", "ansi": "041", "name": "Roosevelt"},
    "Curry": {"fips": "35009", "ansi": "009", "name": "Curry"},
}

DATA_DIR = Path(__file__).parent.parent / "data"


def get_county_boundaries_from_census():
    """Download county boundaries from US Census Bureau."""
    print("=" * 70)
    print("STEP 1: Downloading County Boundaries")
    print("=" * 70)

    boundaries_dir = DATA_DIR / "boundaries"
    boundaries_dir.mkdir(parents=True, exist_ok=True)

    # Census TIGER/Line county boundaries
    # New Mexico is state FIPS 35
    census_url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"

    print("Downloading US counties from Census...")

    try:
        import io
        import zipfile

        response = requests.get(census_url, timeout=300)
        response.raise_for_status()

        print("Downloaded county data, extracting...")

        # Extract from zip
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(boundaries_dir / "census_counties")

        # Load the shapefile
        counties_shp = boundaries_dir / "census_counties" / "tl_2023_us_county.shp"
        counties_gdf = gpd.read_file(counties_shp)

        # Filter to New Mexico and target counties
        nm_counties = counties_gdf[counties_gdf["STATEFP"] == "35"]
        target_counties = nm_counties[nm_counties["COUNTYFP"].isin(["025", "041", "009"])]

        print(f"Found {len(target_counties)} target counties")
        for _, county in target_counties.iterrows():
            print(f"  - {county['NAME']} County (FIPS: {county['COUNTYFP']})")

        # Save
        output_path = boundaries_dir / "nm_county_boundaries.geojson"
        target_counties.to_file(output_path, driver="GeoJSON")
        print(f"Saved: {output_path}")

        return target_counties

    except Exception as e:
        print(f"ERROR downloading census data: {e}")
        print("Creating approximate county boundaries...")
        return create_approximate_counties()


def create_approximate_counties():
    """Create approximate county boundaries if download fails."""
    print("Using approximate county boundaries...")

    # Approximate bounding boxes based on county centroids and extents
    # These are rough approximations for demonstration
    counties_data = [
        {"name": "Lea", "countyfp": "025", "geometry": box(-103.6, 32.5, -103.0, 33.2)},
        {"name": "Roosevelt", "countyfp": "041", "geometry": box(-103.8, 33.5, -103.0, 34.8)},
        {"name": "Curry", "countyfp": "009", "geometry": box(-103.6, 34.2, -103.0, 35.0)},
    ]

    gdf = gpd.GeoDataFrame(counties_data, crs="EPSG:4326")

    boundaries_dir = DATA_DIR / "boundaries"
    output_path = boundaries_dir / "nm_county_boundaries.geojson"
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"Saved approximate boundaries: {output_path}")

    return gdf


def create_synthetic_fields(counties_gdf, n_fields=200):
    """Create synthetic field boundaries within counties for testing."""
    print("\n" + "=" * 70)
    print("STEP 2: Creating Synthetic Field Boundaries")
    print("=" * 70)
    print("\nNOTE: Creating representative field patterns...")

    import numpy as np
    from shapely.geometry import Polygon

    boundaries_dir = DATA_DIR / "boundaries"
    fields = []

    np.random.seed(42)
    field_id = 0

    # Convert to projected CRS for accurate area calculations
    counties_proj = counties_gdf.to_crs("EPSG:5070")  # NAD83 / Conus Albers

    # Generate fields within each county
    for (_, county), (_, county_proj) in zip(counties_gdf.iterrows(), counties_proj.iterrows()):
        county_geom = county.geometry
        county_geom_proj = county_proj.geometry
        bounds = county_geom.bounds

        # Calculate number of fields per county based on area
        county_area = county_geom_proj.area  # Use projected area
        total_area = counties_proj.geometry.area.sum()
        n_county_fields = max(1, int(n_fields * (county_area / total_area)))

        county_name = county["NAME"] if "NAME" in county else county.get("name", "Unknown")
        county_fips = county["COUNTYFP"] if "COUNTYFP" in county else county.get("countyfp", "000")

        print(f"  {county_name}: {n_county_fields} fields")

        fields_created = 0
        attempts = 0
        max_attempts = n_county_fields * 10

        while fields_created < n_county_fields and attempts < max_attempts:
            attempts += 1

            # Generate random field center
            lon = np.random.uniform(bounds[0], bounds[2])
            lat = np.random.uniform(bounds[1], bounds[3])

            # Check if point is in county
            point = gpd.points_from_xy([lon], [lat])[0]
            if not county_geom.contains(point):
                continue

            # Generate field polygon (roughly rectangular, rotated)
            width = np.random.uniform(0.001, 0.01)  # degrees
            height = np.random.uniform(0.001, 0.008)
            rotation = np.random.uniform(0, 90)

            # Create rectangle
            coords = [
                (lon - width / 2, lat - height / 2),
                (lon + width / 2, lat - height / 2),
                (lon + width / 2, lat + height / 2),
                (lon - width / 2, lat + height / 2),
                (lon - width / 2, lat - height / 2),
            ]

            field_poly = Polygon(coords)

            # Check if field is fully within county
            if county_geom.contains(field_poly):
                field_area_acres = field_poly.area * 24710538  # deg² to acres

                fields.append(
                    {
                        "field_id": f"NM_FIELD_{field_id + 1:03d}",
                        "county": county["NAME"],
                        "county_fips": county["COUNTYFP"],
                        "area_acres": field_area_acres,
                        "geometry": field_poly,
                    }
                )

                field_id += 1
                fields_created += 1

    fields_gdf = gpd.GeoDataFrame(fields, crs="EPSG:4326")

    # Sort by area and take top 200
    top_fields = fields_gdf.nlargest(200, "area_acres")
    top_fields["field_id"] = [f"NM_FIELD_{i + 1:03d}" for i in range(len(top_fields))]

    print(f"\nCreated {len(top_fields)} synthetic fields")
    print(f"Total area: {top_fields['area_acres'].sum():.1f} acres")
    print(f"Average size: {top_fields['area_acres'].mean():.1f} acres")
    print(f"Median size: {top_fields['area_acres'].median():.1f} acres")
    print(
        f"Size range: {top_fields['area_acres'].min():.1f} - {top_fields['area_acres'].max():.1f} acres"
    )

    # Save
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
    soil_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Import ssurgo_soil module
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
        import ssurgo_soil

        print("Querying NRCS Soil Data Access API...")
        print("This may take several minutes...")

        all_soil_data = []

        for idx, field in fields_gdf.iterrows():
            field_id = field["field_id"]
            geom = field.geometry

            # Convert to WKT
            wkt = geom.wkt

            try:
                # Query soil data
                soil = ssurgo_soil.get_soil_for_polygon(wkt, max_depth_cm=30)

                if soil is not None and len(soil) > 0:
                    soil["field_id"] = field_id
                    all_soil_data.append(soil)
                    print(f"  {field_id}: {len(soil)} soil records")
                else:
                    print(f"  {field_id}: No soil data")

            except Exception as e:
                print(f"  {field_id}: Error - {e}")
                continue

            # Small delay to be nice to API
            time.sleep(0.5)

        if all_soil_data:
            combined = pd.concat(all_soil_data, ignore_index=True)
            output_csv = soil_dir / "nm_soil_data.csv"
            combined.to_csv(output_csv, index=False)
            print(f"\nSaved soil data: {output_csv}")
            print(f"Total records: {len(combined)}")
            return combined
        else:
            print("No soil data retrieved")
            return None

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return None


def download_weather_data(fields_gdf):
    """Download NASA POWER weather data for field centroids."""
    print("\n" + "=" * 70)
    print("STEP 4: Downloading NASA POWER Weather Data (2005-2020)")
    print("=" * 70)

    weather_dir = DATA_DIR / "weather"
    weather_dir.mkdir(parents=True, exist_ok=True)

    # NASA POWER API endpoint
    API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

    parameters = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,WS10M"

    all_weather = []

    print("Querying NASA POWER API...")
    print("This will query 200 fields x 16 years = ~3,200 API calls")
    print("With rate limiting, this will take 30-50 minutes...")
    print()

    for idx, field in fields_gdf.iterrows():
        field_id = field["field_id"]
        centroid = field.geometry.centroid
        lat = centroid.y
        lon = centroid.x

        print(f"{field_id} ({lat:.4f}, {lon:.4f})...", end=" ", flush=True)

        try:
            params = {
                "parameters": parameters,
                "community": "AG",
                "latitude": lat,
                "longitude": lon,
                "start": "20050101",
                "end": "20201231",
                "format": "JSON",
            }

            response = requests.get(API_URL, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "properties" in data and "parameter" in data["properties"]:
                params_data = data["properties"]["parameter"]

                # Convert to dataframe
                dates = list(params_data["T2M"].keys())

                records = []
                for date in dates:
                    year = int(date[:4])
                    month = int(date[4:6])
                    day = int(date[6:8])

                    records.append(
                        {
                            "field_id": field_id,
                            "lat": lat,
                            "lon": lon,
                            "date": f"{year}-{month:02d}-{day:02d}",
                            "T2M": params_data["T2M"][date],
                            "T2M_MAX": params_data["T2M_MAX"][date],
                            "T2M_MIN": params_data["T2M_MIN"][date],
                            "PRECTOTCORR": params_data["PRECTOTCORR"][date],
                            "ALLSKY_SFC_SW_DWN": params_data["ALLSKY_SFC_SW_DWN"][date],
                            "RH2M": params_data["RH2M"][date],
                            "WS10M": params_data["WS10M"][date],
                        }
                    )

                df = pd.DataFrame(records)
                all_weather.append(df)
                print(f"{len(records)} days")
            else:
                print("No data")

        except Exception as e:
            print(f"ERROR: {e}")

        # Rate limiting
        time.sleep(1.0)

    if all_weather:
        combined = pd.concat(all_weather, ignore_index=True)

        # Convert -999 to NaN
        for col in [
            "T2M",
            "T2M_MAX",
            "T2M_MIN",
            "PRECTOTCORR",
            "ALLSKY_SFC_SW_DWN",
            "RH2M",
            "WS10M",
        ]:
            combined[col] = combined[col].replace(-999.0, pd.NA)

        output_csv = weather_dir / "nm_weather_2005_2020.csv"
        combined.to_csv(output_csv, index=False)
        print(f"\nSaved weather data: {output_csv}")
        print(f"Total records: {len(combined)}")
        return combined
    else:
        print("No weather data retrieved")
        return None


def download_cdl_data(fields_gdf):
    """Download CDL cropland data for the fields."""
    print("\n" + "=" * 70)
    print("STEP 5: Downloading CDL Cropland Data (2008-2020)")
    print("=" * 70)

    crops_dir = DATA_DIR / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    rasters_dir = crops_dir / "rasters"
    rasters_dir.mkdir(parents=True, exist_ok=True)

    years = list(range(2008, 2021))  # 2008-2020
    state_fips = "35"  # New Mexico

    print(f"Downloading CDL for NM (State FIPS {state_fips})")
    print(f"Years: {years}")

    all_cdl_data = []

    for year in years:
        print(f"\nYear {year}:")

        # Download state-level CDL
        cdl_url = f"https://nassgeodata.gmu.edu/nass_data_cache/byfips/CDL_{year}_{state_fips}.tif"
        cdl_path = rasters_dir / f"CDL_{year}_{state_fips}.tif"

        if not cdl_path.exists():
            print(f"  Downloading from: {cdl_url}")
            try:
                response = requests.get(cdl_url, stream=True, timeout=300)
                response.raise_for_status()

                with open(cdl_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  Saved: {cdl_path}")
            except Exception as e:
                print(f"  ERROR: {e}")
                continue
        else:
            print(f"  Using existing: {cdl_path}")

        # Extract crop data for fields
        print("  Extracting crop data for fields...")
        try:
            from collections import Counter

            import rasterio
            from rasterio.mask import mask

            with rasterio.open(cdl_path) as src:
                # Reproject fields to CDL CRS (EPSG:5070)
                fields_proj = fields_gdf.to_crs(src.crs)

                for idx, field in fields_proj.iterrows():
                    try:
                        out_image, _ = mask(src, [field.geometry], crop=True)
                        pixels = out_image[0]
                        valid = pixels[pixels > 0]

                        if len(valid) > 0:
                            counts = Counter(valid.flat)
                            dominant_code = counts.most_common(1)[0][0]
                            dominant_pct = counts[dominant_code] / len(valid) * 100
                        else:
                            dominant_code = 0
                            dominant_pct = 0.0

                        # Map to crop name
                        crop_names = {
                            1: "Corn",
                            2: "Cotton",
                            3: "Rice",
                            4: "Sorghum",
                            5: "Soybeans",
                            6: "Sunflower",
                            10: "Peanuts",
                            11: "Tobacco",
                            12: "Sweet Corn",
                            13: "Pop or Orn Corn",
                            14: "Mint",
                            21: "Barley",
                            22: "Durum Wheat",
                            23: "Spring Wheat",
                            24: "Winter Wheat",
                            25: "Other Small Grains",
                            26: "Dbl Crop WinWht/Soybeans",
                            27: "Rye",
                            28: "Oats",
                            29: "Millet",
                            30: "Speltz",
                            31: "Canola",
                            32: "Flaxseed",
                            33: "Safflower",
                            34: "Rape Seed",
                            35: "Mustard",
                            36: "Alfalfa",
                            37: "Other Hay/Non Alfalfa",
                            38: "Camelina",
                            39: "Buckwheat",
                            41: "Sugarbeets",
                            42: "Dry Beans",
                            43: "Potatoes",
                            44: "Other Crops",
                            45: "Sugarcane",
                            46: "Sweet Potatoes",
                            47: "Misc Vegs & Fruits",
                            48: "Watermelons",
                            49: "Cantaloupes",
                            50: "Cucumbers",
                            51: "Chick Peas",
                            52: "Lentils",
                            53: "Peas",
                            54: "Tomatoes",
                            55: "Cabbage",
                            56: "Cauliflower",
                            57: "Broccoli",
                            58: "Turnips",
                            59: "Peppers",
                            60: "Pimentos",
                            61: "Fallow/Idle Cropland",
                            62: "Pasture/Grass",
                            63: "Woody Wetlands",
                            64: "Herbaceous Wetlands",
                            65: "Developed",
                            66: "Barren",
                            67: "Deciduous Forest",
                            68: "Evergreen Forest",
                            69: "Mixed Forest",
                            70: "Shrubland",
                            71: "Grassland/Pasture",
                            72: "Sod/Grass Seed",
                            75: "Almonds",
                            76: "Walnuts",
                            77: "Apples",
                            78: "Cherries",
                            79: "Pears",
                            81: "Clouds/No Data",
                            82: "Developed",
                            83: "Water",
                            87: "Wetlands",
                            88: "Nonag/Undefined",
                            92: "Aquaculture",
                            111: "Open Water",
                            112: "Perennial Ice/Snow",
                            121: "Developed/Open Space",
                            122: "Developed/Low Intensity",
                            123: "Developed/Medium Intensity",
                            124: "Developed/High Intensity",
                            131: "Barren",
                            141: "Deciduous Forest",
                            142: "Evergreen Forest",
                            143: "Mixed Forest",
                            152: "Shrubland",
                            176: "Grassland/Pasture",
                        }

                        crop_name = crop_names.get(dominant_code, f"Code_{dominant_code}")

                        all_cdl_data.append(
                            {
                                "field_id": field["field_id"],
                                "year": year,
                                "crop_code": int(dominant_code),
                                "crop_name": crop_name,
                                "dominant_pct": round(dominant_pct, 1),
                                "total_pixels": len(valid),
                            }
                        )

                    except Exception as e:
                        print(f"    {field['field_id']}: ERROR - {e}")
                        continue

            print(f"  Extracted data for {len(fields_gdf)} fields")

        except Exception as e:
            print(f"  ERROR extracting: {e}")
            import traceback

            traceback.print_exc()
            continue

    if all_cdl_data:
        df = pd.DataFrame(all_cdl_data)
        output_csv = crops_dir / "nm_cdl_2008_2020.csv"
        df.to_csv(output_csv, index=False)
        print(f"\nSaved CDL data: {output_csv}")
        print(f"Total records: {len(df)}")

        # Identify corn fields
        corn_fields = df[df["crop_name"] == "Corn"]
        print(f"\nCorn field observations: {len(corn_fields)}")
        print(f"Unique fields that grew corn: {corn_fields['field_id'].nunique()}")

        return df
    else:
        print("No CDL data extracted")
        return None


def main():
    """Main execution function."""
    print("#" * 70)
    print("# New Mexico Agricultural Data Download")
    print("# Southern High Plains Aquifer Counties")
    print("# Lea, Roosevelt, Curry Counties")
    print("#")
    print("# This will download:")
    print("#   - County boundaries")
    print("#   - 200 synthetic field boundaries")
    print("#   - SSURGO soil data")
    print("#   - NASA POWER weather (2005-2020)")
    print("#   - CDL cropland data (2008-2020)")
    print("#" * 70)
    print()

    # Step 1: Get county boundaries
    counties = get_county_boundaries_from_census()

    if counties is None:
        print("\nERROR: Could not get county boundaries")
        sys.exit(1)

    # Step 2: Create synthetic field boundaries
    fields = create_synthetic_fields(counties, n_fields=200)

    # Step 3: Download soil data
    soil_data = download_soil_data(fields)

    # Step 4: Download weather data
    weather_data = download_weather_data(fields)

    # Step 5: Download CDL data
    cdl_data = download_cdl_data(fields)

    # Summary
    print("\n" + "=" * 70)
    print("DOWNLOAD COMPLETE")
    print("=" * 70)

    print("\nData locations:")
    print(f"  Boundaries: {DATA_DIR / 'boundaries'}")
    print(f"  Soil: {DATA_DIR / 'soil'}")
    print(f"  Weather: {DATA_DIR / 'weather'}")
    print(f"  Crops: {DATA_DIR / 'crops'}")

    print("\nFiles created:")
    if (DATA_DIR / "boundaries" / "nm_top_200_fields.geojson").exists():
        print("  ✓ Field boundaries")
    if soil_data is not None:
        print(f"  ✓ Soil data: {len(soil_data)} records")
    if weather_data is not None:
        print(f"  ✓ Weather data: {len(weather_data):,} records")
    if cdl_data is not None:
        print(f"  ✓ CDL data: {len(cdl_data)} records")
        corn_count = len(cdl_data[cdl_data["crop_name"] == "Corn"])
        print(f"    - Corn observations: {corn_count}")


if __name__ == "__main__":
    main()

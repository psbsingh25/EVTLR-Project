#!/usr/bin/env python3
"""Extract crop data from CDL rasters for NM fields."""

from collections import Counter
from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask

DATA_DIR = Path(__file__).parent.parent / "data"

# CDL crop codes mapping
CROP_NAMES = {
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


def main():
    print("Extracting CDL data for NM fields (2008-2020)...")

    # Load fields
    fields_gdf = gpd.read_file(DATA_DIR / "boundaries" / "nm_top_200_fields.geojson")
    print(f"Loaded {len(fields_gdf)} fields")

    # Process each year
    all_cdl_data = []
    years = list(range(2008, 2021))

    for year in years:
        print(f"\nYear {year}:")
        cdl_path = DATA_DIR / "crops" / "rasters" / f"CDL_{year}_35.tif"

        if not cdl_path.exists():
            print(f"  File not found: {cdl_path}")
            continue

        print(f"  Processing {cdl_path.name}...")

        try:
            with rasterio.open(cdl_path) as src:
                # Reproject fields to CDL CRS
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

                        crop_name = CROP_NAMES.get(dominant_code, f"Code_{dominant_code}")

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

                print(f"  Extracted {len(fields_gdf)} fields")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    if all_cdl_data:
        df = pd.DataFrame(all_cdl_data)
        output_csv = DATA_DIR / "crops" / "nm_cdl_2008_2020.csv"
        df.to_csv(output_csv, index=False)
        print(f"\n✓ Saved CDL data: {output_csv}")
        print(f"  Total records: {len(df)}")

        # Identify corn fields
        corn_fields = df[df["crop_name"] == "Corn"]
        print(f"\nCorn field observations: {len(corn_fields)}")
        print(f"Unique fields that grew corn: {corn_fields['field_id'].nunique()}")

        # Show year-by-year corn count
        print("\nCorn observations by year:")
        for year in years:
            year_corn = corn_fields[corn_fields["year"] == year]
            print(f"  {year}: {len(year_corn)} fields")
    else:
        print("No CDL data extracted")


if __name__ == "__main__":
    main()

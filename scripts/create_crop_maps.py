#!/usr/bin/env python3
"""Create interactive web maps showing fields colored by crop type."""

import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from pathlib import Path
import random

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "assignment-02"

# Crop color mapping
CROP_COLORS = {
    'Corn': '#FFD700',  # Gold
    'Soybeans': '#90EE90',  # Light green
    'Winter Wheat': '#DAA520',  # Goldenrod
    'Spring Wheat': '#F0E68C',  # Khaki
    'Cotton': '#F5F5DC',  # Beige
    'Sorghum': '#CD853F',  # Peru
    'Grassland/Pasture': '#228B22',  # Forest green
    'Shrubland': '#8FBC8F',  # Dark sea green
    'Alfalfa': '#32CD32',  # Lime green
    'Fallow/Idle Cropland': '#DEB887',  # Burlywood
    'Developed/Low Intensity': '#A9A9A9',  # Dark gray
    'Developed/Medium Intensity': '#696969',  # Dim gray
    'Water': '#1E90FF',  # Dodger blue
    'Unknown': '#808080',  # Gray
}

def create_map_all_crops():
    """Create map showing all fields colored by crop type."""
    print("Creating map: All fields colored by crop type...")
    
    # Load merged data
    gdf = gpd.read_file(OUTPUT_DIR / "fields_with_crops.geojson")
    
    # Calculate centroid for map center
    center = gdf.geometry.centroid.unary_union.centroid
    
    # Create base map
    m = folium.Map(
        location=[center.y, center.x],
        zoom_start=9,
        tiles="OpenStreetMap"
    )
    
    # Add satellite imagery option
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add fields with color by crop
    for idx, row in gdf.iterrows():
        crop = row['dominant_crop']
        color = CROP_COLORS.get(crop, '#808080')
        
        # Create popup content
        popup_content = f"""
        <b>Field ID:</b> {row['field_id']}<br>
        <b>County:</b> {row['county']}<br>
        <b>Area:</b> {row['area_acres']:.1f} acres<br>
        <b>Crop:</b> {crop}<br>
        <b>Coverage:</b> {row['dominant_pct']:.1f}%
        """
        
        # Style function
        style = {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }
        
        # Add polygon
        folium.GeoJson(
            row.geometry,
            style_function=lambda x, style=style: style,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(m)
    
    # Add legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px;
                border:2px solid grey; z-index:9999; 
                background-color:white; padding: 10px;
                font-size:14px;">
    <b>Crop Types</b><br>
    """
    
    for crop, color in CROP_COLORS.items():
        if crop in gdf['dominant_crop'].values:
            count = len(gdf[gdf['dominant_crop'] == crop])
            legend_html += f'<i style="background:{color};width:12px;height:12px;display:inline-block;margin-right:5px;"></i>{crop} ({count})<br>'
    
    legend_html += "</div>"
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save
    output_path = OUTPUT_DIR / "my_fields_map.html"
    m.save(output_path)
    print(f"✓ Saved: {output_path}")
    print(f"  Total fields: {len(gdf)}")
    print(f"  Map center: ({center.y:.4f}, {center.x:.4f})")


def create_map_corn_only():
    """Create map showing only corn fields."""
    print("\nCreating map: Corn fields only...")
    
    # Load corn fields
    corn_gdf = gpd.read_file(OUTPUT_DIR / "fields_corn_only.geojson")
    
    if len(corn_gdf) == 0:
        print("No corn fields found!")
        return
    
    # Calculate centroid
    center = corn_gdf.geometry.centroid.unary_union.centroid
    
    # Create base map
    m = folium.Map(
        location=[center.y, center.x],
        zoom_start=10,
        tiles="OpenStreetMap"
    )
    
    # Add satellite imagery
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add corn fields with gold color
    for idx, row in corn_gdf.iterrows():
        # Get years this field grew corn
        corn_years = row.get('corn_years', 'N/A')
        
        popup_content = f"""
        <b>Field ID:</b> {row['field_id']}<br>
        <b>County:</b> {row['county']}<br>
        <b>Area:</b> {row['area_acres']:.1f} acres<br>
        <b>Crop:</b> Corn<br>
        <b>Years with Corn:</b> {corn_years}
        """
        
        style = {
            'fillColor': '#FFD700',  # Gold for corn
            'color': 'darkgoldenrod',
            'weight': 2,
            'fillOpacity': 0.8
        }
        
        folium.GeoJson(
            row.geometry,
            style_function=lambda x, style=style: style,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(m)
    
    # Add marker for each corn field
    marker_cluster = MarkerCluster(name="Corn Fields").add_to(m)
    
    for idx, row in corn_gdf.iterrows():
        centroid = row.geometry.centroid
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"{row['field_id']} - {row['county']}",
            icon=folium.Icon(color='orange', icon='leaf', prefix='fa')
        ).add_to(marker_cluster)
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 300px;
                background-color: white; padding: 10px;
                border: 2px solid grey; z-index:9999;
                font-size: 16px; font-weight: bold;">
    🌽 Corn Fields in Southern High Plains Aquifer<br>
    <span style="font-size: 12px; font-weight: normal;">
    Lea, Roosevelt, and Curry Counties, NM
    </span>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px;
                border:2px solid grey; z-index:9999; 
                background-color:white; padding: 10px;
                font-size:14px;">
    <b>Legend</b><br>
    <i style="background:#FFD700;width:12px;height:12px;display:inline-block;margin-right:5px;"></i>Corn Fields<br>
    <i style="color:orange; display:inline-block;margin-right:5px;">🌽</i>Field Centers<br>
    <hr style="margin:5px 0;">
    <b>Counties:</b><br>
    """
    for county in corn_gdf['county'].unique():
        count = len(corn_gdf[corn_gdf['county'] == county])
        legend_html += f"• {county}: {count} fields<br>"
    
    legend_html += "</div>"
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save
    output_path = OUTPUT_DIR / "my_fields_corn_map.html"
    m.save(output_path)
    print(f"✓ Saved: {output_path}")
    print(f"  Corn fields: {len(corn_gdf)}")
    print(f"  Map center: ({center.y:.4f}, {center.x:.4f})")


def main():
    """Main function to create both maps."""
    print("#" * 70)
    print("# Creating Interactive Web Maps")
    print("# Southern High Plains Aquifer - NM Counties")
    print("#" * 70)
    print()
    
    # Create map showing all fields by crop type
    create_map_all_crops()
    
    # Create map showing only corn fields
    create_map_corn_only()
    
    print("\n" + "=" * 70)
    print("Maps Created Successfully!")
    print("=" * 70)
    print(f"\nFiles saved in: {OUTPUT_DIR}")
    print(f"  1. my_fields_map.html - All fields colored by crop type")
    print(f"  2. my_fields_corn_map.html - Corn fields only (5 fields)")
    print("\nOpen these files in a web browser to view the interactive maps.")


if __name__ == "__main__":
    main()

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

# --- File Paths ---
stations_csv = "Data/NY EV Charging stations_full.csv"
corridors_path = "GEOJSON/Corridor_Spacing_Analysis.geojson"
dac_path = "GEOJSON/Final_DAC_Attributes.geojson"
queue_path = "GEOJSON/Queue_Risk_Analysis.geojson"
counties_path = "GEOJSON/Counties_Shoreline.geojson"
state_path = "GEOJSON/State_Shoreline.geojson"
output_path = "GEOJSON/Station_Priority_Zones.geojson"

print(" Loading data layers...")

# Load all analysis layers
corridors = gpd.read_file(corridors_path)
dac = gpd.read_file(dac_path)
queue_risk = gpd.read_file(queue_path)
counties = gpd.read_file(counties_path)
ny_state = gpd.read_file(state_path)
stations_df = pd.read_csv(stations_csv)

print(f"   Loaded {len(corridors)} corridor segments")
print(f"   Loaded {len(dac)} DAC areas")
print(f"   Loaded {len(queue_risk)} counties with queue risk data")

# --- Create Analysis Grid ---
print("\n🗺️ Creating analysis grid...")

# Reproject to equal area
ny_state = ny_state.to_crs(epsg=5070)
bounds = ny_state.total_bounds  # minx, miny, maxx, maxy

# Create 10-mile grid cells across NY
CELL_SIZE = 16093.4  # 10 miles in meters
x_coords = np.arange(bounds[0], bounds[2], CELL_SIZE)
y_coords = np.arange(bounds[1], bounds[3], CELL_SIZE)

from shapely.geometry import box

grid_cells = []
for x in x_coords:
    for y in y_coords:
        cell = box(x, y, x + CELL_SIZE, y + CELL_SIZE)
        # Only keep cells that intersect NY state
        if ny_state.geometry.intersects(cell).any():
            grid_cells.append(cell)

grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs="EPSG:5070")
print(f"   Created {len(grid_gdf)} grid cells (10 mile resolution)")

# --- Calculate Priority Scores for Each Cell ---
print("\n Calculating multi-criteria priority scores...")

# Reproject all layers to EPSG:5070
corridors = corridors.to_crs(epsg=5070)
dac = dac.to_crs(epsg=5070)
queue_risk = queue_risk.to_crs(epsg=5070)
counties = counties.to_crs(epsg=5070)

# Prepare stations
stations_df = stations_df.dropna(subset=["Latitude", "Longitude"])
stations_gdf = gpd.GeoDataFrame(
    stations_df,
    geometry=[Point(xy) for xy in zip(stations_df.Longitude, stations_df.Latitude)],
    crs="EPSG:4326"
).to_crs(epsg=5070)

priority_scores = []

for idx, cell in grid_gdf.iterrows():
    cell_geom = cell.geometry
    cell_center = cell_geom.centroid
    
    # 1. CORRIDOR PROXIMITY SCORE (30% weight)
    # Higher score if cell intersects corridors with gaps
    corridor_intersect = corridors[corridors.geometry.intersects(cell_geom)]
    if len(corridor_intersect) > 0:
        # Use worst gap in the cell
        max_gap = corridor_intersect["Max_Gap_Miles"].max()
        avg_gap = corridor_intersect["Max_Gap_Miles"].mean()
        
        # Higher gap = higher priority
        if max_gap > 50:
            corridor_score = 100
        elif max_gap > 30:
            corridor_score = 75
        elif max_gap > 15:
            corridor_score = 50
        else:
            corridor_score = 25
    else:
        corridor_score = 0
    
    # 2. EQUITY SCORE (25% weight)
    # Higher score if cell contains DAC areas
    dac_intersect = dac[dac.geometry.intersects(cell_geom)]
    if len(dac_intersect) > 0:
        # Calculate DAC area within cell
        dac_area = dac_intersect.geometry.intersection(cell_geom).area.sum()
        dac_pct = (dac_area / cell_geom.area) * 100
        equity_score = min(100, dac_pct * 2)  # Scale up
    else:
        equity_score = 0
    
    # 3. QUEUE RISK SCORE (25% weight)
    # Higher score if cell is in high-risk county
    county_intersect = queue_risk[queue_risk.geometry.intersects(cell_center)]
    if len(county_intersect) > 0:
        queue_score = county_intersect.iloc[0]["Queue_Risk_Score"]
    else:
        queue_score = 0
    
    # 4. STATION DENSITY SCORE (20% weight)
    # INVERSE - fewer nearby stations = higher priority
    buffer_5mi = cell_center.buffer(8046.72)  # 5 mile radius
    nearby_stations = stations_gdf[stations_gdf.geometry.within(buffer_5mi)]
    num_nearby = len(nearby_stations)
    
    if num_nearby == 0:
        density_score = 100
    elif num_nearby <= 2:
        density_score = 75
    elif num_nearby <= 5:
        density_score = 50
    else:
        density_score = max(0, 50 - (num_nearby - 5) * 5)
    
    # WEIGHTED COMPOSITE SCORE
    composite_score = (
        corridor_score * 0.30 +
        equity_score * 0.25 +
        queue_score * 0.25 +
        density_score * 0.20
    )
    
    # Priority Category
    if composite_score >= 75:
        priority = "Critical Priority"
    elif composite_score >= 60:
        priority = "High Priority"
    elif composite_score >= 40:
        priority = "Moderate Priority"
    else:
        priority = "Low Priority"
    
    priority_scores.append({
        "Priority_Score": composite_score,
        "Priority_Category": priority,
        "Corridor_Score": corridor_score,
        "Equity_Score": equity_score,
        "Queue_Score": queue_score,
        "Density_Score": density_score,
        "Nearby_Stations": num_nearby,
        "geometry": cell_geom
    })
    
    if (idx + 1) % 100 == 0:
        print(f"   Processed {idx + 1}/{len(grid_gdf)} cells...")

priority_gdf = gpd.GeoDataFrame(priority_scores, geometry="geometry", crs="EPSG:5070")

# Filter to only high-priority cells
priority_zones = priority_gdf[
    priority_gdf["Priority_Score"] >= 40
].copy()

print(f"\n Identified {len(priority_zones)} priority zones for station placement")

# --- Reproject and Save ---
print("\nSaving priority zones...")
priority_zones = priority_zones.to_crs(epsg=4326)
priority_zones.to_file(output_path, driver="GeoJSON")

print(f" Saved to {output_path}")

# --- Summary Statistics ---
print("\n Priority Zone Summary:")
print(priority_zones["Priority_Category"].value_counts())
print(f"\nTop 10 Priority Zones:")
top_zones = priority_zones.nlargest(10, "Priority_Score")[[
    "Priority_Score", "Priority_Category", "Corridor_Score", 
    "Equity_Score", "Queue_Score", "Nearby_Stations"
]]
print(top_zones.to_string(index=False))

print("\n Recommendation: Focus on 'Critical Priority' zones first")
print("   These areas combine corridor gaps, DAC coverage, queue risk, and low station density")
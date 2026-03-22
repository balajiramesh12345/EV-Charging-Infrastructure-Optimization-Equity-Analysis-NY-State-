import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np

# --- File Paths ---
counties_path = "GEOJSON/Counties_Shoreline.geojson"
ev_count_path = "GEOJSON/EV_Count.geojson"
stations_csv = "Data/NY EV Charging stations_full.csv"
output_path = "GEOJSON/Queue_Risk_Analysis.geojson"

print(" Loading data...")
counties = gpd.read_file(counties_path)
ev_data = gpd.read_file(ev_count_path)
stations_df = pd.read_csv(stations_csv)

# --- Process Station Data ---
print(" Processing charging station data...")
stations_df = stations_df.dropna(subset=["Latitude", "Longitude"])

# Calculate total ports per station (with weights for charger types)
stations_df["ev_level1_evse_num"] = pd.to_numeric(stations_df["ev_level1_evse_num"], errors="coerce").fillna(0)
stations_df["ev_level2_evse_num"] = pd.to_numeric(stations_df["ev_level2_evse_num"], errors="coerce").fillna(0)
stations_df["ev_dc_fast_num"] = pd.to_numeric(stations_df["ev_dc_fast_num"], errors="coerce").fillna(0)

# Weighted ports (DC Fast counts more due to faster throughput)
stations_df["Total_Ports"] = (
    stations_df["ev_level1_evse_num"] * 1.0 +
    stations_df["ev_level2_evse_num"] * 1.5 +
    stations_df["ev_dc_fast_num"] * 3.0  # Fast chargers serve 3x more EVs per day
)
stations_df["Total_Ports"] = stations_df["Total_Ports"].replace(0, 1)  # Avoid division by zero

# Create GeoDataFrame
stations_gdf = gpd.GeoDataFrame(
    stations_df,
    geometry=[Point(xy) for xy in zip(stations_df.Longitude, stations_df.Latitude)],
    crs="EPSG:4326"
)

print(f"   Found {len(stations_gdf)} charging stations")
print(f"   Total weighted ports: {stations_gdf['Total_Ports'].sum():.0f}")

# --- Reproject to Equal Area for accurate calculations ---
print(" Reprojecting to CONUS Albers Equal Area (EPSG:5070)...")
counties = counties.to_crs(epsg=5070)
ev_data = ev_data.to_crs(epsg=5070)
stations_gdf = stations_gdf.to_crs(epsg=5070)

# --- Join EV Count with Counties ---
print(" Aggregating EV data from ZIP codes to counties...")

# The EV data is at ZIP code level, we need to aggregate to county level
print(f"   Found {len(ev_data)} ZIP codes with EV data")

# Ensure EV_Count is numeric
ev_data["EV_Count"] = pd.to_numeric(ev_data["EV_Count"], errors='coerce').fillna(0)

print(f"   Total EVs in dataset: {ev_data['EV_Count'].sum():,.0f}")

# Spatial join: find which county each ZIP code is in
print("   Performing spatial join to assign ZIP codes to counties...")
zip_to_county = gpd.sjoin(
    ev_data[["EV_Count", "geometry"]], 
    counties[["NAME", "geometry"]], 
    how="left", 
    predicate="intersects"
)

# Aggregate EV counts by county
ev_summary = zip_to_county.groupby("NAME")["EV_Count"].sum().reset_index()
ev_summary.columns = ["NAME", "Total_EVs"]

print(f"   Aggregated to {len(ev_summary)} counties")
print(f"   Top 5 counties by EV count:")
print(ev_summary.nlargest(5, "Total_EVs")[["NAME", "Total_EVs"]])

counties = counties.merge(ev_summary, on="NAME", how="left")
counties["Total_EVs"] = pd.to_numeric(counties["Total_EVs"], errors='coerce').fillna(0)

# --- Spatial Join: Count stations per county ---
print("📍 Counting charging stations per county...")
stations_in_counties = gpd.sjoin(stations_gdf, counties[["NAME", "geometry"]], how="left", predicate="within")
station_counts = stations_in_counties.groupby("NAME").agg({
    "Total_Ports": "sum",
    "station_name": "count"
}).reset_index()
station_counts.columns = ["NAME", "Total_Ports", "Station_Count"]

counties = counties.merge(station_counts, on="NAME", how="left")
counties["Total_Ports"] = pd.to_numeric(counties["Total_Ports"], errors='coerce').fillna(0)
counties["Station_Count"] = pd.to_numeric(counties["Station_Count"], errors='coerce').fillna(0)

# Ensure Total_EVs is also numeric (safety check)
counties["Total_EVs"] = pd.to_numeric(counties["Total_EVs"], errors='coerce').fillna(0)

# --- Calculate Queue Risk Metrics ---
print("📊 Calculating queue risk metrics...")

# 1. EVs per Port Ratio (higher = worse)
counties["EVs_per_Port"] = np.where(
    counties["Total_Ports"] > 0,
    counties["Total_EVs"] / counties["Total_Ports"],
    999  # Very high risk if no stations
)

# 2. Station Density (stations per 100 sq km)
counties["Area_sqkm"] = counties.geometry.area / 1_000_000
counties["Station_Density"] = np.where(
    counties["Area_sqkm"] > 0,
    (counties["Station_Count"] / counties["Area_sqkm"]) * 100,
    0
)

# 3. Coverage Score (inverse of station density, normalized)
max_density = counties["Station_Density"].max()
if max_density > 0:
    counties["Coverage_Gap_Score"] = 100 * (1 - counties["Station_Density"] / max_density)
else:
    counties["Coverage_Gap_Score"] = 100

# 4. Composite Queue Risk Score (0-100, higher = worse risk)
# Normalize EVs per port to 0-100 scale
max_ev_per_port = counties[counties["EVs_per_Port"] < 999]["EVs_per_Port"].quantile(0.95)  # 95th percentile
counties["EV_Port_Score"] = np.clip((counties["EVs_per_Port"] / max_ev_per_port) * 100, 0, 100)

# Weighted combination
counties["Queue_Risk_Score"] = (
    counties["EV_Port_Score"] * 0.6 +          # 60% weight on EV/port ratio
    counties["Coverage_Gap_Score"] * 0.4       # 40% weight on coverage gaps
)

# 5. Risk Category
counties["Risk_Category"] = pd.cut(
    counties["Queue_Risk_Score"],
    bins=[0, 25, 50, 75, 100],
    labels=["Low", "Moderate", "High", "Critical"]
)

# --- Reproject back to WGS84 ---
print("📐 Reprojecting back to WGS84 for web mapping...")
counties = counties.to_crs(epsg=4326)

# --- Save Results ---
print("💾 Saving queue risk analysis...")
output_cols = [
    "NAME", 
    "Total_EVs", 
    "Station_Count", 
    "Total_Ports",
    "EVs_per_Port", 
    "Station_Density",
    "Queue_Risk_Score",
    "Risk_Category",
    "geometry"
]
counties[output_cols].to_file(output_path, driver="GeoJSON")

print(f" Done! Saved to {output_path}")
print(f"\n Queue Risk Summary Statistics:")
print(f"   Mean Queue Risk Score: {counties['Queue_Risk_Score'].mean():.2f}")
print(f"   Counties at Critical Risk: {(counties['Risk_Category'] == 'Critical').sum()}")
print(f"   Counties at High Risk: {(counties['Risk_Category'] == 'High').sum()}")
print(f"   Counties at Moderate Risk: {(counties['Risk_Category'] == 'Moderate').sum()}")
print(f"   Counties at Low Risk: {(counties['Risk_Category'] == 'Low').sum()}")
print(f"\n Top 5 Highest Risk Counties:")
print(counties.nlargest(5, "Queue_Risk_Score")[["NAME", "Queue_Risk_Score", "EVs_per_Port", "Station_Count"]])
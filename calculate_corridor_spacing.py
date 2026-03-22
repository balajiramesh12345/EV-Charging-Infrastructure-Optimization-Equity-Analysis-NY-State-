import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import numpy as np

# --- File Paths ---
corridors_path = "GEOJSON/AltFuels_rounds1_7_2023_11_07.geojson"
stations_csv = "Data/NY EV Charging stations_full.csv"
state_path = "GEOJSON/State_Shoreline.geojson"
output_corridors = "GEOJSON/Corridor_Spacing_Analysis.geojson"
output_gaps = "GEOJSON/Corridor_Coverage_Gaps.geojson"

print(" Loading data...")
corridors = gpd.read_file(corridors_path)
stations_df = pd.read_csv(stations_csv)
ny_state = gpd.read_file(state_path)

# --- Filter for EV Corridors ---
print(" Filtering for EV corridors...")

if "EV" in corridors.columns:
    ev_corridors = corridors[
        (corridors["EV"].notna()) & 
        (corridors["EV"] != '') &
        (corridors["EV"] != 'N') &
        (corridors["EV"] != 'No') &
        (corridors["EV"] != 0)
    ].copy()
    
    if len(ev_corridors) == 0 and "ELECTRICVE" in corridors.columns:
        ev_corridors = corridors[
            (corridors["ELECTRICVE"].notna()) & 
            (corridors["ELECTRICVE"] != '')
        ].copy()
else:
    ev_corridors = corridors.copy()

if len(ev_corridors) == 0:
    ev_corridors = corridors.copy()

print(f"   Starting with {len(ev_corridors)} corridor segments")

# --- Clip to NY State ---
print("✂️ Clipping to NY state boundaries...")
ev_corridors = ev_corridors.to_crs(epsg=4326)
ny_state = ny_state.to_crs(epsg=4326)
ev_corridors = gpd.clip(ev_corridors, ny_state)
print(f"   Clipped to {len(ev_corridors)} segments within NY")

# --- Process Stations - ONLY DC Fast and Multi-Port Level 2 ---
print(" Processing highway-capable charging stations...")
stations_df = stations_df.dropna(subset=["Latitude", "Longitude"])

stations_df["ev_level2_evse_num"] = pd.to_numeric(stations_df["ev_level2_evse_num"], errors="coerce").fillna(0)
stations_df["ev_dc_fast_num"] = pd.to_numeric(stations_df["ev_dc_fast_num"], errors="coerce").fillna(0)

# Filter for highway-capable stations
highway_stations = stations_df[
    (stations_df["ev_dc_fast_num"] > 0) | 
    (stations_df["ev_level2_evse_num"] >= 4)  # At least 4 Level 2 ports
].copy()

print(f"   Using {len(highway_stations)} highway-capable stations")
print(f"   (Filtered out {len(stations_df) - len(highway_stations)} low-capacity stations)")

stations_gdf = gpd.GeoDataFrame(
    highway_stations,
    geometry=[Point(xy) for xy in zip(highway_stations.Longitude, highway_stations.Latitude)],
    crs="EPSG:4326"
)

# --- Reproject ---
print(" Reprojecting to EPSG:5070...")
ev_corridors = ev_corridors.to_crs(epsg=5070)
stations_gdf = stations_gdf.to_crs(epsg=5070)

# --- Filter for Longer Corridors ---
print(" Filtering for substantial corridor segments...")
ev_corridors["length_mi"] = ev_corridors.geometry.length / 1609.34
MIN_LENGTH = 15  # Increased to 15 miles minimum
ev_corridors = ev_corridors[ev_corridors["length_mi"] >= MIN_LENGTH].copy()
print(f"   Analyzing {len(ev_corridors)} corridors >= {MIN_LENGTH} miles")

if len(ev_corridors) == 0:
    print(" No corridors meet minimum length!")
    exit(1)

# --- Calculate Coverage with Narrow Buffer ---
print(" Analyzing corridor coverage...")

# 0.5 mile buffer - must be very close to corridor
BUFFER_DISTANCE = 804.672  # 0.5 miles in meters
print(f"   Using {BUFFER_DISTANCE/1609.34:.1f} mile buffer for direct corridor access")

valid_corridors = ev_corridors[ev_corridors.geometry.is_valid & ~ev_corridors.geometry.is_empty]
ev_corridors = valid_corridors
ev_corridors["buffer"] = ev_corridors.geometry.buffer(BUFFER_DISTANCE)

corridor_stats = []

for idx, corridor in ev_corridors.iterrows():
    try:
        buffer_geom = corridor["buffer"]
        if buffer_geom is None or buffer_geom.is_empty:
            continue
        
        nearby_stations = stations_gdf[stations_gdf.geometry.within(buffer_geom)]
        corridor_length_mi = corridor["length_mi"]
        
        num_stations = len(nearby_stations)
        num_dc_fast = (nearby_stations["ev_dc_fast_num"] > 0).sum()
        
        # Calculate actual spacing along corridor
        if num_stations == 0:
            avg_spacing = corridor_length_mi
            max_gap = corridor_length_mi
            stations_per_mile = 0
        elif num_stations == 1:
            avg_spacing = corridor_length_mi
            max_gap = corridor_length_mi
            stations_per_mile = 1 / corridor_length_mi
        else:
            # Project stations onto corridor line
            distances = []
            for station_geom in nearby_stations.geometry:
                nearest_point = corridor.geometry.interpolate(
                    corridor.geometry.project(station_geom)
                )
                distances.append(corridor.geometry.project(station_geom))
            
            distances = sorted(distances)
            gaps = []
            
            # Gap from start to first station
            if distances[0] > 0:
                gaps.append(distances[0] / 1609.34)  # meters to miles
            
            # Gaps between stations
            for i in range(len(distances) - 1):
                gap = (distances[i + 1] - distances[i]) / 1609.34
                gaps.append(gap)
            
            # Gap from last station to end
            corridor_length_m = corridor.geometry.length
            if distances[-1] < corridor_length_m:
                gaps.append((corridor_length_m - distances[-1]) / 1609.34)
            
            avg_spacing = np.mean(gaps) if gaps else corridor_length_mi
            max_gap = max(gaps) if gaps else corridor_length_mi
            stations_per_mile = num_stations / corridor_length_mi
        
        corridor_stats.append({
            "Corridor_ID": idx,
            "Road_Name": corridor.get("PRIMARY_NA", "Unknown"),
            "Length_Miles": corridor_length_mi,
            "Num_Stations": num_stations,
            "DC_Fast_Count": num_dc_fast,
            "Avg_Spacing_Miles": avg_spacing,
            "Max_Gap_Miles": max_gap,
            "Stations_per_Mile": stations_per_mile,
            "geometry": corridor.geometry
        })
        
    except Exception as e:
        print(f"   Error processing corridor {idx}: {e}")
        continue

print(f"   Processed {len(corridor_stats)} corridors")

if len(corridor_stats) == 0:
    print(" No corridor data!")
    exit(1)

corridor_analysis = gpd.GeoDataFrame(corridor_stats, geometry='geometry', crs="EPSG:5070")

# --- RELATIVE SCORING BASED ON PERCENTILES ---
print(" Calculating relative coverage scores...")

# Use max gap as primary metric (worst gap determines corridor quality)
gaps = corridor_analysis["Max_Gap_Miles"].values

# Calculate percentiles for relative ranking
percentiles = np.percentile(gaps, [25, 50, 75, 90])
p25, p50, p75, p90 = percentiles

print(f"   Gap Percentiles (miles):")
print(f"   25th: {p25:.1f} | 50th: {p50:.1f} | 75th: {p75:.1f} | 90th: {p90:.1f}")

# Assign categories based on RELATIVE performance
def assign_category(gap):
    if gap <= p25:
        return "Best Covered"  # Top 25%
    elif gap <= p50:
        return "Well Covered"  # Top 50%
    elif gap <= p75:
        return "Adequate"  # Top 75%
    elif gap <= p90:
        return "Moderate Gap"  # Bottom 25%
    else:
        return "Critical Gap"  # Bottom 10%

def assign_score(gap):
    # Inverse scoring: smaller gaps = higher scores
    if gap <= p25:
        return 90 + (p25 - gap) / p25 * 10  # 90-100
    elif gap <= p50:
        return 70 + (p50 - gap) / (p50 - p25) * 20  # 70-90
    elif gap <= p75:
        return 50 + (p75 - gap) / (p75 - p50) * 20  # 50-70
    elif gap <= p90:
        return 25 + (p90 - gap) / (p90 - p75) * 25  # 25-50
    else:
        return max(0, 25 - (gap - p90) / p90 * 25)  # 0-25

corridor_analysis["Gap_Category"] = corridor_analysis["Max_Gap_Miles"].apply(assign_category)
corridor_analysis["Coverage_Score"] = corridor_analysis["Max_Gap_Miles"].apply(assign_score)

# --- Identify Critical Gaps (bottom quartile) ---
critical_gaps = corridor_analysis[
    corridor_analysis["Gap_Category"].isin(["Moderate Gap", "Critical Gap"])
].copy()

print(f"   Found {len(critical_gaps)} corridors with moderate/critical gaps")

# --- Reproject ---
print(" Reprojecting to WGS84...")
corridor_analysis = corridor_analysis.to_crs(epsg=4326)
if len(critical_gaps) > 0:
    critical_gaps = critical_gaps.to_crs(epsg=4326)

# --- Save ---
print("Saving results...")
corridor_analysis.to_file(output_corridors, driver="GeoJSON")
if len(critical_gaps) > 0:
    critical_gaps.to_file(output_gaps, driver="GeoJSON")

print(f"\n Done! Saved to {output_corridors}")
print(f"\n RELATIVE Coverage Distribution:")
print(corridor_analysis["Gap_Category"].value_counts().sort_index())
print(f"\n Categories are RELATIVE - comparing corridors to each other")
print(f"\n Top 10 Corridors with Largest Gaps:")
top_gaps = corridor_analysis.nlargest(10, "Max_Gap_Miles")[
    ["Road_Name", "Length_Miles", "Num_Stations", "Max_Gap_Miles", "Gap_Category"]
]
print(top_gaps.to_string(index=False))
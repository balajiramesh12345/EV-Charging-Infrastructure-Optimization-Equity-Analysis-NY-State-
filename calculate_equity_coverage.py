import geopandas as gpd

# --- File Paths ---
counties_path = "GEOJSON/Counties_Shoreline.geojson"
dac_path = "GEOJSON/Final_DAC_Attributes.geojson"
output_path = "GEOJSON/Equity_Coverage.geojson"

print(" Loading data...")
counties = gpd.read_file(counties_path)
dac = gpd.read_file(dac_path)

print("Reprojecting to CONUS Albers Equal Area (EPSG:5070)...")
counties = counties.to_crs(epsg=5070)
dac = dac.to_crs(epsg=5070)

print(" Filtering for designated DAC areas...")
dac = dac[dac["DAC_Desig"] == "Designated as DAC"]
print(f"   Found {len(dac)} designated DAC areas")

print(" Computing intersections between counties and DAC areas...")
intersections = gpd.overlay(counties, dac, how="intersection")
intersections["DAC_area"] = intersections.geometry.area

print(" Aggregating DAC area by county...")
dac_by_county = intersections.groupby("NAME")["DAC_area"].sum().reset_index()

print(" Merging with county boundaries...")
merged = counties.merge(dac_by_county, on="NAME", how="left")
merged["DAC_area"] = merged["DAC_area"].fillna(0)
merged["Total_area"] = merged.geometry.area
merged["Equity_Coverage_Pct"] = (merged["DAC_area"] / merged["Total_area"]) * 100

print(" Reprojecting back to WGS84 for web mapping...")
merged = merged.to_crs(epsg=4326)

print(" Saving results...")
merged = merged[["NAME", "Equity_Coverage_Pct", "geometry"]]
merged.to_file(output_path, driver="GeoJSON")

print(f" Done! Saved to {output_path}")
print(f"\n Summary Statistics:")
print(f"   Mean DAC Coverage: {merged['Equity_Coverage_Pct'].mean():.2f}%")
print(f"   Max DAC Coverage: {merged['Equity_Coverage_Pct'].max():.2f}%")
print(f"   Min DAC Coverage: {merged['Equity_Coverage_Pct'].min():.2f}%")
print(f"   Counties with >0% DAC: {(merged['Equity_Coverage_Pct'] > 0).sum()}")
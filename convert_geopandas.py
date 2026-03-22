import geopandas as gpd

# Correct path (note: folder is NYS_Civil_Boundaries, not .shp)
gdf = gpd.read_file("Data/NYS_Civil_Boundaries/Shapefiles/Counties.shp")

# Save to GeoJSON
gdf.to_file("Data/ny_counties.geojson", driver="GeoJSON")

print("✅ Conversion done! Saved to Data/ny_counties.geojson")
print(gdf.head())
print(gdf.columns)

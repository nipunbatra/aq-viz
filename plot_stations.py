import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Read stations data
stations = pd.read_csv('stations.csv')

# Create GeoDataFrame from stations
gdf_stations = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations['long'], stations['lat']),
    crs='EPSG:4326'
)

# Read India shapefile (2020 with correct J&K/Ladakh boundaries)
india = gpd.read_file('in_district.shp')

# Create the plot
fig, ax = plt.subplots(figsize=(12, 14))

# Plot India map (district boundaries)
india.boundary.plot(ax=ax, linewidth=0.3, color='gray', alpha=0.6)

# Plot stations
gdf_stations.plot(ax=ax, color='red', markersize=15, alpha=0.7, edgecolor='darkred', linewidth=0.3)

# Set title and labels
ax.set_title('CPCB Air Quality Monitoring Stations (2023)\n537 Stations Across India',
             fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Add text annotation
ax.text(0.02, 0.02, f'Total Stations: {len(stations)}',
        transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Save the plot
plt.tight_layout()
plt.savefig('stations_map.png', dpi=300, bbox_inches='tight')
print(f'Map saved as stations_map.png with {len(stations)} stations')

# Show the plot
plt.show()

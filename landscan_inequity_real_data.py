"""
Air Quality Monitoring Inequity Analysis using Real WorldPop Data
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from scipy.spatial import cKDTree
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import warnings
warnings.filterwarnings('ignore')

print("=== WorldPop Population Inequity Analysis (Real Data) ===\n")

# Read stations data
stations = pd.read_csv('stations.csv')
print(f"Loaded {len(stations)} monitoring stations")

# Create GeoDataFrame
gdf_stations = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations['long'], stations['lat']),
    crs='EPSG:4326'
)

# Read India shapefile
india = gpd.read_file('in_district.shp')
india_boundary = india.dissolve()

# Read WorldPop data
print("\nReading WorldPop population raster...")
with rasterio.open('ind_ppp_2020_constrained.tif') as src:
    print(f"Raster shape: {src.shape}")
    print(f"Raster CRS: {src.crs}")
    print(f"Raster bounds: {src.bounds}")
    print(f"Resolution: {src.res}")

    # Mask to India boundary
    india_geom = [india_boundary.geometry.iloc[0].__geo_interface__]
    pop_data, pop_transform = mask(src, india_geom, crop=True, nodata=0)
    pop_data = pop_data[0]  # Get first band

    print(f"Masked raster shape: {pop_data.shape}")
    print(f"Total population in raster: {pop_data.sum():,.0f}")

    # Get coordinates for each pixel
    rows, cols = np.where(pop_data > 0)  # Only process cells with population
    print(f"Processing {len(rows):,} populated grid cells...")

    # Convert pixel coordinates to geographic coordinates
    xs, ys = rasterio.transform.xy(pop_transform, rows, cols)
    populations = pop_data[rows, cols]

    # Create DataFrame
    grid_df = pd.DataFrame({
        'lon': xs,
        'lat': ys,
        'population': populations
    })

# Calculate distance to nearest monitoring station
print("\nCalculating distances to nearest monitoring stations...")
station_coords = np.array([(geom.x, geom.y) for geom in gdf_stations.geometry])
grid_coords = np.array(grid_df[['lon', 'lat']].values)

# Build KD-tree for efficient nearest neighbor search
tree = cKDTree(station_coords)
distances, indices = tree.query(grid_coords, k=1)

# Convert distance to km (rough approximation: 1 degree ≈ 111 km)
distances_km = distances * 111

grid_df['distance_to_station_km'] = distances_km
grid_df['nearest_station_city'] = [stations.iloc[idx]['city'] for idx in indices]

# Calculate coverage metrics
grid_df['underserved'] = grid_df['distance_to_station_km'] > 50
grid_df['poorly_served'] = (grid_df['distance_to_station_km'] > 25) & (grid_df['distance_to_station_km'] <= 50)
grid_df['adequately_served'] = grid_df['distance_to_station_km'] <= 25

# Population statistics
total_pop = grid_df['population'].sum()
underserved_pop = grid_df[grid_df['underserved']]['population'].sum()
poorly_served_pop = grid_df[grid_df['poorly_served']]['population'].sum()
adequately_served_pop = grid_df[grid_df['adequately_served']]['population'].sum()

print(f"\n=== Coverage Analysis ===")
print(f"Total Population: {total_pop:,.0f}")
print(f"Population within 25km of station: {adequately_served_pop:,.0f} ({100*adequately_served_pop/total_pop:.1f}%)")
print(f"Population 25-50km from station: {poorly_served_pop:,.0f} ({100*poorly_served_pop/total_pop:.1f}%)")
print(f"Population >50km from station: {underserved_pop:,.0f} ({100*underserved_pop/total_pop:.1f}%)")

# Sample data for visualization (too many points to plot all)
print("\nSampling data for visualization...")
# Sample more from underserved areas
sample_size = min(50000, len(grid_df))
sample_weights = grid_df['distance_to_station_km'] ** 0.5  # Weight towards distant areas
grid_sample = grid_df.sample(n=sample_size, weights=sample_weights, random_state=42)

# Create GeoDataFrame for plotting
grid_gdf = gpd.GeoDataFrame(
    grid_sample,
    geometry=gpd.points_from_xy(grid_sample['lon'], grid_sample['lat']),
    crs='EPSG:4326'
)

# Plot 1: Distance to nearest monitoring station
print("\nGenerating maps...")
fig, ax = plt.subplots(figsize=(16, 18))

india_boundary.boundary.plot(ax=ax, linewidth=1, color='black')

# Create distance categories
distance_bins = [0, 10, 25, 50, 100, 200, np.inf]
distance_labels = ['<10km', '10-25km', '25-50km', '50-100km', '100-200km', '>200km']
grid_gdf['distance_category'] = pd.cut(grid_gdf['distance_to_station_km'],
                                        bins=distance_bins,
                                        labels=distance_labels)

# Color scheme: green (good) to red (poor coverage)
colors = ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027', '#a50026']
cmap = LinearSegmentedColormap.from_list('coverage', colors, N=len(distance_labels))

# Plot with population-weighted sizes
grid_gdf.plot(
    column='distance_category',
    ax=ax,
    cmap=cmap,
    markersize=np.log10(grid_gdf['population'] + 1) * 0.5,
    alpha=0.6,
    categorical=True,
    legend=True,
    legend_kwds={'title': 'Distance to Nearest Station',
                 'loc': 'lower left',
                 'frameon': True,
                 'fontsize': 10}
)

# Overlay monitoring stations
gdf_stations.plot(ax=ax, color='blue', markersize=30, alpha=0.9,
                  edgecolor='white', linewidth=1.5, marker='o', zorder=5)

ax.set_title('Air Quality Monitoring Coverage Using WorldPop 2020 Data\nDistance to Nearest Station (point size = population)',
             fontsize=20, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('worldpop_station_accessibility.png', dpi=300, bbox_inches='tight')
print('Saved worldpop_station_accessibility.png')
plt.close()

# Plot 2: Population-weighted vulnerability heat map
print("Generating population-weighted vulnerability map...")
fig, ax = plt.subplots(figsize=(16, 18))

india_boundary.boundary.plot(ax=ax, linewidth=1, color='black')

# Calculate vulnerability score
grid_gdf['vulnerability_score'] = grid_gdf['population'] * grid_gdf['distance_to_station_km']
grid_gdf['log_vulnerability'] = np.log10(grid_gdf['vulnerability_score'] + 1)

scatter = ax.scatter(
    grid_gdf['lon'],
    grid_gdf['lat'],
    c=grid_gdf['log_vulnerability'],
    cmap='YlOrRd',
    s=np.log10(grid_gdf['population'] + 1) * 2,
    alpha=0.5
)

cbar = plt.colorbar(scatter, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label('Population × Distance Score (log scale)', fontsize=11)

# Overlay stations
gdf_stations.plot(ax=ax, color='blue', markersize=30, alpha=0.9,
                  edgecolor='white', linewidth=1.5, marker='o', zorder=5)

ax.set_title('Population-Weighted Monitoring Inequity (WorldPop 2020)\nHigher values = More people living far from monitoring',
             fontsize=20, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('worldpop_population_vulnerability.png', dpi=300, bbox_inches='tight')
print('Saved worldpop_population_vulnerability.png')
plt.close()

# Plot 3: State-level aggregation
print("Calculating state-level statistics...")

# Create GeoDataFrame for all grid points
grid_all_gdf = gpd.GeoDataFrame(
    grid_df,
    geometry=gpd.points_from_xy(grid_df['lon'], grid_df['lat']),
    crs='EPSG:4326'
)

# Spatial join with states
grid_with_states = gpd.sjoin(grid_all_gdf, india[['stname', 'geometry']], how='left', predicate='within')

# Aggregate by state
state_stats = grid_with_states.groupby('stname').agg({
    'population': 'sum',
    'distance_to_station_km': lambda x: np.average(x, weights=grid_with_states.loc[x.index, 'population']),
    'underserved': lambda x: grid_with_states.loc[x.index, 'population'][grid_with_states.loc[x.index, 'underserved']].sum()
}).reset_index()

state_stats.columns = ['state', 'population', 'weighted_avg_distance_km', 'underserved_population']
state_stats['pct_underserved'] = 100 * state_stats['underserved_population'] / state_stats['population']

# Merge with shapefile
india_states = india.dissolve(by='stname').reset_index()
india_states = india_states.merge(state_stats, left_on='stname', right_on='state', how='left')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(28, 16))

# Plot 1: Average distance
india_states['weighted_avg_distance_km'] = india_states['weighted_avg_distance_km'].fillna(0)
bins_dist = [0, 25, 50, 75, 100, 150, np.inf]
labels_dist = ['<25km', '25-50km', '50-75km', '75-100km', '100-150km', '>150km']
india_states['distance_bins'] = pd.cut(india_states['weighted_avg_distance_km'], bins=bins_dist, labels=labels_dist)

colors_dist = ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027', '#a50026']
cmap_dist = LinearSegmentedColormap.from_list('distance', colors_dist, N=len(labels_dist))

india_states.plot(
    column='distance_bins',
    ax=ax1,
    cmap=cmap_dist,
    edgecolor='black',
    linewidth=0.8,
    categorical=True,
    legend=True,
    legend_kwds={'title': 'Pop-Weighted Avg Distance', 'fontsize': 10}
)
ax1.set_title('Population-Weighted Average Distance to Station\nby State/UT', fontsize=16, fontweight='bold')
ax1.axis('off')

# Plot 2: Percent underserved
india_states['pct_underserved'] = india_states['pct_underserved'].fillna(0)
india_states.plot(
    column='pct_underserved',
    ax=ax2,
    cmap='Reds',
    edgecolor='black',
    linewidth=0.8,
    legend=True,
    legend_kwds={'label': 'Population >50km from\nStation (%)', 'shrink': 0.8}
)
ax2.set_title('Percentage of Population Underserved (>50km)\nby State/UT', fontsize=16, fontweight='bold')
ax2.axis('off')

plt.tight_layout()
plt.savefig('worldpop_state_comparison.png', dpi=300, bbox_inches='tight')
print('Saved worldpop_state_comparison.png')
plt.close()

# Save statistics
state_stats_sorted = state_stats.sort_values('pct_underserved', ascending=False)
state_stats_sorted.to_csv('worldpop_state_statistics.csv', index=False)
print('Saved worldpop_state_statistics.csv')

# Create summary report
with open('worldpop_inequity_summary.md', 'w') as f:
    f.write('# Air Quality Monitoring Inequity Analysis\n')
    f.write('## Using WorldPop 2020 Population Data\n\n')

    f.write('## Data Sources\n\n')
    f.write('- **Population Data**: WorldPop 2020 (UN-adjusted, constrained)\n')
    f.write('- **Monitoring Stations**: CPCB 537 stations (2023)\n')
    f.write('- **Resolution**: ~100m grid cells\n\n')

    f.write('## National Coverage Summary\n\n')
    f.write(f'- **Total Population**: {total_pop:,.0f}\n')
    f.write(f'- **Population within 25km of station**: {adequately_served_pop:,.0f} ({100*adequately_served_pop/total_pop:.1f}%)\n')
    f.write(f'- **Population 25-50km from station**: {poorly_served_pop:,.0f} ({100*poorly_served_pop/total_pop:.1f}%)\n')
    f.write(f'- **Population >50km from station**: {underserved_pop:,.0f} ({100*underserved_pop/total_pop:.1f}%)\n\n')

    f.write('## States with Highest Percentage Underserved\n\n')
    f.write('| Rank | State/UT | % Underserved | Population | Avg Distance (km) |\n')
    f.write('|------|----------|---------------|------------|-------------------|\n')

    for i, row in enumerate(state_stats_sorted.head(15).itertuples(), 1):
        if pd.notna(row.pct_underserved):
            f.write(f'| {i} | {row.state} | {row.pct_underserved:.1f}% | {row.population:,.0f} | {row.weighted_avg_distance_km:.1f} |\n')

    f.write('\n## Key Findings\n\n')
    f.write(f'- **{100*underserved_pop/total_pop:.1f}%** of India\'s population lives more than 50km from the nearest air quality monitoring station\n')
    f.write(f'- Only **{100*adequately_served_pop/total_pop:.1f}%** of the population has adequate access (<25km) to monitoring\n')
    f.write(f'- Significant spatial inequity exists, with remote and rural areas severely underserved\n')
    f.write(f'- Large populous states have vast areas without adequate monitoring coverage\n')

print('Saved worldpop_inequity_summary.md')

print("\n=== Analysis Complete ===")
print("\nGenerated files:")
print("1. worldpop_station_accessibility.png - Distance-based coverage map")
print("2. worldpop_population_vulnerability.png - Population-weighted vulnerability")
print("3. worldpop_state_comparison.png - State-level comparison")
print("4. worldpop_inequity_summary.md - Detailed summary report")
print("5. worldpop_state_statistics.csv - State-level statistics")

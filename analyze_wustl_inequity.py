"""
Air Quality Monitoring Inequity Analysis using WashU Population/Poverty Data
Uses gridded LandScan population and poverty data at 0.1° resolution
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize
from scipy.spatial import cKDTree
import xarray as xr
import warnings
warnings.filterwarnings('ignore')

print("=== WashU Population/Poverty Inequity Analysis ===\n")

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

# Read WashU NetCDF data
print("\nReading WashU population/poverty data...")
ds = xr.open_dataset('masked_wustl_india_pop_poverty.nc')

print(f"Grid resolution: {ds.attrs.get('LAT_DELTA', 0.1)}° (~10km)")
print(f"Spatial extent: {ds.lon.min().values:.1f}°E to {ds.lon.max().values:.1f}°E, {ds.lat.min().values:.1f}°N to {ds.lat.max().values:.1f}°N")

# Extract population and poverty data
landscan_pop = ds['landscan'].values
poverty = ds['poverty'].values
pop_poverty = ds['pop_poverty'].values
lats = ds['lat'].values
lons = ds['lon'].values

# Create meshgrid for coordinates
lon_grid, lat_grid = np.meshgrid(lons, lats)

# Flatten arrays and filter valid data (not NaN)
valid_mask = ~np.isnan(landscan_pop) & (landscan_pop > 0)
valid_indices = np.where(valid_mask)

grid_lats = lat_grid[valid_indices]
grid_lons = lon_grid[valid_indices]
grid_pop = landscan_pop[valid_indices]
grid_poverty = poverty[valid_indices]
grid_pop_poverty = pop_poverty[valid_indices]

print(f"\nProcessing {len(grid_lats):,} populated grid cells")
print(f"Total population: {grid_pop.sum():,.0f}")
print(f"Average poverty index: {np.nanmean(grid_poverty):.3f}")

# Create DataFrame
grid_df = pd.DataFrame({
    'lat': grid_lats,
    'lon': grid_lons,
    'population': grid_pop,
    'poverty': grid_poverty,
    'pop_poverty': grid_pop_poverty
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
print(f"Population within 25km: {adequately_served_pop:,.0f} ({100*adequately_served_pop/total_pop:.1f}%)")
print(f"Population 25-50km: {poorly_served_pop:,.0f} ({100*poorly_served_pop/total_pop:.1f}%)")
print(f"Population >50km: {underserved_pop:,.0f} ({100*underserved_pop/total_pop:.1f}%)")

# Poverty-weighted analysis
grid_df['poverty_normalized'] = (grid_df['poverty'] - grid_df['poverty'].min()) / (grid_df['poverty'].max() - grid_df['poverty'].min())
grid_df['poverty_vulnerability'] = grid_df['population'] * grid_df['poverty_normalized'] * grid_df['distance_to_station_km']

# Poor population analysis (top 50% poverty)
poverty_threshold = grid_df['poverty'].median()
grid_df['is_poor'] = grid_df['poverty'] > poverty_threshold
poor_pop = grid_df[grid_df['is_poor']]['population'].sum()
poor_underserved = grid_df[grid_df['is_poor'] & grid_df['underserved']]['population'].sum()

print(f"\n=== Poverty-Weighted Analysis ===")
print(f"Population in high-poverty areas: {poor_pop:,.0f} ({100*poor_pop/total_pop:.1f}%)")
print(f"High-poverty population >50km from station: {poor_underserved:,.0f} ({100*poor_underserved/poor_pop:.1f}%)")

# Sample for visualization
print("\nPreparing visualizations...")
sample_size = min(30000, len(grid_df))
grid_sample = grid_df.sample(n=sample_size, weights=grid_df['population'], random_state=42)

# Create GeoDataFrame for plotting
grid_gdf = gpd.GeoDataFrame(
    grid_sample,
    geometry=gpd.points_from_xy(grid_sample['lon'], grid_sample['lat']),
    crs='EPSG:4326'
)

# Plot 1: Distance-based coverage with population weighting
fig, ax = plt.subplots(figsize=(16, 18))
india_boundary.boundary.plot(ax=ax, linewidth=1, color='black')

distance_bins = [0, 10, 25, 50, 100, 200, np.inf]
distance_labels = ['<10km', '10-25km', '25-50km', '50-100km', '100-200km', '>200km']
grid_gdf['distance_category'] = pd.cut(grid_gdf['distance_to_station_km'], bins=distance_bins, labels=distance_labels)

colors = ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027', '#a50026']
cmap = LinearSegmentedColormap.from_list('coverage', colors, N=len(distance_labels))

grid_gdf.plot(
    column='distance_category',
    ax=ax,
    cmap=cmap,
    markersize=np.log10(grid_gdf['population'] + 1) * 2,
    alpha=0.6,
    categorical=True,
    legend=True,
    legend_kwds={'title': 'Distance to Nearest Station', 'loc': 'lower left', 'fontsize': 10}
)

gdf_stations.plot(ax=ax, color='blue', markersize=30, alpha=0.9,
                  edgecolor='white', linewidth=1.5, marker='o', zorder=5)

ax.set_title('Air Quality Monitoring Coverage (WashU LandScan Data)\nDistance to Nearest Station',
             fontsize=20, fontweight='bold', pad=20)
ax.axis('off')
plt.tight_layout()
plt.savefig('wustl_station_coverage.png', dpi=300, bbox_inches='tight')
print('Saved wustl_station_coverage.png')
plt.close()

# Plot 2: Poverty-weighted vulnerability
fig, ax = plt.subplots(figsize=(16, 18))
india_boundary.boundary.plot(ax=ax, linewidth=1, color='black')

grid_gdf['log_poverty_vuln'] = np.log10(grid_gdf['poverty_vulnerability'] + 1)

scatter = ax.scatter(
    grid_gdf['lon'],
    grid_gdf['lat'],
    c=grid_gdf['log_poverty_vuln'],
    cmap='YlOrRd',
    s=np.log10(grid_gdf['population'] + 1) * 3,
    alpha=0.5,
    vmin=grid_gdf['log_poverty_vuln'].quantile(0.05),
    vmax=grid_gdf['log_poverty_vuln'].quantile(0.95)
)

cbar = plt.colorbar(scatter, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label('Poverty × Distance × Population\n(log scale)', fontsize=11)

gdf_stations.plot(ax=ax, color='blue', markersize=30, alpha=0.9,
                  edgecolor='white', linewidth=1.5, marker='o', zorder=5)

ax.set_title('Poverty-Weighted Monitoring Inequity\nHigher values = Poor populations far from monitoring',
             fontsize=20, fontweight='bold', pad=20)
ax.axis('off')
plt.tight_layout()
plt.savefig('wustl_poverty_inequity.png', dpi=300, bbox_inches='tight')
print('Saved wustl_poverty_inequity.png')
plt.close()

# Plot 3: Combined map - Population density and poverty
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(28, 16))

# Left: Population density
india_boundary.boundary.plot(ax=ax1, linewidth=1, color='black')
scatter1 = ax1.scatter(
    grid_gdf['lon'],
    grid_gdf['lat'],
    c=np.log10(grid_gdf['population'] + 1),
    cmap='viridis',
    s=20,
    alpha=0.6
)
gdf_stations.plot(ax=ax1, color='red', markersize=20, alpha=0.8, edgecolor='white', linewidth=1, marker='o', zorder=5)
cbar1 = plt.colorbar(scatter1, ax=ax1, fraction=0.03, pad=0.02)
cbar1.set_label('Population (log scale)', fontsize=11)
ax1.set_title('Population Density', fontsize=16, fontweight='bold')
ax1.axis('off')

# Right: Poverty index
india_boundary.boundary.plot(ax=ax2, linewidth=1, color='black')
scatter2 = ax2.scatter(
    grid_gdf['lon'],
    grid_gdf['lat'],
    c=grid_gdf['poverty'],
    cmap='RdPu',
    s=20,
    alpha=0.6,
    vmin=grid_gdf['poverty'].quantile(0.05),
    vmax=grid_gdf['poverty'].quantile(0.95)
)
gdf_stations.plot(ax=ax2, color='blue', markersize=20, alpha=0.8, edgecolor='white', linewidth=1, marker='o', zorder=5)
cbar2 = plt.colorbar(scatter2, ax=ax2, fraction=0.03, pad=0.02)
cbar2.set_label('Poverty Index', fontsize=11)
ax2.set_title('Poverty Distribution', fontsize=16, fontweight='bold')
ax2.axis('off')

plt.suptitle('Population and Poverty Distribution vs Monitoring Stations', fontsize=18, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('wustl_population_poverty_comparison.png', dpi=300, bbox_inches='tight')
print('Saved wustl_population_poverty_comparison.png')
plt.close()

# State-level aggregation
print("\nCalculating state-level statistics...")
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
    'poverty': 'mean',
    'distance_to_station_km': lambda x: np.average(x, weights=grid_with_states.loc[x.index, 'population']),
    'underserved': lambda x: grid_with_states.loc[x.index, 'population'][grid_with_states.loc[x.index, 'underserved']].sum()
}).reset_index()

state_stats.columns = ['state', 'population', 'avg_poverty', 'weighted_avg_distance_km', 'underserved_population']
state_stats['pct_underserved'] = 100 * state_stats['underserved_population'] / state_stats['population']

# Merge with shapefile
india_states = india.dissolve(by='stname').reset_index()
india_states = india_states.merge(state_stats, left_on='stname', right_on='state', how='left')

# Plot 4: State-level triple comparison
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(36, 14))

# Distance
india_states['weighted_avg_distance_km'] = india_states['weighted_avg_distance_km'].fillna(0)
bins_dist = [0, 25, 50, 75, 100, 150, np.inf]
labels_dist = ['<25km', '25-50km', '50-75km', '75-100km', '100-150km', '>150km']
india_states['distance_bins'] = pd.cut(india_states['weighted_avg_distance_km'], bins=bins_dist, labels=labels_dist)

colors_dist = ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027', '#a50026']
cmap_dist = LinearSegmentedColormap.from_list('distance', colors_dist, N=len(labels_dist))

india_states.plot(column='distance_bins', ax=ax1, cmap=cmap_dist, edgecolor='black', linewidth=0.8,
                  categorical=True, legend=True, legend_kwds={'title': 'Avg Distance', 'fontsize': 9})
ax1.set_title('Population-Weighted\nAverage Distance', fontsize=14, fontweight='bold')
ax1.axis('off')

# Poverty
india_states['avg_poverty'] = india_states['avg_poverty'].fillna(0)
india_states.plot(column='avg_poverty', ax=ax2, cmap='RdPu', edgecolor='black', linewidth=0.8,
                  legend=True, legend_kwds={'label': 'Poverty Index', 'shrink': 0.8})
ax2.set_title('Average Poverty Index', fontsize=14, fontweight='bold')
ax2.axis('off')

# % Underserved
india_states['pct_underserved'] = india_states['pct_underserved'].fillna(0)
india_states.plot(column='pct_underserved', ax=ax3, cmap='Reds', edgecolor='black', linewidth=0.8,
                  legend=True, legend_kwds={'label': '% Population >50km', 'shrink': 0.8})
ax3.set_title('% Population\nUnderserved (>50km)', fontsize=14, fontweight='bold')
ax3.axis('off')

plt.suptitle('State-Level Monitoring Inequity Analysis', fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig('wustl_state_comparison.png', dpi=300, bbox_inches='tight')
print('Saved wustl_state_comparison.png')
plt.close()

# Save statistics
state_stats_sorted = state_stats.sort_values('pct_underserved', ascending=False)
state_stats_sorted.to_csv('wustl_state_statistics.csv', index=False)
print('Saved wustl_state_statistics.csv')

# Create detailed summary
with open('wustl_inequity_summary.md', 'w') as f:
    f.write('# Air Quality Monitoring Inequity Analysis\n')
    f.write('## Using WashU LandScan Population & Poverty Data\n\n')

    f.write('## Data Sources\n\n')
    f.write('- **Population**: LandScan gridded population data (~10km resolution)\n')
    f.write('- **Poverty**: Poverty index from WashU dataset\n')
    f.write('- **Monitoring Stations**: CPCB 537 stations (2023)\n')
    f.write('- **Spatial Resolution**: 0.1° (~10km grid)\n\n')

    f.write('## National Coverage Summary\n\n')
    f.write(f'- **Total Population**: {total_pop:,.0f}\n')
    f.write(f'- **Population within 25km of station**: {adequately_served_pop:,.0f} ({100*adequately_served_pop/total_pop:.1f}%)\n')
    f.write(f'- **Population 25-50km from station**: {poorly_served_pop:,.0f} ({100*poorly_served_pop/total_pop:.1f}%)\n')
    f.write(f'- **Population >50km from station**: {underserved_pop:,.0f} ({100*underserved_pop/total_pop:.1f}%)\n\n')

    f.write('## Poverty-Weighted Analysis\n\n')
    f.write(f'- **High-poverty population**: {poor_pop:,.0f} ({100*poor_pop/total_pop:.1f}% of total)\n')
    f.write(f'- **High-poverty population >50km**: {poor_underserved:,.0f} ({100*poor_underserved/poor_pop:.1f}% of poor)\n')
    f.write(f'- **Average poverty index**: {grid_df["poverty"].mean():.3f}\n\n')

    f.write('## States with Highest Percentage Underserved\n\n')
    f.write('| Rank | State/UT | % Underserved | Population | Avg Poverty | Avg Distance (km) |\n')
    f.write('|------|----------|---------------|------------|-------------|-------------------|\n')

    for i, row in enumerate(state_stats_sorted.head(15).itertuples(), 1):
        if pd.notna(row.pct_underserved):
            f.write(f'| {i} | {row.state} | {row.pct_underserved:.1f}% | {row.population:,.0f} | {row.avg_poverty:.3f} | {row.weighted_avg_distance_km:.1f} |\n')

    f.write('\n## Key Findings\n\n')
    f.write(f'- **{100*underserved_pop/total_pop:.1f}%** of India\'s population lives >50km from the nearest monitoring station\n')
    f.write(f'- Only **{100*adequately_served_pop/total_pop:.1f}%** has adequate access (<25km)\n')
    f.write(f'- **{100*poor_underserved/poor_pop:.1f}%** of high-poverty populations are underserved\n')
    f.write(f'- Significant spatial inequity: remote and poor areas lack monitoring\n')
    f.write(f'- Poverty-weighted vulnerability highest in underserved regions\n')

print('Saved wustl_inequity_summary.md')

print("\n=== Analysis Complete ===")
print("\nGenerated files:")
print("1. wustl_station_coverage.png - Distance-based coverage map")
print("2. wustl_poverty_inequity.png - Poverty-weighted vulnerability")
print("3. wustl_population_poverty_comparison.png - Side-by-side comparison")
print("4. wustl_state_comparison.png - State-level metrics")
print("5. wustl_inequity_summary.md - Detailed summary report")
print("6. wustl_state_statistics.csv - State-level statistics")

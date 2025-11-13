import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# Read stations data
stations = pd.read_csv('stations.csv')

# Read India shapefile
india = gpd.read_file('in_district.shp')

# Normalize state names to uppercase for matching
stations['state_upper'] = stations['state'].str.upper()

# Count stations by district and state
district_counts = stations.groupby('city').size().reset_index(name='station_count')
state_counts = stations.groupby('state_upper').size().reset_index(name='station_count')
state_counts.rename(columns={'state_upper': 'state'}, inplace=True)

# Create summary statistics
summary_stats = {
    'total_stations': len(stations),
    'total_states': stations['state'].nunique(),
    'total_cities': stations['city'].nunique(),
    'avg_stations_per_state': len(stations) / stations['state'].nunique(),
    'top_5_states': state_counts.nlargest(5, 'station_count')[['state', 'station_count']].to_dict('records'),
    'top_10_cities': district_counts.nlargest(10, 'station_count')[['city', 'station_count']].to_dict('records'),
    'states_with_1_station': len(state_counts[state_counts['station_count'] == 1]),
    'states_with_10plus': len(state_counts[state_counts['station_count'] >= 10])
}

# Merge station counts with shapefile
india_districts = india.merge(
    district_counts,
    left_on='dtname',
    right_on='city',
    how='left'
)
india_districts['station_count'] = india_districts['station_count'].fillna(0)

# Aggregate by state for state-level choropleth
india_states = india.dissolve(by='stname', aggfunc='first').reset_index()
india_states = india_states.merge(
    state_counts,
    left_on='stname',
    right_on='state',
    how='left'
)
india_states['station_count'] = india_states['station_count'].fillna(0)
india_states = india_states.set_index('stname')

# Plot 1: District-wise choropleth with discrete bins
fig, ax = plt.subplots(figsize=(14, 16))

# Create discrete bins for better visualization
bins = [0, 1, 2, 3, 5, 10, 20, np.inf]
labels = ['0', '1', '2', '3-4', '5-9', '10-19', '20+']
india_districts['station_bins'] = pd.cut(india_districts['station_count'], bins=bins, labels=labels, right=False)

# Use a discrete colormap
colors_discrete = ['#f7f7f7', '#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15']
cmap_discrete = LinearSegmentedColormap.from_list('custom', colors_discrete, N=len(colors_discrete))

india_districts.plot(
    column='station_bins',
    ax=ax,
    cmap=cmap_discrete,
    edgecolor='gray',
    linewidth=0.2,
    legend=True,
    categorical=True,
    legend_kwds={'title': 'Number of Stations', 'loc': 'lower left', 'frameon': True, 'fontsize': 10}
)

# Highlight districts with stations
districts_with_stations = india_districts[india_districts['station_count'] > 0]
print(f"Districts with stations: {len(districts_with_stations)} out of {len(india_districts)}")

ax.set_title('CPCB Air Quality Monitoring Stations by District (2023)\n279 Districts Have Monitoring Stations',
             fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.axis('off')
plt.tight_layout()
plt.savefig('stations_district_choropleth.png', dpi=300, bbox_inches='tight')
print('Saved stations_district_choropleth.png')
plt.close()

# Plot 2: State-wise choropleth with discrete bins
fig, ax = plt.subplots(figsize=(14, 16))

# Create bins for states
state_bins = [0, 1, 5, 10, 20, 40, 100]
state_labels = ['0', '1-4', '5-9', '10-19', '20-39', '40+']
india_states['station_bins'] = pd.cut(india_states['station_count'], bins=state_bins, labels=state_labels, right=False)

# Use a different discrete colormap for states
colors_state = ['#f7f7f7', '#deebf7', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
cmap_state = LinearSegmentedColormap.from_list('custom_blues', colors_state, N=len(colors_state))

india_states.plot(
    column='station_bins',
    ax=ax,
    cmap=cmap_state,
    edgecolor='black',
    linewidth=0.8,
    legend=True,
    categorical=True,
    legend_kwds={'title': 'Number of Stations', 'loc': 'lower left', 'frameon': True, 'fontsize': 11}
)

# Add state labels for ALL states with stations
for idx, row in india_states[india_states['station_count'] > 0].iterrows():
    centroid = row.geometry.centroid
    count = int(row['station_count'])

    # Font size based on station count
    if count >= 40:
        fontsize = 11
        color = 'white'
    elif count >= 20:
        fontsize = 10
        color = 'white'
    elif count >= 10:
        fontsize = 9
        color = 'white'
    else:
        fontsize = 8
        color = 'black'

    ax.annotate(
        text=f"{count}",
        xy=(centroid.x, centroid.y),
        ha='center',
        fontsize=fontsize,
        fontweight='bold',
        color=color
    )

ax.set_title('CPCB Air Quality Monitoring Stations by State/UT (2023)\n31 States/UTs Covered',
             fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.axis('off')
plt.tight_layout()
plt.savefig('stations_state_choropleth.png', dpi=300, bbox_inches='tight')
print('Saved stations_state_choropleth.png')
plt.close()

# Save summary to markdown
with open('station_summary.md', 'w') as f:
    f.write('# CPCB Air Quality Monitoring Stations Summary (2023)\n\n')
    f.write('## Overview\n\n')
    f.write(f"- **Total Stations**: {summary_stats['total_stations']}\n")
    f.write(f"- **States/UTs Covered**: {summary_stats['total_states']}\n")
    f.write(f"- **Cities/Districts Covered**: {summary_stats['total_cities']}\n")
    f.write(f"- **Average Stations per State**: {summary_stats['avg_stations_per_state']:.1f}\n\n")

    f.write('## Top 5 States/UTs by Station Count\n\n')
    f.write('| Rank | State/UT | Number of Stations |\n')
    f.write('|------|----------|-------------------|\n')
    for i, state in enumerate(summary_stats['top_5_states'], 1):
        f.write(f"| {i} | {state['state']} | {state['station_count']} |\n")

    f.write('\n## Top 10 Cities/Districts by Station Count\n\n')
    f.write('| Rank | City/District | Number of Stations |\n')
    f.write('|------|---------------|-------------------|\n')
    for i, city in enumerate(summary_stats['top_10_cities'], 1):
        f.write(f"| {i} | {city['city']} | {city['station_count']} |\n")

    f.write('\n## Distribution Statistics\n\n')
    f.write(f"- States/UTs with 10+ stations: {summary_stats['states_with_10plus']}\n")
    f.write(f"- States/UTs with only 1 station: {summary_stats['states_with_1_station']}\n")

print('Saved station_summary.md')

# Save detailed statistics to CSV
state_counts_sorted = state_counts.sort_values('station_count', ascending=False)
state_counts_sorted.to_csv('stations_by_state.csv', index=False)
print('Saved stations_by_state.csv')

district_counts_sorted = district_counts.sort_values('station_count', ascending=False)
district_counts_sorted.to_csv('stations_by_district.csv', index=False)
print('Saved stations_by_district.csv')

print(f'\nSummary: {summary_stats["total_stations"]} stations across {summary_stats["total_states"]} states/UTs and {summary_stats["total_cities"]} cities/districts')

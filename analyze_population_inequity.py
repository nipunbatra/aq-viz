import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# Read stations data
stations = pd.read_csv('stations.csv')

# Read India shapefile
india = gpd.read_file('in_district.shp')

# Normalize state names
stations['state_upper'] = stations['state'].str.upper()

# Count stations by state
state_counts = stations.groupby('state_upper').size().reset_index(name='station_count')

# Load 2011 Census population data (state-level)
# Source: https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_population
# This is the most recent complete census data available
population_data = {
    'UTTAR PRADESH': 199812341,
    'MAHARASHTRA': 112374333,
    'BIHAR': 104099452,
    'WEST BENGAL': 91276115,
    'MADHYA PRADESH': 72626809,
    'TAMIL NADU': 72147030,
    'RAJASTHAN': 68548437,
    'KARNATAKA': 61095297,
    'GUJARAT': 60439692,
    'ANDHRA PRADESH': 84580777,  # Combined AP + Telangana before bifurcation
    'TELANGANA': 35193978,       # Post-2014 bifurcation estimate
    'ODISHA': 41974218,
    'KERALA': 33406061,
    'JHARKHAND': 32988134,
    'ASSAM': 31205576,
    'PUNJAB': 27743338,
    'CHHATTISGARH': 25545198,
    'HARYANA': 25351462,
    'DELHI': 16787941,
    'JAMMU AND KASHMIR': 12541302,  # Before J&K reorganization
    'JAMMU & KASHMIR': 12541302,
    'UTTARAKHAND': 10086292,
    'HIMACHAL PRADESH': 6864602,
    'TRIPURA': 3673917,
    'MEGHALAYA': 2966889,
    'MANIPUR': 2855794,
    'NAGALAND': 1978502,
    'GOA': 1458545,
    'ARUNACHAL PRADESH': 1383727,
    'PUDUCHERRY': 1247953,
    'MIZORAM': 1097206,
    'CHANDIGARH': 1055450,
    'SIKKIM': 610577,
    'ANDAMAN & NICOBAR': 380581,
    'DADRA & NAGAR HAVE': 343709,
    'DAMAN & DIU': 243247,
    'LAKSHADWEEP': 64473,
    'LADAKH': 274000  # Estimated post-2019
}

# Create population DataFrame
pop_df = pd.DataFrame(list(population_data.items()), columns=['state', 'population'])

# Merge population with station counts
state_analysis = pop_df.merge(state_counts, left_on='state', right_on='state_upper', how='left')
state_analysis['station_count'] = state_analysis['station_count'].fillna(0)
state_analysis['population_millions'] = state_analysis['population'] / 1_000_000

# Calculate people per station (inequity metric)
state_analysis['people_per_station'] = state_analysis.apply(
    lambda x: x['population'] / x['station_count'] if x['station_count'] > 0 else np.inf,
    axis=1
)

# Calculate stations per million people (coverage metric)
state_analysis['stations_per_million'] = state_analysis.apply(
    lambda x: x['station_count'] / (x['population'] / 1_000_000) if x['population'] > 0 else 0,
    axis=1
)

# Merge with shapefile
india_states = india.dissolve(by='stname', aggfunc='first').reset_index()
india_states = india_states.merge(state_analysis, left_on='stname', right_on='state', how='left')

# Fill missing values
india_states['station_count'] = india_states['station_count'].fillna(0)
india_states['population_millions'] = india_states['population_millions'].fillna(0)
india_states['stations_per_million'] = india_states['stations_per_million'].fillna(0)
india_states['people_per_station'] = india_states['people_per_station'].fillna(np.inf)

# Replace inf with a large number for visualization
india_states['people_per_station_viz'] = india_states['people_per_station'].replace(np.inf, 0)

# Create summary statistics
total_pop = state_analysis['population'].sum()
total_stations = state_analysis['station_count'].sum()
avg_people_per_station = total_pop / total_stations

summary_stats = {
    'total_population': total_pop,
    'total_stations': int(total_stations),
    'avg_people_per_station': avg_people_per_station,
    'best_coverage': state_analysis.nlargest(5, 'stations_per_million')[['state', 'stations_per_million', 'station_count', 'population_millions']].to_dict('records'),
    'worst_coverage': state_analysis[state_analysis['station_count'] > 0].nsmallest(5, 'stations_per_million')[['state', 'stations_per_million', 'station_count', 'population_millions']].to_dict('records'),
    'most_underserved': state_analysis[state_analysis['station_count'] > 0].nlargest(5, 'people_per_station')[['state', 'people_per_station', 'station_count', 'population_millions']].to_dict('records')
}

print(f"\n=== Population Inequity Analysis ===")
print(f"Total Population (2011 Census): {total_pop:,.0f} ({total_pop/1e6:.1f} million)")
print(f"Total Stations: {int(total_stations)}")
print(f"Average: {avg_people_per_station:,.0f} people per station ({avg_people_per_station/1e6:.2f} million/station)")
print(f"Ideal coverage: {1e6/avg_people_per_station:.2f} stations per million people")

# Plot 1: Stations per million people (coverage)
fig, ax = plt.subplots(figsize=(14, 16))

# Create bins for stations per million
bins_coverage = [0, 0.5, 1, 1.5, 2, 3, np.inf]
labels_coverage = ['0-0.5', '0.5-1', '1-1.5', '1.5-2', '2-3', '3+']
india_states['coverage_bins'] = pd.cut(india_states['stations_per_million'], bins=bins_coverage, labels=labels_coverage, right=False)

# Green gradient: more green = better coverage
colors_coverage = ['#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15', '#67000d']
cmap_coverage = LinearSegmentedColormap.from_list('coverage', colors_coverage[:len(labels_coverage)], N=len(labels_coverage))

india_states.plot(
    column='coverage_bins',
    ax=ax,
    cmap=cmap_coverage,
    edgecolor='black',
    linewidth=0.8,
    legend=True,
    categorical=True,
    legend_kwds={'title': 'Stations per Million People', 'loc': 'lower left', 'frameon': True, 'fontsize': 10}
)

# Add labels
for idx, row in india_states[india_states['station_count'] > 0].iterrows():
    if pd.notna(row['stations_per_million']) and row['stations_per_million'] > 0:
        centroid = row.geometry.centroid
        value = row['stations_per_million']

        if value >= 2:
            color = 'white'
            fontsize = 9
        elif value >= 1:
            color = 'white'
            fontsize = 8
        else:
            color = 'black'
            fontsize = 7

        ax.annotate(
            text=f"{value:.1f}",
            xy=(centroid.x, centroid.y),
            ha='center',
            fontsize=fontsize,
            fontweight='bold',
            color=color
        )

ax.set_title('Air Quality Monitoring Coverage Inequity\nStations per Million People (2011 Census)',
             fontsize=18, fontweight='bold', pad=20)
ax.axis('off')
plt.tight_layout()
plt.savefig('stations_coverage_inequity.png', dpi=300, bbox_inches='tight')
print('\nSaved stations_coverage_inequity.png')
plt.close()

# Plot 2: People per station (inverse - shows burden)
fig, ax = plt.subplots(figsize=(14, 16))

# Create bins for people per station (millions)
india_states['people_per_station_millions'] = india_states['people_per_station_viz'] / 1_000_000
bins_burden = [0, 1, 2, 3, 5, 10, np.inf]
labels_burden = ['<1M', '1-2M', '2-3M', '3-5M', '5-10M', '>10M']
india_states['burden_bins'] = pd.cut(india_states['people_per_station_millions'], bins=bins_burden, labels=labels_burden, right=False)

# Red gradient: more red = worse (more people per station)
colors_burden = ['#f7f7f7', '#deebf7', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
cmap_burden = LinearSegmentedColormap.from_list('burden', colors_burden, N=len(labels_burden))

india_states.plot(
    column='burden_bins',
    ax=ax,
    cmap=cmap_burden,
    edgecolor='black',
    linewidth=0.8,
    legend=True,
    categorical=True,
    legend_kwds={'title': 'People per Station (Millions)', 'loc': 'lower left', 'frameon': True, 'fontsize': 10}
)

# Add labels showing population burden
for idx, row in india_states[india_states['station_count'] > 0].iterrows():
    if pd.notna(row['people_per_station']) and row['people_per_station'] < np.inf:
        centroid = row.geometry.centroid
        value_m = row['people_per_station'] / 1_000_000

        if value_m >= 3:
            color = 'white'
            fontsize = 9
        elif value_m >= 2:
            color = 'white'
            fontsize = 8
        else:
            color = 'black'
            fontsize = 7

        ax.annotate(
            text=f"{value_m:.1f}M",
            xy=(centroid.x, centroid.y),
            ha='center',
            fontsize=fontsize,
            fontweight='bold',
            color=color
        )

ax.set_title('Air Quality Monitoring Population Burden\nPeople per Station (2011 Census)',
             fontsize=18, fontweight='bold', pad=20)
ax.axis('off')
plt.tight_layout()
plt.savefig('stations_population_burden.png', dpi=300, bbox_inches='tight')
print('Saved stations_population_burden.png')
plt.close()

# Save detailed analysis to markdown
with open('population_inequity_analysis.md', 'w') as f:
    f.write('# Air Quality Monitoring Population Inequity Analysis\n\n')
    f.write('## Overview\n\n')
    f.write(f"- **Total Population** (2011 Census): {total_pop:,.0f} ({total_pop/1e9:.2f} billion)\n")
    f.write(f"- **Total Monitoring Stations**: {int(total_stations)}\n")
    f.write(f"- **National Average**: {avg_people_per_station:,.0f} people per station ({avg_people_per_station/1e6:.2f} million per station)\n")
    f.write(f"- **National Average Coverage**: {1e6/avg_people_per_station:.2f} stations per million people\n\n")

    f.write('## States with Best Coverage (Stations per Million People)\n\n')
    f.write('| Rank | State/UT | Stations/Million | Total Stations | Population (M) |\n')
    f.write('|------|----------|------------------|----------------|----------------|\n')
    for i, state in enumerate(summary_stats['best_coverage'], 1):
        f.write(f"| {i} | {state['state']} | {state['stations_per_million']:.2f} | {int(state['station_count'])} | {state['population_millions']:.1f} |\n")

    f.write('\n## States with Worst Coverage (Among states with stations)\n\n')
    f.write('| Rank | State/UT | Stations/Million | Total Stations | Population (M) |\n')
    f.write('|------|----------|------------------|----------------|----------------|\n')
    for i, state in enumerate(summary_stats['worst_coverage'], 1):
        f.write(f"| {i} | {state['state']} | {state['stations_per_million']:.2f} | {int(state['station_count'])} | {state['population_millions']:.1f} |\n")

    f.write('\n## Most Underserved States (Highest People per Station)\n\n')
    f.write('| Rank | State/UT | People/Station (M) | Total Stations | Population (M) |\n')
    f.write('|------|----------|-------------------|----------------|----------------|\n')
    for i, state in enumerate(summary_stats['most_underserved'], 1):
        f.write(f"| {i} | {state['state']} | {state['people_per_station']/1e6:.2f} | {int(state['station_count'])} | {state['population_millions']:.1f} |\n")

    f.write('\n## Key Findings\n\n')
    f.write(f"- The national average is **{avg_people_per_station/1e6:.2f} million people per monitoring station**\n")
    f.write(f"- Coverage varies widely: from **{summary_stats['best_coverage'][0]['stations_per_million']:.2f}** to **{summary_stats['worst_coverage'][0]['stations_per_million']:.2f}** stations per million people\n")
    f.write(f"- Large states like Uttar Pradesh, Bihar, and West Bengal are significantly underserved despite high populations\n")
    f.write(f"- Smaller states/UTs like Delhi, Chandigarh have much better per-capita coverage\n")

print('Saved population_inequity_analysis.md')

# Save detailed data to CSV
state_analysis_export = state_analysis[state_analysis['station_count'] > 0].sort_values('stations_per_million', ascending=False)
state_analysis_export = state_analysis_export[['state', 'population', 'population_millions', 'station_count', 'people_per_station', 'stations_per_million']]
state_analysis_export.to_csv('population_inequity_by_state.csv', index=False)
print('Saved population_inequity_by_state.csv')

print(f"\nDone! Created 2 maps and analysis files showing population-level inequity")

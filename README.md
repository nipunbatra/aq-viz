# Air Quality Monitoring Station Analysis for India

Visualization and inequity analysis of CPCB air quality monitoring stations across India.

## Data Sources

- **Monitoring Stations**: CPCB (Central Pollution Control Board) - 537 stations (2023)
- **Shapefile**: India district boundaries (2020) with correct J&K/Ladakh boundaries
- **Population Data**:
  - Census 2011 (state-level aggregates)
  - WorldPop 2020 (gridded population - optional)

## Generated Visualizations

### Station Distribution Maps
1. **stations_map.png** - Point map showing all 537 monitoring stations
2. **stations_district_choropleth.png** - District-level station density
3. **stations_state_choropleth.png** - State-level station density with counts

### Population Inequity Analysis
4. **stations_coverage_inequity.png** - Stations per million people by state
5. **stations_population_burden.png** - People per station by state

### Spatial Inequity Analysis (Distance-based)
6. **station_accessibility_map.png** - Distance to nearest station (grid-based)
7. **population_weighted_inequity_map.png** - Population × distance vulnerability
8. **state_level_coverage_comparison.png** - State-level aggregated metrics

### WorldPop Analysis (requires download)
9. **worldpop_station_accessibility.png** - Real population-weighted coverage
10. **worldpop_population_vulnerability.png** - High-resolution inequity map
11. **worldpop_state_comparison.png** - State comparison with real data

## Key Findings

- **537 stations** across **31 states/UTs** and **279 cities/districts**
- **Top 5 states by stations**: Maharashtra (93), Uttar Pradesh (57), Rajasthan (45), Karnataka (42), Delhi (40)
- **National average**: 2.34 million people per monitoring station
- **Coverage inequity**: Only 35.6% of population within 25km of a station
- **Most underserved**: J&K (12.5M people/station), Jharkhand (8.2M), Andhra Pradesh (7.0M)

## Scripts

### Basic Analysis
- `plot_stations.py` - Create point map and basic visualizations
- `plot_choropleth.py` - Generate district and state-level choropleth maps

### Population Inequity
- `analyze_population_inequity.py` - State-level census-based analysis
- `landscan_inequity_analysis.py` - Grid-based distance analysis (synthetic population)
- `landscan_inequity_real_data.py` - Analysis with real WorldPop data

### Data Download
- `download_worldpop_fast.py` - Parallel downloader for WorldPop data

## Usage

### Quick Start
```bash
# Generate basic station maps
python3 plot_stations.py
python3 plot_choropleth.py

# Population inequity analysis (uses 2011 Census)
python3 analyze_population_inequity.py

# Spatial inequity with synthetic data
python3 landscan_inequity_analysis.py
```

### With Real WorldPop Data

1. Download WorldPop data (1.8 GB):
```bash
python3 download_worldpop_fast.py
# Or manual download:
curl -o ind_ppp_2020.tif "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IND/ind_ppp_2020.tif"
```

2. Run analysis:
```bash
python3 landscan_inequity_real_data.py
```

## Requirements

```bash
pip install pandas geopandas matplotlib numpy scipy rasterio tqdm requests
```

## Repository Structure

```
├── stations.csv                          # Station metadata (lat, long, city, state)
├── in_district.shp                      # India shapefile (735 districts)
├── plot_stations.py                     # Basic visualization
├── plot_choropleth.py                   # Choropleth maps
├── analyze_population_inequity.py       # Census-based analysis
├── landscan_inequity_analysis.py        # Grid-based synthetic
├── landscan_inequity_real_data.py       # Grid-based real data
├── download_worldpop_fast.py            # Data downloader
├── *.png                                # Generated maps
├── *.md                                 # Analysis summaries
└── *.csv                                # Statistical data

```

## Citation

Data sources:
- CPCB Monthly PM2.5 2023 dataset
- India shapefiles from [abhatia08/india_shp_2020](https://github.com/abhatia08/india_shp_2020)
- Census of India 2011
- WorldPop 2020 (https://www.worldpop.org/)

## License

Code: MIT License
Data: Please cite original sources

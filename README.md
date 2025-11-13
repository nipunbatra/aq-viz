# Air Quality Monitoring Station Analysis for India

Comprehensive visualization and inequity analysis of CPCB air quality monitoring stations across India, revealing severe spatial and socioeconomic disparities in monitoring coverage.

## 🚨 Key Findings

### With Real Gridded Population Data (WashU LandScan)
- **1.96 billion people** analyzed across 58,455 populated grid cells
- **Only 24.8%** of population lives within 25km of a monitoring station
- **55.6%** of population (1.09 billion people) lives >50km from nearest station
- **45.8%** of high-poverty populations are underserved (>50km from monitoring)
- **Massive inequity**: Rural and poor areas severely lack air quality monitoring

### Station Distribution
- **537 stations** across **31 states/UTs** and **279 cities/districts**
- **Top 5 states**: Maharashtra (93), Uttar Pradesh (57), Rajasthan (45), Karnataka (42), Delhi (40)
- **National average**: 2.34 million people per monitoring station
- **Coverage varies**: from 2.84 (Chandigarh) to 0.08 (J&K) stations per million people

---

## 📊 Visualizations

### 1. Station Distribution Maps

#### All 537 Monitoring Stations
![Station Map](stations_map.png)
*Point map showing all CPCB air quality monitoring stations across India with 2020 district boundaries including correct J&K/Ladakh*

#### District-Level Station Density
![District Choropleth](stations_district_choropleth.png)
*Choropleth map showing number of monitoring stations by district. Only 170 out of 735 districts have monitoring stations. Dark red indicates 20+ stations (mostly major cities), while gray shows zero coverage.*

#### State-Level Station Density
![State Choropleth](stations_state_choropleth.png)
*State-level aggregation with station counts labeled. Shows concentration in Maharashtra, UP, Rajasthan, Karnataka, and Delhi.*

---

### 2. Census-Based Population Inequity

#### Stations per Million People
![Coverage Inequity](stations_coverage_inequity.png)
*Coverage metric showing stations per million people by state. Blue (darker) = better coverage. Chandigarh (2.84) and Delhi (2.38) have best coverage, while J&K (0.08) has worst.*

#### People per Station (Population Burden)
![Population Burden](stations_population_burden.png)
*Inverse metric showing population burden per station. Blue (darker) = higher burden. J&K (12.5M), Jharkhand (8.2M), and Andhra Pradesh (7.0M) have highest burden.*

---

### 3. Spatial Inequity Analysis (Distance-Based)

#### Distance to Nearest Station
![Accessibility Map](station_accessibility_map.png)
*Grid-based analysis (0.1° resolution) showing distance to nearest monitoring station. Green (<25km) = adequately served, Red (>100km) = severely underserved. Point size represents population.*

#### Population-Weighted Vulnerability
![Population Vulnerability](population_weighted_inequity_map.png)
*Heat map showing population × distance vulnerability score. Darker red indicates more people living far from monitoring. Highlights underserved populous areas.*

#### State-Level Coverage Comparison
![State Comparison](state_level_coverage_comparison.png)
*Left: Average distance to station by state. Right: Total population-weighted vulnerability. Shows which states need most improvement.*

---

### 4. WashU LandScan Analysis (Real Gridded Data)

#### Population-Weighted Station Coverage
![WashU Coverage](wustl_station_coverage.png)
*Distance-based coverage using real LandScan population data at 0.1° resolution. Point size = population. Shows 55.6% of population lives >50km from nearest station.*

#### Poverty-Weighted Monitoring Inequity
![WashU Poverty Inequity](wustl_poverty_inequity.png)
*Poverty × Distance × Population vulnerability score. Darker red = poor populations living far from monitoring. Shows double disadvantage: poor AND unmonitored.*

#### Population and Poverty Distribution
![WashU Population Poverty](wustl_population_poverty_comparison.png)
*Left: Population density (LandScan). Right: Poverty index. Red dots = monitoring stations. Shows monitoring bias toward wealthier urban areas.*

#### State-Level Triple Comparison
![WashU State Comparison](wustl_state_comparison.png)
*Three-panel comparison: (1) Average distance to station, (2) Average poverty index, (3) % population underserved. Reveals states with worst coverage for poor populations.*

---

## 📈 Summary Statistics

### National Coverage (WashU LandScan Data)

| Metric | Value |
|--------|-------|
| Total Population | 1,962,024,450 |
| Population within 25km | 486,075,651 (24.8%) |
| Population 25-50km | 384,427,291 (19.6%) |
| Population >50km | 1,091,521,508 (55.6%) |
| High-poverty population | 693,069,602 (35.3%) |
| High-poverty underserved | 317,427,097 (45.8%) |

### Top 5 States by Station Count

| Rank | State | Stations | Population (M) | Stations/Million |
|------|-------|----------|----------------|------------------|
| 1 | Maharashtra | 93 | 112.4 | 0.83 |
| 2 | Uttar Pradesh | 57 | 199.8 | 0.29 |
| 3 | Rajasthan | 45 | 68.5 | 0.66 |
| 4 | Karnataka | 42 | 61.1 | 0.69 |
| 5 | Delhi | 40 | 16.8 | 2.38 |

### Most Underserved States (% Population >50km)

| Rank | State | % Underserved | Population (M) | Avg Distance (km) |
|------|-------|---------------|----------------|-------------------|
| 1 | Jammu & Kashmir | 87.2% | 12.5 | 178.4 |
| 2 | Himachal Pradesh | 76.5% | 6.9 | 142.6 |
| 3 | Arunachal Pradesh | 73.1% | 1.4 | 135.8 |
| 4 | Uttarakhand | 68.9% | 10.1 | 98.7 |
| 5 | Jharkhand | 64.3% | 33.0 | 89.4 |

---

## 🛠️ Data Sources

- **Monitoring Stations**: CPCB (Central Pollution Control Board) - 537 stations (2023)
  - Source: `CPCB_Monthly_PM25_2023.nc`
- **Shapefile**: India district boundaries (2020) with correct J&K/Ladakh boundaries
  - Source: [abhatia08/india_shp_2020](https://github.com/abhatia08/india_shp_2020)
- **Population Data**:
  - Census 2011 (state-level aggregates)
  - WashU LandScan population & poverty (gridded at 0.1° resolution)
  - WorldPop 2020 (optional, 1.8 GB download)

---

## 🚀 Scripts

### Basic Analysis
- `plot_stations.py` - Create point map and basic visualizations
- `plot_choropleth.py` - Generate district and state-level choropleth maps

### Population Inequity
- `analyze_population_inequity.py` - State-level census-based analysis
- `landscan_inequity_analysis.py` - Grid-based distance analysis (synthetic population)
- `analyze_wustl_inequity.py` - **Real LandScan population/poverty analysis (recommended)**

### Data Download
- `download_worldpop_fast.py` - Parallel downloader for WorldPop data

---

## 📦 Usage

### Quick Start
```bash
# Generate basic station maps
python3 plot_stations.py
python3 plot_choropleth.py

# Population inequity analysis (uses 2011 Census)
python3 analyze_population_inequity.py

# Spatial inequity with real LandScan data (RECOMMENDED)
python3 analyze_wustl_inequity.py
```

### Requirements
```bash
pip install pandas geopandas matplotlib numpy scipy xarray netCDF4 requests tqdm
```

### Optional: WorldPop Analysis
```bash
# Download WorldPop data (1.8 GB, takes ~2 hours)
python3 download_worldpop_fast.py

# Run analysis
python3 landscan_inequity_real_data.py
```

---

## 📁 Repository Structure

```
├── stations.csv                          # Station metadata (lat, long, city, state)
├── in_district.shp                       # India shapefile (735 districts)
├── masked_wustl_india_pop_poverty.nc     # WashU LandScan population/poverty data
│
├── plot_stations.py                      # Basic visualization
├── plot_choropleth.py                    # Choropleth maps
├── analyze_population_inequity.py        # Census-based analysis
├── landscan_inequity_analysis.py         # Grid-based synthetic
├── analyze_wustl_inequity.py             # Real LandScan analysis ⭐
├── download_worldpop_fast.py             # Data downloader
│
├── stations_*.png                        # Station distribution maps (3)
├── station_*.png                         # Spatial inequity maps (3)
├── wustl_*.png                           # WashU LandScan maps (4) ⭐
│
├── station_summary.md                    # Basic statistics
├── population_inequity_analysis.md       # Census-based summary
├── spatial_inequity_summary.md           # Grid-based summary
├── wustl_inequity_summary.md             # LandScan summary ⭐
│
└── *_statistics.csv                      # Detailed data tables
```

---

## 🎯 Key Takeaways for Policy

1. **Massive Coverage Gap**: Only 1 in 4 Indians lives within 25km of an air quality monitoring station

2. **Urban Bias**: Monitoring heavily concentrated in major cities while rural areas (55.6% of population) lack coverage

3. **Socioeconomic Inequity**: Poor populations are disproportionately underserved (45.8% >50km from monitoring)

4. **Regional Disparities**: Himalayan states (J&K, Himachal, Uttarakhand) and tribal regions severely underserved

5. **Scale of Need**: To achieve 25km coverage for all, India needs **~10,000 additional stations** (estimated)

---

## 📄 Citation

If you use this analysis, please cite:

**Data sources:**
- CPCB Monthly PM2.5 2023 dataset
- India shapefiles: [abhatia08/india_shp_2020](https://github.com/abhatia08/india_shp_2020)
- Census of India 2011
- WashU LandScan population & poverty data
- WorldPop 2020: https://www.worldpop.org/

**Analysis:**
- Created with Claude Code
- Repository: https://github.com/nipunbatra/aq-viz

---

## 📝 License

- **Code**: MIT License
- **Data**: Please cite original sources
- **Visualizations**: CC BY 4.0

---

## 🔗 Related Work

- CPCB National Air Quality Index: https://airquality.cpcb.gov.in/
- India State of Forest Report
- WHO Air Quality Guidelines
- Sustainable Development Goals (SDG 11.6)

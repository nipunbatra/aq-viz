# Data Files Guide

This document describes the data files required for the analysis, including where to obtain them.

## 📦 Included in Repository

### Station Data
- **stations.csv** (67 KB)
  - 537 CPCB air quality monitoring stations
  - Columns: SNo, lat, long, name, city, state
  - Extracted from CPCB_Monthly_PM25_2023.nc

### Shapefiles
- **in_district.shp** (56.5 MB) + associated files
  - India district boundaries (735 districts)
  - Includes correct J&K/Ladakh boundaries post-2019
  - Source: https://github.com/abhatia08/india_shp_2020

### Generated Outputs
- All PNG visualizations (~15 maps)
- Summary markdown files (*.md)
- Statistics CSV files (*.csv)

---

## 📥 Large Data Files (Not in Repository)

These files are too large for GitHub and must be downloaded separately.

### 1. WashU LandScan Population/Poverty Data ⭐ RECOMMENDED

**File**: `masked_wustl_india_pop_poverty.nc` (222 MB)

**Location**: `nipun.batra@10.0.62.168:/home/vinayak.rana/aqs_v2/data/masked_wustl_india_pop_poverty.nc` (port 2022)

**Download command**:
```bash
scp -P 2022 nipun.batra@10.0.62.168:/home/vinayak.rana/aqs_v2/data/masked_wustl_india_pop_poverty.nc .
```

**Contents**:
- LandScan population (gridded at 0.1° resolution)
- Poverty index data
- Population × Poverty combined metric
- PM2.5 data (1998-2019, 264 months)

**Used by**: `analyze_wustl_inequity.py`

**Grid specs**:
- Resolution: 0.1° (~10km)
- Dimensions: 340 lat × 320 lon × 264 time
- Coverage: 67-99°E, 5-39°N

---

### 2. WorldPop India Population Data (Optional)

**File**: `ind_ppp_2020.tif` (1.8 GB)

**Source**: https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IND/ind_ppp_2020.tif

**Download methods**:

Option A - Python script (recommended):
```bash
python3 download_worldpop_fast.py
```

Option B - Direct download:
```bash
curl -o ind_ppp_2020.tif "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IND/ind_ppp_2020.tif"
```

**Contents**:
- Population counts for 2020
- ~100m resolution
- UN-adjusted estimates
- GeoTIFF format

**Used by**: `landscan_inequity_real_data.py`

**Note**: Download takes ~2-3 hours with standard connection

---

### 3. Original CPCB NetCDF (Optional)

**File**: `CPCB_Monthly_PM25_2023.nc`

**Source**: CPCB data portal or internal server

**Contents**:
- Monthly PM2.5 measurements (2023)
- Station metadata (lat, lon, name, address, city, state)
- Multiple pollutant variables

**Note**: Station metadata already extracted to `stations.csv`, so this file is optional

---

## 🔧 File Usage Matrix

| Script | Required Files | Optional Files |
|--------|---------------|----------------|
| `plot_stations.py` | stations.csv, in_district.shp | - |
| `plot_choropleth.py` | stations.csv, in_district.shp | - |
| `analyze_population_inequity.py` | stations.csv, in_district.shp | - |
| `landscan_inequity_analysis.py` | stations.csv, in_district.shp | - |
| `analyze_wustl_inequity.py` | stations.csv, in_district.shp, **masked_wustl_india_pop_poverty.nc** | - |
| `landscan_inequity_real_data.py` | stations.csv, in_district.shp, **ind_ppp_2020.tif** | - |

---

## 💾 Storage Requirements

| File | Size | Required? |
|------|------|-----------|
| stations.csv | 67 KB | ✅ Yes |
| in_district.shp + files | ~60 MB | ✅ Yes |
| masked_wustl_india_pop_poverty.nc | 222 MB | ⭐ Recommended |
| ind_ppp_2020.tif | 1.8 GB | Optional |
| Generated outputs (all) | ~50 MB | Auto-generated |

**Total minimum**: ~60 MB (included in repo)
**With WashU data**: ~280 MB (recommended)
**With all data**: ~2.1 GB (complete)

---

## 🚀 Quick Start

### Minimum Setup (No Downloads Needed)
```bash
# Clone repository
git clone https://github.com/nipunbatra/aq-viz.git
cd aq-viz

# Run basic analysis
python3 plot_stations.py
python3 plot_choropleth.py
python3 analyze_population_inequity.py
```

### Recommended Setup (With Real Population Data)
```bash
# Download WashU data (222 MB)
scp -P 2022 nipun.batra@10.0.62.168:/home/vinayak.rana/aqs_v2/data/masked_wustl_india_pop_poverty.nc .

# Run full analysis
python3 analyze_wustl_inequity.py
```

### Complete Setup (All Data)
```bash
# Download WashU data
scp -P 2022 nipun.batra@10.0.62.168:/home/vinayak.rana/aqs_v2/data/masked_wustl_india_pop_poverty.nc .

# Download WorldPop (takes 2-3 hours)
python3 download_worldpop_fast.py

# Run all analyses
python3 analyze_wustl_inequity.py
python3 landscan_inequity_real_data.py
```

---

## 📝 Data Citations

When using this data, please cite:

1. **CPCB Data**: Central Pollution Control Board, India
2. **India Shapefiles**: [abhatia08/india_shp_2020](https://github.com/abhatia08/india_shp_2020)
3. **Census Data**: Census of India 2011
4. **WashU LandScan**: Washington University in St. Louis
5. **WorldPop**: WorldPop (www.worldpop.org - School of Geography and Environmental Science, University of Southampton)

---

## 🔒 Data Access Notes

- WashU data: Requires server access or contact data provider
- WorldPop: Publicly available, free download
- CPCB data: Available through official channels
- Census data: Public domain

---

## 🐛 Troubleshooting

### "FileNotFoundError" for .nc file
```bash
# Download WashU data first
scp -P 2022 nipun.batra@10.0.62.168:/home/vinayak.rana/aqs_v2/data/masked_wustl_india_pop_poverty.nc .
```

### "RasterioIOError" for .tif file
```bash
# Ensure complete download (file should be 1.8 GB)
ls -lh ind_ppp_2020.tif

# Re-download if incomplete
rm ind_ppp_2020.tif
python3 download_worldpop_fast.py
```

### Slow WorldPop download
- Use `download_worldpop_fast.py` for parallel download
- Download takes 2-3 hours on typical connection
- Can use `-C -` with curl to resume interrupted downloads

---

## 📧 Contact

For data access issues or questions:
- Repository: https://github.com/nipunbatra/aq-viz
- Issues: https://github.com/nipunbatra/aq-viz/issues

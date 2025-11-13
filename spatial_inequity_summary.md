# Spatial Air Quality Monitoring Inequity Analysis

## Methodology

This analysis calculates the distance from every location in India to the nearest air quality monitoring station.
Population data is used to weight the coverage analysis.

**Note**: This analysis uses synthetic population data for demonstration. For production analysis, use actual LandScan or WorldPop gridded population data.

## National Coverage Summary

- **Grid cells analyzed**: 29,024
- **Synthetic population**: 52,789,029
- **Population within 25km of station**: 18,770,732 (35.6%)
- **Population 25-50km from station**: 13,935,914 (26.4%)
- **Population >50km from station**: 20,082,383 (38.0%)

## Distance Categories

- **<25km**: Adequately served (station relatively accessible)
- **25-50km**: Poorly served (limited accessibility)
- **>50km**: Underserved (minimal monitoring coverage)

## States with Worst Average Coverage

| Rank | State/UT | Avg Distance (km) | Population |
|------|----------|-------------------|------------|
| 1 | ANDAMAN & NICOBAR | 1264.2 | 60,000 |
| 2 | LADAKH | 297.0 | 1,670,000 |
| 3 | ARUNACHAL PRADESH | 163.0 | 754,000 |
| 4 | GUJARAT | 156.4 | 2,879,082 |
| 5 | HIMACHAL PRADESH | 134.6 | 529,347 |
| 6 | JAMMU & KASHMIR | 103.2 | 513,000 |
| 7 | UTTARAKHAND | 99.7 | 623,063 |
| 8 | CHHATTISGARH | 95.6 | 1,179,807 |
| 9 | ODISHA | 93.7 | 1,349,142 |
| 10 | TELANGANA | 93.2 | 2,187,386 |

## Key Findings

- Large remote areas remain without adequate air quality monitoring
- Population centers generally have better coverage, but significant gaps exist
- Several states have average distances >100km to nearest monitoring station
- The spatial distribution of monitoring stations shows significant urban bias

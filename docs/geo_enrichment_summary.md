# Geo Enrichment Summary

## Enrichment Date
2026-10-13

## Input Dataset
- **Source**: data/processed/rentals_final.csv
- **Rows**: 22,852
- **Columns**: 27

## Output Dataset
- **Destination**: data/processed/rentals_enriched.csv
- **Rows**: 22,852
- **Columns**: 43 (16 new columns added)

## New Columns Added

### Distance to Nearest Station
- **nearest_station_distance_km**: Distance to nearest metro/rail station in km (haversine calculation)
- **nearest_station_name**: Name of nearest station
- **nearest_station_line**: Line name (e.g., Line 1, Western Rail, Harbour)

### Distance to Business Hubs
- **dist_to_bkc_km**: Distance to Bandra Kurla Complex
- **dist_to_airoli_km**: Distance to Airoli CBD
- **dist_to_vashi_km**: Distance to Vashi CBD
- **dist_to_belapur_km**: Distance to Belapur CBD
- **dist_to_powai_km**: Distance to Powai (IT hub)
- **dist_to_thane_wagle_estate_km**: Distance to Thane Wagle Estate
- **dist_to_lower_parel_km**: Distance to Lower Parel

### Distance to Airport
- **dist_to_airport_km**: Distance to Navi Mumbai International Airport (approximate)

### Proximity Flags
- **near_station_1km**: Boolean flag - True if within 1km of a station
- **near_station_2km**: Boolean flag - True if within 2km of a station

### Distance Buckets
- **station_distance_bucket**: Categorical bucket for station distance
  - 0-0.5km
  - 0.5-1km
  - 1-2km
  - 2-5km
  - 5km+

### Summary Distance
- **min_dist_to_business_hub_km**: Minimum distance to any of the 7 major business hubs

## Distance Statistics

### Nearest Station Distance
- **Mean**: 2.25 km
- **Median**: 1.53 km
- **Min**: 0.01 km
- **Max**: 12.00 km

### Proximity to Stations
- **Within 1km**: 7,144 listings (31.26%)
- **Within 2km**: 14,067 listings (61.56%)

### Distance Bucket Distribution
| Bucket | Count | Percentage |
|--------|-------|------------|
| 0-0.5km | 2,526 | 11.05% |
| 0.5-1km | 4,618 | 20.21% |
| 1-2km | 6,923 | 30.29% |
| 2-5km | 6,088 | 26.66% |
| 5km+ | 2,697 | 11.79% |

### Regional Statistics (Mean Values)
| Region | Station Distance (km) | Min Business Hub Distance (km) | Mean Rent (INR) |
|--------|----------------------|-------------------------------|-----------------|
| Central | 2.34 | 3.65 | 61,073 |
| Far Western | 5.59 | 28.31 | 13,579 |
| Navi Mumbai | 2.67 | 3.86 | 27,332 |
| South Mumbai | 1.49 | 4.84 | 158,377 |
| Thane | 4.07 | 6.98 | 20,559 |
| Western | 1.48 | 7.87 | 68,036 |

## Methodology Notes

### Distance Calculation
- All distances calculated using the haversine formula (great-circle distance)
- Coordinates are locality-level approximations (jittered around centroid for privacy)
- Distances are therefore approximations, not exact building-level measurements

### Business Hub Coordinates
Coordinates are approximate centroids for each business district:
- BKC: (19.07, 72.87)
- Airoli: (19.149, 73.016)
- Vashi: (19.077, 72.999)
- Belapur: (19.015, 73.037)
- Powai: (19.111, 72.883)
- Thane Wagle Estate: (19.20, 72.98)
- Lower Parel: (19.002, 72.834)

### Airport Coordinates
- Navi Mumbai International Airport: (18.89, 73.15) - approximate location in Panvel area

### Station Data
- 75 metro/rail stations from the original dataset
- Covers Mumbai Metro Lines 1, 2A, 3, 7
- Covers Western Rail, Central Rail, Harbour, Trans-Harbour lines

## Limitations
1. **Locality-level coordinates**: Distances are approximations, not exact
2. **Static coordinates**: Does not account for real-world walking paths or road networks
3. **Straight-line distance**: Haversine calculates great-circle distance, not travel time
4. **Airport coordinates**: NMIA is under construction; coordinates are approximate

## Data Quality
- No missing values in new columns
- All distances are positive and within reasonable ranges
- Proximity flags and buckets correctly computed from distance columns

## Next Steps
- Phase 4: SQL Layer (create schema and analytical queries)

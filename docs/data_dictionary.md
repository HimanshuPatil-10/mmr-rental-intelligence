# Data Dictionary

## Dataset: Mumbai Real Estate Sales and Rentals 2020-2026

### Source Information
- **Source**: Kaggle Dataset by Sergio Nefedov
- **URL**: https://www.kaggle.com/datasets/sergionefedov/mumbai-real-estate-sales-and-rentals-2020-2026
- **License**: Publicly available on Kaggle for educational use
- **Collection Date**: 2026-10-13 (downloaded by user)
- **Dataset Period**: January 2020 to April 2026
- **Files Used**:
  - `rentals.csv` (25,000 rows)
  - `metro_stations.csv` (75 rows)

### rentals.csv Schema

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | string | Unique listing identifier | Format: RXXXXXX |
| date_listed | date | Date the property was listed | Format: YYYY-MM-DD |
| locality | string | Neighborhood/suburb within MMR | 84 unique localities |
| region | string | Geographic region | Values: Western, Navi Mumbai, Far Western, Thane, South Mumbai, Central |
| tier | string | Market tier | Values: luxury, premium, mid, affordable |
| lat | float | Latitude (jittered around locality centroid) | Geocoded |
| lon | float | Longitude (jittered around locality centroid) | Geocoded |
| property_type | string | BHK configuration | Values: 1BHK, 2BHK, 3BHK, 4BHK, 5BHK_penthouse |
| bedrooms | int | Number of bedrooms | 1-5 |
| carpet_area_sqft | int | Usable internal area in sqft | RERA-mandated measurement |
| built_up_area_sqft | int | Total area including walls and balcony in sqft | Usually larger than carpet area |
| carpet_area_m2 | float | Carpet area in square meters | Converted from sqft |
| floor | int | Floor number of the unit | 1-30 |
| total_floors | int | Total floors in the building | 1-30 |
| facing | string | Direction unit faces | Values: north, south, east, west, north-east, north-west, south-east, south-west |
| furnishing | string | Furnishing status | Values: unfurnished, semi_furnished, fully_furnished |
| parking | string | Parking availability | Values: none, 1_covered, 2_covered, open |
| metro_station | string | Nearest metro/rail station | Station name |
| metro_line | string | Metro/rail line name | Values: Line 1, Line 2A, Line 3, Line 7, Western Rail, Central Rail, Harbour, Trans-Harbour |
| metro_distance_min | int | Distance to nearest station in minutes | Walk time estimate |
| to_bkc_km | float | Distance to BKC in km | Business hub proximity |
| deposit_months | int | Deposit amount in months of rent | Mumbai-specific: typically 6-12 months |
| brokerage_months | int | Brokerage fee in months of rent | Usually 0-1 month |
| monthly_rent_inr | int | Monthly rent in Indian Rupees | Target variable |
| annual_rent_inr | int | Annual rent in Indian Rupees | Derived: monthly * 12 |
| monthly_rent_usd | int | Monthly rent in USD | Converted from INR |
| rent_per_sqft_carpet_inr | float | Rent per sqft of carpet area | Derived: monthly_rent / carpet_area_sqft |

### metro_stations.csv Schema

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| station_name | string | Name of metro/rail station | 75 stations |
| line | string | Line name | Values: Line 1, Line 2A, Line 3, Line 7, Western Rail, Central Rail, Harbour, Trans-Harbour |
| lat | float | Latitude | Geocoded |
| lon | float | Longitude | Geocoded |
| year_opened | int | Year station opened | Historical data |
| to_bkc_km | float | Distance to BKC in km | Pre-calculated |
| to_nariman_point_km | float | Distance to Nariman Point in km | Pre-calculated |

### Data Quality Notes
- **No missing values** in the raw dataset (all columns complete)
- **Coordinates are jittered** around locality centroids for privacy
- **Distance fields** (metro_distance_min, to_bkc_km) are pre-calculated estimates
- **Rent range**: ₹3,100 to ₹875,600 per month
- **Area range**: 280 to 4,157 sqft
- **84 localities** across 6 regions
- **Time span**: Jan 2020 to April 2026 (including COVID period, stamp duty cut, rate hikes)

### Provenance Statement
This dataset was sourced from Kaggle for educational purposes. It is a synthetic/comprehensive dataset covering the Mumbai Metropolitan Region rental market. The dataset is publicly available and intended for analysis and learning. All rental listings are anonymized with coordinates jittered for privacy.

# Data Cleaning Log

## Cleaning Date
2026-10-13

## Initial Dataset
- **Source**: rentals.csv
- **Initial rows**: 25000
- **Columns**: 28

## Cleaning Steps

### 1. Duplicate Removal
- **Method**: Grouped by locality, BHK, area (rounded to 10 sqft), and rent (rounded to ₹1,000)
- **Rationale**: Listings with identical location, size, and price are likely duplicates or repeated listings
- **Rows removed**: 1752 (7.01%)

### 2. Range Validation
- **Method**: Filtered rents between INR 3,000 and INR 10,00,000; areas between 200 sqft and 5,000 sqft
- **Rationale**: Remove obvious data errors and fake listings
- **Rows removed**: 0 (0.00%)
  - Invalid rent: 0
  - Invalid area: 0

### 3. Outlier Removal (IQR)
- **Method**: Interquartile Range (IQR) method with 1.5×IQR bounds, grouped by locality and BHK
- **Rationale**: Different localities and BHK types have different price distributions; grouping preserves legitimate regional variation
- **Rows removed**: 136 (0.54%)

### 4. Coordinate Validation
- **Method**: Filtered coordinates within MMR bounding box (lat: 18.8-19.5, lon: 72.7-73.2)
- **Rationale**: Ensure all listings are within the Mumbai Metropolitan Region
- **Rows removed**: 260 (1.04%)

## Final Dataset
- **Final rows**: 22852
- **Retention rate**: 91.41%
- **Total removed**: 2148 (8.59%)

## Column Additions
- **bhk**: Extracted from property_type (integer: 1-5)

## Data Quality Checks
- No missing values in original dataset
- All coordinates validated within MMR
- Rent and area ranges sanity-checked
- Duplicates removed

## Next Steps
- Phase 3: Geo Enrichment (distance calculations)

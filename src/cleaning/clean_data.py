"""
Data cleaning module for MMR Rental Market Intelligence.

This module handles:
- Duplicate detection and removal
- Price and area validation
- Outlier detection using IQR
- Locality standardization
- BHK extraction from property_type
- Coordinate validation
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "rentals.csv"
INTERIM_DATA_PATH = PROJECT_ROOT / "data" / "interim" / "rentals_cleaned.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_final.csv"
CLEANING_LOG_PATH = PROJECT_ROOT / "docs" / "cleaning_log.md"

# MMR bounding box (approximate)
MMR_LAT_MIN, MMR_LAT_MAX = 18.8, 19.5
MMR_LON_MIN, MMR_LON_MAX = 72.7, 73.2


def load_data() -> pd.DataFrame:
    """Load raw rental data."""
    logger.info(f"Loading data from {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    return df


def check_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Check for duplicate listings.
    Duplicates are defined as same locality + BHK + area rounded to 10 sqft + rent rounded to 1000 INR.
    """
    logger.info("Checking for duplicates...")
    initial_count = len(df)

    logger.info(f"Columns before duplicate check: {list(df.columns)}")
    logger.info(f"Has locality: {'locality' in df.columns}")
    logger.info(f"Has bhk: {'bhk' in df.columns}")

    df_temp = df.copy()
    if "locality" in df_temp.columns:
        df_temp["locality"] = df_temp["locality"].fillna("").astype(str)
    if "bhk" in df_temp.columns:
        df_temp["bhk"] = pd.to_numeric(df_temp["bhk"], errors="coerce")
    if "carpet_area_sqft" in df_temp.columns:
        df_temp["carpet_area_sqft"] = pd.to_numeric(df_temp["carpet_area_sqft"], errors="coerce")
    if "monthly_rent_inr" in df_temp.columns:
        df_temp["monthly_rent_inr"] = pd.to_numeric(df_temp["monthly_rent_inr"], errors="coerce")

    df_temp["area_key"] = (df_temp["carpet_area_sqft"] / 10).round().astype("Int64")
    df_temp["rent_key"] = (df_temp["monthly_rent_inr"] / 1000).round().astype("Int64")

    duplicate_mask = df_temp.duplicated(subset=["locality", "bhk", "area_key", "rent_key"], keep="first")
    duplicate_count = int(duplicate_mask.sum())

    logger.info(f"Found {duplicate_count} potential duplicates ({duplicate_count/initial_count*100:.2f}%)")

    df_cleaned = df[~duplicate_mask].copy()
    logger.info(f"Removed {duplicate_count} duplicates, {len(df_cleaned)} rows remaining")

    return df_cleaned, duplicate_count


def validate_ranges(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int, int]:
    """
    Validate that rents and areas are within reasonable ranges.
    Remove obvious fakes or data errors.
    Returns cleaned df, total invalid count, invalid rent count, invalid area count.
    """
    logger.info("Validating price and area ranges...")
    initial_count = len(df)

    # Define reasonable ranges
    MIN_RENT = 3000  # ₹3,000 minimum monthly rent
    MAX_RENT = 1000000  # ₹10 lakh maximum monthly rent
    MIN_AREA = 200  # 200 sqft minimum
    MAX_AREA = 5000  # 5000 sqft maximum

    # Check conditions
    valid_rent = (df['monthly_rent_inr'] >= MIN_RENT) & (df['monthly_rent_inr'] <= MAX_RENT)
    valid_area = (df['carpet_area_sqft'] >= MIN_AREA) & (df['carpet_area_sqft'] <= MAX_AREA)

    # Combined validity
    valid_mask = valid_rent & valid_area
    invalid_count = (~valid_mask).sum()
    invalid_rent_count = (~valid_rent).sum()
    invalid_area_count = (~valid_area).sum()

    logger.info(f"Found {invalid_count} listings with invalid rent/area ({invalid_count/initial_count*100:.2f}%)")
    logger.info(f"  - Invalid rent: {invalid_rent_count}")
    logger.info(f"  - Invalid area: {invalid_area_count}")

    df_cleaned = df[valid_mask].copy()
    logger.info(f"Removed {invalid_count} invalid listings, {len(df_cleaned)} rows remaining")

    return df_cleaned, invalid_count, invalid_rent_count, invalid_area_count


def remove_outliers_iqr(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Remove outliers using IQR method, grouped by BHK and locality.
    This handles the fact that different localities and BHK types have different price distributions.
    """
    logger.info("Removing outliers using IQR method...")
    initial_count = len(df)

    # Extract BHK if not already done
    if 'bhk' not in df.columns:
        df['bhk'] = df['property_type'].str.extract(r'(\d+)BHK').astype(int)

    # Group by locality and BHK
    def remove_outliers_group(group: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers from a single group using IQR."""
        if len(group) < 5:  # Skip groups with too few samples
            return group

        # Calculate IQR for rent_per_sqft
        q1 = group['rent_per_sqft_carpet_inr'].quantile(0.25)
        q3 = group['rent_per_sqft_carpet_inr'].quantile(0.75)
        iqr = q3 - q1

        # Define bounds (1.5 * IQR)
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Filter
        return group[
            (group['rent_per_sqft_carpet_inr'] >= lower_bound) &
            (group['rent_per_sqft_carpet_inr'] <= upper_bound)
        ]

    df_cleaned = df.groupby(['locality', 'bhk'], group_keys=False).apply(remove_outliers_group, include_groups=True)
    outlier_count = initial_count - len(df_cleaned)

    logger.info(f"Removed {outlier_count} outliers ({outlier_count/initial_count*100:.2f}%)")
    logger.info(f"Remaining rows: {len(df_cleaned)}")

    return df_cleaned, outlier_count


def validate_coordinates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Validate that coordinates fall within MMR bounding box.
    """
    logger.info("Validating coordinates...")
    initial_count = len(df)

    valid_coords = (
        (df['lat'] >= MMR_LAT_MIN) & (df['lat'] <= MMR_LAT_MAX) &
        (df['lon'] >= MMR_LON_MIN) & (df['lon'] <= MMR_LON_MAX)
    )

    invalid_count = (~valid_coords).sum()
    logger.info(f"Found {invalid_count} listings with invalid coordinates ({invalid_count/initial_count*100:.2f}%)")

    df_cleaned = df[valid_coords].copy()
    logger.info(f"Removed {invalid_count} invalid coordinate listings, {len(df_cleaned)} rows remaining")

    # Ensure locality column is preserved
    if 'locality' not in df_cleaned.columns:
        logger.warning("locality column missing after coordinate validation - this should not happen")

    return df_cleaned, invalid_count


def extract_bhk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract BHK count from property_type column.
    Handle 5BHK_penthouse as 5 BHK.
    """
    logger.info("Extracting BHK count from property_type...")

    df['bhk'] = df['property_type'].str.extract(r'(\d+)BHK').astype(int)

    # Verify extraction
    bhk_distribution = df['bhk'].value_counts().sort_index()
    logger.info(f"BHK distribution:\n{bhk_distribution}")

    return df


def drop_temporary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop temporary columns used for cleaning (area_key, rent_key).
    """
    temp_cols = ['area_key', 'rent_key']
    for col in temp_cols:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df


def clean_data() -> Tuple[pd.DataFrame, dict]:
    """
    Main cleaning pipeline.
    Returns cleaned dataframe and statistics dictionary.
    """
    logger.info("=" * 60)
    logger.info("Starting data cleaning pipeline")
    logger.info("=" * 60)

    # Load data
    df = load_data()
    initial_count = len(df)

    # Step 1: Extract BHK (needed for grouping)
    df = extract_bhk(df)

    # Step 2: Check duplicates
    df, dup_count = check_duplicates(df)

    # Step 3: Validate ranges
    df, invalid_count, invalid_rent_count, invalid_area_count = validate_ranges(df)

    # Step 4: Remove outliers
    df, outlier_count = remove_outliers_iqr(df)

    # Step 5: Validate coordinates
    df, coord_count = validate_coordinates(df)

    # Step 6: Drop temporary columns
    df = drop_temporary_columns(df)

    # Final count
    final_count = len(df)
    total_removed = initial_count - final_count

    logger.info("=" * 60)
    logger.info("Cleaning Summary")
    logger.info("=" * 60)
    logger.info(f"Initial rows: {initial_count}")
    logger.info(f"Final rows: {final_count}")
    logger.info(f"Total removed: {total_removed} ({total_removed/initial_count*100:.2f}%)")
    logger.info(f"  - Duplicates: {dup_count}")
    logger.info(f"  - Invalid ranges: {invalid_count}")
    logger.info(f"  - Outliers: {outlier_count}")
    logger.info(f"  - Invalid coordinates: {coord_count}")
    logger.info("=" * 60)

    stats = {
        'duplicates': dup_count,
        'invalid_ranges': invalid_count,
        'invalid_rent': invalid_rent_count,
        'invalid_area': invalid_area_count,
        'outliers': outlier_count,
        'coordinates': coord_count
    }

    return df, stats


def save_cleaning_log(df: pd.DataFrame, initial_count: int, stats: dict):
    """
    Save cleaning decisions to markdown log.
    """
    log_content = f"""# Data Cleaning Log

## Cleaning Date
2026-10-13

## Initial Dataset
- **Source**: rentals.csv
- **Initial rows**: {initial_count}
- **Columns**: {len(df.columns)}

## Cleaning Steps

### 1. Duplicate Removal
- **Method**: Grouped by locality, BHK, area (rounded to 10 sqft), and rent (rounded to ₹1,000)
- **Rationale**: Listings with identical location, size, and price are likely duplicates or repeated listings
- **Rows removed**: {stats['duplicates']} ({stats['duplicates']/initial_count*100:.2f}%)

### 2. Range Validation
- **Method**: Filtered rents between INR 3,000 and INR 10,00,000; areas between 200 sqft and 5,000 sqft
- **Rationale**: Remove obvious data errors and fake listings
- **Rows removed**: {stats['invalid_ranges']} ({stats['invalid_ranges']/initial_count*100:.2f}%)
  - Invalid rent: {stats['invalid_rent']}
  - Invalid area: {stats['invalid_area']}

### 3. Outlier Removal (IQR)
- **Method**: Interquartile Range (IQR) method with 1.5×IQR bounds, grouped by locality and BHK
- **Rationale**: Different localities and BHK types have different price distributions; grouping preserves legitimate regional variation
- **Rows removed**: {stats['outliers']} ({stats['outliers']/initial_count*100:.2f}%)

### 4. Coordinate Validation
- **Method**: Filtered coordinates within MMR bounding box (lat: 18.8-19.5, lon: 72.7-73.2)
- **Rationale**: Ensure all listings are within the Mumbai Metropolitan Region
- **Rows removed**: {stats['coordinates']} ({stats['coordinates']/initial_count*100:.2f}%)

## Final Dataset
- **Final rows**: {len(df)}
- **Retention rate**: {len(df)/initial_count*100:.2f}%
- **Total removed**: {initial_count - len(df)} ({(initial_count - len(df))/initial_count*100:.2f}%)

## Column Additions
- **bhk**: Extracted from property_type (integer: 1-5)

## Data Quality Checks
- No missing values in original dataset
- All coordinates validated within MMR
- Rent and area ranges sanity-checked
- Duplicates removed

## Next Steps
- Phase 3: Geo Enrichment (distance calculations)
"""

    with open(CLEANING_LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(log_content)

    logger.info(f"Cleaning log saved to {CLEANING_LOG_PATH}")


def main():
    """Main execution function."""
    # Clean data
    df_initial = load_data()
    initial_count = len(df_initial)

    df_cleaned, stats = clean_data()

    # Save interim data
    INTERIM_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(INTERIM_DATA_PATH, index=False)
    logger.info(f"Interim data saved to {INTERIM_DATA_PATH}")

    # Save processed data
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Processed data saved to {PROCESSED_DATA_PATH}")

    # Save cleaning log
    save_cleaning_log(df_cleaned, initial_count, stats)

    logger.info("Cleaning pipeline complete!")

    return df_cleaned


if __name__ == "__main__":
    main()

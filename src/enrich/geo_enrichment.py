"""
Geo enrichment module for MMR Rental Market Intelligence.

This module handles:
- Loading metro/rail station coordinates
- Computing distances to nearest stations using haversine
- Computing distances to major business hubs
- Computing distance to Navi Mumbai International Airport
- Adding distance buckets and proximity flags
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import logging
from haversine import haversine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_final.csv"
ENRICHED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"
METRO_STATIONS_PATH = PROJECT_ROOT / "data" / "raw" / "metro_stations.csv"

# Major business hub coordinates (approximate)
BUSINESS_HUBS = {
    'BKC': (19.07, 72.87),  # Bandra Kurla Complex
    'Airoli': (19.149, 73.016),  # Airoli CBD
    'Vashi': (19.077, 72.999),  # Vashi CBD
    'Belapur': (19.015, 73.037),  # Belapur CBD
    'Powai': (19.111, 72.883),  # Powai (IT hub)
    'Thane_Wagle_Estate': (19.20, 72.98),  # Thane Wagle Estate
    'Lower_Parel': (19.002, 72.834),  # Lower Parel
}

# Navi Mumbai International Airport (approximate coordinates)
NMIA_COORDS = (18.89, 73.15)  # Panvel area


def load_data() -> pd.DataFrame:
    """Load cleaned rental data."""
    logger.info(f"Loading cleaned data from {PROCESSED_DATA_PATH}")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    logger.info(f"Loaded {len(df)} rows")
    return df


def load_stations() -> pd.DataFrame:
    """Load metro/rail station data."""
    logger.info(f"Loading station data from {METRO_STATIONS_PATH}")
    stations = pd.read_csv(METRO_STATIONS_PATH)
    logger.info(f"Loaded {len(stations)} stations")
    return stations


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate haversine distance between two points in kilometers.
    """
    return haversine((lat1, lon1), (lat2, lon2))


def compute_distance_to_nearest_station(row: pd.Series, stations: pd.DataFrame) -> Tuple[float, str, str]:
    """
    Compute distance to nearest metro/rail station.
    Returns distance in km, station name, and line.
    """
    listing_coords = (row['lat'], row['lon'])

    # Calculate distance to all stations
    stations['distance_km'] = stations.apply(
        lambda s: haversine_distance(listing_coords[0], listing_coords[1], s['lat'], s['lon']),
        axis=1
    )

    # Find nearest station
    nearest_idx = stations['distance_km'].idxmin()
    nearest_distance = stations.loc[nearest_idx, 'distance_km']
    nearest_station = stations.loc[nearest_idx, 'station_name']
    nearest_line = stations.loc[nearest_idx, 'line']

    return nearest_distance, nearest_station, nearest_line


def compute_distance_to_business_hubs(row: pd.Series) -> dict:
    """
    Compute distance to each major business hub.
    Returns dictionary of distances in km.
    """
    listing_coords = (row['lat'], row['lon'])
    distances = {}

    for hub_name, hub_coords in BUSINESS_HUBS.items():
        distances[f'dist_to_{hub_name.lower()}_km'] = haversine_distance(
            listing_coords[0], listing_coords[1], hub_coords[0], hub_coords[1]
        )

    return distances


def compute_distance_to_airport(row: pd.Series) -> float:
    """
    Compute distance to Navi Mumbai International Airport.
    """
    listing_coords = (row['lat'], row['lon'])
    return haversine_distance(
        listing_coords[0], listing_coords[1], NMIA_COORDS[0], NMIA_COORDS[1]
    )


def add_distance_features(df: pd.DataFrame, stations: pd.DataFrame) -> pd.DataFrame:
    """
    Add all distance-based features to the dataframe.
    """
    logger.info("Computing distance features...")

    # Compute distance to nearest station
    logger.info("  - Computing distance to nearest station...")
    station_results = df.apply(
        lambda row: compute_distance_to_nearest_station(row, stations),
        axis=1,
        result_type='expand'
    )
    df['nearest_station_distance_km'] = station_results[0]
    df['nearest_station_name'] = station_results[1]
    df['nearest_station_line'] = station_results[2]

    # Compute distance to business hubs
    logger.info("  - Computing distance to business hubs...")
    hub_distances = df.apply(compute_distance_to_business_hubs, axis=1, result_type='expand')
    for col in hub_distances.columns:
        df[col] = hub_distances[col]

    # Compute distance to airport
    logger.info("  - Computing distance to airport...")
    df['dist_to_airport_km'] = df.apply(compute_distance_to_airport, axis=1)

    # Add proximity flags
    logger.info("  - Adding proximity flags...")
    df['near_station_1km'] = df['nearest_station_distance_km'] <= 1.0
    df['near_station_2km'] = df['nearest_station_distance_km'] <= 2.0

    # Add distance buckets for station
    logger.info("  - Adding distance buckets...")
    df['station_distance_bucket'] = pd.cut(
        df['nearest_station_distance_km'],
        bins=[0, 0.5, 1, 2, 5, float('inf')],
        labels=['0-0.5km', '0.5-1km', '1-2km', '2-5km', '5km+']
    )

    # Find minimum distance to any business hub
    hub_cols = [f'dist_to_{hub.lower()}_km' for hub in BUSINESS_HUBS.keys()]
    df['min_dist_to_business_hub_km'] = df[hub_cols].min(axis=1)

    logger.info("Distance features added successfully")
    return df


def validate_enrichment(df: pd.DataFrame) -> None:
    """
    Validate the enriched data.
    """
    logger.info("Validating enriched data...")

    # Check for missing values in new columns
    new_cols = [
        'nearest_station_distance_km', 'nearest_station_name', 'nearest_station_line',
        'dist_to_bkc_km', 'dist_to_airoli_km', 'dist_to_vashi_km', 'dist_to_belapur_km',
        'dist_to_powai_km', 'dist_to_thane_wagle_estate_km', 'dist_to_lower_parel_km',
        'dist_to_airport_km', 'near_station_1km', 'near_station_2km',
        'station_distance_bucket', 'min_dist_to_business_hub_km'
    ]

    for col in new_cols:
        if df[col].isnull().any():
            logger.warning(f"Column {col} has missing values")

    # Log statistics
    logger.info(f"Nearest station distance stats:")
    logger.info(f"  - Mean: {df['nearest_station_distance_km'].mean():.2f} km")
    logger.info(f"  - Median: {df['nearest_station_distance_km'].median():.2f} km")
    logger.info(f"  - Min: {df['nearest_station_distance_km'].min():.2f} km")
    logger.info(f"  - Max: {df['nearest_station_distance_km'].max():.2f} km")

    logger.info(f"Listings within 1km of station: {df['near_station_1km'].sum()} ({df['near_station_1km'].sum()/len(df)*100:.2f}%)")
    logger.info(f"Listings within 2km of station: {df['near_station_2km'].sum()} ({df['near_station_2km'].sum()/len(df)*100:.2f}%)")

    logger.info(f"Distance bucket distribution:")
    logger.info(f"\n{df['station_distance_bucket'].value_counts().sort_index()}")


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Starting Geo Enrichment")
    logger.info("=" * 60)

    # Load data
    df = load_data()
    stations = load_stations()

    # Add distance features
    df_enriched = add_distance_features(df, stations)

    # Validate
    validate_enrichment(df_enriched)

    # Save enriched data
    logger.info(f"Saving enriched data to {ENRICHED_DATA_PATH}")
    df_enriched.to_csv(ENRICHED_DATA_PATH, index=False)

    logger.info("=" * 60)
    logger.info("Geo Enrichment Complete")
    logger.info("=" * 60)
    logger.info(f"Final shape: {df_enriched.shape}")
    logger.info(f"New columns added: {len(df_enriched.columns) - len(df.columns)}")

    return df_enriched


if __name__ == "__main__":
    main()

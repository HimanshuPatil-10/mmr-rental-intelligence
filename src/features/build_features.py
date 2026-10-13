from __future__ import annotations

import pandas as pd


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame["locality"] = frame["locality"].fillna("unknown")
    frame["region"] = frame["region"].fillna("unknown")
    frame["furnishing"] = frame["furnishing"].fillna("unfurnished")
    frame["parking"] = frame["parking"].fillna("none")
    frame["property_type"] = frame["property_type"].fillna("1BHK")
    frame["tier"] = frame["tier"].fillna("mid")
    frame["near_station_1km"] = frame["near_station_1km"].fillna(False).astype(bool)
    frame["min_dist_to_business_hub_km"] = frame["min_dist_to_business_hub_km"].fillna(5.0)
    frame["metro_distance_min"] = frame["metro_distance_min"].fillna(20)
    frame["dist_to_airport_km"] = frame["dist_to_airport_km"].fillna(20.0)
    frame["dist_to_bkc_km"] = frame["dist_to_bkc_km"].fillna(12.0)
    return frame

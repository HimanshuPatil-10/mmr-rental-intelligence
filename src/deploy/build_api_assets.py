from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"
OUTPUT_PATH = PROJECT_ROOT / "api" / "locality_stats.json"
CHART_DATA_PATH = PROJECT_ROOT / "api" / "chart_data.json"

CHART_COLUMNS = [
    "region",
    "locality",
    "bhk",
    "furnishing",
    "near_station_1km",
    "monthly_rent_inr",
    "rent_per_sqft_carpet_inr",
    "carpet_area_sqft",
]


def build_api_assets() -> Path:
    df = pd.read_csv(DATA_PATH)
    region_by_locality = (
        df.groupby(["locality", "region"])
        .size()
        .reset_index(name="count")
        .sort_values(["locality", "count", "region"], ascending=[True, False, True])
        .drop_duplicates("locality")
        .set_index("locality")["region"]
        .to_dict()
    )
    medians = (
        df.groupby(["locality", "bhk"], as_index=False)["monthly_rent_inr"]
        .median()
        .rename(columns={"monthly_rent_inr": "median_rent_inr"})
        .sort_values(["locality", "bhk"])
    )
    payload = {
        "localities": sorted(region_by_locality),
        "region_by_locality": region_by_locality,
        "median_rent_by_locality_bhk": [
            {
                "locality": row.locality,
                "bhk": int(row.bhk),
                "median_rent_inr": float(row.median_rent_inr),
            }
            for row in medians.itertuples(index=False)
        ],
    }
    OUTPUT_PATH.write_text(
        json.dumps(payload, separators=(",", ":")),
        encoding="utf-8",
    )
    chart_rows = df[CHART_COLUMNS].rename(
        columns={
            "monthly_rent_inr": "rent_inr",
            "rent_per_sqft_carpet_inr": "rent_per_sqft_inr",
            "carpet_area_sqft": "area_sqft",
        }
    )
    chart_payload = {
        "record_count": len(chart_rows),
        "regions": sorted(chart_rows["region"].dropna().unique().tolist()),
        "bhk_options": sorted(int(value) for value in chart_rows["bhk"].dropna().unique()),
        "furnishing_options": sorted(
            chart_rows["furnishing"].dropna().unique().tolist()
        ),
        "records": chart_rows.to_dict(orient="records"),
    }
    CHART_DATA_PATH.write_text(
        json.dumps(chart_payload, separators=(",", ":")),
        encoding="utf-8",
    )
    return OUTPUT_PATH


if __name__ == "__main__":
    output = build_api_assets()
    print(f"API locality data written to {output}")
    print(f"Chart data written to {CHART_DATA_PATH}")

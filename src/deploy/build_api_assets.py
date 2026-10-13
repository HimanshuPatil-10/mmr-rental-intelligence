from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"
OUTPUT_PATH = PROJECT_ROOT / "api" / "locality_stats.json"


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
    return OUTPUT_PATH


if __name__ == "__main__":
    output = build_api_assets()
    print(f"API locality data written to {output}")

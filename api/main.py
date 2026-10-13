from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.schemas import RentPredictionRequest, RentPredictionResponse
from src.models.train_model import FEATURE_COLUMNS, load_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCALITY_STATS_PATH = PROJECT_ROOT / "api" / "locality_stats.json"
CHART_DATA_PATH = PROJECT_ROOT / "api" / "chart_data.json"

app = FastAPI(
    title="MMR Rental Market Intelligence API",
    description="Fair-rent estimator and locality insights for the Mumbai Metropolitan Region",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@lru_cache(maxsize=1)
def get_locality_stats() -> dict:
    with LOCALITY_STATS_PATH.open(encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def get_localities() -> list[str]:
    return get_locality_stats()["localities"]


@lru_cache(maxsize=1)
def get_locality_lookup() -> dict[str, str]:
    return get_locality_stats()["region_by_locality"]


@lru_cache(maxsize=1)
def get_model():
    return load_model()


def _build_prediction_row(request: RentPredictionRequest) -> pd.DataFrame:
    locality_lookup = get_locality_lookup()
    locality = request.locality.strip()
    if locality not in locality_lookup:
        raise HTTPException(status_code=400, detail=f"Unknown locality '{locality}'.")

    region = request.region or locality_lookup[locality]
    distance_to_station = request.distance_to_station_km if request.distance_to_station_km is not None else 1.5
    row = {
        "locality": locality,
        "region": region,
        "bhk": int(request.bhk),
        "carpet_area_sqft": float(request.area_sqft),
        "furnishing": request.furnishing.lower(),
        "bedrooms": int(request.bhk),
        "floor": 5,
        "total_floors": 12,
        "parking": "1_covered",
        "property_type": f"{int(request.bhk)}BHK",
        "tier": "mid",
        "near_station_1km": bool(distance_to_station <= 1.0),
        "min_dist_to_business_hub_km": max(distance_to_station * 2.0, 1.5),
        "metro_distance_min": int(max(distance_to_station * 10, 5)),
        "dist_to_airport_km": 18.0 if region == "Navi Mumbai" else 24.0,
        "dist_to_bkc_km": 12.0,
    }
    missing = [col for col in FEATURE_COLUMNS if col not in row]
    if missing:
        raise HTTPException(status_code=500, detail=f"Missing required features: {missing}")
    return pd.DataFrame([row])[FEATURE_COLUMNS]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/localities")
def list_localities() -> dict[str, list[str]]:
    return {"localities": get_localities()}


@lru_cache(maxsize=1)
def get_chart_data() -> dict:
    with CHART_DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


@app.get("/analytics")
def analytics() -> dict:
    return get_chart_data()


@lru_cache(maxsize=1)
def get_locality_distribution() -> dict[tuple[str, int], float]:
    return {
        (entry["locality"], int(entry["bhk"])): float(entry["median_rent_inr"])
        for entry in get_locality_stats()["median_rent_by_locality_bhk"]
    }


@app.post("/predict", response_model=RentPredictionResponse)
def predict(request: RentPredictionRequest) -> RentPredictionResponse:
    model = get_model()
    frame = _build_prediction_row(request)
    prediction = float(model.predict(frame)[0])
    if prediction < 0:
        prediction = abs(prediction)
    if prediction <= 0:
        prediction = 5000.0

    locality_baseline = get_locality_distribution().get((request.locality.strip(), int(request.bhk)))
    if locality_baseline is not None and locality_baseline > 0:
        ratio = prediction / locality_baseline
        label = "overpriced" if ratio > 1.15 else "undervalued" if ratio < 0.85 else "fair"
    else:
        label = "fair"

    band = max(prediction * 0.15, 3000.0)
    response = RentPredictionResponse(
        predicted_rent_inr=round(prediction, 2),
        range_inr={"lower": round(prediction - band, 2), "upper": round(prediction + band, 2)},
        fairness_label=label,
        locality=request.locality,
        bhk=int(request.bhk),
        area_sqft=float(request.area_sqft),
    )
    return response


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MMR Rental Market Intelligence API"}

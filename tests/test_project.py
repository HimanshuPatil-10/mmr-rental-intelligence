import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from src.cleaning.clean_data import check_duplicates, extract_bhk, validate_ranges
from src.models.train_model import MODEL_PATH, load_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "model_metadata.json"


def test_extract_bhk_and_range_validation():
    df = pd.DataFrame(
        {
            "property_type": ["1BHK", "2BHK", "3BHK"],
            "monthly_rent_inr": [2500, 55000, 60000],
            "carpet_area_sqft": [150, 890, 1100],
        }
    )

    df = extract_bhk(df)
    assert df["bhk"].tolist() == [1, 2, 3]

    cleaned, invalid_count, invalid_rent_count, invalid_area_count = validate_ranges(df)
    assert invalid_count == 1
    assert invalid_rent_count == 1
    assert invalid_area_count == 1
    assert cleaned["monthly_rent_inr"].tolist() == [55000, 60000]


def test_duplicate_removal_is_detected():
    df = pd.DataFrame(
        {
            "locality": ["Andheri West", "Andheri West"],
            "bhk": [2, 2],
            "carpet_area_sqft": [850, 850],
            "monthly_rent_inr": [50000, 50000],
        }
    )

    cleaned, dup_count = check_duplicates(df)
    assert dup_count == 1
    assert len(cleaned) == 1


def test_model_metadata_matches_real_artifact():
    assert MODEL_PATH.exists()
    assert MODEL_METADATA_PATH.exists()
    assert MODEL_PATH.stat().st_size < 2_000_000
    assert (PROJECT_ROOT / "api" / "locality_stats.json").stat().st_size < 100_000

    metadata = json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8"))
    test_metrics = metadata["test_metrics"]

    assert metadata["model_name"] == "HistGradientBoostingRegressor"
    assert test_metrics["r2"] > 0.9
    assert test_metrics["mae_inr"] > 0
    assert test_metrics["rmse_inr"] > 0

    model = load_model()
    assert model is not None


def test_api_health_and_prediction_work():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    response = client.post(
        "/predict",
        json={
            "locality": "Andheri West",
            "bhk": 2,
            "area_sqft": 850,
            "furnishing": "semi_furnished",
            "distance_to_station_km": 1.2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["locality"] == "Andheri West"
    assert payload["bhk"] == 2
    assert payload["area_sqft"] == 850.0
    assert payload["predicted_rent_inr"] > 0
    assert payload["fairness_label"] in {"fair", "overpriced", "undervalued"}

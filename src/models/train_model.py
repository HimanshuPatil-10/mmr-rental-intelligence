from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"
MODEL_PATH = PROJECT_ROOT / "data" / "processed" / "mmr_rent_model.joblib"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "model_metadata.json"

FEATURE_COLUMNS = [
    "locality",
    "region",
    "bhk",
    "carpet_area_sqft",
    "furnishing",
    "bedrooms",
    "floor",
    "total_floors",
    "parking",
    "property_type",
    "tier",
    "near_station_1km",
    "min_dist_to_business_hub_km",
    "metro_distance_min",
    "dist_to_airport_km",
    "dist_to_bkc_km",
]

NUMERIC_FEATURES = [
    "bhk",
    "carpet_area_sqft",
    "bedrooms",
    "floor",
    "total_floors",
    "near_station_1km",
    "min_dist_to_business_hub_km",
    "metro_distance_min",
    "dist_to_airport_km",
    "dist_to_bkc_km",
]

CATEGORICAL_FEATURES = [
    "locality",
    "region",
    "furnishing",
    "parking",
    "property_type",
    "tier",
]


def build_model_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                NUMERIC_FEATURES,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                sparse_output=False,
                            ),
                        ),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.08,
        max_leaf_nodes=31,
        l2_regularization=1.0,
        random_state=42,
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def load_training_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[df["monthly_rent_inr"].notna()].copy()
    df = df[df["monthly_rent_inr"] > 0].copy()
    for col in ["locality", "region", "furnishing", "parking", "property_type", "tier"]:
        df[col] = df[col].fillna("unknown")
    df["near_station_1km"] = df["near_station_1km"].fillna(False).astype(bool)
    return df


def compute_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    denom = y_true.replace(0, np.nan)
    mape = ((y_true - y_pred).abs() / denom).mean()
    return {
        "mae_inr": float(mae),
        "rmse_inr": float(rmse),
        "r2": float(r2),
        "mape": float(mape),
    }


def train_model() -> tuple[Pipeline, dict]:
    df = load_training_data()
    X = df[FEATURE_COLUMNS]
    y = df["monthly_rent_inr"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    test_metrics = compute_metrics(y_test, y_pred)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring={
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
        },
    )
    metadata = {
        "model_name": "HistGradientBoostingRegressor",
        "version": "1.0.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "target": "monthly_rent_inr",
        "feature_columns": FEATURE_COLUMNS,
        "test_metrics": test_metrics,
        "cv_mae_inr": float(-cv_scores["test_mae"].mean()),
        "cv_rmse_inr": float(-cv_scores["test_rmse"].mean()),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH, compress=3)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return pipeline, metadata


def ensure_model_artifacts() -> Path:
    if not MODEL_PATH.exists():
        if not DATA_PATH.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {MODEL_PATH} and training data not found at {DATA_PATH}."
            )
        train_model()
    return MODEL_PATH


def load_model() -> Pipeline:
    ensure_model_artifacts()
    return joblib.load(MODEL_PATH)


if __name__ == "__main__":
    pipeline, metadata = train_model()
    print(f"Model trained successfully. MAE: INR {metadata['test_metrics']['mae_inr']:,.0f}")
    print(f"Model saved to {MODEL_PATH}")

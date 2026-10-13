from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"
MODEL_PATH = PROJECT_ROOT / "data" / "processed" / "mmr_rent_model.joblib"


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        from src.models.train_model import train_model

        train_model()
    return joblib.load(MODEL_PATH)


st.set_page_config(page_title="MMR Rental Intelligence", layout="wide")


@st.cache_data
def compute_locality_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("locality", as_index=False)
        .agg(
            median_rent=("monthly_rent_inr", "median"),
            median_rent_per_sqft=("rent_per_sqft_carpet_inr", "median"),
            listing_count=("id", "count"),
        )
        .sort_values("median_rent_per_sqft", ascending=False)
    )


# Load data
rentals = load_data()
locality_summary = compute_locality_summary(rentals)
model = load_model()

st.title("MMR Rental Market Intelligence")

with st.sidebar:
    st.header("Filters")
    locality = st.selectbox("Locality", ["All"] + sorted(rentals["locality"].unique().tolist()))
    bhk = st.selectbox("BHK", ["All", 1, 2, 3, 4, 5])
    furnishing = st.selectbox("Furnishing", ["All", "unfurnished", "semi_furnished", "fully_furnished"])
    station_distance_max = st.slider("Distance to station (km)", 0.0, 10.0, 5.0, step=0.5)

filtered = rentals.copy()
if locality != "All":
    filtered = filtered[filtered["locality"] == locality]
if bhk != "All":
    filtered = filtered[filtered["bhk"] == bhk]
if furnishing != "All":
    filtered = filtered[filtered["furnishing"] == furnishing]
filtered = filtered[filtered["nearest_station_distance_km"] <= station_distance_max]

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric("Listings", f"{len(filtered):,}")
with kpi_col2:
    st.metric("Median rent", f"₹{filtered['monthly_rent_inr'].median():,.0f}")
with kpi_col3:
    st.metric("Median ₹/sqft", f"₹{filtered['rent_per_sqft_carpet_inr'].median():,.0f}")
with kpi_col4:
    overpriced = (filtered["monthly_rent_inr"] > filtered["rent_per_sqft_carpet_inr"].median() * filtered["carpet_area_sqft"]).mean() * 100
    st.metric("Overpriced share", f"{overpriced:.1f}%")

col1, col2 = st.columns(2)
with col1:
    chart_df = locality_summary.head(15)
    fig = px.bar(
        chart_df,
        x="locality",
        y="median_rent_per_sqft",
        title="Median rent per sqft by locality",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    scatter = filtered[["nearest_station_distance_km", "monthly_rent_inr"]].copy()
    fig2 = px.scatter(
        scatter,
        x="nearest_station_distance_km",
        y="monthly_rent_inr",
        title="Rent vs station proximity",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Best-value listings")
value_df = filtered[["locality", "bhk", "carpet_area_sqft", "rent_per_sqft_carpet_inr", "monthly_rent_inr", "nearest_station_distance_km"]].sort_values("rent_per_sqft_carpet_inr").head(15)
st.dataframe(value_df, use_container_width=True)

st.subheader("Fair rent estimator")
with st.form("rent_estimator"):
    locality_in = st.selectbox("Locality", sorted(rentals["locality"].unique().tolist()))
    bhk_in = st.slider("BHK", 1, 5, 2)
    area_in = st.number_input("Area sqft", min_value=200, max_value=4000, value=850, step=50)
    furnishing_in = st.selectbox("Furnishing", ["unfurnished", "semi_furnished", "fully_furnished"])
    dist_in = st.number_input("Distance to station (km)", min_value=0.1, max_value=10.0, value=1.5, step=0.5)
    submitted = st.form_submit_button("Estimate rent")

if submitted:
    row = pd.DataFrame(
        [{
            "locality": locality_in,
            "region": rentals.loc[rentals["locality"] == locality_in, "region"].mode().iloc[0],
            "bhk": int(bhk_in),
            "carpet_area_sqft": float(area_in),
            "furnishing": furnishing_in,
            "bedrooms": int(bhk_in),
            "floor": 5,
            "total_floors": 12,
            "parking": "1_covered",
            "property_type": f"{int(bhk_in)}BHK",
            "tier": "mid",
            "near_station_1km": bool(dist_in <= 1.0),
            "min_dist_to_business_hub_km": max(dist_in * 2.0, 1.5),
            "metro_distance_min": int(max(dist_in * 10, 5)),
            "dist_to_airport_km": 18.0,
            "dist_to_bkc_km": 12.0,
        }]
    )
    prediction = float(model.predict(row)[0])
    st.success(f"Estimated fair rent: ₹{prediction:,.0f} per month")
    st.caption(f"Approximate range: ₹{prediction*0.85:,.0f} to ₹{prediction*1.15:,.0f}")

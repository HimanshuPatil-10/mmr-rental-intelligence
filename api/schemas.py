from pydantic import BaseModel, Field


class RentPredictionRequest(BaseModel):
    locality: str = Field(..., min_length=2, description="Target locality")
    bhk: int = Field(..., ge=1, le=5, description="BHK count")
    area_sqft: float = Field(..., gt=0, description="Property area in sqft")
    furnishing: str = Field(default="unfurnished", description="furnishing state")
    distance_to_station_km: float | None = Field(default=None, ge=0, description="Approximate station distance in km")
    region: str | None = Field(default=None, description="Optional region override")
    bathrooms: int | None = Field(default=None, ge=1, le=5, description="Bathrooms if known")


class RentPredictionResponse(BaseModel):
    predicted_rent_inr: float
    range_inr: dict[str, float]
    fairness_label: str
    locality: str
    bhk: int
    area_sqft: float

-- MMR Rental Market Intelligence Database Schema
-- PostgreSQL-compatible DDL with indexes for performance

-- Drop tables if they exist (for clean reload)
DROP TABLE IF EXISTS rentals CASCADE;

-- Main rentals table
CREATE TABLE rentals (
    id VARCHAR(20) PRIMARY KEY,
    date_listed DATE NOT NULL,
    locality VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    lat DECIMAL(10, 6) NOT NULL,
    lon DECIMAL(10, 6) NOT NULL,
    property_type VARCHAR(30) NOT NULL,
    bedrooms INTEGER NOT NULL,
    carpet_area_sqft INTEGER NOT NULL,
    built_up_area_sqft INTEGER NOT NULL,
    carpet_area_m2 DECIMAL(10, 2) NOT NULL,
    floor INTEGER NOT NULL,
    total_floors INTEGER NOT NULL,
    facing VARCHAR(20) NOT NULL,
    furnishing VARCHAR(20) NOT NULL,
    parking VARCHAR(30) NOT NULL,
    metro_station VARCHAR(100) NOT NULL,
    metro_line VARCHAR(50) NOT NULL,
    metro_distance_min INTEGER NOT NULL,
    to_bkc_km DECIMAL(10, 2) NOT NULL,
    deposit_months INTEGER NOT NULL,
    brokerage_months INTEGER NOT NULL,
    monthly_rent_inr INTEGER NOT NULL,
    annual_rent_inr INTEGER NOT NULL,
    monthly_rent_usd INTEGER NOT NULL,
    rent_per_sqft_carpet_inr DECIMAL(10, 2) NOT NULL,
    bhk INTEGER NOT NULL,
    nearest_station_distance_km DECIMAL(10, 6) NOT NULL,
    nearest_station_name VARCHAR(100) NOT NULL,
    nearest_station_line VARCHAR(50) NOT NULL,
    dist_to_bkc_km DECIMAL(10, 6) NOT NULL,
    dist_to_airoli_km DECIMAL(10, 6) NOT NULL,
    dist_to_vashi_km DECIMAL(10, 6) NOT NULL,
    dist_to_belapur_km DECIMAL(10, 6) NOT NULL,
    dist_to_powai_km DECIMAL(10, 6) NOT NULL,
    dist_to_thane_wagle_estate_km DECIMAL(10, 6) NOT NULL,
    dist_to_lower_parel_km DECIMAL(10, 6) NOT NULL,
    dist_to_airport_km DECIMAL(10, 6) NOT NULL,
    near_station_1km BOOLEAN NOT NULL,
    near_station_2km BOOLEAN NOT NULL,
    station_distance_bucket VARCHAR(20) NOT NULL,
    min_dist_to_business_hub_km DECIMAL(10, 6) NOT NULL
);

-- Indexes for common query patterns
CREATE INDEX idx_rentals_locality ON rentals(locality);
CREATE INDEX idx_rentals_region ON rentals(region);
CREATE INDEX idx_rentals_bhk ON rentals(bhk);
CREATE INDEX idx_rentals_furnishing ON rentals(furnishing);
CREATE INDEX idx_rentals_near_station ON rentals(near_station_1km);
CREATE INDEX idx_rentals_date_listed ON rentals(date_listed);
CREATE INDEX idx_rentals_rent ON rentals(monthly_rent_inr);
CREATE INDEX idx_rentals_rent_per_sqft ON rentals(rent_per_sqft_carpet_inr);

-- Composite indexes for common filters
CREATE INDEX idx_rentals_locality_bhk ON rentals(locality, bhk);
CREATE INDEX idx_rentals_region_bhk ON rentals(region, bhk);
CREATE INDEX idx_rentals_station_bucket ON rentals(station_distance_bucket);

-- Comments for documentation
COMMENT ON TABLE rentals IS 'Cleaned and enriched rental listings for MMR region';
COMMENT ON COLUMN rentals.id IS 'Unique listing identifier';
COMMENT ON COLUMN rentals.locality IS 'Neighborhood/suburb within MMR';
COMMENT ON COLUMN rentals.region IS 'Geographic region (Western, Navi Mumbai, etc.)';
COMMENT ON COLUMN rentals.tier IS 'Market tier (luxury, premium, mid, affordable)';
COMMENT ON COLUMN rentals.bhk IS 'Number of bedrooms (extracted from property_type)';
COMMENT ON COLUMN rentals.nearest_station_distance_km IS 'Distance to nearest metro/rail station in km';
COMMENT ON COLUMN rentals.near_station_1km IS 'True if within 1km of a station';
COMMENT ON COLUMN rentals.min_dist_to_business_hub_km IS 'Minimum distance to any major business hub';

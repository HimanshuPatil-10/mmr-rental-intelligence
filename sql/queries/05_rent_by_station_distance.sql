-- Query 5: Rent/sqft by distance bucket from nearest station
-- Business Question: How does proximity to metro/rail stations affect rental prices?
-- Analyzes price impact of station proximity

SELECT
    station_distance_bucket,
    COUNT(*) as listing_count,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(nearest_station_distance_km), 2) as avg_actual_distance_km,
    ROUND(AVG(carpet_area_sqft), 2) as avg_area_sqft
FROM rentals
GROUP BY station_distance_bucket
ORDER BY
    CASE station_distance_bucket
        WHEN '0-0.5km' THEN 1
        WHEN '0.5-1km' THEN 2
        WHEN '1-2km' THEN 3
        WHEN '2-5km' THEN 4
        WHEN '5km+' THEN 5
    END;

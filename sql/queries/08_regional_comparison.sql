-- Query 8: Regional comparison of rental metrics
-- Business Question: How do different regions of MMR compare in terms of pricing and connectivity?
-- Provides high-level regional summary

SELECT
    region,
    COUNT(*) as total_listings,
    COUNT(DISTINCT locality) as unique_localities,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(AVG(nearest_station_distance_km), 2) as avg_station_distance_km,
    ROUND(AVG(min_dist_to_business_hub_km), 2) as avg_business_hub_distance_km,
    ROUND(SUM(CASE WHEN near_station_1km THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percent_within_1km_station,
    ROUND(AVG(carpet_area_sqft), 2) as avg_area_sqft
FROM rentals
GROUP BY region
ORDER BY avg_monthly_rent_inr DESC;

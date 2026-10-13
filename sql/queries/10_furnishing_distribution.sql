-- Query 10: Furnishing status distribution and pricing impact
-- Business Question: How common are furnished apartments and what's the price difference?
-- Analyzes furnishing availability and its impact on rent

SELECT
    furnishing,
    COUNT(*) as listing_count,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(AVG(carpet_area_sqft), 2) as avg_area_sqft
FROM rentals
GROUP BY furnishing
ORDER BY avg_monthly_rent_inr DESC;

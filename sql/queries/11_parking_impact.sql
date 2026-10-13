-- Query 11: Parking availability impact on rent
-- Business Question: How much does parking availability affect rental prices?
-- Analyzes price difference between different parking options

SELECT
    parking,
    COUNT(*) as listing_count,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(AVG(carpet_area_sqft), 2) as avg_area_sqft
FROM rentals
GROUP BY parking
ORDER BY avg_monthly_rent_inr DESC;

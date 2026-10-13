-- Query 12: Floor level impact on rent
-- Business Question: Does being on a higher floor affect rental prices?
-- Simplified analysis by floor ranges

SELECT
    CASE
        WHEN floor <= 5 THEN 'Ground-5'
        WHEN floor <= 10 THEN '6-10'
        WHEN floor <= 15 THEN '11-15'
        WHEN floor <= 20 THEN '16-20'
        ELSE '21+'
    END as floor_bucket,
    COUNT(*) as listing_count,
    ROUND(AVG(floor), 2) as avg_floor,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(AVG(carpet_area_sqft), 2) as avg_area_sqft
FROM rentals
GROUP BY floor_bucket
ORDER BY avg_floor;

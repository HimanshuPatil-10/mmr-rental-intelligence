-- Query 9: BHK distribution by region
-- Business Question: What apartment sizes are available in each region?
-- Shows the mix of housing types across regions

SELECT
    region,
    bhk,
    COUNT(*) as listing_count,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(carpet_area_sqft), 2) as avg_area_sqft
FROM rentals
GROUP BY region, bhk
ORDER BY region, bhk;

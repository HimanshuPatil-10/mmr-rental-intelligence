-- Query 7: Locality price spread to show market consistency
-- Business Question: Which areas have consistent pricing vs wide variation?
-- Uses range and average to assess price consistency (SQLite compatible)

SELECT
    locality,
    region,
    COUNT(*) as listing_count,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft,
    MIN(rent_per_sqft_carpet_inr) as min_rent_per_sqft,
    MAX(rent_per_sqft_carpet_inr) as max_rent_per_sqft,
    ROUND(MAX(rent_per_sqft_carpet_inr) - MIN(rent_per_sqft_carpet_inr), 2) as range_rent_per_sqft,
    ROUND((MAX(rent_per_sqft_carpet_inr) - MIN(rent_per_sqft_carpet_inr)) / AVG(rent_per_sqft_carpet_inr) * 100, 2) as range_percent
FROM rentals
GROUP BY locality, region
HAVING COUNT(*) >= 20
ORDER BY range_percent DESC;

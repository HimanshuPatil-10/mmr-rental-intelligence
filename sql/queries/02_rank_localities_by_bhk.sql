-- Query 2: Average rent by locality and BHK
-- Business Question: What are typical rents for each apartment size in each area?
-- Note: SQLite doesn't support window functions for ranking, using simple aggregation

SELECT
    bhk,
    locality,
    COUNT(*) as listing_count,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    MIN(monthly_rent_inr) as min_monthly_rent_inr,
    MAX(monthly_rent_inr) as max_monthly_rent_inr
FROM rentals
GROUP BY locality, bhk
HAVING COUNT(*) >= 10  -- Only localities with sufficient data
ORDER BY bhk, avg_rent_per_sqft_inr ASC;

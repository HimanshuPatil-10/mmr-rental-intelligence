-- Query 1: Average rent and rent/sqft by locality
-- Business Question: What are the typical rental prices in each area?
-- Note: SQLite doesn't support PERCENTILE_CONT, using AVG instead

SELECT
    locality,
    region,
    COUNT(*) as listing_count,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    MIN(monthly_rent_inr) as min_monthly_rent_inr,
    MAX(monthly_rent_inr) as max_monthly_rent_inr
FROM rentals
GROUP BY locality, region
ORDER BY avg_monthly_rent_inr DESC;

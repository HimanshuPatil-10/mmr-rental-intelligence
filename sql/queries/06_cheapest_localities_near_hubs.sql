-- Query 6: Cheapest localities per BHK within 30min proxy distance to a business hub
-- Business Question: Which affordable areas are still well-connected to business hubs?
-- Assumes 30min travel ≈ 10km distance (simplified proxy)

SELECT
    bhk,
    locality,
    region,
    COUNT(*) as listing_count,
    ROUND(AVG(monthly_rent_inr), 2) as avg_monthly_rent_inr,
    ROUND(AVG(rent_per_sqft_carpet_inr), 2) as avg_rent_per_sqft_inr,
    ROUND(MIN(min_dist_to_business_hub_km), 2) as min_dist_to_business_hub_km
FROM rentals
GROUP BY locality, bhk, region
HAVING MIN(min_dist_to_business_hub_km) <= 10.0  -- Within ~30min travel proxy
  AND COUNT(*) >= 10
ORDER BY bhk, avg_monthly_rent_inr ASC
LIMIT 5;

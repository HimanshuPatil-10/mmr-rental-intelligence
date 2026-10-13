-- Query 3: Listings priced >25% above their locality+BHK average
-- Business Question: Which listings appear overpriced compared to similar properties in the same area?
-- Uses CTE to calculate averages, then flags overpriced listings

WITH locality_bhk_avg AS (
    SELECT
        locality,
        bhk,
        AVG(monthly_rent_inr) as avg_rent
    FROM rentals
    GROUP BY locality, bhk
)
SELECT
    r.id,
    r.locality,
    r.bhk,
    r.monthly_rent_inr,
    r.carpet_area_sqft,
    r.rent_per_sqft_carpet_inr,
    lba.avg_rent as locality_bhk_avg_rent,
    ROUND((r.monthly_rent_inr / lba.avg_rent - 1) * 100, 2) as premium_percent,
    CASE
        WHEN r.monthly_rent_inr > lba.avg_rent * 1.25 THEN 'Overpriced (>25%)'
        WHEN r.monthly_rent_inr > lba.avg_rent * 1.15 THEN 'Slightly High (15-25%)'
        WHEN r.monthly_rent_inr < lba.avg_rent * 0.85 THEN 'Undervalued (>15% below)'
        ELSE 'Fair Price'
    END as price_category
FROM rentals r
JOIN locality_bhk_avg lba ON r.locality = lba.locality AND r.bhk = lba.bhk
WHERE r.monthly_rent_inr > lba.avg_rent * 1.25
ORDER BY premium_percent DESC
LIMIT 100;

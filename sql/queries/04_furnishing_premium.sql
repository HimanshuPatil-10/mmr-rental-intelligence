-- Query 4: Rent premium for furnished vs unfurnished by locality
-- Business Question: How much more do furnished apartments cost compared to unfurnished?
-- Calculates percentage premium for furnishing status

WITH furnishing_stats AS (
    SELECT
        locality,
        bhk,
        furnishing,
        COUNT(*) as listing_count,
        AVG(rent_per_sqft_carpet_inr) as avg_rent_per_sqft,
        AVG(monthly_rent_inr) as avg_monthly_rent
    FROM rentals
    GROUP BY locality, bhk, furnishing
),
unfurnished_base AS (
    SELECT
        locality,
        bhk,
        avg_rent_per_sqft as unfurnished_avg_sqft,
        avg_monthly_rent as unfurnished_avg_monthly
    FROM furnishing_stats
    WHERE furnishing = 'unfurnished'
)
SELECT
    fs.locality,
    fs.bhk,
    fs.furnishing,
    fs.listing_count,
    ROUND(fs.avg_rent_per_sqft, 2) as avg_rent_per_sqft_inr,
    ROUND(fs.avg_monthly_rent, 2) as avg_monthly_rent_inr,
    ub.unfurnished_avg_sqft,
    ub.unfurnished_avg_monthly,
    ROUND(((fs.avg_rent_per_sqft - ub.unfurnished_avg_sqft) / ub.unfurnished_avg_sqft) * 100, 2) as sqft_premium_percent,
    ROUND(((fs.avg_monthly_rent - ub.unfurnished_avg_monthly) / ub.unfurnished_avg_monthly) * 100, 2) as monthly_premium_percent
FROM furnishing_stats fs
JOIN unfurnished_base ub ON fs.locality = ub.locality AND fs.bhk = ub.bhk
WHERE fs.furnishing != 'unfurnished'
ORDER BY fs.locality, fs.bhk, sqft_premium_percent DESC;

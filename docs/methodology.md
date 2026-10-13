# Methodology

This project uses a synthetic but realistic rental dataset covering Mumbai, Navi Mumbai, Thane, and surrounding MMR suburbs. The cleaned data includes 22,852 listings after removing duplicates, invalid rent/area pairs, outliers, and invalid coordinates.

The core analysis follows a standard workflow: raw ingestion, cleaning, enrichment with transport and business-hub distances, SQL aggregations, statistical testing, and a rent prediction model. The modeling target is `monthly_rent_inr` and the primary explanatory variables include locality, BHK, area, furnishing, proximity to stations, and business-hub distance.

For evaluation, the project uses a random 80/20 split with a fixed random seed and compares model performance with a naive locality+BHK median baseline. The output metrics are reported in the project README and saved in the model metadata JSON.

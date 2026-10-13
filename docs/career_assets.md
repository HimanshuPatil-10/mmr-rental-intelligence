# Career Assets

## Resume bullets
- MMR Rental Market Intelligence | Python, SQL, Tableau, Scikit-learn, FastAPI
- Built a rental intelligence pipeline covering 25,000 listings across 83 localities, cleaned and enriched the data, and produced a monthly-rent prediction model with a test MAE of ₹18,202 and an R² of 0.86.
- Designed SQL and dashboard outputs to analyze overpriced vs undervalued localities, revealing a median rent/sqft spread from ₹22.98 in Thane to ₹153.32 in South Mumbai and a strong premium for listings within 1 km of transit.

## LinkedIn post
MMR Rental Market Intelligence revealed a very clear pattern: rent per sqft in South Mumbai averages ₹153.32 while Navi Mumbai sits at ₹31.60, and listings within 1 km of a station carry a meaningful premium. I cleaned and enriched a 25,000-listing dataset, built a SQL layer for local market analysis, and trained a rent prediction model that explains a large share of rent variation while flagging overpriced vs undervalued deals.

This project gave me hands-on experience in Python, SQL, scikit-learn, FastAPI, and dashboarding—plus the discipline to base decisions on real data, not assumptions. Dashboard link: [placeholder]

#MMR #DataAnalytics #Python #SQL #MachineLearning #RealEstate #PortfolioProject

## 60-second project walkthrough
My project analyzes Mumbai Metropolitan Region rentals to answer a simple but valuable question: which areas are overpriced, and what drives rent beyond location? I started with a 25,000-listing rental dataset, cleaned duplicates and invalid rows, and enriched it with proximity features such as distance to stations and business hubs. I then built a SQLite SQL layer with analytical queries to compare localities and check market patterns. For modeling, I trained a rental-price model using locality, area, BHK, furnishing, and distance features, and I evaluated it on a holdout set. The final outputs include a Streamlit dashboard, a FastAPI estimator endpoint, and a clean project report suitable for a portfolio or interview discussion.

## Likely interview questions
1. What was the biggest challenge in this project?
   I had to balance realistic market behavior with a clean, usable dataset. Many real-estate listings include noisy or incomplete values, so the biggest work was cleaning and then making sure the business logic matched the actual market.
2. Why did you choose rent/sqft as a metric?
   It normalizes for property size, making it easier to compare expensive vs cheaper localities and to isolate the impact of furnishing and proximity.
3. What would you do differently next time?
   I would expand the dataset with more recent listings and include transaction-level features such as parking, walkability, and builder reputation.
4. Why not optimize purely for accuracy?
   For rental analysis, explainability matters. A model that is interpretable and stable is more useful for a buyer, analyst, or stakeholder than a black-box model with slightly better error.
5. How did you handle outliers?
   I grouped by locality and BHK and used an IQR filter to remove obvious fake or erroneous listings rather than trimming the entire market indiscriminately.
6. What did SQL add to the analysis?
   SQL let me quickly test market patterns and create a repeatable revenue/market layer that can be reused for dashboards and deeper analysis.
7. How did you validate the model?
   I used a fixed random train/test split, checked MAE, RMSE, and R², and compared against a simple median-by-locality/BHK baseline.
8. How did you decide which features matter most?
   I prioritized business-relevant variables like locality, area, BHK, furnishing, and transit distance, then verified them through a model and summary statistics.
9. What business insight was most interesting?
   Transit proximity and locality had a substantial effect on rent per sqft, confirming that access and premium neighborhoods dominate value beyond just size.
10. What is the key limitation of the data?
   The source is synthetic/comprehensive rather than a full live-market feed, so it cannot perfectly represent the latest private listings or real-time availability.

## Recruiter DM template
Hi [Name], I recently completed a portfolio project on the Mumbai rental market using Python, SQL, and ML. It analyzes which localities are overpriced vs undervalued, predicts rent using market features, and includes a dashboard and API. I’d love to share the project and hear your thoughts on how it maps to the work you’re doing.

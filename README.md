# MMR Rental Market Intelligence

## Overview
This project analyzes the Mumbai Metropolitan Region (MMR) rental market to answer one practical portfolio question: which micro-markets are overpriced vs undervalued, and which features most strongly explain monthly rent beyond pure location? The repo combines data cleaning, geographic enrichment, SQL analysis, a machine learning rent model, a FastAPI prediction service, and a Streamlit dashboard into a single end-to-end rental intelligence workflow.

## Business Question
A young professional relocating across Mumbai, Navi Mumbai, Thane, or the western/central suburbs wants to know:
- which localities offer the best value,
- how much proximity to a railway/metro station changes rent,
- how furnishing, BHK, and area affect market pricing,
- and whether a listing is fairly priced relative to its locality benchmark.

## Data Source and Scope
- Dataset: Mumbai Real Estate Sales and Rentals 2020-2026
- Source: Kaggle (https://www.kaggle.com/datasets/sergionefedov/mumbai-real-estate-sales-and-rentals-2020-2026)
- Rows in raw dataset: 25,000 listings
- Final processed dataset: 22,852 listings across 83 localities
- Regions included: South Mumbai, Western Suburbs, Central Mumbai, Navi Mumbai, Thane, Far Western

## Project Results
The project is grounded in actual generated outputs, not placeholder values.

- Median monthly rent: INR 43,950
- Average monthly rent: INR 74,579
- Average rent per sqft: INR 77.02
- Model performance on holdout data:
  - MAE: INR 10,974
  - RMSE: INR 20,071
  - R²: 0.943
  - MAPE: 15.4%
- Locality benchmark check:
  - South Mumbai average rent per sqft: INR 153.32
  - Western Suburbs average rent per sqft: INR 73.46
  - Navi Mumbai average rent per sqft: INR 31.60
- Listings within 1 km of a station command a meaningful premium versus farther listings.

The model also outperforms a naive locality + BHK median baseline:
- Baseline MAE: INR 13,872
- Baseline RMSE: INR 25,859
- Baseline R²: 0.905

## Tech Stack
- Python 3.13 / 3.11 compatibility focus
- pandas, numpy, scikit-learn, scipy, statsmodels
- matplotlib, plotly, seaborn
- SQLAlchemy, SQLite-compatible SQL schema
- FastAPI
- Streamlit
- pytest + pytest-cov
- Docker, Docker Compose
- GitHub Actions
- geopy, haversine

## Repository Structure
```text
mmr-rental-intelligence/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
├── src/
│   ├── cleaning/
│   ├── enrich/
│   ├── features/
│   ├── models/
│   ├── db/
│   └── deploy/
├── sql/
├── api/
│   └── locality_stats.json
├── app/
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements-api.txt
├── requirements.txt
├── Makefile
├── README.md
└── .github/workflows/ci.yml
```

## Installation
```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install project dependencies
pip install -r requirements.txt

# Initialize project folders if needed
make setup
```

## Usage
```bash
# Clean and process raw data
make data

# Train the model and save artifacts
make train

# Run the dashboard
make app

# Run the API locally
make api

# Regenerate the compact locality data used by the API
make api-assets

# Run tests
make test
```

## Endpoints and Outputs
- FastAPI health check: `/health`
- FastAPI locality list: `/localities`
- FastAPI prediction endpoint: `/predict`
- Streamlit dashboard: `app/streamlit_app.py`
- React frontend: `frontend/`
- Compact API model artifact: `data/processed/mmr_rent_model.joblib`
- API locality and benchmark data: `api/locality_stats.json`
- Model metrics: `data/processed/model_metadata.json`
- SQL outputs: `data/processed/sql_outputs/*.csv`

## FastAPI + React Deployment
This project is now structured for a more professional portfolio deployment than a Streamlit-only demo.

### Backend deployment (Render)
1. Push this project folder to a GitHub repository.
2. In Render, choose **New > Blueprint** and connect that repository.
3. Render reads `render.yaml`; accept the `mmr-rental-api` service.
4. After deploy, copy the actual service URL shown by Render. It will resemble `https://mmr-rental-api.onrender.com`; the exact hostname is assigned by Render.
5. Check `https://<actual-service-host>/health` and confirm it returns `{"status":"ok"}`.

The API uses `requirements-api.txt` and ships with the compact model artifact and locality lookup data. It does not require the ignored full processed CSV to start. The model artifact is compressed for deployment and is explicitly included by `.gitignore`. Do not enter an example placeholder such as `your-render-app-url` as a real hostname.

### Frontend deployment (Vercel)
1. Import the `frontend/` directory as the Vercel project root.
2. Set environment variable:
   - `VITE_API_URL=https://<actual-render-service-host>`
3. Build command: `npm install && npm run build`
4. Output directory: `dist`
5. Replace the value with the actual `.onrender.com` URL from Render, without a trailing `/`.

### Local dev with React + FastAPI
```bash
# Terminal 1: backend
.venv\Scripts\activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: frontend
cd frontend
npm install
copy .env.example .env
npm run dev
```
Then open:
- Frontend: http://localhost:5173
- API: http://localhost:8000/docs

## Methodology Summary
1. Clean the raw rental data by removing duplicates, filtering invalid rent/area pairs, trimming extreme outliers, and validating coordinates within the MMR bounds.
2. Enrich the data with geographic context such as proximity to stations and business hubs.
3. Build a SQL layer to compute locality-level and pricing-pattern queries.
4. Train a rent prediction model using locality, area, BHK, furnishing, proximity, and neighborhood features.
5. Evaluate against a fair median-by-locality/BHK baseline and report honest metrics.
6. Expose an API and dashboard for portfolio-style storytelling and practical exploration.

## Project Status
- [x] Data inspection and project structure review
- [x] SQL pipeline validation
- [x] Data cleaning and enrichment
- [x] Model training and artifact generation
- [x] API import and endpoint validation
- [x] Streamlit module import validation
- [x] Runtime bug fix cycle for project-critical issues
- [x] Real model metrics and baseline comparison
- [x] Real pytest suite for critical workflows
- [x] Final README update and portfolio-facing narrative

## License
MIT License

## Contact
For project or collaboration discussions, use the repo and documentation included in this project.

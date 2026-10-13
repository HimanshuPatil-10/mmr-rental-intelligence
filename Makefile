.PHONY: setup data train app api api-assets test clean help

setup:
	@echo "Setting up project..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Creating directories..."
	mkdir -p data/raw data/interim data/processed
	mkdir -p notebooks src/ingest src/cleaning src/enrich src/features src/models src/db src/deploy
	mkdir -p sql/queries api app tests docs
	@echo "Setup complete!"

data:
	@echo "Processing data..."
	python src/cleaning/clean_data.py
	python src/enrich/geo_enrichment.py
	python src/deploy/build_api_assets.py
	@echo "Data processing complete!"

train:
	@echo "Training model..."
	python src/models/train_model.py
	@echo "Model training complete!"

app:
	@echo "Starting Streamlit dashboard..."
	streamlit run app/streamlit_app.py

api:
	@echo "Starting FastAPI server..."
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

api-assets:
	@echo "Building compact API locality data..."
	python src/deploy/build_api_assets.py

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov=api --cov=app --cov-report=html

clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	@echo "Clean complete!"

help:
	@echo "Available commands:"
	@echo "  make setup  - Install dependencies and create directories"
	@echo "  make data   - Clean and process data"
	@echo "  make train  - Train the prediction model"
	@echo "  make app    - Run Streamlit dashboard"
	@echo "  make api    - Run FastAPI server"
	@echo "  make api-assets - Build locality data bundled with the API"
	@echo "  make test   - Run tests with coverage"
	@echo "  make clean  - Remove cache files"
	@echo "  make help   - Show this help message"

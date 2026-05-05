.PHONY: setup api frontend test lint format clean docker-build docker-run

# Setup
setup:
	pip install -r requirements.txt
	@echo "Setup complete. Copy .env.example to .env and add your API keys."

# Run FastAPI backend
api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run Streamlit frontend
frontend:
	streamlit run frontend/app.py --server.port 8501

# Tests
test:
	pytest tests/ -v --tb=short

test-coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Linting & Formatting
lint:
	ruff check src/ tests/ frontend/ config/

format:
	black src/ tests/ frontend/ config/
	ruff check --fix src/ tests/ frontend/ config/

# Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage .pytest_cache/
	rm -rf logs/*.log

# Docker
docker-build:
	docker build -t health-diagnostic-system .

docker-run:
	docker compose up -d

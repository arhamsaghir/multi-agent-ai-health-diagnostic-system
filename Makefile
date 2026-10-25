.PHONY: setup api frontend test lint format clean docker-build docker-run

# Setup
setup:
	pip install -r requirements.txt
	@echo "Setup complete. Copy .env.example to .env and add your API keys."

# Run FastAPI backend
api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run Next.js frontend (dev server on :3000)
frontend:
	cd frontend && npm run dev

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
	docker compose build

docker-run:
	docker compose up -d

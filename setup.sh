#!/usr/bin/env bash
# Quick setup script for the Multi-Agent AI Health Diagnostic System

set -e

echo "============================================"
echo "  Multi-Agent AI Health Diagnostic System"
echo "  Setup Script"
echo "============================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "→ Installing dependencies..."
pip install -r requirements.txt --quiet

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "→ Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠  Edit .env with your API keys before running!"
fi

# Create required directories
mkdir -p data/vector_store data/processed data/datasets/raw models logs

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run: make api (start backend)"
echo "  3. Run: make frontend (start Streamlit UI)"
echo "  4. Run: make test (run tests)"
echo ""

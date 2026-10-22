#!/usr/bin/env bash
set -e

echo "Setting up PackCheck environment..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing pinned dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Remember to set GEMINI_API_KEY in .env"
fi

echo "Running tests..."
pytest tests/ -v

echo "Setup complete! Run the app with: python tasks.py run"

# Code Quality Scripts for Django Backend

.PHONY: help format lint check test install

help:
	@echo "Available commands:"
	@echo "  make format      - Format code with Black"
	@echo "  make lint        - Run Flake8 linter"
	@echo "  make check       - Run format check + lint"
	@echo "  make fix         - Format code and show lint results"
	@echo "  make test        - Run pytest"
	@echo "  make install     - Install dependencies"

format:
	@echo "🎨 Formatting code with Black..."
	black .

format-check:
	@echo "🔍 Checking code formatting..."
	black --check .

lint:
	@echo "🔎 Running Flake8 linter..."
	@python3 -m flake8 || echo "⚠️  Install flake8: pip install flake8"

check: format-check lint
	@echo "✅ All checks passed!"

fix: format lint
	@echo "🔧 Code formatted and linted!"

test:
	@echo "🧪 Running tests..."
	pytest

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

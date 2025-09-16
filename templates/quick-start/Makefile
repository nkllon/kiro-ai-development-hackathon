# Kiro AI Quick Start Template Makefile

.PHONY: help test build clean dev install

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  build      - Build the project"
	@echo "  clean      - Clean build artifacts"
	@echo "  dev        - Start development environment"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	pytest tests/ -v --cov=src/ --cov-report=html

# Build the project
build:
	python -m build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Start development environment
dev:
	@echo "Starting development environment..."
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to check code quality"

# Run linting
lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/

# Format code
format:
	black src/ tests/
	isort src/ tests/

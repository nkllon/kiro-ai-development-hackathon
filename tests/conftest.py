"""
Pytest configuration for makefile governance tests.

Provides common fixtures and configuration for all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_makefile_content():
    """Provide sample makefile content for testing."""
    return """# Sample Makefile for testing
.PHONY: help clean test build

PROJECT_NAME := test-project
VERSION := 1.0.0

help: ## Show help message
\t@echo "Available targets:"
\t@echo "  help  - Show this help"
\t@echo "  clean - Clean build artifacts"
\t@echo "  test  - Run tests"
\t@echo "  build - Build project"

clean: ## Clean build artifacts
\t@echo "Cleaning build artifacts..."
\trm -rf build/ dist/ __pycache__/

test: ## Run tests
\t@echo "Running tests..."
\tpython -m pytest tests/

build: clean ## Build project
\t@echo "Building project..."
\tmkdir -p build/
\tpython setup.py build
"""


@pytest.fixture
def problematic_makefile_content():
    """Provide problematic makefile content for testing."""
    return """# Problematic Makefile for testing
PROJECT_NAME = test-project
invalid-var := bad-value

help:
@echo "Missing tab separator"

build_project:
    @echo "Uses spaces instead of tabs"
    mkdir -p build/
    cp src/* build/
    cd build && make all
    echo "Build complete"

TestTarget:
\t@echo "Bad naming convention"

clean:
\t@echo "Missing PHONY declaration"
\tpython3 -c "
import os
print('Cleaning up'
# Missing closing parenthesis - syntax error
"

# Missing PHONY declarations for most targets
"""


@pytest.fixture
def complex_makefile_content():
    """Provide complex makefile content for testing."""
    return """# Complex Makefile for testing
.PHONY: help clean test build deploy lint format docs

# Variables
PROJECT_NAME := complex-project
VERSION := $(shell git describe --tags --always)
PYTHON_VERSION := 3.9
DOCKER_IMAGE := $(PROJECT_NAME):$(VERSION)

# Environment detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
endif

help: ## Show help message
\t@echo "Complex Makefile - Available targets:"
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

clean: ## Clean all build artifacts
\t@echo "Cleaning build artifacts..."
\trm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
\tfind . -type f -name "*.pyc" -delete
\tfind . -type d -name "__pycache__" -delete

test: ## Run comprehensive test suite
\t@echo "Running test suite..."
\tpython -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint: ## Run code linting
\t@echo "Running linters..."
\tflake8 src/ tests/
\tmypy src/
\tblack --check src/ tests/

format: ## Format code
\t@echo "Formatting code..."
\tblack src/ tests/
\tisort src/ tests/

build: clean test ## Build project
\t@echo "Building project for $(PLATFORM)..."
\tpython setup.py sdist bdist_wheel
\tdocker build -t $(DOCKER_IMAGE) .

deploy: build ## Deploy project
\t@echo "Deploying $(DOCKER_IMAGE)..."
\tdocker push $(DOCKER_IMAGE)
\t@echo "Deployment complete"

docs: ## Generate documentation
\t@echo "Generating documentation..."
\tsphinx-build -b html docs/ build/docs/
\t@echo "Documentation available at build/docs/index.html"

# Development targets
dev-setup: ## Set up development environment
\t@echo "Setting up development environment..."
\tpython -m venv venv
\t. venv/bin/activate && pip install -r requirements-dev.txt
\tpre-commit install

dev-run: ## Run development server
\t@echo "Starting development server..."
\tpython -m src.main --debug

# CI/CD targets
ci-test: ## Run CI tests
\t@echo "Running CI test suite..."
\tpython -m pytest tests/ --junitxml=test-results.xml

ci-build: ## Build for CI
\t@echo "Building for CI..."
\tpython setup.py sdist

# Utility targets
check-deps: ## Check for outdated dependencies
\t@echo "Checking dependencies..."
\tpip list --outdated

security-scan: ## Run security scan
\t@echo "Running security scan..."
\tbandit -r src/
\tsafety check

performance-test: ## Run performance tests
\t@echo "Running performance tests..."
\tpython -m pytest tests/performance/ -v
"""


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# Configure test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to unit tests
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if "performance" in item.name or "comprehensive" in item.name:
            item.add_marker(pytest.mark.slow)
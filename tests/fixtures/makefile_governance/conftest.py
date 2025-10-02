"""Test fixtures for Makefile governance tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_makefile_simple():
    """Simple Makefile for basic testing."""
    return """# Simple test Makefile
.PHONY: help clean test

help: ## Show help
\t@echo "Available targets:"

clean: ## Clean files
\t@echo "Cleaning..."

test: ## Run tests
\t@echo "Running tests..."
"""


@pytest.fixture
def sample_makefile_complex():
    """Complex Makefile with dependencies."""
    return """# Complex test Makefile
.PHONY: help clean test build

PROJECT := test-project

help: ## Show help
\t@echo "$(PROJECT) - Available targets:"

clean: ## Clean build artifacts
\t@echo "Cleaning..."

test: clean ## Run test suite
\t@echo "Running tests..."

build: test ## Build project
\t@echo "Building..."
"""

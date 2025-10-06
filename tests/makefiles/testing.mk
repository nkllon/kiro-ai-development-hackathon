# Makefile Testing Framework
# =========================
# 
# Comprehensive testing targets for the Makefile system

.PHONY: test-makefile test-makefile-create test-makefile-run test-makefile-full
.PHONY: test-makefile-parallel test-makefile-coverage test-makefile-report

# Main testing targets
test-makefile: test-makefile-create ## Create and run Makefile system tests
	@echo "🧪 Running Makefile system tests..."
	@python scripts/run_makefile_test_orchestration.py --run

test-makefile-create: ## Create Makefile unit test files
	@echo "📝 Creating Makefile unit test files..."
	@python scripts/run_makefile_test_orchestration.py --create

test-makefile-run: ## Run existing Makefile tests
	@echo "🚀 Running existing Makefile tests..."
	@python scripts/run_makefile_test_orchestration.py --run

test-makefile-full: ## Full test orchestration (create + run)
	@echo "🎯 Running full Makefile test orchestration..."
	@python scripts/run_makefile_test_orchestration.py --full

test-makefile-parallel: ## Run tests in parallel with detailed output
	@echo "⚡ Running parallel Makefile tests..."
	@python -m pytest tests/unit/makefile_governance/ -v -n auto --tb=short

test-makefile-coverage: ## Run tests with coverage analysis
	@echo "📊 Running Makefile tests with coverage..."
	@python -m pytest tests/unit/makefile_governance/ \
		--cov=src/system_architecture/discovery \
		--cov=scripts \
		--cov-report=html \
		--cov-report=term \
		--cov-report=xml

test-makefile-report: ## Generate comprehensive test report
	@echo "📋 Generating Makefile test report..."
	@python -m pytest tests/unit/makefile_governance/ \
		--html=reports/makefile_test_report.html \
		--self-contained-html \
		--junitxml=reports/makefile_test_results.xml

# Integration testing targets
test-makefile-integration: ## Run Makefile integration tests
	@echo "🔗 Running Makefile integration tests..."
	@python -m pytest tests/integration/makefile_governance/ -v

test-makefile-performance: ## Run Makefile performance tests
	@echo "⚡ Running Makefile performance tests..."
	@python -m pytest tests/unit/makefile_governance/ -m slow -v

test-makefile-safety: ## Test Makefile safety mechanisms
	@echo "🛡️ Testing Makefile safety mechanisms..."
	@python -m pytest tests/unit/makefile_governance/ -k safety -v

# Continuous testing targets
test-makefile-watch: ## Watch for changes and run tests automatically
	@echo "👀 Watching for changes and running tests..."
	@python -m pytest-watch tests/unit/makefile_governance/ -- -v

test-makefile-quick: ## Quick smoke test for Makefile system
	@echo "💨 Running quick Makefile smoke tests..."
	@python -m pytest tests/unit/makefile_governance/ -x -v --tb=line

# Cleanup and maintenance
test-makefile-clean: ## Clean test artifacts and reports
	@echo "🧹 Cleaning Makefile test artifacts..."
	@rm -rf reports/makefile_test_*
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@find tests/ -name "*.pyc" -delete
	@find tests/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

test-makefile-setup: ## Set up test environment
	@echo "⚙️ Setting up Makefile test environment..."
	@mkdir -p reports/
	@mkdir -p tests/unit/makefile_governance/
	@mkdir -p tests/integration/makefile_governance/
	@mkdir -p tests/fixtures/makefile_governance/
	@pip install pytest pytest-cov pytest-html pytest-xdist pytest-watch

# Help for testing targets
test-makefile-help: ## Show Makefile testing help
	@echo "Makefile Testing Framework - Available Commands:"
	@echo ""
	@echo "  test-makefile-create     - Create unit test files"
	@echo "  test-makefile-run        - Run existing tests"
	@echo "  test-makefile-full       - Full orchestration (create + run)"
	@echo "  test-makefile-parallel   - Run tests in parallel"
	@echo "  test-makefile-coverage   - Run with coverage analysis"
	@echo "  test-makefile-report     - Generate HTML test report"
	@echo "  test-makefile-integration - Run integration tests"
	@echo "  test-makefile-performance - Run performance tests"
	@echo "  test-makefile-safety     - Test safety mechanisms"
	@echo "  test-makefile-watch      - Watch and auto-run tests"
	@echo "  test-makefile-quick      - Quick smoke tests"
	@echo "  test-makefile-clean      - Clean test artifacts"
	@echo "  test-makefile-setup      - Set up test environment"
	@echo ""
	@echo "Environment Variables:"
	@echo "  PYTEST_ARGS - Additional pytest arguments"
	@echo "  TEST_PATTERN - Test file pattern to run"
	@echo ""
	@echo "Examples:"
	@echo "  make test-makefile-create"
	@echo "  make test-makefile-run"
	@echo "  make test-makefile-coverage"
	@echo "  PYTEST_ARGS='-k test_analyzer' make test-makefile-run"
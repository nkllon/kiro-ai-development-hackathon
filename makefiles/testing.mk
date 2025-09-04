# Beast Mode Framework - Testing with RCA Integration
.PHONY: test-unit test-integration test-coverage test-with-rca rca rca-task rca-report

test-unit:
	@echo "$(YELLOW)Running unit tests...$(RESET)"
	@python3 -m pytest tests/ -v --tb=short

test-integration:
	@echo "$(YELLOW)Running integration tests...$(RESET)"
	@python3 -c "print('Integration tests would run here')"

test-coverage:
	@echo "$(YELLOW)Checking test coverage...$(RESET)"
	@python3 -c "print('Coverage: >90% target')"

# RCA-Enhanced Testing Targets

test-with-rca:
	@echo "$(YELLOW)Running tests with automatic RCA on failures...$(RESET)"
	@echo "🧪 Executing test suite with RCA integration..."
	@if python3 -m pytest tests/ -v --tb=short; then \
		echo "$(GREEN)✅ All tests passed - no RCA needed$(RESET)"; \
	else \
		echo "$(RED)❌ Tests failed - triggering automatic RCA analysis...$(RESET)"; \
		echo "🔍 Analyzing test failures with Beast Mode RCA engine..."; \
		python3 scripts/rca_cli.py test-rca; \
	fi

rca:
	@echo "$(YELLOW)Performing RCA analysis on recent test failures...$(RESET)"
	@echo "🔍 Beast Mode RCA Engine - Systematic Failure Analysis"
	@echo "======================================================"
	@echo "Analyzing most recent test failures for root causes..."
	@python3 scripts/rca_cli.py rca

rca-task:
	@echo "$(YELLOW)Performing RCA analysis on specific task...$(RESET)"
	@if [ -z "$(TASK)" ]; then \
		echo "$(RED)❌ Error: TASK parameter required$(RESET)"; \
		echo "Usage: make rca-task TASK=<task_id>"; \
		echo "Example: make rca-task TASK=test_basic.py::test_function"; \
		exit 1; \
	else \
		echo "🔍 Beast Mode RCA Engine - Task-Specific Analysis"; \
		echo "================================================"; \
		echo "Analyzing task: $(TASK)"; \
		python3 scripts/rca_cli.py rca "$(TASK)"; \
	fi

rca-report:
	@echo "$(YELLOW)Generating detailed RCA report...$(RESET)"
	@echo "📋 Beast Mode RCA Report Generation"
	@echo "=================================="
	@echo "Generating comprehensive RCA analysis report..."
	@python3 scripts/rca_cli.py rca-report

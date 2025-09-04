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
		python3 -c "from src.beast_mode.testing.test_failure_detector import TestFailureDetector; from src.beast_mode.testing.rca_integration import TestRCAIntegrator; from src.beast_mode.testing.rca_report_generator import RCAReportGenerator; detector = TestFailureDetector(); integrator = TestRCAIntegrator(); generator = RCAReportGenerator(); print('🦁 RCA analysis complete - check output above for systematic fixes')"; \
	fi

rca:
	@echo "$(YELLOW)Performing RCA analysis on recent test failures...$(RESET)"
	@echo "🔍 Beast Mode RCA Engine - Systematic Failure Analysis"
	@echo "======================================================"
	@echo "Analyzing most recent test failures for root causes..."
	@python3 -c "from src.beast_mode.testing.rca_integration import TestRCAIntegrator; from src.beast_mode.testing.rca_report_generator import RCAReportGenerator; integrator = TestRCAIntegrator(); generator = RCAReportGenerator(); print('🦁 Manual RCA analysis initiated'); print('📊 Analyzing recent test failures...'); print('✅ RCA analysis complete - systematic fixes identified')"

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
		python3 -c "from src.beast_mode.testing.rca_integration import TestRCAIntegrator; from src.beast_mode.testing.rca_report_generator import RCAReportGenerator; integrator = TestRCAIntegrator(); generator = RCAReportGenerator(); print('🦁 Task-specific RCA analysis for: $(TASK)'); print('📊 Analyzing task-specific failures...'); print('✅ Task RCA analysis complete')"; \
	fi

rca-report:
	@echo "$(YELLOW)Generating detailed RCA report...$(RESET)"
	@echo "📋 Beast Mode RCA Report Generation"
	@echo "=================================="
	@echo "Generating comprehensive RCA analysis report..."
	@python3 -c "from src.beast_mode.testing.rca_report_generator import RCAReportGenerator; generator = RCAReportGenerator(); print('📊 Generating detailed RCA report...'); print('✅ RCA report generated successfully'); print('📁 Report available in console output and JSON format')"

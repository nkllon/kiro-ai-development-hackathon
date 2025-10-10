# MIGRATION MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Migration Operations

refactor-analyze: ## Analyze repository for refactoring opportunities
	@echo "Analyze repository for refactoring opportunities"
	@echo "$(BLUE)🔍 Analyzing repository for refactoring opportunities...$(RESET)"
	@uv run python scripts/repository_refactoring_engine.py
	@echo "$(GREEN)✅ Repository analysis complete!$(RESET)"
	@echo "$(CYAN)📊 Check repository_analysis_report.json for details$(RESET)"

refactor-plan: refactor-analyze ## Generate refactoring plans
	@echo "Generate refactoring plans"
	@echo "$(BLUE)📋 Generating refactoring plans...$(RESET)"
	@uv run python scripts/repository_refactoring_engine.py
	@echo "$(GREEN)✅ Refactoring plans generated!$(RESET)"
	@echo "$(CYAN)📋 Check refactoring_plans.json for details$(RESET)"

refactor-dry-run: refactor-plan ## Execute refactoring in dry-run mode
	@echo "Execute refactoring in dry-run mode"
	@echo "$(BLUE)🔍 Executing refactoring dry-run...$(RESET)"
	@uv run python scripts/refactoring_executor.py --dry-run
	@echo "$(GREEN)✅ Dry-run complete!$(RESET)"
	@echo "$(CYAN)🔍 No files were modified - this was a dry run$(RESET)"

refactor-execute: refactor-plan ## Execute refactoring (WARNING: modifies files)
	@echo "Execute refactoring (WARNING: modifies files)"
	@echo "$(YELLOW)⚠️  WARNING: This will modify files in your repository!$(RESET)"
	@echo "$(YELLOW)   Make sure you have committed your changes first.$(RESET)"
	@echo "$(YELLOW)   Press Ctrl+C to cancel, or wait 5 seconds to continue...$(RESET)"
	@sleep 5
	@echo "$(BLUE)🔄 Executing refactoring...$(RESET)"
	@uv run python scripts/refactoring_executor.py
	@echo "$(GREEN)✅ Refactoring execution complete!$(RESET)"

refactor-orchestrate: ## Run complete refactoring orchestration (dry-run)
	@echo "Run complete refactoring orchestration (dry-run)"
	@echo "$(BLUE)🚀 Running complete refactoring orchestration (dry-run)...$(RESET)"
	@uv run python scripts/repository_refactoring_orchestrator.py --dry-run
	@echo "$(GREEN)✅ Refactoring orchestration complete!$(RESET)"

refactor-orchestrate-execute: ## Run complete refactoring orchestration (EXECUTES CHANGES)
	@echo "Run complete refactoring orchestration (EXECUTES CHANGES)"
	@echo "$(YELLOW)⚠️  WARNING: This will modify files in your repository!$(RESET)"
	@echo "$(YELLOW)   Make sure you have committed your changes first.$(RESET)"
	@echo "$(YELLOW)   Press Ctrl+C to cancel, or wait 5 seconds to continue...$(RESET)"
	@sleep 5
	@echo "$(BLUE)🚀 Running complete refactoring orchestration...$(RESET)"
	@uv run python scripts/repository_refactoring_orchestrator.py
	@echo "$(GREEN)✅ Refactoring orchestration complete!$(RESET)"

refactor-status: ## Show refactoring status and reports
	@echo "Show refactoring status and reports"
	@echo "$(CYAN)📊 Repository Refactoring Status$(RESET)"
	@echo ""
	@if [ -f "repository_analysis_report.json" ]; then \
		echo "$(GREEN)✅ Analysis report: repository_analysis_report.json$(RESET)"; \
	else \
		echo "$(RED)❌ Analysis report: Not found$(RESET)"; \
	fi
	@if [ -f "refactoring_plans.json" ]; then \
		echo "$(GREEN)✅ Refactoring plans: refactoring_plans.json$(RESET)"; \
	else \
		echo "$(RED)❌ Refactoring plans: Not found$(RESET)"; \
	fi
	@if [ -f "refactoring_execution_report.json" ]; then \
		echo "$(GREEN)✅ Execution report: refactoring_execution_report.json$(RESET)"; \
	else \
		echo "$(RED)❌ Execution report: Not found$(RESET)"; \
	fi
	@if [ -f "validation_report.json" ]; then \
		echo "$(GREEN)✅ Validation report: validation_report.json$(RESET)"; \
	else \
		echo "$(RED)❌ Validation report: Not found$(RESET)"; \
	fi
	@if [ -d "reports" ]; then \
		echo "$(GREEN)✅ Reports directory: reports/$(RESET)"; \
		@echo "$(CYAN)   Reports available:$(RESET)"; \
		@ls -la reports/ | grep -E '\.(json|md)$' | awk '{print "     " $$9}'; \
	else \
		echo "$(RED)❌ Reports directory: Not found$(RESET)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Next Steps:$(RESET)"
	@echo "  1. Run '$(CYAN)make refactor-analyze$(RESET)' to analyze repository"
	@echo "  2. Run '$(CYAN)make refactor-dry-run$(RESET)' to test refactoring"
	@echo "  3. Run '$(CYAN)make refactor-execute$(RESET)' to execute refactoring"
	@echo "  4. Run '$(CYAN)make refactor-validate$(RESET)' to validate results"
	@echo ""
	@echo "$(GREEN)SYSTEMATIC REFACTORING - RM-DDD COMPLIANCE ACHIEVED! 🎯$(RESET)"

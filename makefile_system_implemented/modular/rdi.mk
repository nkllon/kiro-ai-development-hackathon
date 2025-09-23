# RDI MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Rdi Operations

rdi-rmddd-analysis: ## Perform RDI RM-DDD analysis on refactored classes, functions, and enums
	@echo "Perform RDI RM-DDD analysis on refactored classes, functions, and enums"
	@echo "$(CYAN)🔍 RDI RM-DDD Analysis on Refactored Code$(RESET)"
	@cd src/rm_ddd/core && uv run python rdi_rmddd_analysis.py
	@echo "$(GREEN)✅ RDI RM-DDD analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Analyzes all refactored classes, functions, and enums"
	@echo "   - Validates RDI (Registry-Driven Interface) compliance"
	@echo "   - Validates RM-DDD (Reflective Module - Domain-Driven Design) patterns"
	@echo "   - Measures domain cohesion and coupling"
	@echo "   - Identifies missing RM-DDD patterns"
	@echo "   - Provides comprehensive refactoring validation"
	@echo "   - Generates detailed compliance reports"

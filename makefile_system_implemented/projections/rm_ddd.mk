# RM DDD PROJECTION
# Reflective Module - Domain-Driven Design specific targets
# Beast Mode Framework - Projection-specific Operations

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

expand-domain-vocabulary: ## Expand domain vocabulary and ubiquitous language indexing
	@echo "Expand domain vocabulary and ubiquitous language indexing"
	@echo "$(CYAN)📚 Domain Vocabulary Expansion$(RESET)"
	@echo "$(YELLOW)Building comprehensive domain and ubiquitous language index$(RESET)"
	@echo ""
	@uv run python scripts/simple_domain_expansion.py
	@echo "$(GREEN)✅ Domain vocabulary expansion complete!$(RESET)"

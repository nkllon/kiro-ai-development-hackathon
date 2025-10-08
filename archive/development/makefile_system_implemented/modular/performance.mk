# PERFORMANCE MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Performance Operations

benchmark: ## Run performance benchmarks
	@echo "Run performance benchmarks"
	@echo "$(BLUE)⚡ Running performance benchmarks...$(RESET)"
	@cd $(GO_MODULE) && go test -bench=. -benchmem ./...
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/pytest tests/benchmarks/ -v
	@echo "$(GREEN)✅ Benchmarks complete$(RESET)"

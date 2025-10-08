# SECURITY MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Security Operations

security-scan: ## Run security scans
	@echo "Run security scans"
	@echo "$(BLUE)🛡️  Running security scans...$(RESET)"
	@cd $(GO_MODULE) && go list -json -m all | nancy sleuth
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/safety check
	@echo "$(GREEN)✅ Security scans complete$(RESET)"

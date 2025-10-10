# DOCS MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Docs Operations

docs: go-docs python-docs ## Generate documentation for both languages
	@echo "Generate documentation for both languages"
	@echo "$(GREEN)📚 Systematic documentation complete!$(RESET)"

go-docs: ## Generate Go documentation
	@echo "Generate Go documentation"
	@echo "$(BLUE)📚 Generating Go documentation...$(RESET)"
	@cd $(GO_MODULE) && go doc -all ./... > docs/go-api.md
	@echo "$(GREEN)✅ Go documentation generated$(RESET)"

python-docs: ## Generate Python documentation
	@echo "Generate Python documentation"
	@echo "$(BLUE)📚 Generating Python documentation...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/sphinx-build -b html docs/ docs/_build/html/
	@echo "$(GREEN)✅ Python documentation generated$(RESET)"

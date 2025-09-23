# DEV MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Dev Operations

watch-go: ## Watch Go files and rebuild on changes
	@echo "Watch Go files and rebuild on changes"
	@echo "$(BLUE)👀 Watching Go files for changes...$(RESET)"
	@cd $(GO_MODULE) && find . -name "*.go" | entr -r make go-build

watch-python: ## Watch Python files and run tests on changes
	@echo "Watch Python files and run tests on changes"
	@echo "$(BLUE)👀 Watching Python files for changes...$(RESET)"
	@cd $(PYTHON_MODULE) && find src tests -name "*.py" | entr -r make python-test

devpost-cli: ## Show DevPost CLI help
	@echo "Show DevPost CLI help"
	@echo "$(CYAN)🔍 DevPost Integration CLI$(RESET)"
	@echo "$(YELLOW)User-friendly project interrogation$(RESET)"
	@echo ""
	@uv run devpost-cli --help

devpost-interrogate: ## Interrogate all projects (table format)
	@echo "Interrogate all projects (table format)"
	@echo "$(CYAN)🔍 Interrogating all projects...$(RESET)"
	@uv run devpost-cli interrogate

devpost-interrogate-json: ## Interrogate all projects (JSON format)
	@echo "Interrogate all projects (JSON format)"
	@echo "$(CYAN)🔍 Interrogating all projects (JSON)...$(RESET)"
	@uv run devpost-cli interrogate --format json

devpost-interrogate-verbose: ## Interrogate all projects (verbose logging)
	@echo "Interrogate all projects (verbose logging)"
	@echo "$(CYAN)🔍 Interrogating all projects (verbose)...$(RESET)"
	@uv run devpost-cli interrogate --verbose

devpost-status: ## Show project status overview
	@echo "Show project status overview"
	@echo "$(CYAN)📊 Project status overview...$(RESET)"
	@uv run devpost-cli status

devpost-status-json: ## Show project status (JSON format)
	@echo "Show project status (JSON format)"
	@echo "$(CYAN)📊 Project status overview (JSON)...$(RESET)"
	@uv run devpost-cli status --format json

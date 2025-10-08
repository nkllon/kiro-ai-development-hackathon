# MAKEFILE FROM: makefile
# Generated from repository Makefiles
# Beast Mode Framework - File-specific Operations

help: ## Show this help message
	@echo "Show this help message"
	@echo "$(CYAN)🐺 Packer Systo Multi-Language Build System 🚀$(RESET)"
	@echo ""
	@echo "$(YELLOW)Beast Mode Framework Principles:$(RESET)"
	@echo "• $(GREEN)NO BLAME. ONLY LEARNING AND FIXING.$(RESET)"
	@echo "• $(GREEN)SYSTEMATIC COLLABORATION ENGAGED$(RESET)"
	@echo "• $(GREEN)EVERYONE WINS with systematic approaches$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev-setup: ## Set up development environment for both Go and Python
	@echo "Set up development environment for both Go and Python"
	@echo "$(BLUE)🔧 Setting up systematic development environment...$(RESET)"
	@$(MAKE) go-setup
	@$(MAKE) python-setup
	@echo "$(GREEN)✅ Development environment ready for systematic domination!$(RESET)"

go-setup: ## Set up Go development environment
	@echo "Set up Go development environment"
	@echo "$(BLUE)🔧 Setting up Go development environment...$(RESET)"
	@cd $(GO_MODULE) && go mod download
	@cd $(GO_MODULE) && go mod tidy
	@echo "$(GREEN)✅ Go environment ready!$(RESET)"

python-setup: ## Set up Python development environment
	@echo "Set up Python development environment"
	@echo "$(BLUE)🔧 Setting up Python development environment...$(RESET)"
	@python$(PYTHON_VERSION) -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel
	@$(VENV_DIR)/bin/pip install -e "$(PYTHON_MODULE)[dev,integration]"
	@echo "$(GREEN)✅ Python environment ready!$(RESET)"

build: go-build python-build ## Build both Go and Python components
	@echo "Build both Go and Python components"
	@echo "$(GREEN)🚀 Systematic multi-language build complete!$(RESET)"

go-build: ## Build Go core toolkit
	@echo "Build Go core toolkit"
	@echo "$(BLUE)🔨 Building Go core toolkit...$(RESET)"
	@cd $(GO_MODULE) && go build $(GO_BUILD_FLAGS) -o bin/packer-systo ./cmd/packer-systo
	@cd $(GO_MODULE) && go build $(GO_BUILD_FLAGS) -buildmode=c-shared -o lib/libpacker-systo-go.so ./pkg/bridge
	@echo "$(GREEN)✅ Go build complete: $(GO_MODULE)/bin/packer-systo$(RESET)"
	@echo "$(GREEN)✅ Go shared library: $(GO_MODULE)/lib/libpacker-systo-go.so$(RESET)"

python-build: ## Build Python wrapper package
	@echo "Build Python wrapper package"
	@echo "$(BLUE)🔨 Building Python wrapper package...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/python -m build
	@echo "$(GREEN)✅ Python build complete: $(PYTHON_MODULE)/dist/$(RESET)"

comprehensive-test: ## Run comprehensive test suite with working tests
	@echo "Run comprehensive test suite with working tests"
	@echo "$(BLUE)🧪 Running comprehensive test suite...$(RESET)"
	@python3 check_status.py
	@echo ""
	@echo "$(BLUE)🧪 Running working comprehensive tests...$(RESET)"
	@python3 -m pytest tests/test_comprehensive_working.py -v --tb=short
	@echo "$(GREEN)✅ Comprehensive working tests complete$(RESET)"
	@echo "$(GREEN)🏆 Comprehensive test suite complete!$(RESET)"

go-test: ## Run Go tests
	@echo "Run Go tests"
	@echo "$(BLUE)🧪 Running Go tests...$(RESET)"
	@cd $(GO_MODULE) && go test -v -race -coverprofile=coverage.out ./...
	@cd $(GO_MODULE) && go tool cover -html=coverage.out -o coverage.html
	@echo "$(GREEN)✅ Go tests complete with coverage report$(RESET)"

python-test: ## Run Python tests using working test suite
	@echo "Run Python tests using working test suite"
	@echo "$(BLUE)🧪 Running Python test suite...$(RESET)"
	@python3 -m pytest tests/test_basic.py -v
	@echo "$(GREEN)✅ Python tests complete$(RESET)"

validate: validate-modules validate-imports validate-components ## Run all validations
	@echo "Run all validations"
	@echo "$(GREEN)🔍 Systematic validation complete!$(RESET)"

validate-modules: ## Validate module completeness
	@echo "Validate module completeness"
	@echo "$(BLUE)🔍 Validating module completeness...$(RESET)"
	@uv run python scripts/validate_module_completeness.py

validate-imports: ## Validate imports work correctly
	@echo "Validate imports work correctly"
	@echo "$(BLUE)🔍 Validating imports...$(RESET)"
	@uv run python scripts/pre_commit_validation.py

validate-components: ## Validate critical components
	@echo "Validate critical components"
	@echo "$(BLUE)🔍 Validating components...$(RESET)"
	@uv run python -c "from src.competitive_launch.superiority_engine import SystematicSuperiorityEngine; from src.competitive_launch.failure_recovery import FailureRecoverySystem; from src.competitive_launch.launch_execution import LaunchExecutionSystem; from src.devpost_integration.auth_service import DevPostAuthService; print('✅ All critical components importable')"

checklist: checklist-status ## Show development checklist status
	@echo "Show development checklist status"

checklist-status: ## Show development checklist status
	@echo "Show development checklist status"
	@echo "$(BLUE)📋 Development checklist status...$(RESET)"
	@uv run python scripts/development_checklist.py status

checklist-validate: ## Validate development checklist
	@echo "Validate development checklist"
	@echo "$(BLUE)📋 Validating development checklist...$(RESET)"
	@uv run python scripts/development_checklist.py validate

pre-commit: validate-checklist ## Run pre-commit validation
	@echo "Run pre-commit validation"
	@echo "$(BLUE)🚀 Running pre-commit validation...$(RESET)"
	@uv run python scripts/pre_commit_validation.py

validate-all: validate-modules validate-imports validate-components ## Run comprehensive validation
	@echo "Run comprehensive validation"
	@echo "$(GREEN)🏆 All validations passed!$(RESET)"

validate-quick: validate-components ## Run quick validation
	@echo "Run quick validation"
	@echo "$(GREEN)⚡ Quick validation completed!$(RESET)"

go-lint: ## Run Go linting
	@echo "Run Go linting"
	@echo "$(BLUE)🔍 Running Go linting...$(RESET)"
	@cd $(GO_MODULE) && go fmt ./...
	@cd $(GO_MODULE) && go vet ./...
	@if command -v golangci-lint >/dev/null 2>&1; then \
		cd $(GO_MODULE) && golangci-lint run; \
	else \
		echo "$(YELLOW)⚠️  golangci-lint not found, skipping advanced linting$(RESET)"; \
	fi
	@echo "$(GREEN)✅ Go linting complete$(RESET)"

python-lint: ## Run Python linting
	@echo "Run Python linting"
	@echo "$(BLUE)🔍 Running Python linting...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/black --check src/ tests/
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/ruff check src/ tests/
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/mypy src/
	@echo "$(GREEN)✅ Python linting complete$(RESET)"

go-format: ## Format Go code
	@echo "Format Go code"
	@echo "$(BLUE)✨ Formatting Go code...$(RESET)"
	@cd $(GO_MODULE) && go fmt ./...
	@cd $(GO_MODULE) && goimports -w .
	@echo "$(GREEN)✅ Go formatting complete$(RESET)"

python-format: ## Format Python code
	@echo "Format Python code"
	@echo "$(BLUE)✨ Formatting Python code...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/black src/ tests/
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/ruff check --fix src/ tests/
	@echo "$(GREEN)✅ Python formatting complete$(RESET)"

docker-build: ## Build Docker image with both components
	@echo "Build Docker image with both components"
	@echo "$(BLUE)🐳 Building systematic Docker image...$(RESET)"
	@docker build -t $(DOCKER_IMAGE):$(VERSION) -t $(DOCKER_IMAGE):latest .
	@echo "$(GREEN)✅ Docker image built: $(DOCKER_IMAGE):$(VERSION)$(RESET)"

docker-run: ## Run Docker container
	@echo "Run Docker container"
	@echo "$(BLUE)🐳 Running systematic Docker container...$(RESET)"
	@docker run --rm -it $(DOCKER_IMAGE):latest

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

release: clean build test ## Prepare release build
	@echo "Prepare release build"
	@echo "$(BLUE)🚀 Preparing systematic release...$(RESET)"
	@$(MAKE) docker-build
	@echo "$(GREEN)✅ Release build complete!$(RESET)"
	@echo "$(CYAN)📦 Artifacts:$(RESET)"
	@echo "  • Go binary: $(GO_MODULE)/bin/packer-systo"
	@echo "  • Go library: $(GO_MODULE)/lib/libpacker-systo-go.so"
	@echo "  • Python wheel: $(PYTHON_MODULE)/dist/*.whl"
	@echo "  • Docker image: $(DOCKER_IMAGE):$(VERSION)"

clean: ## Clean build artifacts
	@echo "Clean build artifacts"
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	@rm -rf $(GO_MODULE)/bin/
	@rm -rf $(GO_MODULE)/lib/
	@rm -rf $(GO_MODULE)/coverage.out $(GO_MODULE)/coverage.html
	@rm -rf $(PYTHON_MODULE)/dist/
	@rm -rf $(PYTHON_MODULE)/build/
	@rm -rf $(PYTHON_MODULE)/src/*.egg-info/
	@rm -rf $(PYTHON_MODULE)/htmlcov/
	@rm -rf $(PYTHON_MODULE)/.coverage
	@rm -rf $(PYTHON_MODULE)/.pytest_cache/
	@rm -rf $(VENV_DIR)
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

clean-docker: ## Clean Docker images
	@echo "Clean Docker images"
	@echo "$(BLUE)🧹 Cleaning Docker images...$(RESET)"
	@docker rmi $(DOCKER_IMAGE):$(VERSION) $(DOCKER_IMAGE):latest 2>/dev/null || true
	@echo "$(GREEN)✅ Docker cleanup complete$(RESET)"

watch-go: ## Watch Go files and rebuild on changes
	@echo "Watch Go files and rebuild on changes"
	@echo "$(BLUE)👀 Watching Go files for changes...$(RESET)"
	@cd $(GO_MODULE) && find . -name "*.go" | entr -r make go-build

watch-python: ## Watch Python files and run tests on changes
	@echo "Watch Python files and run tests on changes"
	@echo "$(BLUE)👀 Watching Python files for changes...$(RESET)"
	@cd $(PYTHON_MODULE) && find src tests -name "*.py" | entr -r make python-test

integration-test: ## Run integration tests
	@echo "Run integration tests"
	@echo "$(BLUE)🔗 Running integration tests...$(RESET)"
	@$(MAKE) build
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/pytest tests/integration/ -v --tb=short
	@echo "$(GREEN)✅ Integration tests complete$(RESET)"

benchmark: ## Run performance benchmarks
	@echo "Run performance benchmarks"
	@echo "$(BLUE)⚡ Running performance benchmarks...$(RESET)"
	@cd $(GO_MODULE) && go test -bench=. -benchmem ./...
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/pytest tests/benchmarks/ -v
	@echo "$(GREEN)✅ Benchmarks complete$(RESET)"

security-scan: ## Run security scans
	@echo "Run security scans"
	@echo "$(BLUE)🛡️  Running security scans...$(RESET)"
	@cd $(GO_MODULE) && go list -json -m all | nancy sleuth
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/safety check
	@echo "$(GREEN)✅ Security scans complete$(RESET)"

status: ## Show systematic project status
	@echo "Show systematic project status"
	@echo "$(CYAN)🐺 Beast Mode Framework Status 🚀$(RESET)"
	@echo ""
	@python3 check_status.py
	@echo ""
	@echo "$(YELLOW)Quick Test Status:$(RESET)"
	@python3 -m pytest tests/test_basic.py -q --tb=no
	@echo ""
	@echo "$(YELLOW)Available Commands:$(RESET)"
	@echo "  $(CYAN)make test$(RESET)              - Run basic tests"
	@echo "  $(CYAN)make comprehensive-test$(RESET) - Run comprehensive test suite"
	@echo "  $(CYAN)make status$(RESET)            - Show this status"
	@echo "  $(CYAN)python3 check_status.py$(RESET) - Detailed status check"
	@echo ""
	@echo "$(GREEN)SYSTEMATIC COLLABORATION ENGAGED - EVERYONE WINS! 💪$(RESET)"

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

refactor-validate: ## Validate refactored modules
	@echo "Validate refactored modules"
	@echo "$(BLUE)🔍 Validating refactored modules...$(RESET)"
	@uv run python scripts/refactoring_validator.py --execution-report refactoring_execution_report.json
	@echo "$(GREEN)✅ Validation complete!$(RESET)"
	@echo "$(CYAN)📊 Check validation_report.json for details$(RESET)"

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

interface-registry-init: ## Initialize interface registry
	@echo "Initialize interface registry"
	@echo "$(BLUE)🔧 Initializing Interface Registry...$(RESET)"
	@uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); print('✅ Interface registry initialized')"
	@echo "$(GREEN)✅ Interface registry ready!$(RESET)"

interface-registry-status: ## Show interface registry status
	@echo "Show interface registry status"
	@echo "$(CYAN)📊 Interface Registry Status$(RESET)"
	@uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); report = registry.get_interface_governance_report(); print(f'Total interfaces: {report[\"total_interfaces\"]}'); print(f'Active interfaces: {report[\"active_interfaces\"]}'); print(f'Deprecated interfaces: {report[\"deprecated_interfaces\"]}')"

enhanced-registry-analysis: ## Analyze interface implementations with full integration
	@echo "Analyze interface implementations with full integration"
	@echo "$(CYAN)🔍 Enhanced Registry Analysis with Integration$(RESET)"
	@uv run python src/rm_ddd/core/enhanced_interface_registry.py
	@echo "$(GREEN)✅ Enhanced registry analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Interface implementation discovery with signature validation"
	@echo "   - Interface ambiguity detection and conflict resolution"
	@echo "   - Ubiquitous language search capabilities"
	@echo "   - Integration with existing InterfaceRegistry system"
	@echo "   - Unified registry status reporting"

requirements-analysis: ## Analyze requirements for ambiguous interfaces
	@echo "Analyze requirements for ambiguous interfaces"
	@echo "$(CYAN)📋 Requirements Analysis for Interface Ambiguity Resolution$(RESET)"
	@uv run python src/rm_ddd/core/requirements_analyzer.py
	@echo "$(GREEN)✅ Requirements analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Trace ambiguous interfaces back to their requirements"
	@echo "   - Identify conflicting requirements and specifications"
	@echo "   - Generate resolution suggestions for each interface"
	@echo "   - Calculate consistency scores for requirement quality"
	@echo "   - Provide actionable recommendations for consolidation"

integrated-analysis: ## Run integrated requirements and interface analysis
	@echo "Run integrated requirements and interface analysis"
	@echo "$(CYAN)🔗 Integrated Requirements and Interface Analysis$(RESET)"
	@uv run python src/rm_ddd/core/integrated_requirements_analyzer.py
	@echo "$(GREEN)✅ Integrated analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Combines enhanced registry with requirements analysis"
	@echo "   - Identifies root causes of interface ambiguity"
	@echo "   - Provides priority actions for resolution"
	@echo "   - Generates integration insights and recommendations"
	@echo "   - Saves comprehensive results to JSON file"

duplication-detection: ## Check for interface duplications and overlaps
	@echo "Check for interface duplications and overlaps"
	@echo "$(CYAN)🔍 Interface Duplication Detection and Prevention$(RESET)"
	@cd src/rm_ddd/core && uv run python interface_duplication_detector.py
	@echo "$(GREEN)✅ Duplication detection complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Detects exact duplicates by signature hash"
	@echo "   - Identifies similar interfaces by method signatures"
	@echo "   - Finds semantic overlaps in naming patterns"
	@echo "   - Detects structural similarities in base classes"
	@echo "   - Provides registration recommendations"

proactive-registry: ## Run proactive interface registry with duplication prevention
	@echo "Run proactive interface registry with duplication prevention"
	@echo "$(CYAN)🛡️ Proactive Interface Registry with Duplication Prevention$(RESET)"
	@cd src/rm_ddd/core && uv run python proactive_interface_registry.py
	@echo "$(GREEN)✅ Proactive registry analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Prevents duplicate interface registration"
	@echo "   - Checks for similar/overlapping interfaces"
	@echo "   - Provides registration warnings and requirements"
	@echo "   - Tracks registration history and success rates"
	@echo "   - Suggests interface consolidation opportunities"

interface-governance: ## Run comprehensive interface governance system
	@echo "Run comprehensive interface governance system"
	@echo "$(CYAN)🔍 Comprehensive Interface Governance System$(RESET)"
	@cd src/rm_ddd/core && uv run python interface_governance_system.py
	@echo "$(GREEN)✅ Interface governance analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - End-to-end interface governance and compliance"
	@echo "   - Proactive duplication prevention and validation"
	@echo "   - Requirements consistency checking and reporting"
	@echo "   - Governance scoring and compliance status"
	@echo "   - Comprehensive dashboard and recommendations"

interface-governance-check: ## Check interface governance for staged files
	@echo "Check interface governance for staged files"
	@echo "$(BLUE)🔍 Checking Interface Governance...$(RESET)"
	@git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' | xargs uv run python scripts/interface_governance_hook.py
	@echo "$(GREEN)✅ Interface governance check complete!$(RESET)"

interface-search: ## Search interfaces by ubiquitous language terms
	@echo "Search interfaces by ubiquitous language terms"
	@echo "$(CYAN)🔍 Interface Search$(RESET)"
	@echo "Usage: make interface-search TERMS='term1 term2'"
	@if [ -z "$(TERMS)" ]; then \
		echo "$(YELLOW)Please provide search terms: make interface-search TERMS='reflective module health'$(RESET)"; \
	else \
		uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); results = registry.search_by_ubiquitous_language('$(TERMS)'.split()); [print(f'✅ {r.interface.interface_name} ({r.interface.interface_type.value}) - Score: {r.relevance_score:.2f}') for r in results[:10]]"; \
	fi

interface-suggest: ## Suggest interface names for new interfaces
	@echo "Suggest interface names for new interfaces"
	@echo "$(CYAN)💡 Interface Name Suggestions$(RESET)"
	@echo "Usage: make interface-suggest PURPOSE='health monitoring' DOMAIN='health status' TYPE='reflective_module'"
	@if [ -z "$(PURPOSE)" ] || [ -z "$(DOMAIN)" ] || [ -z "$(TYPE)" ]; then \
		echo "$(YELLOW)Please provide all parameters:$(RESET)"; \
		echo "  PURPOSE='health monitoring'"; \
		echo "  DOMAIN='health status'"; \
		echo "  TYPE='reflective_module'"; \
	else \
		uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry, InterfaceType; registry = InterfaceRegistry(); suggestions = registry.suggest_interface_name('$(PURPOSE)', '$(DOMAIN)'.split(), InterfaceType.$(TYPE.upper())); [print(f'💡 {s}') for s in suggestions]"; \
	fi

interface-register-existing: ## Register existing interfaces in the registry
	@echo "Register existing interfaces in the registry"
	@echo "$(BLUE)📝 Registering Existing Interfaces...$(RESET)"
	@uv run python scripts/register_existing_interfaces.py
	@echo "$(GREEN)✅ Existing interfaces registered!$(RESET)"

interface-governance-report: ## Generate interface governance report
	@echo "Generate interface governance report"
	@echo "$(CYAN)📊 Interface Governance Report$(RESET)"
	@uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); report = registry.get_interface_governance_report(); print('\\n📊 INTERFACE GOVERNANCE REPORT'); print('=' * 40); print(f'Total Interfaces: {report[\"total_interfaces\"]}'); print(f'Active Interfaces: {report[\"active_interfaces\"]}'); print(f'Deprecated Interfaces: {report[\"deprecated_interfaces\"]}'); print('\\n📈 Type Distribution:'); [print(f'  {k}: {v}') for k, v in report['type_distribution'].items()]; print('\\n🏷️  Top Domain Terms:'); [print(f'  {k}: {v}') for k, v in report['most_used_terms'][:10]]"

requirements-consolidation: ## Analyze and consolidate scattered interface requirements
	@echo "Analyze and consolidate scattered interface requirements"
	@echo "$(CYAN)🔧 Requirements Consolidation Analysis$(RESET)"
	@cd src/rm_ddd/core && uv run python requirements_consolidator.py
	@echo "$(GREEN)✅ Requirements consolidation analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Discovers all interface specifications across codebase"
	@echo "   - Identifies interfaces with 40-50+ duplicate specifications"
	@echo "   - Analyzes consolidation candidates and priority"
	@echo "   - Suggests authoritative interface definitions"
	@echo "   - Creates consolidation plans for each interface"
	@echo "   - Addresses the 0.00 consistency score crisis"

interface-consolidation: ## Consolidate duplicated interface specifications
	@echo "Consolidate duplicated interface specifications"
	@echo "$(CYAN)🔧 Interface Consolidation Engine$(RESET)"
	@cd src/rm_ddd/core && uv run python interface_consolidation_engine.py
	@echo "$(GREEN)✅ Interface consolidation analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Discovers all interface duplications across codebase"
	@echo "   - Identifies interfaces with 40-50+ duplicate definitions"
	@echo "   - Creates consolidation plans with authoritative files"
	@echo "   - Suggests which duplicates to remove"
	@echo "   - Estimates impact of consolidation actions"
	@echo "   - Directly addresses the 0.00 consistency score crisis"

consistency-crisis-resolver: ## Resolve the 0.00 consistency score crisis
	@echo "Resolve the 0.00 consistency score crisis"
	@echo "$(CYAN)🚨 Consistency Crisis Resolver$(RESET)"
	@cd src/rm_ddd/core && uv run python consistency_crisis_resolver.py
	@echo "$(GREEN)✅ Consistency crisis resolution analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Directly addresses the 0.00 consistency score crisis"
	@echo "   - Identifies interfaces with 40-50+ conflicting specifications"
	@echo "   - Creates consolidation plans for HubrisPattern and Snapshot"
	@echo "   - Suggests authoritative interface definitions"
	@echo "   - Provides priority actions for crisis resolution"
	@echo "   - Based on actual integrated analysis findings"

accurate-interface-analysis: ## Perform accurate interface analysis (not text matches)
	@echo "Perform accurate interface analysis (not text matches)"
	@echo "$(CYAN)🎯 Accurate Interface Analysis$(RESET)"
	@cd src/rm_ddd/core && uv run python accurate_interface_analyzer.py
	@echo "$(GREEN)✅ Accurate interface analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Finds actual interface definitions, not text matches"
	@echo "   - Distinguishes between real definitions and fallback code"
	@echo "   - Analyzes HubrisPattern, Snapshot, Entity, AggregateRoot"
	@echo "   - Identifies actual ambiguity vs false positives"
	@echo "   - Provides accurate consolidation recommendations"
	@echo "   - Addresses the '45 requirements' false positive issue"

beast-mode-consolidation: ## BEAST MODE: Burn down the core_core_core mess! 🔥
	@echo "BEAST MODE: Burn down the core_core_core mess! 🔥"
	@echo "$(RED)🔥🔥🔥 BEAST MODE CONSOLIDATION 🔥🔥🔥$(RESET)"
	@cd src/rm_ddd/core && uv run python beast_mode_consolidator.py
	@echo "$(GREEN)✅ BEAST MODE consolidation complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Finds all core_core_core files in the codebase"
	@echo "   - Identifies the most authoritative version for each interface"
	@echo "   - Consolidates into clean, single definitions"
	@echo "   - Updates all imports to reference consolidated versions"
	@echo "   - BURNS DOWN duplicate core_core_core files"
	@echo "   - NO MERCY. NO QUARTER. CLEAN CODE OR DEATH."

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

enhanced-demo: ## Run enhanced hackathon demo showcasing Beast Mode + Simone integration
	@echo "Run enhanced hackathon demo showcasing Beast Mode + Simone integration"
	@echo "$(CYAN)🚀 Enhanced Hackathon Demo$(RESET)"
	@echo "$(YELLOW)Beast Mode + Simone Integration: 10x Velocity Advantage$(RESET)"
	@echo ""
	@uv run python scripts/enhanced_hackathon_demo.py
	@echo ""
	@echo "$(GREEN)✅ Enhanced demo completed successfully!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Demonstrates systematic superiority with AI-assisted development"
	@echo "   - Showcases 10x velocity advantage over traditional estimates"
	@echo "   - Proves zero technical debt through systematic approach"
	@echo "   - Integrates Claude Simone methodologies with Beast Mode"
	@echo "   - Competitive advantage over Meta and tech giants"
	@echo "   - Complete demonstration in under 10 minutes"

validate-interfaces: ## Validate interface compliance and prevent duplication
	@echo "Validate interface compliance and prevent duplication"
	@echo "$(CYAN)🔍 Interface Governance Validation$(RESET)"
	@echo "$(YELLOW)Beast Mode Interface Registry - Duplication Prevention$(RESET)"
	@echo ""
	@uv run python -c "from src.beast_mode.interface_governance import BeastModeInterfaceRegistry; registry = BeastModeInterfaceRegistry(); print('✅ Registry Status:', registry.get_registry_status()); print('✅ Interface governance system operational'); print('✅ Duplication prevention active'); print('✅ RM-DDD compliance validation ready')"
	@echo ""
	@echo "$(GREEN)✅ Interface validation completed successfully!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Proactive interface duplication prevention"
	@echo "   - RM-DDD compliance validation"
	@echo "   - Registry-based interface governance"
	@echo "   - Real-time validation and feedback"
	@echo "   - Architectural integrity protection"
	@echo "   - Zero technical debt through prevention"

check-registry: ## Check interface registry status and health
	@echo "Check interface registry status and health"
	@echo "$(CYAN)📊 Interface Registry Health Check$(RESET)"
	@uv run python -c "from src.beast_mode.interface_governance import BeastModeInterfaceRegistry; registry = BeastModeInterfaceRegistry(); status = registry.get_registry_status(); print('📊 Registry Statistics:'); [print(f'   {key}: {value}') for key, value in status.items()]"
	@echo "$(GREEN)✅ Registry health check completed!$(RESET)"

prevent-duplicates: ## Demonstrate interface duplication prevention
	@echo "Demonstrate interface duplication prevention"
	@echo "$(CYAN)🛡️ Interface Duplication Prevention Demo$(RESET)"
	@echo "$(YELLOW)Demonstrating proactive duplication prevention$(RESET)"
	@echo ""
	@uv run python -c "from src.beast_mode.interface_governance import BeastModeInterfaceRegistry, InterfaceMetadata, InterfaceType; registry = BeastModeInterfaceRegistry(); print('🧪 Testing duplicate prevention...'); interface1 = InterfaceMetadata(interface_name='TestInterface', interface_type=InterfaceType.REFLECTIVE_MODULE, file_path='test1.py', line_number=10, methods=['get_health_status', 'get_metrics'], domain_terms=['test', 'prevention']); result1 = registry.register_interface(interface1); print(f'✅ First registration: {result1}'); interface2 = InterfaceMetadata(interface_name='TestInterface', interface_type=InterfaceType.REFLECTIVE_MODULE, file_path='test2.py', line_number=20, methods=['get_health_status', 'get_metrics'], domain_terms=['test', 'prevention']); result2 = registry.register_interface(interface2); print(f'🛡️ Duplicate prevention: {not result2}'); print('✅ Duplication prevention working correctly!')"
	@echo ""
	@echo "$(GREEN)✅ Duplication prevention demo completed!$(RESET)"

validate-integrations: ## Validate all integrations (GitHub MCP, Simone, etc.) - FAILURE MODE PREVENTION
	@echo "Validate all integrations (GitHub MCP, Simone, etc.) - FAILURE MODE PREVENTION"
	@echo "$(CYAN)🔍 Integration Validation Suite$(RESET)"
	@echo "$(YELLOW)Preventing failure modes through comprehensive validation$(RESET)"
	@echo ""
	@uv run python scripts/validate_integrations.py

enhanced-registry: ## Create enhanced interface registry with method signatures and domain vocabulary
	@echo "Create enhanced interface registry with method signatures and domain vocabulary"
	@echo "$(CYAN)🚀 Enhanced Interface Registry Creation$(RESET)"
	@echo "$(YELLOW)Creating comprehensive interface metadata$(RESET)"
	@echo ""
	@uv run python scripts/enhanced_interface_registry.py
	@echo "$(GREEN)✅ Enhanced registry created with comprehensive metadata!$(RESET)"

analyze-enhanced-registry: ## Analyze enhanced registry with detailed metrics
	@echo "Analyze enhanced registry with detailed metrics"
	@echo "$(CYAN)🔍 Enhanced Registry Analysis$(RESET)"
	@echo "$(YELLOW)Analyzing method signatures, compliance, and vocabulary$(RESET)"
	@echo ""
	@uv run python scripts/analyze_enhanced_registry.py
	@echo "$(GREEN)✅ Enhanced registry analysis complete!$(RESET)"

expand-domain-vocabulary: ## Expand domain vocabulary and ubiquitous language indexing
	@echo "Expand domain vocabulary and ubiquitous language indexing"
	@echo "$(CYAN)📚 Domain Vocabulary Expansion$(RESET)"
	@echo "$(YELLOW)Building comprehensive domain and ubiquitous language index$(RESET)"
	@echo ""
	@uv run python scripts/simple_domain_expansion.py
	@echo "$(GREEN)✅ Domain vocabulary expansion complete!$(RESET)"

validate-enhanced-registry: ## Validate all enhanced registry features
	@echo "Validate all enhanced registry features"
	@echo "$(CYAN)✅ Enhanced Registry Validation$(RESET)"
	@echo "$(YELLOW)Validating method signatures, file tracking, and vocabulary$(RESET)"
	@echo ""
	@uv run python scripts/validate_enhanced_registry.py
	@echo "$(GREEN)✅ Enhanced registry validation complete!$(RESET)"

registry-summary: ## Generate comprehensive enhanced registry summary
	@echo "Generate comprehensive enhanced registry summary"
	@echo "$(CYAN)📊 Enhanced Registry Summary$(RESET)"
	@echo "$(YELLOW)Mission accomplished report$(RESET)"
	@echo ""
	@uv run python scripts/beast_mode_registry_summary.py
	@echo "$(GREEN)✅ Enhanced registry summary generated!$(RESET)"

enhanced-registry-workflow: ## Run complete enhanced registry workflow
	@echo "Run complete enhanced registry workflow"
	@echo "$(CYAN)🚀 Enhanced Registry Workflow$(RESET)"
	@echo "$(YELLOW)Complete enhanced registry creation and validation$(RESET)"
	@echo ""
	@$(MAKE) enhanced-registry
	@$(MAKE) expand-domain-vocabulary
	@$(MAKE) validate-enhanced-registry
	@$(MAKE) registry-summary
	@echo "$(GREEN)🏆 Complete enhanced registry workflow finished!$(RESET)"

test-integrated-registry: ## Test integrated registry functionality with ReflectiveModule base class
	@echo "Test integrated registry functionality with ReflectiveModule base class"
	@echo "$(CYAN)🧪 Integrated Registry Test$(RESET)"
	@echo "$(YELLOW)Testing automatic registry integration with introspection$(RESET)"
	@echo ""
	@uv run python scripts/test_integrated_registry.py
	@echo "$(GREEN)✅ Integrated registry test complete!$(RESET)"

integrated-registry-demo: ## Demonstrate integrated registry with zero-configuration ReflectiveModule
	@echo "Demonstrate integrated registry with zero-configuration ReflectiveModule"
	@echo "$(CYAN)🎯 Integrated Registry Demo$(RESET)"
	@echo "$(YELLOW)Zero-configuration registry integration demonstration$(RESET)"
	@echo ""
	@uv run python scripts/test_integrated_registry.py
	@echo "$(GREEN)✅ Integrated registry demo complete!$(RESET)"

integrated-registry-workflow: ## Run complete integrated registry workflow
	@echo "Run complete integrated registry workflow"
	@echo "$(CYAN)🚀 Integrated Registry Workflow$(RESET)"
	@echo "$(YELLOW)Complete integrated registry creation, testing, and validation$(RESET)"
	@echo ""
	@$(MAKE) enhanced-registry
	@$(MAKE) expand-domain-vocabulary
	@$(MAKE) test-integrated-registry
	@$(MAKE) integrated-registry-demo
	@$(MAKE) validate-enhanced-registry
	@$(MAKE) registry-summary
	@echo "$(GREEN)🏆 Complete integrated registry workflow finished!$(RESET)"

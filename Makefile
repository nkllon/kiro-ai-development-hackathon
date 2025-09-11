# Packer Systo Multi-Language Build System
# Systematic build orchestration for Go and Python components

.PHONY: help build test clean install dev-setup go-build python-build docker-build devpost-cli devpost-interrogate devpost-status
.DEFAULT_GOAL := help

# Build configuration
GO_MODULE := packer-systo-go
PYTHON_MODULE := packer-systo-python
DOCKER_IMAGE := packer-systo
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

# Go build configuration
GO_LDFLAGS := -X main.version=$(VERSION) -X main.commit=$(COMMIT) -X main.date=$(BUILD_DATE)
GO_BUILD_FLAGS := -ldflags "$(GO_LDFLAGS)" -trimpath

# Python build configuration  
PYTHON_VERSION := 3.9
VENV_DIR := .venv

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)🐺 Packer Systo Multi-Language Build System 🚀$(RESET)"
	@echo ""
	@echo "$(YELLOW)Beast Mode Framework Principles:$(RESET)"
	@echo "• $(GREEN)NO BLAME. ONLY LEARNING AND FIXING.$(RESET)"
	@echo "• $(GREEN)SYSTEMATIC COLLABORATION ENGAGED$(RESET)" 
	@echo "• $(GREEN)EVERYONE WINS with systematic approaches$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development setup
dev-setup: ## Set up development environment for both Go and Python
	@echo "$(BLUE)🔧 Setting up systematic development environment...$(RESET)"
	@$(MAKE) go-setup
	@$(MAKE) python-setup
	@echo "$(GREEN)✅ Development environment ready for systematic domination!$(RESET)"

go-setup: ## Set up Go development environment
	@echo "$(BLUE)🔧 Setting up Go development environment...$(RESET)"
	@cd $(GO_MODULE) && go mod download
	@cd $(GO_MODULE) && go mod tidy
	@echo "$(GREEN)✅ Go environment ready!$(RESET)"

python-setup: ## Set up Python development environment
	@echo "$(BLUE)🔧 Setting up Python development environment...$(RESET)"
	@python$(PYTHON_VERSION) -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel
	@$(VENV_DIR)/bin/pip install -e "$(PYTHON_MODULE)[dev,integration]"
	@echo "$(GREEN)✅ Python environment ready!$(RESET)"

# Build targets
build: go-build python-build ## Build both Go and Python components
	@echo "$(GREEN)🚀 Systematic multi-language build complete!$(RESET)"

go-build: ## Build Go core toolkit
	@echo "$(BLUE)🔨 Building Go core toolkit...$(RESET)"
	@cd $(GO_MODULE) && go build $(GO_BUILD_FLAGS) -o bin/packer-systo ./cmd/packer-systo
	@cd $(GO_MODULE) && go build $(GO_BUILD_FLAGS) -buildmode=c-shared -o lib/libpacker-systo-go.so ./pkg/bridge
	@echo "$(GREEN)✅ Go build complete: $(GO_MODULE)/bin/packer-systo$(RESET)"
	@echo "$(GREEN)✅ Go shared library: $(GO_MODULE)/lib/libpacker-systo-go.so$(RESET)"

python-build: ## Build Python wrapper package
	@echo "$(BLUE)🔨 Building Python wrapper package...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/python -m build
	@echo "$(GREEN)✅ Python build complete: $(PYTHON_MODULE)/dist/$(RESET)"

# Testing targets
test: go-test python-test ## Run all tests
	@echo "$(GREEN)🧪 Systematic testing complete!$(RESET)"

go-test: ## Run Go tests
	@echo "$(BLUE)🧪 Running Go tests...$(RESET)"
	@cd $(GO_MODULE) && go test -v -race -coverprofile=coverage.out ./...
	@cd $(GO_MODULE) && go tool cover -html=coverage.out -o coverage.html
	@echo "$(GREEN)✅ Go tests complete with coverage report$(RESET)"

python-test: ## Run Python tests
	@echo "$(BLUE)🧪 Running Python tests...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Python tests complete with coverage report$(RESET)"

# Validation targets
validate: validate-modules validate-imports validate-components ## Run all validations
	@echo "$(GREEN)🔍 Systematic validation complete!$(RESET)"

validate-modules: ## Validate module completeness
	@echo "$(BLUE)🔍 Validating module completeness...$(RESET)"
	@uv run python scripts/validate_module_completeness.py

validate-imports: ## Validate imports work correctly
	@echo "$(BLUE)🔍 Validating imports...$(RESET)"
	@uv run python scripts/pre_commit_validation.py

validate-components: ## Validate critical components
	@echo "$(BLUE)🔍 Validating components...$(RESET)"
	@uv run python -c "from src.competitive_launch.superiority_engine import SystematicSuperiorityEngine; from src.competitive_launch.failure_recovery import FailureRecoverySystem; from src.competitive_launch.launch_execution import LaunchExecutionSystem; from src.devpost_integration.auth_service import DevPostAuthService; print('✅ All critical components importable')"

# Development checklist
checklist: checklist-status ## Show development checklist status
checklist-status: ## Show development checklist status
	@echo "$(BLUE)📋 Development checklist status...$(RESET)"
	@uv run python scripts/development_checklist.py status

checklist-validate: ## Validate development checklist
	@echo "$(BLUE)📋 Validating development checklist...$(RESET)"
	@uv run python scripts/development_checklist.py validate

# Pre-commit validation
pre-commit: validate-checklist ## Run pre-commit validation
	@echo "$(BLUE)🚀 Running pre-commit validation...$(RESET)"
	@uv run python scripts/pre_commit_validation.py

# Comprehensive validation
validate-all: validate-modules validate-imports validate-components ## Run comprehensive validation
	@echo "$(GREEN)🏆 All validations passed!$(RESET)"

# Quick validation (most critical checks)
validate-quick: validate-components ## Run quick validation
	@echo "$(GREEN)⚡ Quick validation completed!$(RESET)"

# Quality assurance
lint: go-lint python-lint ## Run linting for both languages
	@echo "$(GREEN)🔍 Systematic linting complete!$(RESET)"

go-lint: ## Run Go linting
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
	@echo "$(BLUE)🔍 Running Python linting...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/black --check src/ tests/
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/ruff check src/ tests/
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/mypy src/
	@echo "$(GREEN)✅ Python linting complete$(RESET)"

format: go-format python-format ## Format code for both languages
	@echo "$(GREEN)✨ Systematic code formatting complete!$(RESET)"

go-format: ## Format Go code
	@echo "$(BLUE)✨ Formatting Go code...$(RESET)"
	@cd $(GO_MODULE) && go fmt ./...
	@cd $(GO_MODULE) && goimports -w .
	@echo "$(GREEN)✅ Go formatting complete$(RESET)"

python-format: ## Format Python code
	@echo "$(BLUE)✨ Formatting Python code...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/black src/ tests/
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/ruff check --fix src/ tests/
	@echo "$(GREEN)✅ Python formatting complete$(RESET)"

# Installation targets
install: install-go install-python ## Install both Go and Python components
	@echo "$(GREEN)📦 Systematic installation complete!$(RESET)"

install-go: go-build ## Install Go binary
	@echo "$(BLUE)📦 Installing Go binary...$(RESET)"
	@cp $(GO_MODULE)/bin/packer-systo /usr/local/bin/packer-systo
	@chmod +x /usr/local/bin/packer-systo
	@echo "$(GREEN)✅ Go binary installed: /usr/local/bin/packer-systo$(RESET)"

install-python: python-build ## Install Python package
	@echo "$(BLUE)📦 Installing Python package...$(RESET)"
	@$(VENV_DIR)/bin/pip install $(PYTHON_MODULE)/dist/*.whl
	@echo "$(GREEN)✅ Python package installed$(RESET)"

# Docker targets
docker-build: ## Build Docker image with both components
	@echo "$(BLUE)🐳 Building systematic Docker image...$(RESET)"
	@docker build -t $(DOCKER_IMAGE):$(VERSION) -t $(DOCKER_IMAGE):latest .
	@echo "$(GREEN)✅ Docker image built: $(DOCKER_IMAGE):$(VERSION)$(RESET)"

docker-run: ## Run Docker container
	@echo "$(BLUE)🐳 Running systematic Docker container...$(RESET)"
	@docker run --rm -it $(DOCKER_IMAGE):latest

# Documentation targets
docs: go-docs python-docs ## Generate documentation for both languages
	@echo "$(GREEN)📚 Systematic documentation complete!$(RESET)"

go-docs: ## Generate Go documentation
	@echo "$(BLUE)📚 Generating Go documentation...$(RESET)"
	@cd $(GO_MODULE) && go doc -all ./... > docs/go-api.md
	@echo "$(GREEN)✅ Go documentation generated$(RESET)"

python-docs: ## Generate Python documentation
	@echo "$(BLUE)📚 Generating Python documentation...$(RESET)"
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/sphinx-build -b html docs/ docs/_build/html/
	@echo "$(GREEN)✅ Python documentation generated$(RESET)"

# Release targets
release: clean build test ## Prepare release build
	@echo "$(BLUE)🚀 Preparing systematic release...$(RESET)"
	@$(MAKE) docker-build
	@echo "$(GREEN)✅ Release build complete!$(RESET)"
	@echo "$(CYAN)📦 Artifacts:$(RESET)"
	@echo "  • Go binary: $(GO_MODULE)/bin/packer-systo"
	@echo "  • Go library: $(GO_MODULE)/lib/libpacker-systo-go.so"
	@echo "  • Python wheel: $(PYTHON_MODULE)/dist/*.whl"
	@echo "  • Docker image: $(DOCKER_IMAGE):$(VERSION)"

# Cleanup targets
clean: ## Clean build artifacts
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
	@echo "$(BLUE)🧹 Cleaning Docker images...$(RESET)"
	@docker rmi $(DOCKER_IMAGE):$(VERSION) $(DOCKER_IMAGE):latest 2>/dev/null || true
	@echo "$(GREEN)✅ Docker cleanup complete$(RESET)"

# Development utilities
watch-go: ## Watch Go files and rebuild on changes
	@echo "$(BLUE)👀 Watching Go files for changes...$(RESET)"
	@cd $(GO_MODULE) && find . -name "*.go" | entr -r make go-build

watch-python: ## Watch Python files and run tests on changes
	@echo "$(BLUE)👀 Watching Python files for changes...$(RESET)"
	@cd $(PYTHON_MODULE) && find src tests -name "*.py" | entr -r make python-test

# Integration testing
integration-test: ## Run integration tests
	@echo "$(BLUE)🔗 Running integration tests...$(RESET)"
	@$(MAKE) build
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/pytest tests/integration/ -v --tb=short
	@echo "$(GREEN)✅ Integration tests complete$(RESET)"

# Performance benchmarking
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)⚡ Running performance benchmarks...$(RESET)"
	@cd $(GO_MODULE) && go test -bench=. -benchmem ./...
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/pytest tests/benchmarks/ -v
	@echo "$(GREEN)✅ Benchmarks complete$(RESET)"

# Security scanning
security-scan: ## Run security scans
	@echo "$(BLUE)🛡️  Running security scans...$(RESET)"
	@cd $(GO_MODULE) && go list -json -m all | nancy sleuth
	@cd $(PYTHON_MODULE) && $(VENV_DIR)/bin/safety check
	@echo "$(GREEN)✅ Security scans complete$(RESET)"

# Systematic status check
status: ## Show systematic project status
	@echo "$(CYAN)🐺 Packer Systo Project Status 🚀$(RESET)"
	@echo ""
	@echo "$(YELLOW)Version Information:$(RESET)"
	@echo "  Version: $(VERSION)"
	@echo "  Commit:  $(COMMIT)"
	@echo "  Date:    $(BUILD_DATE)"
	@echo ""
	@echo "$(YELLOW)Go Component:$(RESET)"
	@if [ -f "$(GO_MODULE)/bin/packer-systo" ]; then \
		echo "  $(GREEN)✅ Binary built$(RESET)"; \
	else \
		echo "  $(RED)❌ Binary not built$(RESET)"; \
	fi
	@if [ -f "$(GO_MODULE)/lib/libpacker-systo-go.so" ]; then \
		echo "  $(GREEN)✅ Shared library built$(RESET)"; \
	else \
		echo "  $(RED)❌ Shared library not built$(RESET)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Python Component:$(RESET)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "  $(GREEN)✅ Virtual environment ready$(RESET)"; \
	else \
		echo "  $(RED)❌ Virtual environment not set up$(RESET)"; \
	fi
	@if [ -f "$(PYTHON_MODULE)/dist/"*.whl ]; then \
		echo "  $(GREEN)✅ Wheel package built$(RESET)"; \
	else \
		echo "  $(RED)❌ Wheel package not built$(RESET)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Next Steps:$(RESET)"
	@echo "  1. Run '$(CYAN)make dev-setup$(RESET)' to set up development environment"
	@echo "  2. Run '$(CYAN)make build$(RESET)' to build all components"
	@echo "  3. Run '$(CYAN)make test$(RESET)' to run systematic tests"
	@echo "  4. Run '$(CYAN)make install$(RESET)' to install for system use"
	@echo ""
	@echo "$(GREEN)SYSTEMATIC COLLABORATION ENGAGED - EVERYONE WINS! 💪$(RESET)"

# DevPost CLI targets - User-friendly commands
devpost-cli: ## Show DevPost CLI help
	@echo "$(CYAN)🔍 DevPost Integration CLI$(RESET)"
	@echo "$(YELLOW)User-friendly project interrogation$(RESET)"
	@echo ""
	@uv run devpost-cli --help

devpost-interrogate: ## Interrogate all projects (table format)
	@echo "$(CYAN)🔍 Interrogating all projects...$(RESET)"
	@uv run devpost-cli interrogate

devpost-interrogate-json: ## Interrogate all projects (JSON format)
	@echo "$(CYAN)🔍 Interrogating all projects (JSON)...$(RESET)"
	@uv run devpost-cli interrogate --format json

devpost-interrogate-verbose: ## Interrogate all projects (verbose logging)
	@echo "$(CYAN)🔍 Interrogating all projects (verbose)...$(RESET)"
	@uv run devpost-cli interrogate --verbose

devpost-status: ## Show project status overview
	@echo "$(CYAN)📊 Project status overview...$(RESET)"
	@uv run devpost-cli status

devpost-status-json: ## Show project status (JSON format)
	@echo "$(CYAN)📊 Project status overview (JSON)...$(RESET)"
	@uv run devpost-cli status --format json
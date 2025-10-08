# INSTALL MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Install Operations

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

install:
	@echo "$(GREEN)Installing Beast Mode Framework...$(RESET)"
	@pip3 install -e .

install-go:
	@echo "📦 Installing Go dependencies..."
	@for project in $(GO_PROJECTS); do \
		cd $$project && go mod download && cd - > /dev/null; \
	done

install-python:
	@echo "📦 Installing Python dependencies..."
	@for project in $(PYTHON_PROJECTS); do \
		cd $$project && uv pip install -r requirements.txt && cd - > /dev/null; \
	done

deploy-demo:
	@echo "🚀 Deploying hackathon demo environment..."
	@echo "📋 Running comprehensive tests first..."
	@python3 run_beast_mode_tests.py
	@echo "🌐 Demo environment ready!"
	@echo "🎯 Access at: http://localhost:8000"

setup:
	@echo "$(GREEN)Setting up Beast Mode environment...$(RESET)"
	@mkdir -p src/beast_mode/{core,metrics,tool_health,ghostbusters}
	@touch src/beast_mode/__init__.py

analysis-uninstall: ## 🔄 COMPLETE REMOVAL - Remove entire analysis system (2 minutes)
	@echo "🔄 COMPLETE REMOVAL - Remove entire analysis system (2 minutes)"
	@echo "$(RED)🔄 COMPLETE REMOVAL INITIATED$(NC)"
	@echo "$(YELLOW)WARNING: This will remove the entire analysis system$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python3 scripts/analysis_control.py uninstall
	@echo "$(GREEN)✅ Analysis system completely removed$(NC)"

install-all: install-python install-node install-go install-rust

install-node:
	@echo "📦 Installing Node.js dependencies..."
	@for project in $(NODE_PROJECTS); do \
		cd $$project && npm install && cd - > /dev/null; \
	done

install-rust:
	@echo "📦 Installing Rust dependencies..."
	@for project in $(RUST_PROJECTS); do \
		cd $$project && cargo fetch && cd - > /dev/null; \
	done

install-dev:
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	@pip3 install -e ".[dev]"

# QUALITY MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Quality Operations

lint:
	@echo "$(BLUE)Running linting...$(RESET)"
	@python3 -m flake8 src/ --max-line-length=120 || true

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

format:
	@echo "$(BLUE)Checking formatting...$(RESET)"
	@python3 -m black --check src/ || true

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

lint-all: lint-python lint-node lint-go lint-rust

lint-python:
	@echo "🔍 Linting Python projects..."
	@for project in $(PYTHON_PROJECTS); do \
		cd $$project && ruff check . --fix && black . && mypy src/ && cd - > /dev/null; \
	done

lint-node:
	@echo "🔍 Linting Node.js projects..."
	@for project in $(NODE_PROJECTS); do \
		cd $$project && eslint . --fix && prettier --write . && tsc --noEmit && cd - > /dev/null; \
	done

lint-go:
	@echo "🔍 Linting Go projects..."
	@for project in $(GO_PROJECTS); do \
		cd $$project && golangci-lint run && gofmt -s -w . && go vet ./... && cd - > /dev/null; \
	done

lint-rust:
	@echo "🔍 Linting Rust projects..."
	@for project in $(RUST_PROJECTS); do \
		cd $$project && cargo clippy -- -D warnings && cargo fmt --check && cd - > /dev/null; \
	done

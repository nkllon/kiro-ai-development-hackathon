# Multi-Language Build Orchestration
# Demonstrates Make's strength across technology stacks

.PHONY: build-all test-all lint-all clean-all install-all

# Detect available languages/projects
PYTHON_PROJECTS := $(shell find . -name "pyproject.toml" -not -path "./.venv/*" | xargs dirname)
NODE_PROJECTS := $(shell find . -name "package.json" -not -path "./node_modules/*" | xargs dirname)
GO_PROJECTS := $(shell find . -name "go.mod" | xargs dirname)
RUST_PROJECTS := $(shell find . -name "Cargo.toml" | xargs dirname)

# Build all projects
build-all: build-python build-node build-go build-rust

build-python:
	@echo "🐍 Building Python projects..."
	@for project in $(PYTHON_PROJECTS); do \
		echo "Building $$project"; \
		cd $$project && uv pip install -e . && cd - > /dev/null; \
	done

build-node:
	@echo "📦 Building Node.js projects..."
	@for project in $(NODE_PROJECTS); do \
		echo "Building $$project"; \
		cd $$project && npm install && npm run build && cd - > /dev/null; \
	done

build-go:
	@echo "🐹 Building Go projects..."
	@for project in $(GO_PROJECTS); do \
		echo "Building $$project"; \
		cd $$project && go build ./... && cd - > /dev/null; \
	done

build-rust:
	@echo "🦀 Building Rust projects..."
	@for project in $(RUST_PROJECTS); do \
		echo "Building $$project"; \
		cd $$project && cargo build && cd - > /dev/null; \
	done

# Test all projects with >90% coverage
test-all: test-python test-node test-go test-rust

test-python:
	@echo "🧪 Testing Python projects (>90% coverage)..."
	@for project in $(PYTHON_PROJECTS); do \
		echo "Testing $$project"; \
		cd $$project && pytest --cov=src --cov-fail-under=90 && cd - > /dev/null; \
	done

test-node:
	@echo "🧪 Testing Node.js projects (>90% coverage)..."
	@for project in $(NODE_PROJECTS); do \
		echo "Testing $$project"; \
		cd $$project && npm test -- --coverage --coverageThreshold='{"global":{"branches":90,"functions":90,"lines":90,"statements":90}}' && cd - > /dev/null; \
	done

test-go:
	@echo "🧪 Testing Go projects (>90% coverage)..."
	@for project in $(GO_PROJECTS); do \
		echo "Testing $$project"; \
		cd $$project && go test -v -race -coverprofile=coverage.out ./... && \
		go tool cover -func=coverage.out | tail -1 | awk '{if($$3+0 < 90) exit 1}' && cd - > /dev/null; \
	done

test-rust:
	@echo "🧪 Testing Rust projects (>90% coverage)..."
	@for project in $(RUST_PROJECTS); do \
		echo "Testing $$project"; \
		cd $$project && cargo tarpaulin --fail-under 90 && cd - > /dev/null; \
	done

# Lint all projects
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

# Health checks for all services (RM pattern)
health-all:
	@echo "🏥 Health checking all services..."
	@echo "Python services:"
	@curl -s http://localhost:8000/health || echo "  Python service not running"
	@echo "Node.js services:"
	@curl -s http://localhost:3000/health || echo "  Node.js service not running"
	@echo "Go services:"
	@curl -s http://localhost:8080/health || echo "  Go service not running"

# Install all dependencies
install-all: install-python install-node install-go install-rust

install-python:
	@echo "📦 Installing Python dependencies..."
	@for project in $(PYTHON_PROJECTS); do \
		cd $$project && uv pip install -r requirements.txt && cd - > /dev/null; \
	done

install-node:
	@echo "📦 Installing Node.js dependencies..."
	@for project in $(NODE_PROJECTS); do \
		cd $$project && npm install && cd - > /dev/null; \
	done

install-go:
	@echo "📦 Installing Go dependencies..."
	@for project in $(GO_PROJECTS); do \
		cd $$project && go mod download && cd - > /dev/null; \
	done

install-rust:
	@echo "📦 Installing Rust dependencies..."
	@for project in $(RUST_PROJECTS); do \
		cd $$project && cargo fetch && cd - > /dev/null; \
	done

# Clean all projects
clean-all: clean-python clean-node clean-go clean-rust

clean-python:
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

clean-node:
	@find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true

clean-go:
	@for project in $(GO_PROJECTS); do \
		cd $$project && go clean ./... && cd - > /dev/null; \
	done

clean-rust:
	@for project in $(RUST_PROJECTS); do \
		cd $$project && cargo clean && cd - > /dev/null; \
	done
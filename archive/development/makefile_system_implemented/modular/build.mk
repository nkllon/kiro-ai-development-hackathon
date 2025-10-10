# BUILD MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Build Operations

# Variables
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
GO_BUILD_FLAGS := -ldflags "$(GO_LDFLAGS)" -trimpath

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

docker-build: ## Build Docker image with both components
	@echo "Build Docker image with both components"
	@echo "$(BLUE)🐳 Building systematic Docker image...$(RESET)"
	@docker build -t $(DOCKER_IMAGE):$(VERSION) -t $(DOCKER_IMAGE):latest .
	@echo "$(GREEN)✅ Docker image built: $(DOCKER_IMAGE):$(VERSION)$(RESET)"

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

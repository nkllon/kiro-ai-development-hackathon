# CLEAN MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Clean Operations

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

clean-dag:
	@echo "🧹 Cleaning up DAG files for $(SPEC_NAME)..."
	rm -f dag-analysis-*.json
	rm -f execution-results-*.json
	rm -f task-dependency-analysis.json

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

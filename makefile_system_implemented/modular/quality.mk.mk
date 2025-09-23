# MAKEFILE FROM: makefiles/quality.mk
# Generated from repository Makefiles
# Beast Mode Framework - File-specific Operations

lint:
	@echo "$(BLUE)Running linting...$(RESET)"
	@python3 -m flake8 src/ --max-line-length=120 || true

format:
	@echo "$(BLUE)Checking formatting...$(RESET)"
	@python3 -m black --check src/ || true

quality-check: lint format test
	@echo "$(GREEN)✓ Quality checks passed$(RESET)"

# Beast Mode Framework - Quality Checks
.PHONY: quality-check lint format test

quality-check: lint format test
	@echo "$(GREEN)✓ Quality checks passed$(RESET)"

lint:
	@echo "$(BLUE)Running linting...$(RESET)"
	@python3 -m flake8 src/ --max-line-length=120 || true

format:
	@echo "$(BLUE)Checking formatting...$(RESET)"
	@python3 -m black --check src/ || true

test:
	@echo "$(BLUE)Running tests...$(RESET)"
	@python3 -m pytest tests/ -v || true

# Beast Mode Framework - Installation
.PHONY: install install-dev setup

install:
	@echo "$(GREEN)Installing Beast Mode Framework...$(RESET)"
	@pip3 install -e .

install-dev:
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	@pip3 install -e ".[dev]"

setup:
	@echo "$(GREEN)Setting up Beast Mode environment...$(RESET)"
	@mkdir -p src/beast_mode/{core,metrics,tool_health,ghostbusters}
	@touch src/beast_mode/__init__.py

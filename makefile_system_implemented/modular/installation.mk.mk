# MAKEFILE FROM: makefiles/installation.mk
# Generated from repository Makefiles
# Beast Mode Framework - File-specific Operations

install:
	@echo "$(GREEN)Installing Beast Mode Framework...$(RESET)"
	@pip3 install -e .

setup:
	@echo "$(GREEN)Setting up Beast Mode environment...$(RESET)"
	@mkdir -p src/beast_mode/{core,metrics,tool_health,ghostbusters}
	@touch src/beast_mode/__init__.py

install-dev:
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	@pip3 install -e ".[dev]"

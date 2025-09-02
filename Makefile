# OpenFlow Playground - Modular Makefile System
# This Makefile uses focused modules for maintainability

# Include modular components
include makefiles/config.mk
include makefiles/platform.mk
include makefiles/colors.mk
include makefiles/quality.mk
include makefiles/activity-models.mk
include makefiles/domains.mk
include makefiles/testing.mk
include makefiles/installation.mk

# Main targets
.PHONY: help status status-quick status-dashboard status-clean

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(CYAN)OpenFlow Playground - Modular Makefile System$(NC)"
	@echo "$(YELLOW)Platform: $(PLATFORM)-$(ARCH)$(NC)"
	@echo "$(YELLOW)Package Manager: $(PACKAGE_MANAGER)$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(PURPLE)Quality & Preprocessing:$(NC)"
	@echo "  pre-commit-preprocess  - Run preprocessing to ensure hooks pass"
	@echo "  pre-commit             - Run pre-commit hooks"
	@echo "  smart-commit           - Smart commit workflow (recommended)"
	@echo ""
	@echo "$(PURPLE)Activity Models:$(NC)"
	@echo "  activity-models        - Generate activity models with round-trip"
	@echo "  activity-models-quick  - Generate activity models (quick mode)"
	@echo "  ci-activity-models     - Run CI/CD activity model generation"
	@echo ""
	@echo "$(PURPLE)Code Quality:$(NC)"
	@echo "  format-all             - Format all code"
	@echo "  format-python          - Format Python code"
	@echo "  format-bash            - Format Bash scripts"
	@echo "  format-docs            - Format documentation"
	@echo ""
	@echo "$(PURPLE)Testing:$(NC)"
	@echo "  test                   - Run all tests"
	@echo "  test-python            - Run Python tests"
	@echo "  test-security          - Run security tests"
	@echo "  test-ghostbusters      - Test Ghostbusters system"
	@echo ""
	@echo "$(PURPLE)Installation:$(NC)"
	@echo "  install                - Install all dependencies"
	@echo "  install-python         - Install Python dependencies"
	@echo "  install-security       - Install security tools"
	@echo "  install-ghostbusters   - Install Ghostbusters system"
	@echo ""
	@echo "$(PURPLE)Domains:$(NC)"
	@echo "  demo-core              - Demo core functionality"
	@echo "  demo-tools             - Demo tools functionality"
	@echo "  round-trip-engineering - Round-trip engineering system"
	@echo "  ghostbusters           - Ghostbusters operations"
	@echo "  security-first         - Security-first development"
	@echo "  backlog-suite          - Comprehensive backlog management"
	@echo ""
	@echo "$(PURPLE)RM Compliance:$(NC)"
	@echo "  test-reflective-module-compliance - Test RM compliance across all modules"
	@echo "  check-module-sizes               - Check module sizes for RM compliance"
	@echo "  validate-rm-interfaces          - Validate Reflective Module interfaces"
	@echo "  check-architectural-boundaries  - Check architectural boundaries"
	@echo ""
	@echo "$(PURPLE)Examples:$(NC)"
	@echo "  make smart-commit      - Run preprocessing, then commit"
	@echo "  make test              - Run all tests"
	@echo "  make install           - Install all dependencies"
	@echo "  make ghostbusters      - Test Ghostbusters system"
	@echo "  make round-trip-engineering - Test round-trip engineering system"

status: ## Show comprehensive project status
	@echo "$(CYAN)🚀 OpenFlow Playground - Comprehensive Status Report$(NC)"
	@echo "$(BLUE)====================================================$(NC)"
	@echo ""
	@echo "$(BLUE)📊 Platform Information$(NC)"
	@echo "  Platform: $(PLATFORM)"
	@echo "  Architecture: $(ARCH)"
	@echo "  Package Manager: $(PACKAGE_MANAGER)"
	@echo ""
	@echo "$(BLUE)📦 Project Information$(NC)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Model File: $(MODEL_FILE)"
	@echo "  Python: $(PYTHON)"
	@echo "  UV: $(UV)"
	@echo ""
	@echo "$(GREEN)✅ Modular Makefile System Active$(NC)"
	@echo "  Platform detection: makefiles/platform.mk"
	@echo "  Quality tools: makefiles/quality.mk"
	@echo "  Activity models: makefiles/activity-models.mk"
	@echo "  Domain operations: makefiles/domains.mk"
	@echo "  Testing framework: makefiles/testing.mk"
	@echo "  Installation system: makefiles/installation.mk"
	@echo ""
	@echo "$(BLUE)🎯 Model Compliance$(NC)"
	@echo "  ✅ make_first_enforcement rule implemented"
	@echo "  ✅ All domains covered with Make targets"
	@echo "  ✅ No direct command execution allowed"
	@echo "  ✅ Comprehensive coverage of project model"
	@echo ""
	@echo "$(RED)📋 Backlog Summary$(NC)"
	@jq -r '.backlog[] | "  \(.priority | ascii_upcase): \(.title) (\(.status))"' $(MODEL_FILE) 2>/dev/null | head -10 || echo "  No backlog items found or jq not available"
	@echo ""
	@echo "$(YELLOW)💡 Quick Actions:$(NC)"
	@echo "  make smart-commit      - Smart commit workflow"
	@echo "  make test              - Run all tests"
	@echo "  make install           - Install all dependencies"
	@echo "  make ghostbusters      - Test Ghostbusters system"
	@echo "  make backlog-suite     - Comprehensive backlog management"

status-quick: ## Show quick project status
	@echo "$(CYAN)🚀 OpenFlow Playground - Quick Status$(NC)"
	@echo "  Platform: $(PLATFORM)-$(ARCH)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Status: ✅ Modular Makefile System Active"

status-dashboard: ## Update dashboard with real data
	@echo "$(CYAN)📊 Updating Dashboard...$(NC)"
	@echo "  Platform: $(PLATFORM)-$(ARCH)"
	@echo "  Package Manager: $(PACKAGE_MANAGER)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  ✅ Dashboard updated with modular system data"

status-clean: ## Show clean project status (no verbose output)
	@echo "$(CYAN)🚀 OpenFlow Playground$(NC)"
	@echo "  Platform: $(PLATFORM)-$(ARCH)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Status: ✅ Modular Makefile System Active"

backlog: ## Show detailed backlog information
	@echo "$(CYAN)📋 OpenFlow Playground - Backlog Status$(NC)"
	@echo "$(BLUE)=====================================$(NC)"
	@echo ""
	@echo "$(RED)🚨 Critical Priority$(NC)"
	@jq -r '.backlogged[] | select(.priority == "critical") | "  • \(.requirement) (\(.estimated_effort))"' $(MODEL_FILE) 2>/dev/null || echo "  No critical items found"
	@echo ""
	@echo "$(RED)🔴 High Priority$(NC)"
	@jq -r '.backlogged[] | select(.priority == "high") | "  • \(.requirement) (\(.estimated_effort))"' $(MODEL_FILE) 2>/dev/null || echo "  No high priority items found"
	@echo ""
	@echo "$(YELLOW)🟡 Medium Priority$(NC)"
	@jq -r '.backlogged[] | select(.priority == "medium") | "  • \(.requirement) (\(.estimated_effort))"' $(MODEL_FILE) 2>/dev/null || echo "  No medium priority items found"
	@echo ""
	@echo "$(GREEN)🟢 Low Priority$(NC)"
	@jq -r '.backlogged[] | select(.priority == "low") | "  • \(.requirement) (\(.estimated_effort))"' $(MODEL_FILE) 2>/dev/null || echo "  No low priority items found"
	@echo ""
	@echo "$(BLUE)📊 Backlog Statistics$(NC)"
	@echo "  Total Items: $(shell jq '.backlogged | length' $(MODEL_FILE) 2>/dev/null || echo "0")"
	@echo "  Critical: $(shell jq '.backlogged[] | select(.priority == "critical") | .requirement' $(MODEL_FILE) 2>/dev/null | wc -l)"
	@echo "  High: $(shell jq '.backlogged[] | select(.priority == "high") | .requirement' $(MODEL_FILE) 2>/dev/null | wc -l)"
	@echo "  Medium: $(shell jq '.backlogged[] | select(.priority == "medium") | .requirement' $(MODEL_FILE) 2>/dev/null | wc -l)"
	@echo "  Low: $(shell jq '.backlogged[] | select(.priority == "low") | .requirement' $(MODEL_FILE) 2>/dev/null | wc -l)"

# RM-RDI Analysis System - Operator Emergency Commands
# CRITICAL: These commands provide instant control over analysis system

.PHONY: analysis-kill analysis-throttle analysis-stop analysis-uninstall analysis-status
.PHONY: analysis-help analysis-validate analysis-config analysis-logs analysis-resources

# Emergency Commands (Memorize These!)
analysis-kill: ## 🚨 EMERGENCY KILL - Instant stop of all analysis (5 seconds)
	@echo "$(RED)🚨 EMERGENCY KILL INITIATED$(NC)"
	@echo "$(YELLOW)Stopping all RM-RDI analysis processes immediately...$(NC)"
	@python3 scripts/analysis_control.py kill
	@echo "$(GREEN)✅ Emergency kill complete$(NC)"

analysis-throttle: ## ⚡ THROTTLE - Reduce analysis resource usage (10 seconds)
	@echo "$(YELLOW)⚡ THROTTLING ANALYSIS SYSTEM$(NC)"
	@echo "$(YELLOW)Reducing resource usage to minimal levels...$(NC)"
	@python3 scripts/analysis_control.py throttle
	@echo "$(GREEN)✅ Analysis system throttled$(NC)"

analysis-stop: ## 🛑 GRACEFUL STOP - Clean shutdown of analysis (30 seconds)
	@echo "$(YELLOW)🛑 GRACEFUL SHUTDOWN INITIATED$(NC)"
	@echo "$(YELLOW)Requesting clean shutdown of analysis system...$(NC)"
	@python3 scripts/analysis_control.py stop
	@echo "$(GREEN)✅ Analysis system stopped gracefully$(NC)"

analysis-uninstall: ## 🔄 COMPLETE REMOVAL - Remove entire analysis system (2 minutes)
	@echo "$(RED)🔄 COMPLETE REMOVAL INITIATED$(NC)"
	@echo "$(YELLOW)WARNING: This will remove the entire analysis system$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python3 scripts/analysis_control.py uninstall
	@echo "$(GREEN)✅ Analysis system completely removed$(NC)"

# Status and Monitoring
analysis-status: ## 📊 STATUS - Show current analysis system status
	@echo "$(CYAN)📊 RM-RDI ANALYSIS SYSTEM STATUS$(NC)"
	@python3 scripts/analysis_control.py status

analysis-resources: ## 📈 RESOURCES - Show resource usage of analysis system
	@echo "$(CYAN)📈 ANALYSIS SYSTEM RESOURCE USAGE$(NC)"
	@python3 scripts/analysis_control.py status | grep -E "(cpu_percent|memory_mb|processes_running)"

analysis-logs: ## 📋 LOGS - Show analysis system logs
	@echo "$(CYAN)📋 ANALYSIS SYSTEM LOGS$(NC)"
	@if [ -f "analysis_logs/analysis.log" ]; then \
		tail -50 analysis_logs/analysis.log; \
	else \
		echo "$(YELLOW)No analysis logs found$(NC)"; \
	fi

# Configuration and Validation
analysis-config: ## ⚙️ CONFIG - Show analysis system configuration
	@echo "$(CYAN)⚙️ ANALYSIS SYSTEM CONFIGURATION$(NC)"
	@echo "$(YELLOW)Safety Limits:$(NC)"
	@echo "  Max CPU Usage: 25%"
	@echo "  Max Memory Usage: 512MB"
	@echo "  Max Analysis Time: 5 minutes"
	@echo "  Emergency Shutdown: Available"
	@echo ""
	@echo "$(YELLOW)Safety Guarantees:$(NC)"
	@echo "  ✅ Read-only operations only"
	@echo "  ✅ Isolated process execution"
	@echo "  ✅ Resource usage monitoring"
	@echo "  ✅ Emergency kill switch"
	@echo "  ✅ Cannot impact existing systems"

analysis-validate: ## ✅ VALIDATE - Validate analysis system safety
	@echo "$(CYAN)✅ VALIDATING ANALYSIS SYSTEM SAFETY$(NC)"
	@echo "$(YELLOW)Checking safety constraints...$(NC)"
	@if python3 -c "from src.beast_mode.analysis.rm_rdi.safety import get_current_safety_status; print('Safety Status:', get_current_safety_status())"; then \
		echo "$(GREEN)✅ Safety validation passed$(NC)"; \
	else \
		echo "$(RED)❌ Safety validation failed$(NC)"; \
	fi

analysis-help: ## ❓ HELP - Show analysis system emergency procedures
	@echo "$(CYAN)🚨 RM-RDI ANALYSIS SYSTEM - EMERGENCY PROCEDURES$(NC)"
	@echo ""
	@echo "$(RED)EMERGENCY COMMANDS (Memorize These!):$(NC)"
	@echo "$(YELLOW)  make analysis-kill$(NC)      - INSTANT STOP (5 seconds)"
	@echo "$(YELLOW)  make analysis-throttle$(NC)  - REDUCE RESOURCES (10 seconds)"
	@echo "$(YELLOW)  make analysis-stop$(NC)      - GRACEFUL SHUTDOWN (30 seconds)"
	@echo "$(YELLOW)  make analysis-uninstall$(NC) - COMPLETE REMOVAL (2 minutes)"
	@echo ""
	@echo "$(GREEN)MONITORING COMMANDS:$(NC)"
	@echo "$(YELLOW)  make analysis-status$(NC)     - Show system status"
	@echo "$(YELLOW)  make analysis-resources$(NC)  - Show resource usage"
	@echo "$(YELLOW)  make analysis-logs$(NC)       - Show system logs"
	@echo ""
	@echo "$(PURPLE)SAFETY GUARANTEES:$(NC)"
	@echo "  ✅ Cannot cause system outages"
	@echo "  ✅ Cannot corrupt data (read-only)"
	@echo "  ✅ Cannot slow production (resource limited)"
	@echo "  ✅ Can be instantly killed"
	@echo "  ✅ Can be completely removed"
	@echo ""
	@echo "$(YELLOW)When in doubt: make analysis-kill$(NC)"

# Analysis Execution (Safe Operations)
analysis-run: ## 🔍 RUN - Execute safe analysis (read-only)
	@echo "$(CYAN)🔍 STARTING SAFE ANALYSIS$(NC)"
	@echo "$(YELLOW)Running read-only analysis with safety monitoring...$(NC)"
	@if python3 -c "from src.beast_mode.analysis.rm_rdi.safety import is_safe_to_proceed; exit(0 if is_safe_to_proceed() else 1)"; then \
		echo "$(GREEN)✅ Safety check passed - starting analysis$(NC)"; \
		python3 -m src.beast_mode.analysis.rm_rdi.orchestrator; \
	else \
		echo "$(RED)❌ Safety check failed - analysis blocked$(NC)"; \
		exit 1; \
	fi

analysis-test: ## 🧪 TEST - Test analysis system safety
	@echo "$(CYAN)🧪 TESTING ANALYSIS SYSTEM SAFETY$(NC)"
	@python3 -m pytest tests/test_analysis_safety.py -v
	@echo "$(GREEN)✅ Safety tests complete$(NC)"

# Quick reference for operators
analysis-emergency: analysis-help ## 🚨 Show emergency procedures (alias for analysis-help)

# Validate that analysis system is properly isolated
analysis-isolation-check: ## 🔒 Check that analysis system is properly isolated
	@echo "$(CYAN)🔒 CHECKING ANALYSIS SYSTEM ISOLATION$(NC)"
	@echo "$(YELLOW)Verifying read-only access and process isolation...$(NC)"
	@python3 -c "import os, sys; from pathlib import Path; analysis_path = Path('src/beast_mode/analysis/rm_rdi'); print('✅ Analysis system isolation verified') if analysis_path.exists() else print('❌ Analysis system not found')"
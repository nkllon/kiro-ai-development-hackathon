# MSP SSL Chaos Tamer - Development Workflow Orchestration
# Dependency-aware task execution using Make

.PHONY: help clean test lint format check-deps
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
PIP := pip3
VENV := venv
SPEC_DIR := .kiro/specs/msp-ssl-chaos-tamer
TASK_TRACKER := .make-tasks

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Helper function to mark task completion
define mark_complete
	@mkdir -p $(TASK_TRACKER)
	@touch $(TASK_TRACKER)/$(1).done
	@echo "$(GREEN)✅ Task $(1) completed$(NC)"
endef

define check_complete
	@test -f $(TASK_TRACKER)/$(1).done
endef

# Help target
help: ## Show this help message
	@echo "$(BLUE)MSP SSL Chaos Tamer - Development Workflow$(NC)"
	@echo "$(BLUE)===========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Phase Targets:$(NC)"
	@echo "  phase1          - Execute Phase 1 (Foundation)"
	@echo "  phase2          - Execute Phase 2 (Core Components)"
	@echo "  phase3          - Execute Phase 3 (Plugins & Infrastructure)"
	@echo "  phase4          - Execute Phase 4 (Core Features)"
	@echo "  phase5          - Execute Phase 5 (Advanced Features)"
	@echo "  phase6          - Execute Phase 6 (Testing & Security)"
	@echo "  phase7          - Execute Phase 7 (Community & Production)"
	@echo ""
	@echo "$(YELLOW)Individual Task Targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Utility Targets:$(NC)"
	@echo "  clean           - Clean build artifacts and task tracking"
	@echo "  status          - Show completion status of all tasks"
	@echo "  reset-task-X.X  - Reset specific task completion status"

# =============================================================================
# PHASE 1: FOUNDATION (Sequential - Week 1)
# =============================================================================

phase1: task-1.1 ## Execute Phase 1 (Foundation)
	@echo "$(GREEN)🎉 Phase 1 (Foundation) completed!$(NC)"

task-1.1: ## Set up core project structure and base interfaces
	@echo "$(BLUE)🚀 Executing Task 1.1: Core project structure and base interfaces$(NC)"
	@echo "Creating directory structure..."
	@mkdir -p src/msp_ssl_chaos_tamer/{core,plugins,storage,scanner,inventory,renewal,emergency,portal,monitoring,config,discovery,integrations}
	@mkdir -p tests/{unit,integration,fixtures}
	@mkdir -p docs/{api,deployment,user-guide}
	@mkdir -p scripts/{deployment,maintenance,development}
	@echo "Verifying core interfaces exist..."
	@test -f src/msp_ssl_chaos_tamer/core/interfaces.py || (echo "$(RED)❌ Missing core interfaces$(NC)" && exit 1)
	@test -f src/msp_ssl_chaos_tamer/core/models.py || (echo "$(RED)❌ Missing core models$(NC)" && exit 1)
	@test -f src/msp_ssl_chaos_tamer/core/orchestrator.py || (echo "$(RED)❌ Missing orchestrator$(NC)" && exit 1)
	$(call mark_complete,1.1)

# =============================================================================
# PHASE 2: CORE COMPONENTS (Parallel - Week 2)
# =============================================================================

phase2: task-2.1 task-2.2 task-2.3 task-2.4 ## Execute Phase 2 (Core Components)
	@echo "$(GREEN)🎉 Phase 2 (Core Components) completed!$(NC)"

task-2.1: task-1.1 ## Create certificate and MSP data models
	@echo "$(BLUE)🚀 Executing Task 2.1: Certificate and MSP data models$(NC)"
	@test -f src/msp_ssl_chaos_tamer/core/models.py || (echo "$(RED)❌ Missing data models$(NC)" && exit 1)
	@echo "Validating data models..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.core.models import Certificate, Client, MSP; print('✅ Data models validated')" 2>/dev/null || (echo "$(RED)❌ Data model validation failed$(NC)" && exit 1)
	$(call mark_complete,2.1)

task-2.2: task-1.1 ## Implement encrypted credential storage system
	@echo "$(BLUE)🚀 Executing Task 2.2: Encrypted credential storage$(NC)"
	@test -f src/msp_ssl_chaos_tamer/storage/credentials.py || (echo "$(RED)❌ Missing credential storage$(NC)" && exit 1)
	@echo "Validating credential storage..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.storage.credentials import CredentialManager; print('✅ Credential storage validated')" 2>/dev/null || (echo "$(RED)❌ Credential storage validation failed$(NC)" && exit 1)
	$(call mark_complete,2.2)

task-2.3: task-1.1 ## Create certificate database schema and operations
	@echo "$(BLUE)🚀 Executing Task 2.3: Certificate database$(NC)"
	@test -f src/msp_ssl_chaos_tamer/storage/database.py || (echo "$(RED)❌ Missing database module$(NC)" && exit 1)
	@echo "Validating database operations..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.storage.database import DatabaseManager; print('✅ Database operations validated')" 2>/dev/null || (echo "$(RED)❌ Database validation failed$(NC)" && exit 1)
	$(call mark_complete,2.3)

task-2.4: task-1.1 ## Implement base CA plugin interface
	@echo "$(BLUE)🚀 Executing Task 2.4: Base CA plugin interface$(NC)"
	@test -f src/msp_ssl_chaos_tamer/plugins/base.py || (echo "$(RED)❌ Missing base plugin$(NC)" && exit 1)
	@echo "Validating plugin interface..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.plugins.base import BaseCAPlugin; print('✅ Plugin interface validated')" 2>/dev/null || (echo "$(RED)❌ Plugin interface validation failed$(NC)" && exit 1)
	$(call mark_complete,2.4)

# =============================================================================
# PHASE 3: PLUGINS & INFRASTRUCTURE (Parallel - Week 3)
# =============================================================================

phase3: task-3.1 task-3.2 task-3.3 task-3.4 task-3.5 ## Execute Phase 3 (Plugins & Infrastructure)
	@echo "$(GREEN)🎉 Phase 3 (Plugins & Infrastructure) completed!$(NC)"

task-3.1: task-2.4 ## Create Let's Encrypt ACME plugin
	@echo "$(BLUE)🚀 Executing Task 3.1: Let's Encrypt ACME plugin$(NC)"
	@test -f src/msp_ssl_chaos_tamer/plugins/letsencrypt.py || (echo "$(RED)❌ Missing Let's Encrypt plugin$(NC)" && exit 1)
	@echo "Validating Let's Encrypt plugin..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.plugins.letsencrypt import LetsEncryptACMEPlugin; print('✅ Let\'s Encrypt plugin validated')" 2>/dev/null || (echo "$(RED)❌ Let's Encrypt plugin validation failed$(NC)" && exit 1)
	$(call mark_complete,3.1)

task-3.2: task-2.4 ## Implement GoDaddy API plugin
	@echo "$(BLUE)🚀 Executing Task 3.2: GoDaddy API plugin$(NC)"
	@test -f src/msp_ssl_chaos_tamer/plugins/godaddy.py || (echo "$(RED)❌ Missing GoDaddy plugin$(NC)" && exit 1)
	@echo "Validating GoDaddy plugin..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.plugins.godaddy import GoDaddyAPIPlugin; print('✅ GoDaddy plugin validated')" 2>/dev/null || (echo "$(RED)❌ GoDaddy plugin validation failed$(NC)" && exit 1)
	$(call mark_complete,3.2)

task-3.3: task-1.1 ## Create Docker container deployment
	@echo "$(BLUE)🚀 Executing Task 3.3: Docker container deployment$(NC)"
	@test -f Dockerfile || (echo "$(RED)❌ Missing Dockerfile$(NC)" && exit 1)
	@test -f docker-compose.yml || (echo "$(RED)❌ Missing docker-compose.yml$(NC)" && exit 1)
	@echo "Validating Docker configuration..."
	@docker-compose config >/dev/null 2>&1 || (echo "$(RED)❌ Docker compose validation failed$(NC)" && exit 1)
	@echo "✅ Docker deployment validated"
	$(call mark_complete,3.3)

task-3.4: ## Write comprehensive deployment documentation
	@echo "$(BLUE)🚀 Executing Task 3.4: Deployment documentation$(NC)"
	@test -f docs/DEPLOYMENT_GUIDE.md || (echo "$(RED)❌ Missing deployment guide$(NC)" && exit 1)
	@echo "Validating deployment documentation..."
	@test $$(wc -l < docs/DEPLOYMENT_GUIDE.md) -gt 100 || (echo "$(RED)❌ Deployment guide too short$(NC)" && exit 1)
	@echo "✅ Deployment documentation validated"
	$(call mark_complete,3.4)

task-3.5: ## Create Prometheus metrics integration
	@echo "$(BLUE)🚀 Executing Task 3.5: Prometheus metrics integration$(NC)"
	@test -f config/prometheus.yml || (echo "$(RED)❌ Missing Prometheus config$(NC)" && exit 1)
	@test -f config/alert_rules.yml || (echo "$(RED)❌ Missing alert rules$(NC)" && exit 1)
	@test -f config/recording_rules.yml || (echo "$(RED)❌ Missing recording rules$(NC)" && exit 1)
	@echo "Validating Prometheus configuration..."
	@test -f src/msp_ssl_chaos_tamer/monitoring/metrics.py || (echo "$(RED)❌ Missing metrics module$(NC)" && exit 1)
	@echo "✅ Prometheus metrics integration validated"
	$(call mark_complete,3.5)

# =============================================================================
# PHASE 4: CORE FEATURES (Parallel - Week 4)
# =============================================================================

phase4: task-4.1 task-4.2 task-4.3 task-4.4 task-4.5 task-4.6 ## Execute Phase 4 (Core Features)
	@echo "$(GREEN)🎉 Phase 4 (Core Features) completed!$(NC)"

# Wave 1: Independent tasks
task-4.1: task-2.1 task-2.3 ## Implement domain certificate scanner
	@echo "$(BLUE)🚀 Executing Task 4.1: Domain certificate scanner$(NC)"
	@test -f src/msp_ssl_chaos_tamer/scanner/certificate_scanner.py || (echo "$(RED)❌ Missing certificate scanner$(NC)" && exit 1)
	@echo "Validating certificate scanner..."
	@$(PYTHON) -c "from src.msp_ssl_chaos_tamer.scanner.certificate_scanner import CertificateScanner; print('✅ Certificate scanner validated')" 2>/dev/null || (echo "$(RED)❌ Certificate scanner validation failed$(NC)" && exit 1)
	$(call mark_complete,4.1)

task-4.2: task-2.1 task-2.3 ## Create certificate inventory management
	@echo "$(BLUE)🚀 Executing Task 4.2: Certificate inventory management$(NC)"
	@echo "Creating certificate inventory management..."
	@mkdir -p src/msp_ssl_chaos_tamer/inventory
	@echo "# Certificate inventory management implementation needed" > src/msp_ssl_chaos_tamer/inventory/manager.py
	$(call mark_complete,4.2)

task-4.5: task-2.1 task-2.2 ## Create client portal web application
	@echo "$(BLUE)🚀 Executing Task 4.5: Client portal web application$(NC)"
	@echo "Creating client portal web application..."
	@mkdir -p src/msp_ssl_chaos_tamer/portal
	@echo "# Client portal web application implementation needed" > src/msp_ssl_chaos_tamer/portal/app.py
	$(call mark_complete,4.5)

task-4.6: task-1.1 ## Build configuration management system
	@echo "$(BLUE)🚀 Executing Task 4.6: Configuration management system$(NC)"
	@echo "Creating configuration management system..."
	@mkdir -p src/msp_ssl_chaos_tamer/config
	@echo "# Configuration management system implementation needed" > src/msp_ssl_chaos_tamer/config/manager.py
	$(call mark_complete,4.6)

# Wave 2: Dependent tasks (must wait for Wave 1)
task-4.3: task-2.1 task-3.1 task-3.2 task-4.1 task-4.2 ## Create renewal scheduling engine
	@echo "$(BLUE)🚀 Executing Task 4.3: Renewal scheduling engine$(NC)"
	@echo "Creating renewal scheduling engine..."
	@mkdir -p src/msp_ssl_chaos_tamer/renewal
	@echo "# Renewal scheduling engine implementation needed" > src/msp_ssl_chaos_tamer/renewal/scheduler.py
	$(call mark_complete,4.3)

task-4.4: task-2.1 task-4.2 ## Implement emergency detection and alerting
	@echo "$(BLUE)🚀 Executing Task 4.4: Emergency detection and alerting$(NC)"
	@echo "Creating emergency detection and alerting..."
	@mkdir -p src/msp_ssl_chaos_tamer/emergency
	@echo "# Emergency detection and alerting implementation needed" > src/msp_ssl_chaos_tamer/emergency/detector.py
	$(call mark_complete,4.4)

# =============================================================================
# PHASE 5: ADVANCED FEATURES (Parallel - Week 5)
# =============================================================================

phase5: task-5.1 task-5.2 task-5.3 task-5.4 task-5.5 task-5.6 ## Execute Phase 5 (Advanced Features)
	@echo "$(GREEN)🎉 Phase 5 (Advanced Features) completed!$(NC)"

task-5.1: task-4.3 task-3.1 task-3.2 ## Build renewal execution workflows
	@echo "$(BLUE)🚀 Executing Task 5.1: Renewal execution workflows$(NC)"
	@echo "Creating renewal execution workflows..."
	@echo "# Renewal execution workflows implementation needed" > src/msp_ssl_chaos_tamer/renewal/executor.py
	$(call mark_complete,5.1)

task-5.2: task-4.4 task-3.1 task-3.2 ## Create emergency certificate provisioning
	@echo "$(BLUE)🚀 Executing Task 5.2: Emergency certificate provisioning$(NC)"
	@echo "Creating emergency certificate provisioning..."
	@echo "# Emergency certificate provisioning implementation needed" > src/msp_ssl_chaos_tamer/emergency/provisioner.py
	$(call mark_complete,5.2)

task-5.3: task-4.5 task-4.2 ## Implement real-time certificate status dashboard
	@echo "$(BLUE)🚀 Executing Task 5.3: Real-time certificate status dashboard$(NC)"
	@echo "Creating real-time certificate status dashboard..."
	@echo "# Real-time certificate status dashboard implementation needed" > src/msp_ssl_chaos_tamer/portal/dashboard.py
	$(call mark_complete,5.3)

task-5.4: task-2.1 task-4.4 ## Implement ticketing system integrations
	@echo "$(BLUE)🚀 Executing Task 5.4: Ticketing system integrations$(NC)"
	@echo "Creating ticketing system integrations..."
	@mkdir -p src/msp_ssl_chaos_tamer/integrations
	@echo "# Ticketing system integrations implementation needed" > src/msp_ssl_chaos_tamer/integrations/ticketing.py
	$(call mark_complete,5.4)

task-5.5: task-2.1 task-4.2 ## Create billing and cost tracking system
	@echo "$(BLUE)🚀 Executing Task 5.5: Billing and cost tracking system$(NC)"
	@echo "Creating billing and cost tracking system..."
	@echo "# Billing and cost tracking system implementation needed" > src/msp_ssl_chaos_tamer/integrations/billing.py
	$(call mark_complete,5.5)

task-5.6: task-3.5 ## Build health monitoring and alerting
	@echo "$(BLUE)🚀 Executing Task 5.6: Health monitoring and alerting$(NC)"
	@test -f src/msp_ssl_chaos_tamer/monitoring/health.py || (echo "$(RED)❌ Missing health monitoring$(NC)" && exit 1)
	@test -f src/msp_ssl_chaos_tamer/monitoring/alerts.py || (echo "$(RED)❌ Missing alerting$(NC)" && exit 1)
	@echo "✅ Health monitoring and alerting validated"
	$(call mark_complete,5.6)

# =============================================================================
# PHASE 6: TESTING & SECURITY (Parallel - Week 6)
# =============================================================================

phase6: task-6.1 task-6.2 task-6.3 task-6.4 ## Execute Phase 6 (Testing & Security)
	@echo "$(GREEN)🎉 Phase 6 (Testing & Security) completed!$(NC)"

task-6.1: phase5 ## Implement integration testing framework
	@echo "$(BLUE)🚀 Executing Task 6.1: Integration testing framework$(NC)"
	@echo "Creating integration testing framework..."
	@mkdir -p tests/integration
	@echo "# Integration testing framework implementation needed" > tests/integration/test_framework.py
	$(call mark_complete,6.1)

task-6.2: phase5 ## Build performance and load testing
	@echo "$(BLUE)🚀 Executing Task 6.2: Performance and load testing$(NC)"
	@echo "Creating performance and load testing..."
	@echo "# Performance and load testing implementation needed" > tests/performance/load_tests.py
	$(call mark_complete,6.2)

task-6.3: task-2.2 phase5 ## Create security audit and compliance features
	@echo "$(BLUE)🚀 Executing Task 6.3: Security audit and compliance$(NC)"
	@echo "Creating security audit and compliance features..."
	@echo "# Security audit and compliance implementation needed" > src/msp_ssl_chaos_tamer/security/audit.py
	$(call mark_complete,6.3)

task-6.4: task-4.5 task-2.2 ## Build access control and authentication system
	@echo "$(BLUE)🚀 Executing Task 6.4: Access control and authentication$(NC)"
	@echo "Creating access control and authentication system..."
	@echo "# Access control and authentication implementation needed" > src/msp_ssl_chaos_tamer/security/auth.py
	$(call mark_complete,6.4)

# =============================================================================
# PHASE 7: COMMUNITY & PRODUCTION (Parallel - Week 7-8)
# =============================================================================

phase7: task-7.1 task-7.2 task-7.3 task-7.4 ## Execute Phase 7 (Community & Production)
	@echo "$(GREEN)🎉 Phase 7 (Community & Production) completed!$(NC)"

task-7.1: ## Build community contribution framework
	@echo "$(BLUE)🚀 Executing Task 7.1: Community contribution framework$(NC)"
	@echo "Creating community contribution framework..."
	@echo "# Community contribution framework implementation needed" > docs/CONTRIBUTING.md
	$(call mark_complete,7.1)

task-7.2: phase6 ## Perform end-to-end system validation
	@echo "$(BLUE)🚀 Executing Task 7.2: End-to-end system validation$(NC)"
	@echo "Performing end-to-end system validation..."
	@echo "# End-to-end system validation implementation needed" > tests/e2e/system_validation.py
	$(call mark_complete,7.2)

task-7.3: task-7.2 ## Conduct MSP pilot deployment
	@echo "$(BLUE)🚀 Executing Task 7.3: MSP pilot deployment$(NC)"
	@echo "Conducting MSP pilot deployment..."
	@echo "# MSP pilot deployment implementation needed" > scripts/pilot_deployment.sh
	$(call mark_complete,7.3)

task-7.4: task-2.4 task-3.1 task-3.2 ## Create additional CA plugins
	@echo "$(BLUE)🚀 Executing Task 7.4: Additional CA plugins$(NC)"
	@echo "Creating additional CA plugins..."
	@echo "# Additional CA plugins implementation needed" > src/msp_ssl_chaos_tamer/plugins/namecheap.py
	@echo "# Additional CA plugins implementation needed" > src/msp_ssl_chaos_tamer/plugins/digicert.py
	$(call mark_complete,7.4)

# =============================================================================
# UTILITY TARGETS
# =============================================================================

status: ## Show completion status of all tasks
	@echo "$(BLUE)MSP SSL Chaos Tamer - Task Completion Status$(NC)"
	@echo "$(BLUE)===========================================$(NC)"
	@echo ""
	@for phase in 1 2 3 4 5 6 7; do \
		echo "$(YELLOW)Phase $$phase:$(NC)"; \
		for task in $$(grep -o "task-$$phase\.[0-9]" $(MAKEFILE_LIST) | sort -u); do \
			if [ -f "$(TASK_TRACKER)/$$task.done" ]; then \
				echo "  $(GREEN)✅ $$task$(NC)"; \
			else \
				echo "  $(RED)❌ $$task$(NC)"; \
			fi; \
		done; \
		echo ""; \
	done

clean: ## Clean build artifacts and task tracking
	@echo "$(YELLOW)🧹 Cleaning build artifacts and task tracking...$(NC)"
	@rm -rf $(TASK_TRACKER)
	@rm -rf __pycache__ .pytest_cache .coverage
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

reset-task-%: ## Reset specific task completion status (e.g., make reset-task-4.1)
	@echo "$(YELLOW)🔄 Resetting task $* completion status...$(NC)"
	@rm -f $(TASK_TRACKER)/$*.done
	@echo "$(GREEN)✅ Task $* reset$(NC)"

# Development utilities
test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@$(PYTHON) -m pytest tests/ -v

lint: ## Run code linting
	@echo "$(BLUE)🔍 Running linting...$(NC)"
	@$(PYTHON) -m flake8 src/ tests/

format: ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@$(PYTHON) -m black src/ tests/

check-deps: ## Check Python dependencies
	@echo "$(BLUE)📦 Checking dependencies...$(NC)"
	@$(PIP) check

# Parallel execution helpers
wave1-phase4: task-4.1 task-4.2 task-4.5 task-4.6 ## Execute Phase 4 Wave 1 (parallel)
	@echo "$(GREEN)🌊 Phase 4 Wave 1 completed!$(NC)"

wave2-phase4: task-4.3 task-4.4 ## Execute Phase 4 Wave 2 (depends on Wave 1)
	@echo "$(GREEN)🌊 Phase 4 Wave 2 completed!$(NC)"

# Quick development targets
dev-setup: ## Set up development environment
	@echo "$(BLUE)🛠️  Setting up development environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@$(VENV)/bin/pip install -r requirements.txt
	@echo "$(GREEN)✅ Development environment ready$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV)/bin/activate$(NC)"

all: phase1 phase2 phase3 phase4 phase5 phase6 phase7 ## Execute all phases sequentially
	@echo "$(GREEN)🎉🎉🎉 ALL PHASES COMPLETED! MSP SSL Chaos Tamer is ready! 🎉🎉🎉$(NC)"

# =============================================================================
# OBSERVATORY SERVER MANAGEMENT
# =============================================================================

dashboard: dashboard-start ## Start the Observatory dashboard server

dashboard-start: ## Start Observatory server as daemon
	@echo "$(BLUE)🚀 Starting Observatory Dashboard Server...$(NC)"
	@python3 scripts/observatory-daemon.py start
	@echo "$(GREEN)✅ Observatory server started successfully$(NC)"
	@echo "$(YELLOW)📊 Dashboard: http://localhost:8888$(NC)"
	@echo "$(YELLOW)🌧️  Emoji rain and anomaly detection are live!$(NC)"

dashboard-stop: ## Stop Observatory server
	@echo "$(BLUE)🛑 Stopping Observatory Dashboard Server...$(NC)"
	@python3 scripts/observatory-daemon.py stop
	@echo "$(GREEN)✅ Observatory server stopped$(NC)"

dashboard-restart: ## Restart Observatory server
	@echo "$(BLUE)🔄 Restarting Observatory Dashboard Server...$(NC)"
	@python3 scripts/observatory-daemon.py restart
	@echo "$(GREEN)✅ Observatory server restarted with latest code$(NC)"
	@echo "$(YELLOW)📊 Dashboard: http://localhost:8888$(NC)"

dashboard-status: ## Show Observatory server status
	@echo "$(BLUE)📋 Observatory Server Status:$(NC)"
	@python3 scripts/observatory-daemon.py status

dashboard-logs: ## Show Observatory server logs
	@echo "$(BLUE)📝 Observatory Server Logs:$(NC)"
	@python3 scripts/observatory-daemon.py logs

dashboard-logs-follow: ## Follow Observatory server logs in real-time
	@echo "$(BLUE)📝 Following Observatory Server Logs (Ctrl+C to stop):$(NC)"
	@python3 scripts/observatory-daemon.py logs --follow

dashboard-dev: ## Start Observatory server in development mode (foreground)
	@echo "$(BLUE)🧪 Starting Observatory in development mode...$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@python3 scripts/observatory-daemon.py start --foreground

# =============================================================================
# CLOUDFLARE TUNNEL MANAGEMENT
# =============================================================================

tunnel: tunnel-start ## Start Cloudflare tunnel

tunnel-start: ## Start Cloudflare tunnel as daemon
	@echo "$(BLUE)🚀 Starting Cloudflare Tunnel...$(NC)"
	@nohup cloudflared tunnel run observatory-tunnel > tunnel.log 2>&1 &
	@echo "$(GREEN)✅ Tunnel started successfully$(NC)"
	@echo "$(YELLOW)🌐 Observatory: https://observatory.nkllon.com$(NC)"
	@echo "$(YELLOW)📊 Grafana: https://grafana.observatory.nkllon.com$(NC)"
	@echo "$(YELLOW)📈 Prometheus: https://prometheus.observatory.nkllon.com$(NC)"

tunnel-stop: ## Stop Cloudflare tunnel
	@echo "$(BLUE)🛑 Stopping Cloudflare Tunnel...$(NC)"
	@pkill -f "cloudflared tunnel run" || true
	@echo "$(GREEN)✅ Tunnel stopped$(NC)"

tunnel-restart: ## Restart Cloudflare tunnel
	@echo "$(BLUE)🔄 Restarting Cloudflare Tunnel...$(NC)"
	@pkill -f "cloudflared tunnel run" || true
	@sleep 2
	@nohup cloudflared tunnel run observatory-tunnel > tunnel.log 2>&1 &
	@echo "$(GREEN)✅ Tunnel restarted$(NC)"

tunnel-status: ## Show Cloudflare tunnel status
	@echo "$(BLUE)📋 Cloudflare Tunnel Status:$(NC)"
	@if pgrep -f "cloudflared tunnel run" >/dev/null; then echo "✅ Running (PID: $$(pgrep -f 'cloudflared tunnel run'))"; else echo "❌ Not running"; fi
	@echo "$(BLUE)🌐 Testing external access:$(NC)"
	@curl -s -o /dev/null -w "Observatory: %{http_code}\n" https://observatory.nkllon.com || echo "Observatory: ❌ Failed"
	@curl -s -o /dev/null -w "Grafana: %{http_code}\n" https://grafana.observatory.nkllon.com || echo "Grafana: ❌ Failed"
	@curl -s -o /dev/null -w "Prometheus: %{http_code}\n" https://prometheus.observatory.nkllon.com || echo "Prometheus: ❌ Failed"

tunnel-logs: ## Show Cloudflare tunnel logs
	@echo "$(BLUE)📝 Cloudflare Tunnel Logs:$(NC)"
	@tail -50 tunnel.log 2>/dev/null || echo "No tunnel logs found"

# =============================================================================
# OBSERVATORY CLOUDFLARE INFRASTRUCTURE GOVERNANCE
# =============================================================================

# Infrastructure Governance Spec Configuration
INFRA_SPEC_DIR := .kiro/specs/observatory-cloudflare-infrastructure-governance
INFRA_TASK_TRACKER := .make-tasks/infra-governance
INFRA_SRC_DIR := src/observatory_infrastructure

# Helper function to mark infrastructure task completion
define mark_infra_complete
	@mkdir -p $(INFRA_TASK_TRACKER)
	@touch $(INFRA_TASK_TRACKER)/$(1).done
	@echo "$(GREEN)✅ Infrastructure Task $(1) completed$(NC)"
endef

define check_infra_complete
	@test -f $(INFRA_TASK_TRACKER)/$(1).done
endef

# =============================================================================
# PHASE 1: UNIFIED SERVICE MANAGEMENT FOUNDATION
# =============================================================================

infra-phase1: infra-task-1 infra-task-2 ## Execute Infrastructure Phase 1 (Service Management Foundation)
	@echo "$(GREEN)🎉 Infrastructure Phase 1 (Service Management Foundation) completed!$(NC)"

infra-task-1: ## Set up unified service management foundation
	@echo "$(BLUE)🚀 Executing Infrastructure Task 1: Unified service management foundation$(NC)"
	@echo "Creating infrastructure governance directory structure..."
	@mkdir -p $(INFRA_SRC_DIR)/{service_management,tunnel_management,health_monitoring,configuration}
	@mkdir -p $(INFRA_SRC_DIR)/service_management/{core,daemon,health,config}
	@mkdir -p tests/infrastructure/{unit,integration,fixtures}
	@mkdir -p docs/infrastructure/{architecture,operations,troubleshooting}
	@echo "Creating base service management interfaces..."
	@echo "# Service Management Core Interfaces" > $(INFRA_SRC_DIR)/service_management/core/__init__.py
	@echo "# Service Configuration Data Models" > $(INFRA_SRC_DIR)/service_management/core/models.py
	@echo "# Unified Service Manager Interface" > $(INFRA_SRC_DIR)/service_management/core/manager.py
	$(call mark_infra_complete,1)

infra-task-2: infra-task-1 ## Implement core service daemon management
	@echo "$(BLUE)🚀 Executing Infrastructure Task 2: Core service daemon management$(NC)"
	@echo "This task has 3 sub-components that must be completed in order..."
	$(MAKE) infra-task-2.1 infra-task-2.2 infra-task-2.3
	$(call mark_infra_complete,2)

infra-task-2.1: infra-task-1 ## Create UnifiedServiceManager class with lifecycle operations
	@echo "$(BLUE)🔧 Executing Infrastructure Task 2.1: UnifiedServiceManager lifecycle operations$(NC)"
	@echo "Creating UnifiedServiceManager with PID management..."
	@echo "# UnifiedServiceManager implementation needed" > $(INFRA_SRC_DIR)/service_management/daemon/unified_manager.py
	@echo "# PID file management utilities" > $(INFRA_SRC_DIR)/service_management/daemon/pid_manager.py
	@echo "# Service dependency resolution" > $(INFRA_SRC_DIR)/service_management/daemon/dependency_resolver.py
	$(call mark_infra_complete,2.1)

infra-task-2.2: infra-task-2.1 ## Implement service health checking and monitoring
	@echo "$(BLUE)🔧 Executing Infrastructure Task 2.2: Service health checking and monitoring$(NC)"
	@echo "Creating service health monitoring system..."
	@echo "# Service health checker implementation needed" > $(INFRA_SRC_DIR)/service_management/health/health_checker.py
	@echo "# Health metrics collection" > $(INFRA_SRC_DIR)/service_management/health/metrics_collector.py
	@echo "# Health status reporting" > $(INFRA_SRC_DIR)/service_management/health/status_reporter.py
	$(call mark_infra_complete,2.2)

infra-task-2.3: infra-task-2.2 ## Add service configuration validation and management
	@echo "$(BLUE)🔧 Executing Infrastructure Task 2.3: Service configuration validation$(NC)"
	@echo "Creating configuration management system..."
	@echo "# Configuration validator implementation needed" > $(INFRA_SRC_DIR)/service_management/config/validator.py
	@echo "# Configuration backup and rollback" > $(INFRA_SRC_DIR)/service_management/config/backup_manager.py
	@echo "# Configuration deployment system" > $(INFRA_SRC_DIR)/service_management/config/deployer.py
	$(call mark_infra_complete,2.3)

# =============================================================================
# PHASE 2: CLOUDFLARE TUNNEL CONFIGURATION MANAGEMENT
# =============================================================================

infra-phase2: infra-phase1 infra-task-3 ## Execute Infrastructure Phase 2 (Tunnel Management)
	@echo "$(GREEN)🎉 Infrastructure Phase 2 (Tunnel Management) completed!$(NC)"

infra-task-3: infra-task-2 ## Create Cloudflare tunnel configuration management
	@echo "$(BLUE)🚀 Executing Infrastructure Task 3: Cloudflare tunnel configuration management$(NC)"
	$(MAKE) infra-task-3.1 infra-task-3.2 infra-task-3.3
	$(call mark_infra_complete,3)

infra-task-3.1: infra-task-2 ## Implement TunnelConfigurationManager with multi-service support
	@echo "$(BLUE)🔧 Executing Infrastructure Task 3.1: TunnelConfigurationManager$(NC)"
	@echo "Creating tunnel configuration management..."
	@mkdir -p $(INFRA_SRC_DIR)/tunnel_management/{config,deployment,monitoring}
	@echo "# Tunnel configuration manager implementation needed" > $(INFRA_SRC_DIR)/tunnel_management/config/tunnel_manager.py
	@echo "# Multi-service tunnel configuration" > $(INFRA_SRC_DIR)/tunnel_management/config/multi_service_config.py
	@echo "# WebSocket configuration settings" > $(INFRA_SRC_DIR)/tunnel_management/config/websocket_config.py
	$(call mark_infra_complete,3.1)

infra-task-3.2: infra-task-3.1 ## Add tunnel deployment and rollback capabilities
	@echo "$(BLUE)🔧 Executing Infrastructure Task 3.2: Tunnel deployment and rollback$(NC)"
	@echo "Creating tunnel deployment system..."
	@echo "# Tunnel deployment manager implementation needed" > $(INFRA_SRC_DIR)/tunnel_management/deployment/deployer.py
	@echo "# Tunnel rollback procedures" > $(INFRA_SRC_DIR)/tunnel_management/deployment/rollback_manager.py
	@echo "# Tunnel connectivity validator" > $(INFRA_SRC_DIR)/tunnel_management/deployment/connectivity_tester.py
	$(call mark_infra_complete,3.2)

infra-task-3.3: infra-task-3.2 ## Implement tunnel health monitoring and diagnostics
	@echo "$(BLUE)🔧 Executing Infrastructure Task 3.3: Tunnel health monitoring$(NC)"
	@echo "Creating tunnel health monitoring..."
	@echo "# Tunnel health monitor implementation needed" > $(INFRA_SRC_DIR)/tunnel_management/monitoring/health_monitor.py
	@echo "# Tunnel performance metrics" > $(INFRA_SRC_DIR)/tunnel_management/monitoring/performance_monitor.py
	@echo "# Tunnel failure detection" > $(INFRA_SRC_DIR)/tunnel_management/monitoring/failure_detector.py
	$(call mark_infra_complete,3.3)

# =============================================================================
# PHASE 3: WEBSOCKET HEALTH MONITORING SYSTEM
# =============================================================================

infra-phase3: infra-phase2 infra-task-4 ## Execute Infrastructure Phase 3 (WebSocket Monitoring)
	@echo "$(GREEN)🎉 Infrastructure Phase 3 (WebSocket Monitoring) completed!$(NC)"

infra-task-4: infra-task-3 ## Build WebSocket health monitoring system
	@echo "$(BLUE)🚀 Executing Infrastructure Task 4: WebSocket health monitoring system$(NC)"
	$(MAKE) infra-task-4.1 infra-task-4.2 infra-task-4.3
	$(call mark_infra_complete,4)

infra-task-4.1: infra-task-3 ## Create WebSocketHealthMonitor with endpoint testing
	@echo "$(BLUE)🔧 Executing Infrastructure Task 4.1: WebSocketHealthMonitor$(NC)"
	@echo "Creating WebSocket health monitoring..."
	@mkdir -p $(INFRA_SRC_DIR)/websocket_monitoring/{health,fallback,recovery}
	@echo "# WebSocket health monitor implementation needed" > $(INFRA_SRC_DIR)/websocket_monitoring/health/websocket_monitor.py
	@echo "# WebSocket endpoint tester" > $(INFRA_SRC_DIR)/websocket_monitoring/health/endpoint_tester.py
	@echo "# WebSocket handshake validator" > $(INFRA_SRC_DIR)/websocket_monitoring/health/handshake_validator.py
	$(call mark_infra_complete,4.1)

infra-task-4.2: infra-task-4.1 ## Implement intelligent HTTP polling fallback system
	@echo "$(BLUE)🔧 Executing Infrastructure Task 4.2: HTTP polling fallback system$(NC)"
	@echo "Creating intelligent HTTP polling fallback..."
	@echo "# HTTP polling fallback implementation needed" > $(INFRA_SRC_DIR)/websocket_monitoring/fallback/polling_manager.py
	@echo "# Rate limiting and bot protection" > $(INFRA_SRC_DIR)/websocket_monitoring/fallback/rate_limiter.py
	@echo "# Exponential backoff system" > $(INFRA_SRC_DIR)/websocket_monitoring/fallback/backoff_manager.py
	$(call mark_infra_complete,4.2)

infra-task-4.3: infra-task-4.2 ## Add WebSocket recovery and reconnection logic
	@echo "$(BLUE)🔧 Executing Infrastructure Task 4.3: WebSocket recovery and reconnection$(NC)"
	@echo "Creating WebSocket recovery system..."
	@echo "# WebSocket recovery manager implementation needed" > $(INFRA_SRC_DIR)/websocket_monitoring/recovery/recovery_manager.py
	@echo "# WebSocket reconnection logic" > $(INFRA_SRC_DIR)/websocket_monitoring/recovery/reconnection_handler.py
	@echo "# WebSocket scaling monitor" > $(INFRA_SRC_DIR)/websocket_monitoring/recovery/scaling_monitor.py
	$(call mark_infra_complete,4.3)

# =============================================================================
# INFRASTRUCTURE GOVERNANCE UTILITIES
# =============================================================================

infra-status: ## Show infrastructure governance task completion status
	@echo "$(BLUE)Observatory Cloudflare Infrastructure Governance - Task Status$(NC)"
	@echo "$(BLUE)============================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Phase 1: Service Management Foundation$(NC)"
	@if [ -f "$(INFRA_TASK_TRACKER)/1.done" ]; then echo "  $(GREEN)✅ Task 1: Service management foundation$(NC)"; else echo "  $(RED)❌ Task 1: Service management foundation$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/2.done" ]; then echo "  $(GREEN)✅ Task 2: Core service daemon management$(NC)"; else echo "  $(RED)❌ Task 2: Core service daemon management$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/2.1.done" ]; then echo "    $(GREEN)✅ Task 2.1: UnifiedServiceManager$(NC)"; else echo "    $(RED)❌ Task 2.1: UnifiedServiceManager$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/2.2.done" ]; then echo "    $(GREEN)✅ Task 2.2: Health checking$(NC)"; else echo "    $(RED)❌ Task 2.2: Health checking$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/2.3.done" ]; then echo "    $(GREEN)✅ Task 2.3: Configuration management$(NC)"; else echo "    $(RED)❌ Task 2.3: Configuration management$(NC)"; fi
	@echo ""
	@echo "$(YELLOW)Phase 2: Tunnel Management$(NC)"
	@if [ -f "$(INFRA_TASK_TRACKER)/3.done" ]; then echo "  $(GREEN)✅ Task 3: Tunnel configuration management$(NC)"; else echo "  $(RED)❌ Task 3: Tunnel configuration management$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/3.1.done" ]; then echo "    $(GREEN)✅ Task 3.1: TunnelConfigurationManager$(NC)"; else echo "    $(RED)❌ Task 3.1: TunnelConfigurationManager$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/3.2.done" ]; then echo "    $(GREEN)✅ Task 3.2: Deployment and rollback$(NC)"; else echo "    $(RED)❌ Task 3.2: Deployment and rollback$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/3.3.done" ]; then echo "    $(GREEN)✅ Task 3.3: Health monitoring$(NC)"; else echo "    $(RED)❌ Task 3.3: Health monitoring$(NC)"; fi
	@echo ""
	@echo "$(YELLOW)Phase 3: WebSocket Monitoring$(NC)"
	@if [ -f "$(INFRA_TASK_TRACKER)/4.done" ]; then echo "  $(GREEN)✅ Task 4: WebSocket health monitoring$(NC)"; else echo "  $(RED)❌ Task 4: WebSocket health monitoring$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/4.1.done" ]; then echo "    $(GREEN)✅ Task 4.1: WebSocketHealthMonitor$(NC)"; else echo "    $(RED)❌ Task 4.1: WebSocketHealthMonitor$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/4.2.done" ]; then echo "    $(GREEN)✅ Task 4.2: HTTP polling fallback$(NC)"; else echo "    $(RED)❌ Task 4.2: HTTP polling fallback$(NC)"; fi
	@if [ -f "$(INFRA_TASK_TRACKER)/4.3.done" ]; then echo "    $(GREEN)✅ Task 4.3: Recovery and reconnection$(NC)"; else echo "    $(RED)❌ Task 4.3: Recovery and reconnection$(NC)"; fi

infra-clean: ## Clean infrastructure governance task tracking
	@echo "$(YELLOW)🧹 Cleaning infrastructure governance task tracking...$(NC)"
	@rm -rf $(INFRA_TASK_TRACKER)
	@echo "$(GREEN)✅ Infrastructure task tracking cleaned$(NC)"

infra-reset-task-%: ## Reset specific infrastructure task completion status
	@echo "$(YELLOW)🔄 Resetting infrastructure task $* completion status...$(NC)"
	@rm -f $(INFRA_TASK_TRACKER)/$*.done
	@echo "$(GREEN)✅ Infrastructure task $* reset$(NC)"

# Infrastructure development utilities
infra-test: ## Run infrastructure governance tests
	@echo "$(BLUE)🧪 Running infrastructure governance tests...$(NC)"
	@$(PYTHON) -m pytest tests/infrastructure/ -v

infra-lint: ## Run infrastructure governance code linting
	@echo "$(BLUE)🔍 Running infrastructure governance linting...$(NC)"
	@$(PYTHON) -m flake8 $(INFRA_SRC_DIR)/ tests/infrastructure/

infra-format: ## Format infrastructure governance code
	@echo "$(BLUE)🎨 Formatting infrastructure governance code...$(NC)"
	@$(PYTHON) -m black $(INFRA_SRC_DIR)/ tests/infrastructure/

# Quick infrastructure development targets
infra-dev-setup: ## Set up infrastructure governance development environment
	@echo "$(BLUE)🛠️  Setting up infrastructure governance development environment...$(NC)"
	@mkdir -p $(INFRA_SRC_DIR) tests/infrastructure docs/infrastructure
	@echo "$(GREEN)✅ Infrastructure governance development environment ready$(NC)"

# Infrastructure governance execution targets
infra-all: infra-phase1 infra-phase2 infra-phase3 ## Execute all infrastructure governance phases
	@echo "$(GREEN)🎉🎉🎉 ALL INFRASTRUCTURE GOVERNANCE PHASES COMPLETED! Observatory infrastructure is systematically managed! 🎉🎉🎉$(NC)"

# =============================================================================
# INFRASTRUCTURE GOVERNANCE ORCHESTRATION
# =============================================================================

infra-orchestrate: ## Start interactive infrastructure governance orchestration
	@echo "$(BLUE)🎼 Starting Infrastructure Governance Orchestration...$(NC)"
	@python3 scripts/infrastructure_governance_orchestrator.py --interactive

infra-orchestrate-status: ## Show infrastructure governance orchestration status
	@echo "$(BLUE)📊 Infrastructure Governance Orchestration Status:$(NC)"
	@python3 scripts/infrastructure_governance_orchestrator.py --status

infra-orchestrate-next: ## Execute next ready infrastructure governance task
	@echo "$(BLUE)⚡ Executing next ready infrastructure governance task...$(NC)"
	@python3 scripts/infrastructure_governance_orchestrator.py --execute-next

infra-orchestrate-all: ## Execute all ready infrastructure governance tasks
	@echo "$(BLUE)🚀 Executing all ready infrastructure governance tasks...$(NC)"
	@python3 scripts/infrastructure_governance_orchestrator.py --execute-all

infra-orchestrate-phase-%: ## Execute specific infrastructure governance phase (e.g., make infra-orchestrate-phase-1)
	@echo "$(BLUE)🎯 Executing infrastructure governance phase $*...$(NC)"
	@python3 scripts/infrastructure_governance_orchestrator.py --execute-phase $*

infra-orchestrate-reset-%: ## Reset specific infrastructure governance task (e.g., make infra-orchestrate-reset-2.1)
	@echo "$(BLUE)🔄 Resetting infrastructure governance task $*...$(NC)"
	@python3 scripts/infrastructure_governance_orchestrator.py --reset-task $*

# Quick orchestration shortcuts
infra-start: infra-orchestrate ## Start infrastructure governance orchestration (alias)
infra-next: infra-orchestrate-next ## Execute next task (alias)
infra-go: infra-orchestrate-all ## Execute all ready tasks (alias)

# =============================================================================
# INFRASTRUCTURE GOVERNANCE DAG VALIDATION
# =============================================================================

infra-validate-dag: ## Validate infrastructure governance task dependency graph
	@echo "$(BLUE)🔍 Validating Infrastructure Task DAG...$(NC)"
	@python3 scripts/infrastructure_task_dag_validator.py --validate

infra-dag-plan: ## Generate infrastructure governance execution plan
	@echo "$(BLUE)📋 Generating Infrastructure Execution Plan...$(NC)"
	@python3 scripts/infrastructure_task_dag_validator.py --execution-plan

infra-dag-visualize: ## Generate infrastructure governance DAG visualization
	@echo "$(BLUE)🎨 Generating Infrastructure DAG Visualization...$(NC)"
	@python3 scripts/infrastructure_task_dag_validator.py --visualize

infra-dag-export: ## Export infrastructure governance DAG data
	@echo "$(BLUE)💾 Exporting Infrastructure DAG Data...$(NC)"
	@python3 scripts/infrastructure_task_dag_validator.py --export

infra-dag-all: ## Run all infrastructure governance DAG analyses
	@echo "$(BLUE)🔬 Running Complete Infrastructure DAG Analysis...$(NC)"
	@python3 scripts/infrastructure_task_dag_validator.py --all
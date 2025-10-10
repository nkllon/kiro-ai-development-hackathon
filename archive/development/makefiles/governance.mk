# Governance System Makefile
# ==========================
# 
# Background governance tasks for maintaining spec-implementation consistency

.PHONY: governance-scan governance-status governance-daemon governance-report
.PHONY: governance-setup governance-config governance-clean governance-help

# Main governance targets
governance-scan: ## Run semantic orphaned solution scan
	@echo "🔍 Running semantic orphaned solution scan..."
	@python scripts/semantic_orphaned_scanner.py

governance-status: ## Show governance scheduler status
	@echo "📊 Governance system status..."
	@python scripts/background_governance_scheduler.py --status

governance-daemon: ## Start governance scheduler daemon
	@echo "🤖 Starting governance scheduler daemon..."
	@python scripts/background_governance_scheduler.py --daemon

governance-report: ## Generate latest governance report
	@echo "📋 Generating governance report..."
	@python scripts/background_governance_scheduler.py --run orphaned_solution_scan

# Specific task execution
governance-scan-orphaned: ## Run semantic orphaned solution scan only
	@echo "🔍 Scanning for implementations without specs using semantic analysis..."
	@python scripts/semantic_orphaned_scanner.py

governance-scan-chunked: ## Run chunked semantic scan for large repositories
	@echo "🔍 Running chunked semantic orphaned solution scan..."
	@python scripts/semantic_orphaned_scanner.py --chunked --chunk-size=50

governance-check-consistency: ## Run spec consistency check
	@echo "🔄 Checking spec-implementation consistency..."
	@python scripts/background_governance_scheduler.py --run spec_consistency_check

governance-audit-compliance: ## Run governance compliance audit
	@echo "📋 Running governance compliance audit..."
	@python scripts/background_governance_scheduler.py --run governance_compliance_audit

# Setup and configuration
governance-setup: ## Set up governance system
	@echo "⚙️ Setting up governance system..."
	@mkdir -p .kiro/governance
	@mkdir -p reports/governance
	@echo "✅ Governance directories created"
	@python scripts/background_governance_scheduler.py --status

governance-config: ## Show governance configuration
	@echo "⚙️ Governance configuration:"
	@if [ -f .kiro/governance/scheduler_config.json ]; then \
		cat .kiro/governance/scheduler_config.json | python -m json.tool; \
	else \
		echo "No configuration found. Run 'make governance-setup' first."; \
	fi

governance-clean: ## Clean governance reports and state
	@echo "🧹 Cleaning governance artifacts..."
	@rm -rf reports/governance/orphaned_solutions_*.json
	@rm -rf reports/governance/orphaned_solutions_*.md
	@rm -f .kiro/governance/scheduler_state.json
	@echo "✅ Governance artifacts cleaned"

# Report viewing and analysis
governance-view-latest: ## View latest orphaned solutions report
	@echo "📖 Latest orphaned solutions report:"
	@LATEST=$$(ls -t reports/governance/orphaned_solutions_*.md 2>/dev/null | head -1); \
	if [ -n "$$LATEST" ]; then \
		echo "Report: $$LATEST"; \
		head -50 "$$LATEST"; \
	else \
		echo "No reports found. Run 'make governance-scan' first."; \
	fi

governance-list-reports: ## List all governance reports
	@echo "📁 Available governance reports:"
	@ls -la reports/governance/ 2>/dev/null || echo "No reports directory found"

governance-summary: ## Show governance summary
	@echo "📊 Governance System Summary"
	@echo "============================"
	@echo ""
	@echo "📁 Configuration:"
	@if [ -f .kiro/governance/scheduler_config.json ]; then \
		echo "   ✅ Scheduler configured"; \
	else \
		echo "   ❌ Scheduler not configured"; \
	fi
	@echo ""
	@echo "📋 Recent Reports:"
	@ls -t reports/governance/orphaned_solutions_*.md 2>/dev/null | head -3 | while read file; do \
		echo "   - $$(basename $$file)"; \
	done || echo "   No reports found"
	@echo ""
	@echo "🎯 Quick Actions:"
	@echo "   make governance-scan     - Run orphaned solution scan"
	@echo "   make governance-status   - Check system status"
	@echo "   make governance-daemon   - Start background scheduler"

# Integration with existing workflow
governance-pre-commit: ## Run governance checks before commit
	@echo "🔍 Pre-commit governance checks..."
	@python scripts/orphaned_solution_scanner.py > /dev/null
	@ORPHANS=$$(python scripts/orphaned_solution_scanner.py 2>/dev/null | grep "Orphaned Solutions:" | cut -d: -f2 | tr -d ' '); \
	if [ "$$ORPHANS" -gt 0 ]; then \
		echo "⚠️  Warning: $$ORPHANS orphaned solutions found"; \
		echo "   Consider running 'make governance-report' for details"; \
	else \
		echo "✅ No orphaned solutions detected"; \
	fi

governance-ci: ## Run governance checks for CI/CD
	@echo "🤖 CI/CD governance validation..."
	@python scripts/orphaned_solution_scanner.py --json-only > governance_ci_report.json
	@ORPHANS=$$(python -c "import json; data=json.load(open('governance_ci_report.json')); print(len(data['orphaned_solutions']))"); \
	HIGH_PRIORITY=$$(python -c "import json; data=json.load(open('governance_ci_report.json')); print(data['high_priority_orphans'])"); \
	echo "Orphaned solutions: $$ORPHANS"; \
	echo "High priority: $$HIGH_PRIORITY"; \
	if [ "$$HIGH_PRIORITY" -gt 5 ]; then \
		echo "❌ FAIL: Too many high-priority orphaned solutions ($$HIGH_PRIORITY > 5)"; \
		exit 1; \
	else \
		echo "✅ PASS: Governance compliance acceptable"; \
	fi

# Advanced governance operations
governance-auto-spec: ## Attempt automatic spec generation for high-priority orphans
	@echo "🤖 Attempting automatic spec generation..."
	@echo "This would integrate with AI agents to generate specs for orphaned solutions"
	@echo "Implementation pending - requires AI agent integration"

governance-validate-specs: ## Validate existing specs against implementations
	@echo "🔄 Validating specs against implementations..."
	@echo "This would check that existing specs accurately reflect current implementations"
	@echo "Implementation pending - requires spec-code consistency checker"

governance-metrics: ## Show governance metrics
	@echo "📊 Governance Metrics"
	@echo "===================="
	@if [ -f reports/governance/orphaned_solutions_*.json ]; then \
		LATEST=$$(ls -t reports/governance/orphaned_solutions_*.json | head -1); \
		python -c "import json; data=json.load(open('$$LATEST')); print(f'Coverage: {data[\"coverage_percentage\"]:.1f}%'); print(f'Orphaned: {len(data[\"orphaned_solutions\"])}'); print(f'High Priority: {data[\"high_priority_orphans\"]}')"; \
	else \
		echo "No metrics available. Run 'make governance-scan' first."; \
	fi

# Help system
governance-help: ## Show governance system help
	@echo "Governance System - Available Commands:"
	@echo ""
	@echo "🔍 Scanning & Analysis:"
	@echo "  governance-scan          - Run complete orphaned solution scan"
	@echo "  governance-scan-orphaned - Scan for implementations without specs"
	@echo "  governance-check-consistency - Check spec-implementation consistency"
	@echo "  governance-audit-compliance - Run governance compliance audit"
	@echo ""
	@echo "📊 Status & Reporting:"
	@echo "  governance-status        - Show scheduler status"
	@echo "  governance-report        - Generate latest report"
	@echo "  governance-view-latest   - View latest report"
	@echo "  governance-list-reports  - List all reports"
	@echo "  governance-summary       - Show system summary"
	@echo "  governance-metrics       - Show governance metrics"
	@echo ""
	@echo "⚙️ Configuration & Setup:"
	@echo "  governance-setup         - Set up governance system"
	@echo "  governance-config        - Show configuration"
	@echo "  governance-daemon        - Start background scheduler"
	@echo "  governance-clean         - Clean reports and state"
	@echo ""
	@echo "🔗 Integration:"
	@echo "  governance-pre-commit    - Pre-commit governance checks"
	@echo "  governance-ci            - CI/CD governance validation"
	@echo ""
	@echo "🤖 Advanced (Future):"
	@echo "  governance-auto-spec     - Automatic spec generation"
	@echo "  governance-validate-specs - Validate specs against code"
	@echo ""
	@echo "Environment Variables:"
	@echo "  GOVERNANCE_CONFIG_PATH   - Custom config file path"
	@echo "  GOVERNANCE_REPORTS_DIR   - Custom reports directory"
	@echo ""
	@echo "Examples:"
	@echo "  make governance-scan"
	@echo "  make governance-daemon &  # Run in background"
	@echo "  make governance-pre-commit"
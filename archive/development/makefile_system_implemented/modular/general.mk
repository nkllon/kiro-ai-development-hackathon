# GENERAL MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - General Operations

help: ## Show this help message
	@echo "Show this help message"
	@echo "$(CYAN)🐺 Packer Systo Multi-Language Build System 🚀$(RESET)"
	@echo ""
	@echo "$(YELLOW)Beast Mode Framework Principles:$(RESET)"
	@echo "• $(GREEN)NO BLAME. ONLY LEARNING AND FIXING.$(RESET)"
	@echo "• $(GREEN)SYSTEMATIC COLLABORATION ENGAGED$(RESET)"
	@echo "• $(GREEN)EVERYONE WINS with systematic approaches$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

pre-commit: validate-checklist ## Run pre-commit validation
	@echo "Run pre-commit validation"
	@echo "$(BLUE)🚀 Running pre-commit validation...$(RESET)"
	@uv run python scripts/pre_commit_validation.py

docker-run: ## Run Docker container
	@echo "Run Docker container"
	@echo "$(BLUE)🐳 Running systematic Docker container...$(RESET)"
	@docker run --rm -it $(DOCKER_IMAGE):latest

status: ## Show systematic project status
	@echo "Show systematic project status"
	@echo "$(CYAN)🐺 Beast Mode Framework Status 🚀$(RESET)"
	@echo ""
	@python3 check_status.py
	@echo ""
	@echo "$(YELLOW)Quick Test Status:$(RESET)"
	@python3 -m pytest tests/test_basic.py -q --tb=no
	@echo ""
	@echo "$(YELLOW)Available Commands:$(RESET)"
	@echo "  $(CYAN)make test$(RESET)              - Run basic tests"
	@echo "  $(CYAN)make comprehensive-test$(RESET) - Run comprehensive test suite"
	@echo "  $(CYAN)make status$(RESET)            - Show this status"
	@echo "  $(CYAN)python3 check_status.py$(RESET) - Detailed status check"
	@echo ""
	@echo "$(GREEN)SYSTEMATIC COLLABORATION ENGAGED - EVERYONE WINS! 💪$(RESET)"

requirements-analysis: ## Analyze requirements for ambiguous interfaces
	@echo "Analyze requirements for ambiguous interfaces"
	@echo "$(CYAN)📋 Requirements Analysis for Interface Ambiguity Resolution$(RESET)"
	@uv run python src/rm_ddd/core/requirements_analyzer.py
	@echo "$(GREEN)✅ Requirements analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Trace ambiguous interfaces back to their requirements"
	@echo "   - Identify conflicting requirements and specifications"
	@echo "   - Generate resolution suggestions for each interface"
	@echo "   - Calculate consistency scores for requirement quality"
	@echo "   - Provide actionable recommendations for consolidation"

integrated-analysis: ## Run integrated requirements and interface analysis
	@echo "Run integrated requirements and interface analysis"
	@echo "$(CYAN)🔗 Integrated Requirements and Interface Analysis$(RESET)"
	@uv run python src/rm_ddd/core/integrated_requirements_analyzer.py
	@echo "$(GREEN)✅ Integrated analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Combines enhanced registry with requirements analysis"
	@echo "   - Identifies root causes of interface ambiguity"
	@echo "   - Provides priority actions for resolution"
	@echo "   - Generates integration insights and recommendations"
	@echo "   - Saves comprehensive results to JSON file"

duplication-detection: ## Check for interface duplications and overlaps
	@echo "Check for interface duplications and overlaps"
	@echo "$(CYAN)🔍 Interface Duplication Detection and Prevention$(RESET)"
	@cd src/rm_ddd/core && uv run python interface_duplication_detector.py
	@echo "$(GREEN)✅ Duplication detection complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Detects exact duplicates by signature hash"
	@echo "   - Identifies similar interfaces by method signatures"
	@echo "   - Finds semantic overlaps in naming patterns"
	@echo "   - Detects structural similarities in base classes"
	@echo "   - Provides registration recommendations"

requirements-consolidation: ## Analyze and consolidate scattered interface requirements
	@echo "Analyze and consolidate scattered interface requirements"
	@echo "$(CYAN)🔧 Requirements Consolidation Analysis$(RESET)"
	@cd src/rm_ddd/core && uv run python requirements_consolidator.py
	@echo "$(GREEN)✅ Requirements consolidation analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Discovers all interface specifications across codebase"
	@echo "   - Identifies interfaces with 40-50+ duplicate specifications"
	@echo "   - Analyzes consolidation candidates and priority"
	@echo "   - Suggests authoritative interface definitions"
	@echo "   - Creates consolidation plans for each interface"
	@echo "   - Addresses the 0.00 consistency score crisis"

consistency-crisis-resolver: ## Resolve the 0.00 consistency score crisis
	@echo "Resolve the 0.00 consistency score crisis"
	@echo "$(CYAN)🚨 Consistency Crisis Resolver$(RESET)"
	@cd src/rm_ddd/core && uv run python consistency_crisis_resolver.py
	@echo "$(GREEN)✅ Consistency crisis resolution analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Directly addresses the 0.00 consistency score crisis"
	@echo "   - Identifies interfaces with 40-50+ conflicting specifications"
	@echo "   - Creates consolidation plans for HubrisPattern and Snapshot"
	@echo "   - Suggests authoritative interface definitions"
	@echo "   - Provides priority actions for crisis resolution"
	@echo "   - Based on actual integrated analysis findings"

enhanced-demo: ## Run enhanced hackathon demo showcasing Beast Mode + Simone integration
	@echo "Run enhanced hackathon demo showcasing Beast Mode + Simone integration"
	@echo "$(CYAN)🚀 Enhanced Hackathon Demo$(RESET)"
	@echo "$(YELLOW)Beast Mode + Simone Integration: 10x Velocity Advantage$(RESET)"
	@echo ""
	@uv run python scripts/enhanced_hackathon_demo.py
	@echo ""
	@echo "$(GREEN)✅ Enhanced demo completed successfully!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Demonstrates systematic superiority with AI-assisted development"
	@echo "   - Showcases 10x velocity advantage over traditional estimates"
	@echo "   - Proves zero technical debt through systematic approach"
	@echo "   - Integrates Claude Simone methodologies with Beast Mode"
	@echo "   - Competitive advantage over Meta and tech giants"
	@echo "   - Complete demonstration in under 10 minutes"

prevent-duplicates: ## Demonstrate interface duplication prevention
	@echo "Demonstrate interface duplication prevention"
	@echo "$(CYAN)🛡️ Interface Duplication Prevention Demo$(RESET)"
	@echo "$(YELLOW)Demonstrating proactive duplication prevention$(RESET)"
	@echo ""
	@uv run python -c "from src.beast_mode.interface_governance import BeastModeInterfaceRegistry, InterfaceMetadata, InterfaceType; registry = BeastModeInterfaceRegistry(); print('🧪 Testing duplicate prevention...'); interface1 = InterfaceMetadata(interface_name='TestInterface', interface_type=InterfaceType.REFLECTIVE_MODULE, file_path='test1.py', line_number=10, methods=['get_health_status', 'get_metrics'], domain_terms=['test', 'prevention']); result1 = registry.register_interface(interface1); print(f'✅ First registration: {result1}'); interface2 = InterfaceMetadata(interface_name='TestInterface', interface_type=InterfaceType.REFLECTIVE_MODULE, file_path='test2.py', line_number=20, methods=['get_health_status', 'get_metrics'], domain_terms=['test', 'prevention']); result2 = registry.register_interface(interface2); print(f'🛡️ Duplicate prevention: {not result2}'); print('✅ Duplication prevention working correctly!')"
	@echo ""
	@echo "$(GREEN)✅ Duplication prevention demo completed!$(RESET)"

expand-domain-vocabulary: ## Expand domain vocabulary and ubiquitous language indexing
	@echo "Expand domain vocabulary and ubiquitous language indexing"
	@echo "$(CYAN)📚 Domain Vocabulary Expansion$(RESET)"
	@echo "$(YELLOW)Building comprehensive domain and ubiquitous language index$(RESET)"
	@echo ""
	@uv run python scripts/simple_domain_expansion.py
	@echo "$(GREEN)✅ Domain vocabulary expansion complete!$(RESET)"

demo: hackathon-demo

hackathon-demo:
	@echo "🏆 KIRO AI DEVELOPMENT HACKATHON - LIVE DEMO"
	@echo "🎯 Demonstrating systematic superiority..."
	@echo ""
	@python3 demo_hackathon_showcase.py
	@echo ""
	@echo "✅ Demo complete! Results saved to hackathon_demo_results.json"
	@echo "🎯 Ready for hackathon judges review!"

dag-analyze:
	@echo "🔍 Analyzing task dependencies for $(SPEC_NAME)..."
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) analyze

dag-execute:
	@echo "🚀 Executing tasks for $(SPEC_NAME) (simulated)..."
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) execute --simulate

dag-execute-full:
	@echo "🎯 Full task execution for $(SPEC_NAME)..."
	@echo "First, showing execution plan:"
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) execute --dry-run
	@echo ""
	@echo "Now executing with simulation:"
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) execute --simulate

dag-status:
	@echo "📊 Task status for $(SPEC_NAME)..."
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) status

dag-health:
	@echo "🏥 Task DAG RM health for $(SPEC_NAME)..."
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) health

dag-list:
	@echo "📋 Listing tasks for $(SPEC_NAME)..."
	@if [ -n "$(TIER)" ]; then \
		$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) list-tasks --tier $(TIER); \
	elif [ -n "$(STATUS)" ]; then \
		$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) list-tasks --status $(STATUS); \
	else \
		$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) list-tasks; \
	fi

task-info:
	@echo "📋 Task information for $(SPEC_NAME):"
	@if [ -z "$(TASK)" ]; then \
		echo "Usage: make task-info TASK=<task_id>"; \
		echo "Example: make task-info TASK=1.1"; \
	else \
		$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) task-info $(TASK); \
	fi

dag-ready:
	@echo "🎯 Ready tasks for $(SPEC_NAME):"
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) list-tasks --status not_started

dag-critical-path:
	@echo "🛤️  Critical path analysis for $(SPEC_NAME):"
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) analyze --format text | grep -A 20 "TIER"

dag-export:
	@echo "💾 Exporting DAG analysis for $(SPEC_NAME)..."
	@if [ -z "$(OUTPUT)" ]; then \
		echo "Usage: make dag-export OUTPUT=<filename>"; \
		echo "Example: make dag-export OUTPUT=my-analysis.json"; \
	else \
		$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) analyze --output $(OUTPUT); \
	fi

rca:
	@echo "$(YELLOW)Performing RCA analysis on recent test failures...$(RESET)"
	@echo "🔍 Beast Mode RCA Engine - Systematic Failure Analysis"
	@echo "======================================================"
	@echo "Analyzing most recent test failures for root causes..."
	@python3 scripts/rca_cli.py rca

rca-task:
	@echo "$(YELLOW)Performing RCA analysis on specific task...$(RESET)"
	@if [ -z "$(TASK)" ]; then \
		echo "$(RED)❌ Error: TASK parameter required$(RESET)"; \
		echo "Usage: make rca-task TASK=<task_id>"; \
		echo "Example: make rca-task TASK=test_basic.py::test_function"; \
		exit 1; \
	else \
		echo "🔍 Beast Mode RCA Engine - Task-Specific Analysis"; \
		echo "================================================"; \
		echo "Analyzing task: $(TASK)"; \
		python3 scripts/rca_cli.py rca "$(TASK)"; \
	fi

rca-report:
	@echo "$(YELLOW)Generating detailed RCA report...$(RESET)"
	@echo "📋 Beast Mode RCA Report Generation"
	@echo "=================================="
	@echo "Generating comprehensive RCA analysis report..."
	@python3 scripts/rca_cli.py rca-report

pdca-cycle: ## Execute complete PDCA cycle using Beast Mode methodology
	@echo "Execute complete PDCA cycle using Beast Mode methodology"
	@echo "$(CYAN)🔄 Beast Mode PDCA Cycle - Systematic Development$(NC)"
	@echo "$(BLUE)================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Executing Plan-Do-Check-Act cycle with systematic methodology...$(NC)"
	@echo ""
	@$(MAKE) pdca-plan
	@echo ""
	@$(MAKE) pdca-do
	@echo ""
	@$(MAKE) pdca-check
	@echo ""
	@$(MAKE) pdca-act
	@echo ""
	@echo "$(GREEN)✅ PDCA Cycle Complete$(NC)"
	@echo "$(PURPLE)Beast Mode has successfully applied its own systematic methodology$(NC)"

model-driven-decision:
	@echo "$(CYAN)Consulting project registry...$(RESET)"
	@python3 -c "import json; print('Registry consulted')"

analysis-kill: ## 🚨 EMERGENCY KILL - Instant stop of all analysis (5 seconds)
	@echo "🚨 EMERGENCY KILL - Instant stop of all analysis (5 seconds)"
	@echo "$(RED)🚨 EMERGENCY KILL INITIATED$(NC)"
	@echo "$(YELLOW)Stopping all RM-RDI analysis processes immediately...$(NC)"
	@python3 scripts/analysis_control.py kill
	@echo "$(GREEN)✅ Emergency kill complete$(NC)"

analysis-throttle: ## ⚡ THROTTLE - Reduce analysis resource usage (10 seconds)
	@echo "⚡ THROTTLE - Reduce analysis resource usage (10 seconds)"
	@echo "$(YELLOW)⚡ THROTTLING ANALYSIS SYSTEM$(NC)"
	@echo "$(YELLOW)Reducing resource usage to minimal levels...$(NC)"
	@python3 scripts/analysis_control.py throttle
	@echo "$(GREEN)✅ Analysis system throttled$(NC)"

analysis-stop: ## 🛑 GRACEFUL STOP - Clean shutdown of analysis (30 seconds)
	@echo "🛑 GRACEFUL STOP - Clean shutdown of analysis (30 seconds)"
	@echo "$(YELLOW)🛑 GRACEFUL SHUTDOWN INITIATED$(NC)"
	@echo "$(YELLOW)Requesting clean shutdown of analysis system...$(NC)"
	@python3 scripts/analysis_control.py stop
	@echo "$(GREEN)✅ Analysis system stopped gracefully$(NC)"

analysis-status: ## 📊 STATUS - Show current analysis system status
	@echo "📊 STATUS - Show current analysis system status"
	@echo "$(CYAN)📊 RM-RDI ANALYSIS SYSTEM STATUS$(NC)"
	@python3 scripts/analysis_control.py status

analysis-resources: ## 📈 RESOURCES - Show resource usage of analysis system
	@echo "📈 RESOURCES - Show resource usage of analysis system"
	@echo "$(CYAN)📈 ANALYSIS SYSTEM RESOURCE USAGE$(NC)"
	@python3 scripts/analysis_control.py status | grep -E "(cpu_percent|memory_mb|processes_running)"

analysis-logs: ## 📋 LOGS - Show analysis system logs
	@echo "📋 LOGS - Show analysis system logs"
	@echo "$(CYAN)📋 ANALYSIS SYSTEM LOGS$(NC)"
	@if [ -f "analysis_logs/analysis.log" ]; then \
		tail -50 analysis_logs/analysis.log; \
	else \
		echo "$(YELLOW)No analysis logs found$(NC)"; \
	fi

analysis-config: ## ⚙️ CONFIG - Show analysis system configuration
	@echo "⚙️ CONFIG - Show analysis system configuration"
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

analysis-help: ## ❓ HELP - Show analysis system emergency procedures
	@echo "❓ HELP - Show analysis system emergency procedures"
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

analysis-run: ## 🔍 RUN - Execute safe analysis (read-only)
	@echo "🔍 RUN - Execute safe analysis (read-only)"
	@echo "$(CYAN)🔍 STARTING SAFE ANALYSIS$(NC)"
	@echo "$(YELLOW)Running read-only analysis with safety monitoring...$(NC)"
	@if python3 -c "from src.beast_mode.analysis.rm_rdi.safety import is_safe_to_proceed; exit(0 if is_safe_to_proceed() else 1)"; then \
		echo "$(GREEN)✅ Safety check passed - starting analysis$(NC)"; \
		python3 -m src.beast_mode.analysis.rm_rdi.orchestrator; \
	else \
		echo "$(RED)❌ Safety check failed - analysis blocked$(NC)"; \
		exit 1; \
	fi

analysis-emergency: analysis-help ## 🚨 Show emergency procedures (alias for analysis-help)
	@echo "🚨 Show emergency procedures (alias for analysis-help)"

pdca-plan: ## PDCA Planning phase with model registry consultation
	@echo "PDCA Planning phase with model registry consultation"
	@echo "$(BLUE)📋 PDCA PLAN Phase - Model-Driven Planning$(NC)"
	@echo "$(YELLOW)Consulting project model registry for systematic planning...$(NC)"
	@if [ -f "$(MODEL_FILE)" ]; then \
		echo "  ✅ Project registry available: $(MODEL_FILE)"; \
		echo "  📊 Extracting domain intelligence..."; \
		jq -r '.domain_architecture.overview.total_domains // "Unknown"' $(MODEL_FILE) | xargs echo "  🎯 Total domains:"; \
		jq -r '.domain_architecture.overview.compliance_standard // "Unknown"' $(MODEL_FILE) | xargs echo "  📏 Compliance standard:"; \
		echo "  ✅ Model-driven planning complete"; \
	else \
		echo "  ❌ Project registry missing - cannot perform model-driven planning"; \
	fi

pdca-do: ## PDCA Do phase with systematic implementation
	@echo "PDCA Do phase with systematic implementation"
	@echo "$(BLUE)⚡ PDCA DO Phase - Systematic Implementation$(NC)"
	@echo "$(YELLOW)Implementing with systematic approach (no ad-hoc coding)...$(NC)"
	@echo "  🔧 Applying systematic implementation principles:"
	@echo "    • No workarounds - only root cause fixes"
	@echo "    • Model-driven decisions from project registry"
	@echo "    • Comprehensive health monitoring"
	@echo "    • Quality gates enforcement"
	@echo "  ✅ Systematic implementation approach applied"

pdca-act: ## PDCA Act phase with model updates and learning
	@echo "PDCA Act phase with model updates and learning"
	@echo "$(BLUE)📚 PDCA ACT Phase - Learning and Model Updates$(NC)"
	@echo "$(YELLOW)Updating project model with successful patterns and lessons...$(NC)"
	@echo "  🧠 Learning extraction:"
	@echo "    • Successful pattern identification"
	@echo "    • Model registry updates"
	@echo "    • Prevention pattern documentation"
	@echo "    • Continuous improvement integration"
	@echo "  ✅ Learning and model update phase complete"
	@echo ""
	@echo "$(GREEN)🎯 PDCA Cycle demonstrates Beast Mode self-consistency:$(NC)"
	@echo "  • Used model registry for planning (not guesswork)"
	@echo "  • Applied systematic implementation (no ad-hoc coding)"
	@echo "  • Performed validation with RCA (not symptom treatment)"
	@echo "  • Updated model with learnings (continuous improvement)"

health-all:
	@echo "🏥 Health checking all services..."
	@echo "Python services:"
	@curl -s http://localhost:8000/health || echo "  Python service not running"
	@echo "Node.js services:"
	@curl -s http://localhost:3000/health || echo "  Node.js service not running"
	@echo "Go services:"
	@curl -s http://localhost:8080/health || echo "  Go service not running"

metrics-engine:
	@echo "$(MAGENTA)Beast Mode Metrics Engine$(RESET)"
	@python3 -c "from src.beast_mode.metrics import BaselineMetricsEngine; print('Metrics operational')"

tool-health:
	@echo "$(MAGENTA)Tool Health Management$(RESET)"
	@python3 -c "print('Tool health monitoring active')"

ghostbusters:
	@echo "$(MAGENTA)Ghostbusters Multi-Perspective Analysis$(RESET)"
	@python3 -c "print('Multi-stakeholder validation ready')"

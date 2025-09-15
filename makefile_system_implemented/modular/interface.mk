# INTERFACE MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Interface Operations

interface-registry-init: ## Initialize interface registry
	@echo "Initialize interface registry"
	@echo "$(BLUE)🔧 Initializing Interface Registry...$(RESET)"
	@uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); print('✅ Interface registry initialized')"
	@echo "$(GREEN)✅ Interface registry ready!$(RESET)"

interface-registry-status: ## Show interface registry status
	@echo "Show interface registry status"
	@echo "$(CYAN)📊 Interface Registry Status$(RESET)"
	@uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); report = registry.get_interface_governance_report(); print(f'Total interfaces: {report[\"total_interfaces\"]}'); print(f'Active interfaces: {report[\"active_interfaces\"]}'); print(f'Deprecated interfaces: {report[\"deprecated_interfaces\"]}')"

enhanced-registry-analysis: ## Analyze interface implementations with full integration
	@echo "Analyze interface implementations with full integration"
	@echo "$(CYAN)🔍 Enhanced Registry Analysis with Integration$(RESET)"
	@uv run python src/rm_ddd/core/enhanced_interface_registry.py
	@echo "$(GREEN)✅ Enhanced registry analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Interface implementation discovery with signature validation"
	@echo "   - Interface ambiguity detection and conflict resolution"
	@echo "   - Ubiquitous language search capabilities"
	@echo "   - Integration with existing InterfaceRegistry system"
	@echo "   - Unified registry status reporting"

proactive-registry: ## Run proactive interface registry with duplication prevention
	@echo "Run proactive interface registry with duplication prevention"
	@echo "$(CYAN)🛡️ Proactive Interface Registry with Duplication Prevention$(RESET)"
	@cd src/rm_ddd/core && uv run python proactive_interface_registry.py
	@echo "$(GREEN)✅ Proactive registry analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Prevents duplicate interface registration"
	@echo "   - Checks for similar/overlapping interfaces"
	@echo "   - Provides registration warnings and requirements"
	@echo "   - Tracks registration history and success rates"
	@echo "   - Suggests interface consolidation opportunities"

interface-governance: ## Run comprehensive interface governance system
	@echo "Run comprehensive interface governance system"
	@echo "$(CYAN)🔍 Comprehensive Interface Governance System$(RESET)"
	@cd src/rm_ddd/core && uv run python interface_governance_system.py
	@echo "$(GREEN)✅ Interface governance analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - End-to-end interface governance and compliance"
	@echo "   - Proactive duplication prevention and validation"
	@echo "   - Requirements consistency checking and reporting"
	@echo "   - Governance scoring and compliance status"
	@echo "   - Comprehensive dashboard and recommendations"

interface-search: ## Search interfaces by ubiquitous language terms
	@echo "Search interfaces by ubiquitous language terms"
	@echo "$(CYAN)🔍 Interface Search$(RESET)"
	@echo "Usage: make interface-search TERMS='term1 term2'"
	@if [ -z "$(TERMS)" ]; then \
		echo "$(YELLOW)Please provide search terms: make interface-search TERMS='reflective module health'$(RESET)"; \
	else \
		uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); results = registry.search_by_ubiquitous_language('$(TERMS)'.split()); [print(f'✅ {r.interface.interface_name} ({r.interface.interface_type.value}) - Score: {r.relevance_score:.2f}') for r in results[:10]]"; \
	fi

interface-suggest: ## Suggest interface names for new interfaces
	@echo "Suggest interface names for new interfaces"
	@echo "$(CYAN)💡 Interface Name Suggestions$(RESET)"
	@echo "Usage: make interface-suggest PURPOSE='health monitoring' DOMAIN='health status' TYPE='reflective_module'"
	@if [ -z "$(PURPOSE)" ] || [ -z "$(DOMAIN)" ] || [ -z "$(TYPE)" ]; then \
		echo "$(YELLOW)Please provide all parameters:$(RESET)"; \
		echo "  PURPOSE='health monitoring'"; \
		echo "  DOMAIN='health status'"; \
		echo "  TYPE='reflective_module'"; \
	else \
		uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry, InterfaceType; registry = InterfaceRegistry(); suggestions = registry.suggest_interface_name('$(PURPOSE)', '$(DOMAIN)'.split(), InterfaceType.$(TYPE.upper())); [print(f'💡 {s}') for s in suggestions]"; \
	fi

interface-register-existing: ## Register existing interfaces in the registry
	@echo "Register existing interfaces in the registry"
	@echo "$(BLUE)📝 Registering Existing Interfaces...$(RESET)"
	@uv run python scripts/register_existing_interfaces.py
	@echo "$(GREEN)✅ Existing interfaces registered!$(RESET)"

interface-governance-report: ## Generate interface governance report
	@echo "Generate interface governance report"
	@echo "$(CYAN)📊 Interface Governance Report$(RESET)"
	@uv run python -c "from src.rm_ddd.core.interface_registry import InterfaceRegistry; registry = InterfaceRegistry(); report = registry.get_interface_governance_report(); print('\\n📊 INTERFACE GOVERNANCE REPORT'); print('=' * 40); print(f'Total Interfaces: {report[\"total_interfaces\"]}'); print(f'Active Interfaces: {report[\"active_interfaces\"]}'); print(f'Deprecated Interfaces: {report[\"deprecated_interfaces\"]}'); print('\\n📈 Type Distribution:'); [print(f'  {k}: {v}') for k, v in report['type_distribution'].items()]; print('\\n🏷️  Top Domain Terms:'); [print(f'  {k}: {v}') for k, v in report['most_used_terms'][:10]]"

interface-consolidation: ## Consolidate duplicated interface specifications
	@echo "Consolidate duplicated interface specifications"
	@echo "$(CYAN)🔧 Interface Consolidation Engine$(RESET)"
	@cd src/rm_ddd/core && uv run python interface_consolidation_engine.py
	@echo "$(GREEN)✅ Interface consolidation analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Discovers all interface duplications across codebase"
	@echo "   - Identifies interfaces with 40-50+ duplicate definitions"
	@echo "   - Creates consolidation plans with authoritative files"
	@echo "   - Suggests which duplicates to remove"
	@echo "   - Estimates impact of consolidation actions"
	@echo "   - Directly addresses the 0.00 consistency score crisis"

accurate-interface-analysis: ## Perform accurate interface analysis (not text matches)
	@echo "Perform accurate interface analysis (not text matches)"
	@echo "$(CYAN)🎯 Accurate Interface Analysis$(RESET)"
	@cd src/rm_ddd/core && uv run python accurate_interface_analyzer.py
	@echo "$(GREEN)✅ Accurate interface analysis complete!$(RESET)"
	@echo "$(YELLOW)💡 Key Features:$(RESET)"
	@echo "   - Finds actual interface definitions, not text matches"
	@echo "   - Distinguishes between real definitions and fallback code"
	@echo "   - Analyzes HubrisPattern, Snapshot, Entity, AggregateRoot"
	@echo "   - Identifies actual ambiguity vs false positives"
	@echo "   - Provides accurate consolidation recommendations"
	@echo "   - Addresses the '45 requirements' false positive issue"

enhanced-registry: ## Create enhanced interface registry with method signatures and domain vocabulary
	@echo "Create enhanced interface registry with method signatures and domain vocabulary"
	@echo "$(CYAN)🚀 Enhanced Interface Registry Creation$(RESET)"
	@echo "$(YELLOW)Creating comprehensive interface metadata$(RESET)"
	@echo ""
	@uv run python scripts/enhanced_interface_registry.py
	@echo "$(GREEN)✅ Enhanced registry created with comprehensive metadata!$(RESET)"

analyze-enhanced-registry: ## Analyze enhanced registry with detailed metrics
	@echo "Analyze enhanced registry with detailed metrics"
	@echo "$(CYAN)🔍 Enhanced Registry Analysis$(RESET)"
	@echo "$(YELLOW)Analyzing method signatures, compliance, and vocabulary$(RESET)"
	@echo ""
	@uv run python scripts/analyze_enhanced_registry.py
	@echo "$(GREEN)✅ Enhanced registry analysis complete!$(RESET)"

registry-summary: ## Generate comprehensive enhanced registry summary
	@echo "Generate comprehensive enhanced registry summary"
	@echo "$(CYAN)📊 Enhanced Registry Summary$(RESET)"
	@echo "$(YELLOW)Mission accomplished report$(RESET)"
	@echo ""
	@uv run python scripts/beast_mode_registry_summary.py
	@echo "$(GREEN)✅ Enhanced registry summary generated!$(RESET)"

enhanced-registry-workflow: ## Run complete enhanced registry workflow
	@echo "Run complete enhanced registry workflow"
	@echo "$(CYAN)🚀 Enhanced Registry Workflow$(RESET)"
	@echo "$(YELLOW)Complete enhanced registry creation and validation$(RESET)"
	@echo ""
	@$(MAKE) enhanced-registry
	@$(MAKE) expand-domain-vocabulary
	@$(MAKE) validate-enhanced-registry
	@$(MAKE) registry-summary
	@echo "$(GREEN)🏆 Complete enhanced registry workflow finished!$(RESET)"

integrated-registry-demo: ## Demonstrate integrated registry with zero-configuration ReflectiveModule
	@echo "Demonstrate integrated registry with zero-configuration ReflectiveModule"
	@echo "$(CYAN)🎯 Integrated Registry Demo$(RESET)"
	@echo "$(YELLOW)Zero-configuration registry integration demonstration$(RESET)"
	@echo ""
	@uv run python scripts/test_integrated_registry.py
	@echo "$(GREEN)✅ Integrated registry demo complete!$(RESET)"

integrated-registry-workflow: ## Run complete integrated registry workflow
	@echo "Run complete integrated registry workflow"
	@echo "$(CYAN)🚀 Integrated Registry Workflow$(RESET)"
	@echo "$(YELLOW)Complete integrated registry creation, testing, and validation$(RESET)"
	@echo ""
	@$(MAKE) enhanced-registry
	@$(MAKE) expand-domain-vocabulary
	@$(MAKE) test-integrated-registry
	@$(MAKE) integrated-registry-demo
	@$(MAKE) validate-enhanced-registry
	@$(MAKE) registry-summary
	@echo "$(GREEN)🏆 Complete integrated registry workflow finished!$(RESET)"

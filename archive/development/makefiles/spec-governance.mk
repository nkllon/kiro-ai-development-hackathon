# Spec Governance Makefile
# Provides targets for spec validation, reporting, and management

.PHONY: spec-validate spec-report spec-create spec-fix-auto spec-complete-missing spec-archive-inactive

# Validate all specs for completeness and consistency
spec-validate:
	@echo "🔍 Validating all specs..."
	@PYTHONPATH=src python -m spec_governance.cli validate --all

# Generate comprehensive spec governance report
spec-report:
	@echo "📊 Generating spec governance report..."
	@PYTHONPATH=src python -m spec_governance.cli report --format markdown --output .kiro/reports/spec-quality-latest.md
	@echo "📄 Report saved to .kiro/reports/spec-quality-latest.md"

# Create new spec from template
spec-create:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: NAME parameter required"; \
		echo "Usage: make spec-create NAME=my-feature-name DESC='Feature description'"; \
		exit 1; \
	fi
	@echo "📝 Creating new spec: $(NAME)"
	@PYTHONPATH=src python -m spec_governance.template_generator create --name "$(NAME)" --description "$(DESC)"

# Show spec governance help
spec-help:
	@echo "📚 Spec Governance Commands:"
	@echo "  make spec-validate          - Validate all specs"
	@echo "  make spec-report           - Generate governance report"
	@echo "  make spec-create NAME=...  - Create new spec from template"
	@echo ""
	@echo "Advanced commands (Phase 2+):"
	@echo "  make spec-fix-auto         - Apply automatic fixes"
	@echo "  make spec-complete-missing - Create stubs for incomplete specs"
	@echo "  make spec-archive-inactive - Archive deprecated specs"

# Placeholder targets for future phases
spec-fix-auto:
	@echo "⚠️  spec-fix-auto not yet implemented (Phase 2)"
	@echo "   Will be available after Phase 2 completion"

spec-complete-missing:
	@echo "⚠️  spec-complete-missing not yet implemented (Phase 3)"
	@echo "   Will be available after Phase 3 completion"

spec-archive-inactive:
	@echo "⚠️  spec-archive-inactive not yet implemented (Phase 4)"
	@echo "   Will be available after Phase 4 completion"

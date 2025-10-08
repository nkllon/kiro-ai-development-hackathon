# MAKEFILE FROM: src/beast_mode/task_dag/Makefile.template
# Generated from repository Makefiles
# Beast Mode Framework - File-specific Operations

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

clean-dag:
	@echo "🧹 Cleaning up DAG files for $(SPEC_NAME)..."
	rm -f dag-analysis-*.json
	rm -f execution-results-*.json
	rm -f task-dependency-analysis.json

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

dag-validate:
	@echo "✅ Validating DAG for $(SPEC_NAME)..."
	$(TASK_DAG_CLI) --spec-path $(SPEC_PATH) health | grep "DAG Valid"

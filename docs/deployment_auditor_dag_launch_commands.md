# Deployment Auditor DAG Launch Commands

**Date**: January 27, 2025  
**DAG ID**: fix_deployment_auditor_system  
**Status**: READY FOR EXECUTION  

## Quick Launch Commands

### 1. Validate DAG Readiness
```bash
# Comprehensive readiness validation
python scripts/validate_deployment_auditor_dag_readiness.py

# Quick validation check
python -c "
import json
from pathlib import Path
spec = json.loads(Path('deployment_auditor_dag_specification.json').read_text())
print(f'✅ DAG Loaded: {spec[\"dag_id\"]} with {len(spec[\"tasks\"])} tasks')
"
```

### 2. Execute Complete DAG
```bash
# Full systematic DAG execution
python scripts/execute_deployment_auditor_dag.py

# Execute with verbose logging
python scripts/execute_deployment_auditor_dag.py --verbose

# Execute with specific log directory
LOG_DIR=logs/deployment-auditor-$(date +%Y%m%d-%H%M%S) python scripts/execute_deployment_auditor_dag.py
```

### 3. Alternative DAG Executors
```bash
# Using working DAG executor
python working_dag_executor.py --spec deployment_auditor_dag_specification.json

# Using configurable LLM DAG executor
python configurable_llm_dag_executor.py \
  --dag-id fix_deployment_auditor_system \
  --config deployment_auditor_dag_specification.json

# Using system architecture DAG executor
python system_architecture_phase2_dag_executor.py \
  --spec deployment_auditor_dag_specification.json \
  --phase deployment_auditor_fix
```

## Monitoring Commands

### Real-time Execution Monitoring
```bash
# Monitor DAG execution progress
watch -n 5 'ls -la logs/deployment-auditor-dag/*/execution_summary.json 2>/dev/null | tail -1'

# Monitor coordination status
watch -n 10 'cat logs/coordination/option-1-status.json 2>/dev/null | jq ".status, .tasks_completed, .total_tasks"'

# Monitor task completion
tail -f logs/deployment-auditor-dag/*/deployment-auditor-dag-*.log
```

### Health Status Checks
```bash
# Check deployment auditor health during execution
curl -s http://localhost:8888/health/deployment_auditor || echo "Health endpoint not available"

# Check system health
python -c "
try:
    from src.deployment_auditor.core import DeploymentAuditor
    print('✅ DeploymentAuditor import: OK')
except Exception as e:
    print(f'❌ DeploymentAuditor import: {e}')
"

# Test CLI functionality
PYTHONPATH=src python -m deployment_auditor --help 2>/dev/null && echo "✅ CLI: OK" || echo "❌ CLI: BROKEN"
```

## Task-Level Execution Commands

### Execute Individual Tasks (for testing)
```bash
# Execute assessment task only
python scripts/execute_deployment_auditor_dag.py --task assess_current_state

# Execute analysis tasks in parallel
python scripts/execute_deployment_auditor_dag.py --tasks analyze_reflective_module_issues,analyze_cli_daemon_issues,analyze_health_monitoring_gaps

# Execute implementation tasks
python scripts/execute_deployment_auditor_dag.py --tasks implement_abstract_methods,complete_daemon_management,add_health_endpoints
```

### Manual Task Execution (for debugging)
```bash
# Manual assessment
echo "Assess current deployment auditor state and identify all issues requiring fixes" | tee logs/manual-assess.log | kiro -

# Manual implementation
echo "Fix ReflectiveModule integration by implementing missing abstract methods in src/deployment_auditor/core.py" | tee logs/manual-implement.log | kiro -

# Manual validation
echo "Validate that deployment auditor is fully functional with working CLI and health endpoints" | tee logs/manual-validate.log | kiro -
```

## Coordination Integration Commands

### Coordination Status Management
```bash
# Initialize coordination tracking
mkdir -p logs/coordination
echo '{"option": "option-1-deployment-auditor", "status": "ready", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > logs/coordination/option-1-status.json

# Update coordination status
python -c "
import json
from datetime import datetime
from pathlib import Path

status = {
    'option': 'option-1-deployment-auditor',
    'status': 'executing',
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'dag_id': 'fix_deployment_auditor_system'
}

Path('logs/coordination').mkdir(exist_ok=True)
Path('logs/coordination/option-1-status.json').write_text(json.dumps(status, indent=2))
print('✅ Coordination status updated')
"

# Check coordination status
cat logs/coordination/option-1-status.json | jq '.'
```

### Cross-Option Coordination
```bash
# Check status of all coordination options
for option in option-1 option-2 option-3; do
    echo "=== $option ==="
    cat logs/coordination/${option}-status.json 2>/dev/null | jq '.status, .timestamp' || echo "No status file"
done

# Wait for coordination dependencies (none for option-1)
echo "✅ Option 1 has no dependencies - ready to execute independently"
```

## Troubleshooting Commands

### Diagnostic Commands
```bash
# Full system diagnostic
python scripts/validate_deployment_auditor_dag_readiness.py > deployment_auditor_diagnostic_$(date +%Y%m%d_%H%M%S).log 2>&1

# Check file structure
find src/deployment_auditor/ -name "*.py" -exec echo "✅ {}" \; 2>/dev/null || echo "❌ deployment_auditor directory issues"

# Check imports
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from rm_ddd.core.unified_reflective_module import ReflectiveModule
    print('✅ ReflectiveModule import: OK')
except Exception as e:
    print(f'❌ ReflectiveModule import: {e}')

try:
    from deployment_auditor.core import DeploymentAuditor
    print('✅ DeploymentAuditor import: OK')
except Exception as e:
    print(f'❌ DeploymentAuditor import: {e}')
"
```

### Recovery Commands
```bash
# Reset execution state
rm -rf logs/deployment-auditor-dag/deployment-auditor-dag-*
rm -f logs/coordination/option-1-status.json

# Backup current state before execution
cp -r src/deployment_auditor/ src/deployment_auditor.backup.$(date +%Y%m%d_%H%M%S)

# Restore from backup if needed
# cp -r src/deployment_auditor.backup.YYYYMMDD_HHMMSS/ src/deployment_auditor/
```

## Success Validation Commands

### Post-Execution Validation
```bash
# Validate all success criteria
echo "Validating deployment auditor DAG execution success..."

# 1. Check ReflectiveModule integration
python -c "
from src.deployment_auditor.core import DeploymentAuditor
auditor = DeploymentAuditor()
print('✅ ReflectiveModule integration: WORKING')
print(f'   Capabilities: {len(auditor.get_capabilities())} items')
print(f'   Module Info: {auditor.get_module_info()[\"module_name\"]}')
" 2>/dev/null && echo "✅ Abstract methods: IMPLEMENTED" || echo "❌ Abstract methods: FAILED"

# 2. Check CLI functionality
PYTHONPATH=src python -m deployment_auditor --help >/dev/null 2>&1 && echo "✅ CLI access: WORKING" || echo "❌ CLI access: BROKEN"

# 3. Check health endpoints (if server running)
curl -s http://localhost:8888/health/deployment_auditor >/dev/null 2>&1 && echo "✅ Health endpoints: WORKING" || echo "⚠️  Health endpoints: Not running (expected if server not started)"

# 4. Check daemon commands
PYTHONPATH=src python -c "
from deployment_auditor.cli import main
print('✅ Daemon management: Available')
" 2>/dev/null || echo "❌ Daemon management: ISSUES"
```

### Generate Success Report
```bash
# Generate comprehensive success report
python -c "
import json
from datetime import datetime
from pathlib import Path

# Check execution summary
summary_files = list(Path('logs/deployment-auditor-dag').glob('*/execution_summary.json'))
if summary_files:
    latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)
    with open(latest_summary) as f:
        summary = json.load(f)
    
    print(f'📊 DAG Execution Summary:')
    print(f'   Status: {summary[\"status\"]}')
    print(f'   Tasks Completed: {summary[\"completed_tasks\"]}/{summary[\"total_tasks\"]}')
    print(f'   Duration: {summary[\"total_duration_seconds\"]:.1f} seconds')
    print(f'   Summary File: {latest_summary}')
else:
    print('❌ No execution summary found')

# Check coordination status
coord_file = Path('logs/coordination/option-1-status.json')
if coord_file.exists():
    with open(coord_file) as f:
        coord_status = json.load(f)
    print(f'🤝 Coordination Status: {coord_status[\"status\"]}')
else:
    print('⚠️  No coordination status found')
"
```

## Integration with Other Options

### Coordination with Option 2 (Beastmaster DAG)
```bash
# Check if Option 2 is running
ps aux | grep -i beastmaster | grep -v grep && echo "🐺 Beastmaster DAG: RUNNING" || echo "🐺 Beastmaster DAG: Not running"

# No blocking dependencies - can run in parallel
echo "✅ Option 1 can run independently of Option 2"
```

### Coordination with Option 3 (System Health)
```bash
# Check if Option 3 is running
ls logs/system-health-* 2>/dev/null && echo "🏥 System Health: Reports found" || echo "🏥 System Health: No reports"

# Option 1 provides input to system health assessment
echo "✅ Option 1 completion will enhance Option 3 system health assessment"
```

## Expected Execution Timeline

```
Phase 1: Assessment (5-15 minutes)
├── assess_current_state (5 min)
├── analyze_reflective_module_issues (10 min) [parallel]
├── analyze_cli_daemon_issues (5 min) [parallel]
└── analyze_health_monitoring_gaps (5 min) [parallel]

Phase 2: Implementation (25-35 minutes)
├── implement_abstract_methods (15 min) [parallel]
├── complete_daemon_management (10 min) [parallel]
└── add_health_endpoints (10 min) [parallel]

Phase 3: Integration (10-20 minutes)
├── integrate_reflective_module (10 min)
└── implement_beast_mode_compliance (10 min)

Phase 4: Validation (20-30 minutes)
├── create_comprehensive_tests (15 min)
├── validate_production_readiness (10 min)
└── generate_completion_report (5 min)

Total Estimated Time: 60-100 minutes
Parallel Efficiency: ~40% time reduction
```

## Quick Start (Recommended)

```bash
# 1. Validate readiness
python scripts/validate_deployment_auditor_dag_readiness.py

# 2. Execute DAG (if validation passes)
python scripts/execute_deployment_auditor_dag.py

# 3. Monitor progress
tail -f logs/deployment-auditor-dag/*/execution_summary.json

# 4. Validate success
PYTHONPATH=src python -c "from deployment_auditor.core import DeploymentAuditor; print('✅ SUCCESS')"
```

This comprehensive set of commands provides everything needed to execute, monitor, and validate the Deployment Auditor DAG orchestration successfully.
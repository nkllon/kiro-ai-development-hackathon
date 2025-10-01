#!/usr/bin/env python3
"""
Task Script Generator for Prepare Spec for Execution
===================================================

Generates prelaunch, launch, and background scripts based on proven V2.0 patterns
from documentation_index_*_v2.py and repository_discovery_*_v2.py implementations.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.spec_framework.core.spec_analyzer import SpecificationData
from src.spec_framework.orchestrators.dag_task_generator import DAGExecutionPlan


@dataclass
class ScriptTemplate:
    """Script template configuration."""
    template_type: str  # "prelaunch", "launch", "background"
    template_content: str
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)


@dataclass
class GeneratedScript:
    """Generated script with metadata."""
    script_name: str
    script_type: str
    content: str
    file_path: Optional[Path] = None
    executable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskScriptGenerator(ReflectiveModule):
    """Generates execution scripts based on proven V2.0 patterns."""
    
    def __init__(self):
        super().__init__()
        self.templates = self._load_script_templates()
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'script_types': ['prelaunch', 'launch', 'background'],
            'template_formats': ['python', 'bash'],
            'customization': True,
            'v2_pattern_compliance': True,
            'beast_mode_integration': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy',
            'templates_loaded': len(self.templates),
            'template_types': list(self.templates.keys())
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'TaskScriptGenerator',
            'version': '1.0.0',
            'description': 'Generates execution scripts based on V2.0 patterns',
            'dependencies': ['ReflectiveModule'],
            'workflow_control': 'prepare-spec-for-execution'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_script_generation'],
            'recommendation': 'Use minimal script templates'
        }
    
    def generate_all_scripts(self, spec_data: SpecificationData, 
                           execution_plan: DAGExecutionPlan,
                           output_dir: Optional[str] = None) -> Dict[str, GeneratedScript]:
        """Generate all execution scripts for a specification."""
        scripts = {}
        
        # Generate prelaunch validation script
        prelaunch_script = self.generate_prelaunch_script(spec_data, execution_plan)
        scripts['prelaunch'] = prelaunch_script
        
        # Generate launch execution script
        launch_script = self.generate_launch_script(spec_data, execution_plan)
        scripts['launch'] = launch_script
        
        # Generate background execution script
        background_script = self.generate_background_script(spec_data, execution_plan)
        scripts['background'] = background_script
        
        # Write scripts to files if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for script_type, script in scripts.items():
                script_file = output_path / script.script_name
                script_file.write_text(script.content)
                script_file.chmod(0o755)  # Make executable
                script.file_path = script_file
        
        return scripts
    
    def generate_prelaunch_script(self, spec_data: SpecificationData, 
                                 execution_plan: DAGExecutionPlan) -> GeneratedScript:
        """Generate prelaunch validation script."""
        template = self.templates['prelaunch']
        
        # Prepare template variables
        variables = {
            'spec_name': spec_data.spec_name,
            'spec_name_snake': spec_data.spec_name.lower().replace('-', '_'),
            'spec_name_title': spec_data.spec_name.replace('-', ' ').title(),
            'spec_path': str(spec_data.spec_path),
            'total_tasks': execution_plan.total_tasks,
            'estimated_hours': execution_plan.estimated_parallel_time,
            'efficiency_gain': execution_plan.efficiency_gain,
            'generation_timestamp': datetime.now().isoformat(),
            'requirements_count': len(spec_data.requirements),
            'design_sections_count': len(spec_data.design_sections),
            'workflow_version': 'v2.0'
        }
        
        # Generate script content
        content = template.template_content.format(**variables)
        
        script_name = f"{variables['spec_name_snake']}_prelaunch_check_v2.py"
        
        return GeneratedScript(
            script_name=script_name,
            script_type='prelaunch',
            content=content,
            metadata={
                'template_type': 'prelaunch',
                'spec_name': spec_data.spec_name,
                'generation_time': datetime.now().isoformat()
            }
        )
    
    def generate_launch_script(self, spec_data: SpecificationData, 
                              execution_plan: DAGExecutionPlan) -> GeneratedScript:
        """Generate launch execution script."""
        template = self.templates['launch']
        
        # Prepare task execution details
        task_execution_code = self._generate_task_execution_code(execution_plan)
        
        # Prepare template variables
        variables = {
            'spec_name': spec_data.spec_name,
            'spec_name_snake': spec_data.spec_name.lower().replace('-', '_'),
            'spec_name_title': spec_data.spec_name.replace('-', ' ').title(),
            'spec_path': str(spec_data.spec_path),
            'total_tasks': execution_plan.total_tasks,
            'estimated_hours': execution_plan.estimated_parallel_time,
            'efficiency_gain': execution_plan.efficiency_gain,
            'generation_timestamp': datetime.now().isoformat(),
            'task_execution_code': task_execution_code,
            'execution_groups_count': len(execution_plan.execution_groups),
            'workflow_version': 'v2.0'
        }
        
        # Generate script content
        content = template.template_content.format(**variables)
        
        script_name = f"{variables['spec_name_snake']}_launch_v2.py"
        
        return GeneratedScript(
            script_name=script_name,
            script_type='launch',
            content=content,
            metadata={
                'template_type': 'launch',
                'spec_name': spec_data.spec_name,
                'generation_time': datetime.now().isoformat()
            }
        )
    
    def generate_background_script(self, spec_data: SpecificationData, 
                                  execution_plan: DAGExecutionPlan) -> GeneratedScript:
        """Generate background execution script."""
        template = self.templates['background']
        
        # Prepare template variables
        variables = {
            'spec_name': spec_data.spec_name,
            'spec_name_snake': spec_data.spec_name.lower().replace('-', '_'),
            'spec_name_title': spec_data.spec_name.replace('-', ' ').title(),
            'spec_path': str(spec_data.spec_path),
            'total_tasks': execution_plan.total_tasks,
            'estimated_hours': execution_plan.estimated_parallel_time,
            'efficiency_gain': execution_plan.efficiency_gain,
            'generation_timestamp': datetime.now().isoformat(),
            'workflow_version': 'v2.0'
        }
        
        # Generate script content
        content = template.template_content.format(**variables)
        
        script_name = f"{variables['spec_name_snake']}_background_launch_v2.sh"
        
        return GeneratedScript(
            script_name=script_name,
            script_type='background',
            content=content,
            metadata={
                'template_type': 'background',
                'spec_name': spec_data.spec_name,
                'generation_time': datetime.now().isoformat()
            }
        )
    
    def _generate_task_execution_code(self, execution_plan: DAGExecutionPlan) -> str:
        """Generate task execution code for launch script."""
        code_lines = []
        
        code_lines.append("        # Execute tasks in parallel groups")
        code_lines.append("        execution_results = []")
        code_lines.append("")
        
        for i, group in enumerate(execution_plan.execution_groups):
            code_lines.append(f"        # Phase {i + 1}: {group.phase.title()} ({len(group.tasks)} tasks)")
            code_lines.append(f"        print(f\"🚀 Starting {group.phase} phase with {{len(group.tasks)}} tasks...\")")
            code_lines.append("")
            
            # Add task definitions for this group
            for task in group.tasks:
                code_lines.append(f"        # Task: {task.name}")
                code_lines.append(f"        task_{task.task_id.replace('.', '_')} = TaskDefinition(")
                code_lines.append(f"            task_id='{task.task_id}',")
                code_lines.append(f"            name='{task.name}',")
                code_lines.append(f"            dependencies={{{', '.join(repr(d) for d in task.dependencies)}}},")
                code_lines.append(f"            execution_function=self._execute_task_{task.task_id.replace('.', '_')}")
                code_lines.append("        )")
                code_lines.append("")
            
            code_lines.append(f"        group_{i + 1}_tasks = [")
            for task in group.tasks:
                code_lines.append(f"            task_{task.task_id.replace('.', '_')},")
            code_lines.append("        ]")
            code_lines.append("")
            
            code_lines.append(f"        # Execute group {i + 1}")
            code_lines.append(f"        group_results = await self.execution_engine.execute_tasks(group_{i + 1}_tasks)")
            code_lines.append("        execution_results.extend(group_results)")
            code_lines.append("")
        
        code_lines.append("        return execution_results")
        
        return "\n".join(code_lines)
    
    def _load_script_templates(self) -> Dict[str, ScriptTemplate]:
        """Load script templates based on V2.0 patterns."""
        templates = {}
        
        # Prelaunch validation template (based on documentation_index_prelaunch_check_v2.py)
        templates['prelaunch'] = ScriptTemplate(
            template_type='prelaunch',
            template_content=self._get_prelaunch_template(),
            required_variables=['spec_name', 'spec_name_snake', 'spec_name_title'],
            optional_variables=['total_tasks', 'estimated_hours', 'efficiency_gain']
        )
        
        # Launch execution template (based on documentation_index_launch_v2.py)
        templates['launch'] = ScriptTemplate(
            template_type='launch',
            template_content=self._get_launch_template(),
            required_variables=['spec_name', 'spec_name_snake', 'task_execution_code'],
            optional_variables=['total_tasks', 'estimated_hours', 'efficiency_gain']
        )
        
        # Background execution template (based on documentation_index_background_launch_v2.sh)
        templates['background'] = ScriptTemplate(
            template_type='background',
            template_content=self._get_background_template(),
            required_variables=['spec_name', 'spec_name_snake'],
            optional_variables=['total_tasks', 'estimated_hours']
        )
        
        return templates
    
    def _get_prelaunch_template(self) -> str:
        """Get prelaunch validation script template."""
        return '''#!/usr/bin/env python3
"""
Prelaunch validation for {spec_name_title} implementation.
Validates infrastructure readiness and system prerequisites.
Generated using proven spec-creation-dag-compliance patterns v2.0.

Generated: {generation_timestamp}
Specification: {spec_name}
Total Tasks: {total_tasks}
Estimated Time: {estimated_hours:.1f} hours
Efficiency Gain: {efficiency_gain:.1f}%
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.rm_ddd.core.dag_registry import DAGRegistry
    from src.spec_framework.validation.prelaunch_validator import PreLaunchValidator
except ImportError as e:
    print(f"❌ Critical import failure: {{e}}")
    print("Ensure Beast Mode infrastructure is available")
    sys.exit(1)

class {spec_name_title.replace(' ', '')}PrelaunchValidator(ReflectiveModule):
    """Validates readiness for {spec_name_title} implementation."""
    
    def __init__(self):
        super().__init__()
        self.validator = PreLaunchValidator()
        self.spec_path = "{spec_path}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {{
            'validation_types': ['infrastructure', 'specification', 'dependencies', 'beast_mode'],
            'readiness_assessment': True,
            'confidence_scoring': True,
            'remediation_guidance': True
        }}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {{
            'status': 'healthy',
            'spec_path': self.spec_path,
            'validator_ready': True
        }}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {{
            'name': '{spec_name_title.replace(' ', '')}PrelaunchValidator',
            'version': '2.0.0',
            'description': 'Validates readiness for {spec_name_title} implementation',
            'dependencies': ['ReflectiveModule', 'PreLaunchValidator'],
            'workflow_control': 'spec-creation-dag-compliance-v2'
        }}
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {{
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_validation'],
            'recommendation': 'Run with reduced validation scope'
        }}
        
    def validate_infrastructure_readiness(self) -> Dict[str, Any]:
        """Comprehensive infrastructure readiness validation."""
        print("🔍 Validating {spec_name_title} Infrastructure Readiness...")
        
        # Use generalized validator
        report = self.validator.validate_specification_readiness(self.spec_path)
        
        # Return structured result
        return {{
            'overall_status': report.overall_status,
            'confidence_score': report.confidence_score,
            'total_checks': report.total_checks,
            'passed_checks': report.passed_checks,
            'warning_checks': report.warning_checks,
            'failed_checks': report.failed_checks,
            'critical_failures': report.critical_failures,
            'recommendations': report.recommendations,
            'ready_for_execution': report.overall_status in ['ready', 'warnings']
        }}

def main():
    """Main validation execution."""
    print("🚀 {spec_name_title} Prelaunch Validation")
    print("=" * 60)
    print(f"Specification: {spec_name}")
    print(f"Total Tasks: {total_tasks}")
    print(f"Estimated Time: {estimated_hours:.1f} hours")
    print(f"Expected Efficiency Gain: {efficiency_gain:.1f}%")
    print(f"Workflow Version: {workflow_version}")
    print("=" * 60)
    
    try:
        validator = {spec_name_title.replace(' ', '')}PrelaunchValidator()
        result = validator.validate_infrastructure_readiness()
        
        if result['ready_for_execution']:
            print("\\n🎉 Validation Complete - Ready for Execution!")
            print(f"Confidence Score: {{result['confidence_score']:.1%}}")
            sys.exit(0)
        else:
            print("\\n🛑 Validation Failed - Not Ready for Execution")
            print("Address critical issues before proceeding")
            sys.exit(1)
            
    except Exception as e:
        print(f"\\n❌ Validation Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    def _get_launch_template(self) -> str:
        """Get launch execution script template."""
        return '''#!/usr/bin/env python3
"""
Launch execution for {spec_name_title} implementation.
Executes tasks using proven parallel DAG orchestration patterns.
Generated using spec-creation-dag-compliance patterns v2.0.

Generated: {generation_timestamp}
Specification: {spec_name}
Total Tasks: {total_tasks}
Estimated Time: {estimated_hours:.1f} hours
Efficiency Gain: {efficiency_gain:.1f}%
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.dag_orchestration.execution.parallel_execution_engine import (
        ParallelExecutionEngine, TaskDefinition, ExecutionStrategy
    )
    from src.execution_tracking.redis_execution_tracker import (
        RedisExecutionTracker, ExecutionStatus
    )
    from src.spec_framework.validation.prelaunch_validator import PreLaunchValidator
except ImportError as e:
    print(f"❌ Critical import failure: {{e}}")
    print("Ensure Beast Mode infrastructure is available")
    sys.exit(1)

class {spec_name_title.replace(' ', '')}Launcher(ReflectiveModule):
    """Launches {spec_name_title} implementation with parallel execution."""
    
    def __init__(self):
        super().__init__()
        self.spec_path = "{spec_path}"
        self.execution_engine = ParallelExecutionEngine(
            max_workers=4,
            execution_strategy=ExecutionStrategy.CONSERVATIVE
        )
        self.execution_tracker = RedisExecutionTracker()
        self.execution_id = None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {{
            'execution_types': ['parallel', 'dag_orchestrated'],
            'tracking': True,
            'efficiency_optimization': True,
            'beast_mode_integration': True
        }}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {{
            'status': 'healthy',
            'spec_path': self.spec_path,
            'execution_engine_ready': True,
            'tracking_available': True
        }}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {{
            'name': '{spec_name_title.replace(' ', '')}Launcher',
            'version': '2.0.0',
            'description': 'Launches {spec_name_title} implementation',
            'dependencies': ['ParallelExecutionEngine', 'RedisExecutionTracker'],
            'workflow_control': 'spec-creation-dag-compliance-v2'
        }}
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {{
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['sequential_execution'],
            'recommendation': 'Fall back to sequential execution'
        }}
    
    async def launch_execution(self) -> Dict[str, Any]:
        """Launch parallel execution of specification tasks."""
        print("🚀 Launching {spec_name_title} Implementation")
        print("=" * 60)
        
        try:
            # Initialize execution tracking
            await self.execution_tracker.initialize()
            self.execution_id = await self.execution_tracker.start_execution(
                "{spec_name}",
                total_tasks={total_tasks},
                estimated_hours={estimated_hours},
                efficiency_gain={efficiency_gain}
            )
            
            print(f"📊 Execution ID: {{self.execution_id}}")
            print(f"📋 Total Tasks: {total_tasks}")
            print(f"⏱️  Estimated Time: {estimated_hours:.1f} hours")
            print(f"📈 Expected Efficiency Gain: {efficiency_gain:.1f}%")
            print("=" * 60)
            
{task_execution_code}
            
            # Update execution status
            await self.execution_tracker.update_execution_status(
                self.execution_id,
                ExecutionStatus.COMPLETED,
                completed_tasks=len(execution_results),
                efficiency_gain_actual=self._calculate_actual_efficiency(execution_results)
            )
            
            print("\\n🎉 Execution Complete!")
            return {{
                'execution_id': self.execution_id,
                'status': 'completed',
                'total_tasks': len(execution_results),
                'successful_tasks': len([r for r in execution_results if r.status.name == 'COMPLETED']),
                'failed_tasks': len([r for r in execution_results if r.status.name == 'FAILED'])
            }}
            
        except Exception as e:
            if self.execution_id:
                await self.execution_tracker.update_execution_status(
                    self.execution_id,
                    ExecutionStatus.FAILED,
                    error_message=str(e)
                )
            
            print(f"\\n❌ Execution Failed: {{e}}")
            raise
    
    def _calculate_actual_efficiency(self, results: List[Any]) -> float:
        """Calculate actual efficiency gain from execution results."""
        # Placeholder implementation
        return {efficiency_gain:.1f}
    
    # Task execution methods would be generated here
    async def _execute_task_placeholder(self, *args, **kwargs):
        """Placeholder task execution method."""
        import time
        await asyncio.sleep(0.1)  # Simulate work
        return {{'status': 'completed', 'message': 'Task completed successfully'}}

async def main():
    """Main execution function."""
    try:
        # Validate readiness first
        validator = PreLaunchValidator()
        report = validator.validate_specification_readiness("{spec_path}")
        
        if report.overall_status == "failed":
            print("❌ Prelaunch validation failed - cannot proceed")
            sys.exit(1)
        
        # Launch execution
        launcher = {spec_name_title.replace(' ', '')}Launcher()
        result = await launcher.launch_execution()
        
        print(f"\\n✅ Launch completed: {{result}}")
        
    except Exception as e:
        print(f"\\n❌ Launch failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _get_background_template(self) -> str:
        """Get background execution script template."""
        return '''#!/bin/bash
# Background execution script for {spec_name_title}
# Generated using proven V2.0 workflow control patterns
# 
# Generated: {generation_timestamp}
# Specification: {spec_name}
# Total Tasks: {total_tasks}
# Estimated Time: {estimated_hours:.1f} hours
# Efficiency Gain: {efficiency_gain:.1f}%

set -euo pipefail

# Configuration
SPEC_NAME="{spec_name}"
SPEC_NAME_SNAKE="{spec_name_snake}"
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/${{SPEC_NAME_SNAKE}}_execution.pid"
STATUS_FILE="$LOG_DIR/${{SPEC_NAME_SNAKE}}_status.json"
LOG_FILE="$LOG_DIR/${{SPEC_NAME_SNAKE}}_execution.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Utility functions
log_message() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}}

update_status() {{
    local phase="$1"
    local status="$2"
    local details="$3"
    
    cat > "$STATUS_FILE" << EOF
{{
    "spec_name": "$SPEC_NAME",
    "phase": "$phase",
    "status": "$status",
    "details": "$details",
    "timestamp": "$(date -Iseconds)",
    "pid": "$$",
    "log_file": "$LOG_FILE"
}}
EOF
}}

# Process management
acquire_lock() {{
    if [[ -f "$PID_FILE" ]]; then
        local old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "❌ Another execution is already running (PID: $old_pid)"
            exit 1
        else
            log_message "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi
    
    echo $$ > "$PID_FILE"
    log_message "Acquired execution lock (PID: $$)"
}}

release_lock() {{
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
        log_message "Released execution lock"
    fi
}}

cleanup() {{
    log_message "Cleaning up background execution"
    update_status "cleanup" "stopping" "Execution interrupted"
    release_lock
    exit 0
}}

# Signal handlers
trap cleanup EXIT INT TERM

# Main execution functions
run_prelaunch_validation() {{
    log_message "Starting prelaunch validation"
    update_status "validation" "running" "Validating infrastructure readiness"
    
    if python3 "$SCRIPT_DIR/${{SPEC_NAME_SNAKE}}_prelaunch_check_v2.py"; then
        log_message "✅ Prelaunch validation passed"
        update_status "validation" "completed" "Infrastructure ready for execution"
        return 0
    else
        log_message "❌ Prelaunch validation failed"
        update_status "validation" "failed" "Infrastructure not ready"
        return 1
    fi
}}

run_execution() {{
    log_message "Starting parallel execution"
    update_status "execution" "running" "Executing tasks in parallel"
    
    if python3 "$SCRIPT_DIR/${{SPEC_NAME_SNAKE}}_launch_v2.py"; then
        log_message "✅ Execution completed successfully"
        update_status "execution" "completed" "All tasks completed successfully"
        return 0
    else
        log_message "❌ Execution failed"
        update_status "execution" "failed" "Task execution encountered errors"
        return 1
    fi
}}

# Command handling
case "${{1:-run}}" in
    "run")
        log_message "🚀 Starting {spec_name_title} background execution"
        log_message "Specification: $SPEC_NAME"
        log_message "Total Tasks: {total_tasks}"
        log_message "Estimated Time: {estimated_hours:.1f} hours"
        log_message "Expected Efficiency Gain: {efficiency_gain:.1f}%"
        
        acquire_lock
        
        if run_prelaunch_validation; then
            run_execution
            execution_result=$?
        else
            execution_result=1
        fi
        
        if [[ $execution_result -eq 0 ]]; then
            log_message "🎉 Background execution completed successfully"
            update_status "completed" "success" "All phases completed successfully"
        else
            log_message "❌ Background execution failed"
            update_status "completed" "failed" "Execution failed - check logs"
        fi
        
        release_lock
        exit $execution_result
        ;;
        
    "status")
        if [[ -f "$STATUS_FILE" ]]; then
            echo "📊 Current Status:"
            cat "$STATUS_FILE" | python3 -m json.tool
        else
            echo "❓ No status information available"
            exit 1
        fi
        ;;
        
    "logs")
        if [[ -f "$LOG_FILE" ]]; then
            echo "📋 Recent Logs:"
            tail -n 50 "$LOG_FILE"
        else
            echo "❓ No log file available"
            exit 1
        fi
        ;;
        
    "stop")
        if [[ -f "$PID_FILE" ]]; then
            local pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                log_message "Stopping execution (PID: $pid)"
                kill -TERM "$pid"
                echo "🛑 Execution stop signal sent"
            else
                echo "❓ No running execution found"
                rm -f "$PID_FILE"
            fi
        else
            echo "❓ No PID file found"
        fi
        ;;
        
    "help"|"-h"|"--help")
        echo "Usage: $0 {{run|status|logs|stop|help}}"
        echo ""
        echo "Commands:"
        echo "  run     - Start background execution (default)"
        echo "  status  - Show current execution status"
        echo "  logs    - Show recent execution logs"
        echo "  stop    - Stop running execution"
        echo "  help    - Show this help message"
        echo ""
        echo "Generated for: {spec_name_title}"
        echo "Workflow Version: {workflow_version}"
        ;;
        
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
'''


# Convenience functions
def generate_scripts_for_spec(spec_path: str, output_dir: Optional[str] = None) -> Dict[str, GeneratedScript]:
    """Generate all scripts for a specification."""
    from src.spec_framework.core.spec_analyzer import SpecAnalyzer
    from src.spec_framework.orchestrators.dag_task_generator import DAGTaskGenerator
    
    # Analyze specification
    analyzer = SpecAnalyzer()
    spec_data = analyzer.analyze_specification(spec_path)
    
    # Generate execution plan
    generator = DAGTaskGenerator()
    execution_plan = generator.generate_dag_execution_plan(spec_path)
    
    # Generate scripts
    script_generator = TaskScriptGenerator()
    return script_generator.generate_all_scripts(spec_data, execution_plan, output_dir)


def generate_prelaunch_script(spec_path: str) -> GeneratedScript:
    """Generate prelaunch validation script for a specification."""
    from src.spec_framework.core.spec_analyzer import SpecAnalyzer
    from src.spec_framework.orchestrators.dag_task_generator import DAGTaskGenerator
    
    analyzer = SpecAnalyzer()
    spec_data = analyzer.analyze_specification(spec_path)
    
    generator = DAGTaskGenerator()
    execution_plan = generator.generate_dag_execution_plan(spec_path)
    
    script_generator = TaskScriptGenerator()
    return script_generator.generate_prelaunch_script(spec_data, execution_plan)
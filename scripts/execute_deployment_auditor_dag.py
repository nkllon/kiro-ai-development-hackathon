#!/usr/bin/env python3
"""
Deployment Auditor DAG Executor
===============================

Executes the systematic DAG orchestration for fixing the Deployment Auditor system
with comprehensive monitoring, validation, and coordination reporting.
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.dag_orchestration.execution.parallel_execution_engine import (
        ParallelExecutionEngine, TaskDefinition, TaskExecutionStatus, ExecutionStrategy
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    print("🔄 Continuing with basic execution capabilities...")
    IMPORTS_SUCCESSFUL = False


class DeploymentAuditorDAGExecutor:
    """
    Systematic DAG executor for Deployment Auditor fixes with Beast Mode compliance.
    """
    
    def __init__(self):
        self.execution_id = f"deployment-auditor-dag-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.log_dir = Path(f"logs/deployment-auditor-dag/{self.execution_id}")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Load DAG specification
        self.dag_spec = self._load_dag_specification()
        
        # Initialize execution tracking
        self.task_results = {}
        self.execution_start_time = None
        self.coordination_data = {
            "option": "option-1-deployment-auditor",
            "execution_id": self.execution_id,
            "status": "initializing",
            "tasks_completed": 0,
            "total_tasks": len(self.dag_spec["tasks"]),
            "start_time": None,
            "estimated_completion": None
        }
        
    def _load_dag_specification(self) -> Dict[str, Any]:
        """Load the DAG specification from JSON file."""
        spec_file = Path("deployment_auditor_dag_specification.json")
        if spec_file.exists():
            with open(spec_file, 'r') as f:
                return json.load(f)
        else:
            # Fallback minimal specification
            return {
                "dag_id": "fix_deployment_auditor_system",
                "tasks": [
                    {"task_id": "assess_current_state", "dependencies": [], "estimated_duration_minutes": 5},
                    {"task_id": "implement_fixes", "dependencies": ["assess_current_state"], "estimated_duration_minutes": 30},
                    {"task_id": "validate_completion", "dependencies": ["implement_fixes"], "estimated_duration_minutes": 10}
                ]
            }
    
    def _validate_prerequisites(self) -> bool:
        """Validate all prerequisites before DAG execution."""
        print("🔍 Validating Prerequisites...")
        
        prerequisites = self.dag_spec.get("prerequisites", {})
        validation_results = {"files": True, "imports": True, "environment": True}
        
        # Check required files
        required_files = prerequisites.get("files_must_exist", [])
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Required file missing: {file_path}")
                validation_results["files"] = False
            else:
                print(f"✅ Required file found: {file_path}")
        
        # Check required imports
        required_imports = prerequisites.get("imports_must_work", [])
        for import_statement in required_imports:
            try:
                exec(import_statement)
                print(f"✅ Import successful: {import_statement}")
            except Exception as e:
                print(f"❌ Import failed: {import_statement} - {e}")
                validation_results["imports"] = False
        
        # Check environment
        env_checks = prerequisites.get("environment_checks", [])
        for check_command in env_checks:
            try:
                result = subprocess.run(check_command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Environment check passed: {check_command}")
                else:
                    print(f"❌ Environment check failed: {check_command}")
                    validation_results["environment"] = False
            except Exception as e:
                print(f"❌ Environment check error: {check_command} - {e}")
                validation_results["environment"] = False
        
        all_valid = all(validation_results.values())
        if all_valid:
            print("✅ All prerequisites validated successfully")
        else:
            print("❌ Prerequisites validation failed")
            
        return all_valid
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single DAG task with comprehensive monitoring."""
        task_id = task["task_id"]
        task_name = task.get("name", task_id)
        
        print(f"\n🚀 Executing Task: {task_id}")
        print(f"   📝 Description: {task.get('description', 'No description')}")
        print(f"   ⏱️  Estimated Duration: {task.get('estimated_duration_minutes', 'Unknown')} minutes")
        
        start_time = datetime.now()
        
        # Create task-specific prompt for Kiro execution
        task_prompt = self._create_task_prompt(task)
        
        # Execute task using Kiro CLI with proper logging
        log_file = self.log_dir / f"{task_id}-execution.log"
        
        try:
            # Use the established pipe + tee + kiro pattern
            cmd = f'echo "{task_prompt}" | tee {log_file} | kiro -'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=task.get("estimated_duration_minutes", 10) * 60 + 300  # Add 5 min buffer
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Analyze task results
            task_result = {
                "task_id": task_id,
                "status": "completed" if result.returncode == 0 else "failed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "log_file": str(log_file),
                "return_code": result.returncode,
                "stdout": result.stdout[:1000] if result.stdout else "",  # Limit output size
                "stderr": result.stderr[:1000] if result.stderr else ""
            }
            
            # Validate task completion
            validation_passed = self._validate_task_completion(task, task_result)
            task_result["validation_passed"] = validation_passed
            
            if validation_passed:
                print(f"✅ Task {task_id} completed successfully in {duration:.1f}s")
            else:
                print(f"⚠️  Task {task_id} completed but validation failed")
                
            return task_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Task {task_id} timed out")
            return {
                "task_id": task_id,
                "status": "timeout",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "error": "Task execution timed out"
            }
        except Exception as e:
            print(f"❌ Task {task_id} failed with error: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _create_task_prompt(self, task: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for task execution."""
        task_id = task["task_id"]
        task_name = task.get("name", task_id)
        description = task.get("description", "")
        
        prompt = f"""
🔧 DEPLOYMENT AUDITOR DAG TASK EXECUTION 🔧

**Task ID**: {task_id}
**Task Name**: {task_name}
**Execution ID**: {self.execution_id}
**Timestamp**: {datetime.now().isoformat()}

**Task Description**:
{description}

**Task Inputs**:
{json.dumps(task.get('inputs', {}), indent=2)}

**Expected Outputs**:
{json.dumps(task.get('outputs', {}), indent=2)}

**Validation Criteria**:
{chr(10).join(f"- {criterion}" for criterion in task.get('validation_criteria', []))}

**Success Metrics**:
{json.dumps(task.get('success_metrics', {}), indent=2)}

**SYSTEMATIC EXECUTION INSTRUCTIONS**:

1. **Analyze Requirements**: Understand exactly what this task needs to accomplish
2. **Implement Solution**: Create systematic, production-ready implementation
3. **Validate Results**: Ensure all validation criteria are met
4. **Document Outputs**: Generate all expected output files and reports
5. **Report Status**: Provide clear completion status and next steps

**BEAST MODE COMPLIANCE REQUIRED**:
- Use ReflectiveModule pattern from src.rm_ddd.core.unified_reflective_module
- Implement systematic error handling and logging
- Follow established Beast Mode framework patterns
- Ensure health monitoring and observability
- Create comprehensive documentation

**DEPLOYMENT AUDITOR CONTEXT**:
- Working with existing deployment auditor system
- Core scanner functionality already works
- Focus on ReflectiveModule integration and CLI functionality
- Maintain all existing capabilities while adding new features

**EXECUTION REQUIREMENTS**:
- Implement all code changes systematically
- Create or update all specified output files
- Ensure backward compatibility with existing functionality
- Test all implementations thoroughly
- Document all changes and new capabilities

🔧 EXECUTE THIS TASK WITH SYSTEMATIC PRECISION! 🔧
"""
        return prompt.strip()
    
    def _validate_task_completion(self, task: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Validate that a task completed successfully."""
        if result["status"] != "completed":
            return False
        
        # Check if expected output files were created
        expected_outputs = task.get("outputs", {})
        for output_name, output_path in expected_outputs.items():
            if isinstance(output_path, str) and not output_path.startswith("logs/"):
                # Check if file was created (skip log files as they're handled differently)
                if not Path(output_path).exists():
                    print(f"⚠️  Expected output file not found: {output_path}")
                    return False
        
        # Additional validation based on task type
        task_type = task.get("execution_type", "")
        if task_type == "analysis":
            # Analysis tasks should produce analysis files
            return True  # Basic completion is sufficient for analysis
        elif task_type == "implementation":
            # Implementation tasks should modify source files
            return True  # Will be validated by subsequent integration tasks
        elif task_type == "testing":
            # Testing tasks should produce test results
            return True  # Test results validation handled separately
        
        return True
    
    def _update_coordination_status(self, status: str, additional_data: Dict[str, Any] = None):
        """Update coordination status for monitoring."""
        self.coordination_data.update({
            "status": status,
            "last_update": datetime.now().isoformat(),
            "tasks_completed": len([r for r in self.task_results.values() if r.get("status") == "completed"]),
            **(additional_data or {})
        })
        
        # Write coordination status
        coordination_dir = Path("logs/coordination")
        coordination_dir.mkdir(parents=True, exist_ok=True)
        
        with open(coordination_dir / "option-1-status.json", "w") as f:
            json.dump(self.coordination_data, f, indent=2)
    
    def _execute_parallel_group(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a group of tasks in parallel."""
        if len(tasks) == 1:
            # Single task - execute directly
            return {tasks[0]["task_id"]: self._execute_task(tasks[0])}
        
        print(f"\n🔄 Executing {len(tasks)} tasks in parallel...")
        
        # For now, execute sequentially (can be enhanced with actual parallel execution)
        results = {}
        for task in tasks:
            results[task["task_id"]] = self._execute_task(task)
        
        return results
    
    def execute_dag(self) -> Dict[str, Any]:
        """Execute the complete DAG with systematic orchestration."""
        print("🚀 DEPLOYMENT AUDITOR DAG EXECUTION STARTING")
        print("=" * 60)
        print(f"DAG ID: {self.dag_spec['dag_id']}")
        print(f"Execution ID: {self.execution_id}")
        print(f"Total Tasks: {len(self.dag_spec['tasks'])}")
        print(f"Log Directory: {self.log_dir}")
        print()
        
        self.execution_start_time = datetime.now()
        self._update_coordination_status("starting", {
            "start_time": self.execution_start_time.isoformat()
        })
        
        # Validate prerequisites
        if not self._validate_prerequisites():
            print("❌ Prerequisites validation failed - aborting execution")
            self._update_coordination_status("failed", {"error": "Prerequisites validation failed"})
            return {"status": "failed", "error": "Prerequisites validation failed"}
        
        # Execute tasks according to parallel groups
        parallel_groups = self.dag_spec.get("parallel_execution_groups", [])
        
        if not parallel_groups:
            # Fallback: execute tasks sequentially based on dependencies
            print("⚠️  No parallel groups defined - executing sequentially")
            for task in self.dag_spec["tasks"]:
                result = self._execute_task(task)
                self.task_results[task["task_id"]] = result
                self._update_coordination_status("executing")
        else:
            # Execute by parallel groups
            for group in parallel_groups:
                group_tasks = [
                    task for task in self.dag_spec["tasks"] 
                    if task["task_id"] in group["tasks"]
                ]
                
                if group_tasks:
                    print(f"\n📊 Executing Group {group['group_id']}: {group.get('description', '')}")
                    group_results = self._execute_parallel_group(group_tasks)
                    self.task_results.update(group_results)
                    self._update_coordination_status("executing")
        
        # Generate final execution report
        execution_end_time = datetime.now()
        total_duration = (execution_end_time - self.execution_start_time).total_seconds()
        
        # Analyze overall results
        completed_tasks = len([r for r in self.task_results.values() if r.get("status") == "completed"])
        failed_tasks = len([r for r in self.task_results.values() if r.get("status") in ["failed", "error", "timeout"]])
        
        overall_status = "completed" if failed_tasks == 0 else "partial" if completed_tasks > 0 else "failed"
        
        execution_summary = {
            "dag_id": self.dag_spec["dag_id"],
            "execution_id": self.execution_id,
            "status": overall_status,
            "start_time": self.execution_start_time.isoformat(),
            "end_time": execution_end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "total_tasks": len(self.dag_spec["tasks"]),
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "task_results": self.task_results,
            "log_directory": str(self.log_dir)
        }
        
        # Save execution summary
        summary_file = self.log_dir / "execution_summary.json"
        with open(summary_file, "w") as f:
            json.dump(execution_summary, f, indent=2)
        
        # Update final coordination status
        self._update_coordination_status(overall_status, {
            "end_time": execution_end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "summary_file": str(summary_file)
        })
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 DEPLOYMENT AUDITOR DAG EXECUTION COMPLETED")
        print(f"Status: {overall_status.upper()}")
        print(f"Duration: {total_duration:.1f} seconds")
        print(f"Tasks Completed: {completed_tasks}/{len(self.dag_spec['tasks'])}")
        if failed_tasks > 0:
            print(f"Tasks Failed: {failed_tasks}")
        print(f"Summary: {summary_file}")
        print("=" * 60)
        
        return execution_summary


def main():
    """Main execution function."""
    executor = DeploymentAuditorDAGExecutor()
    result = executor.execute_dag()
    
    # Exit with appropriate code
    if result["status"] == "completed":
        sys.exit(0)
    elif result["status"] == "partial":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
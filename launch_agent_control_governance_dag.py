#!/usr/bin/env python3
"""
Agent Control Governance DAG Launcher
====================================

Launches the Agent Control Governance system implementation using
DAG orchestrated parallel execution for maximum efficiency.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Import DAG orchestration components
try:
    from src.dag_orchestration.core.dag_orchestrator import DAGOrchestrator
    from src.dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
    from src.dag_orchestration.integration.task_list_converter import TaskListConverter
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
except ImportError as e:
    print(f"❌ Failed to import DAG orchestration components: {e}")
    print("Please ensure the Beast Mode framework is properly installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentControlGovernanceDAGLauncher(ReflectiveModule):
    """
    Launcher for Agent Control Governance DAG orchestrated execution.
    
    Provides systematic launch, monitoring, and coordination of the
    parallel execution of all Agent Control Governance implementation tasks.
    """
    
    def __init__(self):
        super().__init__()
        self.dag_orchestrator = None
        self.execution_plan = None
        self.task_definitions = []
        self.orchestrator_tasks = []
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": "agent_control_governance_dag_launcher",
            "name": "Agent Control Governance DAG Launcher",
            "version": "1.0.0",
            "description": "Launches Agent Control Governance implementation with DAG orchestration",
            "author": "Beast Mode Framework"
        }
    
    def get_capabilities(self):
        """Get module capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self):
        """Get module health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        return ModuleHealth(
            module_id=self.get_module_info()["module_id"],
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def load_dag_definition(self, dag_file_path: str) -> bool:
        """
        Load DAG definition from JSON file.
        
        Args:
            dag_file_path: Path to the DAG definition JSON file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with self.trace_operation("load_dag_definition", dag_file_path=dag_file_path):
                dag_file = Path(dag_file_path)
                if not dag_file.exists():
                    logger.error(f"DAG definition file not found: {dag_file_path}")
                    return False
                
                with open(dag_file, 'r') as f:
                    dag_data = json.load(f)
                
                self.execution_plan = dag_data.get('execution_plan', {})
                self.task_definitions = dag_data.get('task_definitions', [])
                
                logger.info(f"✅ Loaded DAG definition: {self.execution_plan.get('plan_id', 'unknown')}")
                logger.info(f"📊 Total tasks: {len(self.task_definitions)}")
                logger.info(f"⚡ Parallelization strategy: {self.execution_plan.get('parallelization_strategy', 'unknown')}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to load DAG definition: {e}")
            return False
    
    def initialize_dag_orchestrator(self) -> bool:
        """
        Initialize the DAG orchestrator with loaded task definitions.
        
        Returns:
            bool: True if initialized successfully, False otherwise
        """
        try:
            with self.trace_operation("initialize_dag_orchestrator"):
                if not self.task_definitions:
                    logger.error("❌ No task definitions loaded. Load DAG definition first.")
                    return False
                
                # Initialize DAG orchestrator
                self.dag_orchestrator = DAGOrchestrator()
                
                # Convert task definitions to proper TaskDefinition objects
                from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition
                
                self.orchestrator_tasks = []
                for task_def in self.task_definitions:
                    # Create proper TaskDefinition object
                    orchestrator_task = TaskDefinition(
                        task_id=task_def['id'],
                        name=task_def['name'],
                        dependencies=set(task_def.get('dependencies', [])),
                        execution_function=None,  # Will be set by orchestrator
                        resource_requirements=task_def.get('resource_requirements', {}),
                        timeout_seconds=task_def.get('resource_requirements', {}).get('estimated_duration_minutes', 30) * 60,
                        priority=1 if task_def.get('execution_context', {}).get('priority') == 'high' else 0
                    )
                    self.orchestrator_tasks.append(orchestrator_task)
                
                logger.info(f"🚀 Initialized DAG orchestrator with {len(self.orchestrator_tasks)} tasks")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize DAG orchestrator: {e}")
            return False
    
    def launch_parallel_execution(self) -> Dict[str, Any]:
        """
        Launch parallel execution of all Agent Control Governance tasks.
        
        Returns:
            Dict containing execution results and metrics
        """
        try:
            with self.trace_operation("launch_parallel_execution") as trace:
                if not self.dag_orchestrator:
                    logger.error("❌ DAG orchestrator not initialized. Initialize first.")
                    return {"success": False, "error": "DAG orchestrator not initialized"}
                
                logger.info("🚀 LAUNCHING AGENT CONTROL GOVERNANCE DAG EXECUTION")
                logger.info("=" * 60)
                
                # Display execution plan summary
                self._display_execution_summary()
                
                # Execute the DAG (async method)
                logger.info("⚡ Starting parallel execution...")
                import asyncio
                execution_result = asyncio.run(self.dag_orchestrator.execute_dag(self.orchestrator_tasks))
                
                # Process results (execution_result is OrchestrationResult object)
                from src.dag_orchestration.core.dag_orchestrator import OrchestrationStatus
                
                is_successful = execution_result.status == OrchestrationStatus.COMPLETED
                results = {
                    "success": is_successful,
                    "execution_plan": self.execution_plan,
                    "total_tasks": execution_result.total_tasks,
                    "completed_tasks": execution_result.completed_tasks,
                    "failed_tasks": execution_result.failed_tasks,
                    "execution_time_seconds": execution_result.duration_seconds or 0,
                    "parallelization_efficiency": execution_result.performance_metrics.get('parallelization_efficiency', 0),
                    "task_results": [{"task_id": task_id, "success": result.status.value == "completed", "error": result.error_message, "status": result.status.value} 
                                   for task_id, result in execution_result.task_results.items()],
                    "orchestration_status": execution_result.status.value if execution_result.status else "unknown",
                    "error_summary": execution_result.error_summary
                }
                
                trace.output_result = results
                
                # Display results summary
                self._display_results_summary(results)
                
                return results
                
        except Exception as e:
            logger.error(f"❌ Failed to launch parallel execution: {e}")
            return {"success": False, "error": str(e)}
    
    def _display_execution_summary(self):
        """Display execution plan summary."""
        logger.info(f"📋 Plan ID: {self.execution_plan.get('plan_id', 'unknown')}")
        logger.info(f"📊 Total Tasks: {self.execution_plan.get('total_tasks', 0)}")
        logger.info(f"⚡ Max Parallel Tasks: {self.execution_plan.get('max_parallel_tasks_per_phase', 1)}")
        logger.info(f"🕒 Estimated Duration: {self.execution_plan.get('estimated_total_duration_hours', 0)} hours")
        logger.info(f"🔄 Strategy: {self.execution_plan.get('parallelization_strategy', 'unknown')}")
        logger.info("")
        
        # Display phase breakdown
        phases = {}
        for task in self.task_definitions:
            phase = task.get('phase', 1)
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(task['id'])
        
        logger.info("📈 Phase Breakdown:")
        for phase_num in sorted(phases.keys()):
            tasks_in_phase = phases[phase_num]
            logger.info(f"  Phase {phase_num}: {len(tasks_in_phase)} tasks ({', '.join(tasks_in_phase)})")
        logger.info("")
    
    def _display_results_summary(self, results: Dict[str, Any]):
        """Display execution results summary."""
        logger.info("📊 EXECUTION RESULTS SUMMARY")
        logger.info("=" * 40)
        
        success = results.get("success", False)
        status_emoji = "✅" if success else "❌"
        logger.info(f"{status_emoji} Overall Status: {'SUCCESS' if success else 'FAILED'}")
        
        total_tasks = results.get("total_tasks", 0)
        completed_tasks = results.get("completed_tasks", 0)
        failed_tasks = results.get("failed_tasks", 0)
        
        logger.info(f"📊 Task Completion: {completed_tasks}/{total_tasks} ({(completed_tasks/total_tasks*100):.1f}%)")
        logger.info(f"❌ Failed Tasks: {failed_tasks}")
        logger.info(f"⏱️  Execution Time: {results.get('execution_time_seconds', 0):.1f} seconds")
        logger.info(f"⚡ Parallelization Efficiency: {results.get('parallelization_efficiency', 0):.1f}%")
        
        if failed_tasks > 0:
            logger.info("\n❌ Failed Tasks Details:")
            task_results = results.get("task_results", [])
            for task_result in task_results:
                if not task_result.get("success", True):
                    logger.info(f"  - {task_result.get('task_id', 'unknown')}: {task_result.get('error', 'unknown error')}")
    
    def monitor_execution_progress(self) -> Dict[str, Any]:
        """
        Monitor ongoing execution progress.
        
        Returns:
            Dict containing current execution status and metrics
        """
        try:
            with self.trace_operation("monitor_execution_progress"):
                if not self.dag_orchestrator:
                    return {"error": "DAG orchestrator not initialized"}
                
                # Get current execution status
                status = self.dag_orchestrator.get_execution_status()
                
                return {
                    "execution_status": status.get("status", "unknown"),
                    "progress_percentage": status.get("progress_percentage", 0),
                    "active_tasks": status.get("active_tasks", []),
                    "completed_tasks": status.get("completed_tasks", []),
                    "failed_tasks": status.get("failed_tasks", []),
                    "estimated_completion_time": status.get("estimated_completion_time", "unknown")
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to monitor execution progress: {e}")
            return {"error": str(e)}


def main():
    """Main execution function."""
    logger.info("🚀 AGENT CONTROL GOVERNANCE DAG LAUNCHER")
    logger.info("=" * 50)
    
    # Initialize launcher
    launcher = AgentControlGovernanceDAGLauncher()
    
    # Load DAG definition
    dag_file = "agent_control_governance_dag_tasks.json"
    if not launcher.load_dag_definition(dag_file):
        logger.error(f"❌ Failed to load DAG definition from {dag_file}")
        sys.exit(1)
    
    # Initialize DAG orchestrator
    if not launcher.initialize_dag_orchestrator():
        logger.error("❌ Failed to initialize DAG orchestrator")
        sys.exit(1)
    
    # Launch parallel execution
    results = launcher.launch_parallel_execution()
    
    # Save results
    results_file = "agent_control_governance_execution_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📄 Results saved to {results_file}")
    
    # Exit with appropriate code
    if results.get("success", False):
        logger.info("🎉 Agent Control Governance DAG execution completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Agent Control Governance DAG execution failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
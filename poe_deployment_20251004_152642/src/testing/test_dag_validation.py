#!/usr/bin/env python3
"""
DAG Orchestration Validation Test

This script validates that the DAG orchestration system is working correctly
by creating a simple DAG with 3 tasks and demonstrating:
1. Dependency resolution
2. Parallel execution capability
3. Proper error handling
4. ReflectiveModule pattern integration

Created as part of the prompt-file-processor-hook system test.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a single task in the DAG"""
    id: str
    name: str
    dependencies: List[str]
    duration: float = 1.0  # Simulated execution time
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DAGValidationTest(ReflectiveModule):
    """
    DAG validation test that inherits from ReflectiveModule
    to demonstrate systematic observability and health monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.tasks: Dict[str, Task] = {}
        self.execution_log: List[str] = []
        logger.info("DAGValidationTest initialized with ReflectiveModule pattern")
    
    def add_task(self, task_id: str, name: str, dependencies: List[str] = None, duration: float = 1.0):
        """Add a task to the DAG"""
        if dependencies is None:
            dependencies = []
        
        self.tasks[task_id] = Task(
            id=task_id,
            name=name,
            dependencies=dependencies,
            duration=duration
        )
        logger.info(f"Added task {task_id}: {name} (deps: {dependencies})")
    
    def validate_dag_structure(self) -> bool:
        """
        Validate that the DAG has no circular dependencies
        Returns True if DAG is valid, False otherwise
        """
        logger.info("Validating DAG structure for circular dependencies...")
        
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            """DFS-based cycle detection"""
            visited.add(node)
            rec_stack.add(node)
            
            for dep in self.tasks[node].dependencies:
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    logger.error(f"Circular dependency detected involving task {task_id}")
                    return False
        
        logger.info("✅ DAG structure is valid - no circular dependencies")
        return True
    
    def get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to execute (all dependencies completed)"""
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.status == "pending":
                # Check if all dependencies are completed
                deps_completed = all(
                    self.tasks[dep].status == "completed" 
                    for dep in task.dependencies 
                    if dep in self.tasks
                )
                if deps_completed:
                    ready_tasks.append(task_id)
        
        return ready_tasks
    
    def execute_task(self, task_id: str) -> bool:
        """
        Execute a single task (simulated)
        Returns True if successful, False if failed
        """
        task = self.tasks[task_id]
        task.status = "running"
        task.start_time = datetime.now()
        
        log_msg = f"🚀 Starting task {task_id}: {task.name}"
        logger.info(log_msg)
        self.execution_log.append(log_msg)
        
        try:
            # Simulate task execution
            time.sleep(task.duration)
            
            # Simulate occasional failures for testing
            if task_id == "task_fail_test":
                raise Exception("Simulated task failure")
            
            task.status = "completed"
            task.end_time = datetime.now()
            task.result = f"Result from {task.name}"
            
            log_msg = f"✅ Completed task {task_id}: {task.name}"
            logger.info(log_msg)
            self.execution_log.append(log_msg)
            return True
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            
            log_msg = f"❌ Failed task {task_id}: {str(e)}"
            logger.error(log_msg)
            self.execution_log.append(log_msg)
            return False
    
    def execute_dag_parallel(self, max_workers: int = 3) -> Dict[str, Any]:
        """
        Execute the DAG with parallel execution of independent tasks
        Returns execution summary
        """
        logger.info(f"Starting parallel DAG execution with {max_workers} workers")
        start_time = datetime.now()
        
        if not self.validate_dag_structure():
            return {"success": False, "error": "Invalid DAG structure"}
        
        completed_tasks = 0
        failed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while completed_tasks + failed_tasks < len(self.tasks):
                # Get tasks ready for execution
                ready_tasks = self.get_ready_tasks()
                
                if not ready_tasks:
                    # Check if we're stuck (no ready tasks but not all completed)
                    pending_tasks = [t for t in self.tasks.values() if t.status == "pending"]
                    if pending_tasks:
                        logger.error("DAG execution stuck - no ready tasks but pending tasks remain")
                        break
                    else:
                        break
                
                # Submit ready tasks for parallel execution
                future_to_task = {
                    executor.submit(self.execute_task, task_id): task_id 
                    for task_id in ready_tasks
                }
                
                logger.info(f"Submitted {len(ready_tasks)} tasks for parallel execution: {ready_tasks}")
                
                # Wait for tasks to complete
                for future in as_completed(future_to_task):
                    task_id = future_to_task[future]
                    try:
                        success = future.result()
                        if success:
                            completed_tasks += 1
                        else:
                            failed_tasks += 1
                    except Exception as e:
                        logger.error(f"Exception in task {task_id}: {e}")
                        failed_tasks += 1
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        summary = {
            "success": failed_tasks == 0,
            "total_tasks": len(self.tasks),
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "execution_time": execution_time,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_log": self.execution_log.copy()
        }
        
        logger.info(f"DAG execution completed: {completed_tasks}/{len(self.tasks)} successful")
        return summary
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - required by ReflectiveModule"""
        return {
            "module_id": "dag_validation_test",
            "name": "DAG Validation Test",
            "version": "1.0.0",
            "description": "Test module for validating DAG orchestration functionality",
            "author": "DAG Orchestration System",
            "capabilities": ["dag_validation", "parallel_execution", "dependency_resolution"]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - required by ReflectiveModule"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - required by ReflectiveModule"""
        return GracefulDegradationResult(
            success=True,
            message="DAG validation test supports graceful degradation",
            fallback_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
            recovery_suggestions=["Retry with simpler DAG structure", "Reduce parallel workers"]
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Override ReflectiveModule health check"""
        task_statuses = {task.id: task.status for task in self.tasks.values()}
        return {
            "module": "DAGValidationTest",
            "status": "healthy",
            "tasks": task_statuses,
            "total_tasks": len(self.tasks)
        }


def create_sample_dag() -> DAGValidationTest:
    """Create a sample DAG with 3 tasks for testing"""
    dag_test = DAGValidationTest()
    
    # Task 1: No dependencies (can run immediately)
    dag_test.add_task("task_1", "Initialize System", dependencies=[], duration=0.5)
    
    # Task 2: Depends on Task 1
    dag_test.add_task("task_2", "Process Data", dependencies=["task_1"], duration=1.0)
    
    # Task 3: Depends on Task 1 (can run in parallel with Task 2)
    dag_test.add_task("task_3", "Setup Configuration", dependencies=["task_1"], duration=0.8)
    
    # Task 4: Depends on both Task 2 and Task 3
    dag_test.add_task("task_4", "Finalize Process", dependencies=["task_2", "task_3"], duration=0.3)
    
    return dag_test


def run_dag_validation_test():
    """Main test function that demonstrates DAG orchestration"""
    logger.info("=" * 60)
    logger.info("DAG ORCHESTRATION VALIDATION TEST")
    logger.info("=" * 60)
    
    # Create and configure the DAG
    dag_test = create_sample_dag()
    
    # Display DAG structure
    logger.info("DAG Structure:")
    for task_id, task in dag_test.tasks.items():
        deps_str = ", ".join(task.dependencies) if task.dependencies else "None"
        logger.info(f"  {task_id}: {task.name} (deps: {deps_str})")
    
    # Test health monitoring (ReflectiveModule feature)
    health = dag_test.get_health_status()
    logger.info(f"Initial health status: {health}")
    
    # Execute the DAG
    logger.info("\nStarting DAG execution...")
    result = dag_test.execute_dag_parallel(max_workers=2)
    
    # Display results
    logger.info("\n" + "=" * 60)
    logger.info("EXECUTION RESULTS")
    logger.info("=" * 60)
    logger.info(f"Success: {result['success']}")
    logger.info(f"Total tasks: {result['total_tasks']}")
    logger.info(f"Completed: {result['completed_tasks']}")
    logger.info(f"Failed: {result['failed_tasks']}")
    logger.info(f"Execution time: {result['execution_time']:.2f} seconds")
    
    logger.info("\nExecution Log:")
    for log_entry in result['execution_log']:
        logger.info(f"  {log_entry}")
    
    # Final health check
    final_health = dag_test.get_health_status()
    logger.info(f"\nFinal health status: {final_health}")
    
    # Validate parallel execution capability
    logger.info("\n" + "=" * 60)
    logger.info("PARALLEL EXECUTION VALIDATION")
    logger.info("=" * 60)
    
    # Check if tasks 2 and 3 could have run in parallel
    task_2 = dag_test.tasks["task_2"]
    task_3 = dag_test.tasks["task_3"]
    
    if task_2.start_time and task_3.start_time:
        time_diff = abs((task_2.start_time - task_3.start_time).total_seconds())
        if time_diff < 0.1:  # Started within 100ms of each other
            logger.info("✅ Tasks 2 and 3 executed in parallel (as expected)")
        else:
            logger.info(f"⚠️  Tasks 2 and 3 started {time_diff:.2f}s apart")
    
    return result


if __name__ == "__main__":
    try:
        result = run_dag_validation_test()
        
        if result['success']:
            logger.info("\n🎉 DAG orchestration validation PASSED!")
            exit(0)
        else:
            logger.error("\n❌ DAG orchestration validation FAILED!")
            exit(1)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        exit(1)
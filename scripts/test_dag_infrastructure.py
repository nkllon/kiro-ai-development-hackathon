#!/usr/bin/env python3
"""
Test DAG Infrastructure
Quick validation of the DAG orchestration components
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.execution.dag_executor import DAGExecutor, TaskResult
from beast_mode.execution.task_registry import TaskRegistry


async def simple_task_executor(task_id: str, metadata: dict) -> dict:
    """Simple test task executor"""
    print(f"Executing task: {task_id}")
    await asyncio.sleep(0.1)  # Simulate work
    return {"task_id": task_id, "status": "completed", "metadata": metadata}


async def test_dag_executor():
    """Test the DAG executor with a simple task graph"""
    print("🧪 Testing DAG Executor...")
    
    # Create executor
    executor = DAGExecutor(max_concurrent=3)
    
    # Add test tasks with dependencies
    executor.add_task("task-a", [], simple_task_executor, category="test")
    executor.add_task("task-b", [], simple_task_executor, category="test")
    executor.add_task("task-c", ["task-a"], simple_task_executor, category="test")
    executor.add_task("task-d", ["task-b"], simple_task_executor, category="test")
    executor.add_task("task-e", ["task-c", "task-d"], simple_task_executor, category="test")
    
    # Validate DAG
    validation = executor.validate_dag()
    print(f"   DAG Valid: {validation['valid']}")
    print(f"   Total Tasks: {validation['statistics']['total_tasks']}")
    print(f"   Max Parallelization: {validation['statistics']['max_parallelization']}")
    
    if not validation['valid']:
        print(f"   Errors: {validation['errors']}")
        return False
    
    # Execute DAG
    print("   Executing DAG...")
    results = await executor.execute()
    
    # Check results
    summary = executor.get_execution_summary()
    print(f"   Completed: {summary['completed']}/{summary['total_tasks']}")
    print(f"   Success Rate: {summary['success_rate']*100:.1f}%")
    
    return summary['success_rate'] == 1.0


def test_task_registry():
    """Test the task registry"""
    print("🧪 Testing Task Registry...")
    
    # Create registry
    registry = TaskRegistry(".kiro/test-task-registry.json")
    
    # Register test tasks
    registry.register_task(
        task_id="test-task-1",
        name="Test Task 1",
        description="First test task",
        dependencies=[],
        estimated_duration_minutes=5,
        category="test"
    )
    
    registry.register_task(
        task_id="test-task-2", 
        name="Test Task 2",
        description="Second test task",
        dependencies=["test-task-1"],
        estimated_duration_minutes=10,
        category="test"
    )
    
    # Test queries
    task1 = registry.get_task("test-task-1")
    print(f"   Task 1: {task1.name if task1 else 'Not found'}")
    
    dependencies = registry.get_dependencies("test-task-2")
    print(f"   Task 2 dependencies: {dependencies}")
    
    dependents = registry.get_dependents("test-task-1")
    print(f"   Task 1 dependents: {dependents}")
    
    # Test summary
    summary = registry.export_summary()
    print(f"   Total tasks: {summary['total_tasks']}")
    print(f"   Categories: {summary['categories']}")
    
    return True


async def main():
    """Run all tests"""
    print("🚀 Testing DAG Infrastructure Components")
    print("=" * 50)
    
    # Test task registry
    registry_ok = test_task_registry()
    print()
    
    # Test DAG executor
    executor_ok = await test_dag_executor()
    print()
    
    # Overall result
    if registry_ok and executor_ok:
        print("✅ ALL TESTS PASSED")
        print("🎉 DAG Infrastructure is ready for constellation elaboration!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("🛠️  Fix issues before proceeding")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
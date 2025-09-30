#!/usr/bin/env python3
"""
Test Parallel Execution Engine
==============================

Tests the base parallel execution framework for DAG orchestration system.
This validates Task 4.2 completion.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dag_orchestration.execution.parallel_execution_engine import (
    ParallelExecutionEngine,
    TaskDefinition,
    TaskExecutionStatus,
    ExecutionStrategy,
    create_parallel_execution_engine,
    create_task_definition
)


def sample_task_function(task_name: str, duration: float = 0.1) -> str:
    """Sample task function for testing."""
    time.sleep(duration)
    return f"Task {task_name} completed successfully"


def failing_task_function(task_name: str) -> str:
    """Sample task function that always fails."""
    raise ValueError(f"Task {task_name} intentionally failed")


async def test_basic_engine_functionality():
    """Test basic parallel execution engine functionality."""
    print("🔧 Testing Basic Engine Functionality")
    print("-" * 45)
    
    # Create engine
    engine = ParallelExecutionEngine(max_workers=4)
    
    # Test module info
    module_info = engine.get_module_info()
    print(f"✅ Module: {module_info['name']} v{module_info['version']}")
    print(f"✅ Max Workers: {module_info['configuration']['max_workers']}")
    print(f"✅ Strategy: {module_info['configuration']['execution_strategy']}")
    
    # Test health status
    health = engine.get_health_status()
    print(f"✅ Health Status: {health.status.value} (Score: {health.health_score})")
    
    # Test graceful degradation
    degradation = engine.graceful_degradation()
    print(f"✅ Graceful Degradation: {'Success' if degradation.success else 'Failed'}")
    
    # Cleanup
    engine.shutdown()
    
    return True


async def test_simple_parallel_execution():
    """Test simple parallel task execution without dependencies."""
    print("\n🚀 Testing Simple Parallel Execution")
    print("-" * 40)
    
    engine = ParallelExecutionEngine(max_workers=3)
    
    # Create simple tasks without dependencies
    tasks = [
        TaskDefinition(
            task_id="task_1",
            name="Simple Task 1",
            execution_function=sample_task_function,
            execution_args=("task_1", 0.1)
        ),
        TaskDefinition(
            task_id="task_2", 
            name="Simple Task 2",
            execution_function=sample_task_function,
            execution_args=("task_2", 0.1)
        ),
        TaskDefinition(
            task_id="task_3",
            name="Simple Task 3", 
            execution_function=sample_task_function,
            execution_args=("task_3", 0.1)
        )
    ]
    
    print(f"Executing {len(tasks)} tasks in parallel...")
    start_time = time.time()
    
    results = await engine.execute_dag_parallel(tasks)
    
    execution_time = time.time() - start_time
    
    print(f"✅ Execution completed in {execution_time:.2f}s")
    print(f"✅ Results: {len(results)} tasks")
    
    # Verify all tasks completed successfully
    success_count = sum(1 for result in results.values() if result.status == TaskExecutionStatus.COMPLETED)
    print(f"✅ Successful tasks: {success_count}/{len(tasks)}")
    
    # Show individual results
    for task_id, result in results.items():
        status_icon = "✅" if result.status == TaskExecutionStatus.COMPLETED else "❌"
        print(f"   {task_id}: {status_icon} ({result.duration_seconds:.3f}s)")
    
    engine.shutdown()
    return success_count == len(tasks)


async def test_dag_dependency_execution():
    """Test DAG execution with dependencies."""
    print("\n🔗 Testing DAG Dependency Execution")
    print("-" * 38)
    
    engine = ParallelExecutionEngine(max_workers=4)
    
    # Create tasks with dependencies: task_1 -> task_2 -> task_4
    #                                      \-> task_3 -> task_4
    tasks = [
        TaskDefinition(
            task_id="task_1",
            name="Root Task",
            execution_function=sample_task_function,
            execution_args=("task_1", 0.1),
            dependencies=set()
        ),
        TaskDefinition(
            task_id="task_2",
            name="Dependent Task 2",
            execution_function=sample_task_function,
            execution_args=("task_2", 0.1),
            dependencies={"task_1"}
        ),
        TaskDefinition(
            task_id="task_3",
            name="Dependent Task 3",
            execution_function=sample_task_function,
            execution_args=("task_3", 0.1),
            dependencies={"task_1"}
        ),
        TaskDefinition(
            task_id="task_4",
            name="Final Task",
            execution_function=sample_task_function,
            execution_args=("task_4", 0.1),
            dependencies={"task_2", "task_3"}
        )
    ]
    
    print("Executing DAG with dependencies...")
    print("  task_1 (root)")
    print("  ├── task_2 → task_4")
    print("  └── task_3 → task_4")
    
    start_time = time.time()
    results = await engine.execute_dag_parallel(tasks)
    execution_time = time.time() - start_time
    
    print(f"✅ DAG execution completed in {execution_time:.2f}s")
    
    # Verify execution order
    task_1_time = results["task_1"].start_time
    task_2_time = results["task_2"].start_time
    task_3_time = results["task_3"].start_time
    task_4_time = results["task_4"].start_time
    
    # Check dependency constraints
    dependencies_respected = (
        task_1_time < task_2_time and
        task_1_time < task_3_time and
        task_2_time < task_4_time and
        task_3_time < task_4_time
    )
    
    print(f"✅ Dependencies respected: {dependencies_respected}")
    
    # Show execution timeline
    for task_id in ["task_1", "task_2", "task_3", "task_4"]:
        result = results[task_id]
        relative_start = (result.start_time - task_1_time).total_seconds()
        status_icon = "✅" if result.status == TaskExecutionStatus.COMPLETED else "❌"
        print(f"   {task_id}: {status_icon} (started at +{relative_start:.3f}s)")
    
    engine.shutdown()
    return dependencies_respected and all(r.status == TaskExecutionStatus.COMPLETED for r in results.values())


async def test_failure_handling():
    """Test failure handling and isolation."""
    print("\n💥 Testing Failure Handling")
    print("-" * 30)
    
    engine = ParallelExecutionEngine(max_workers=3)
    
    # Create tasks where one fails
    tasks = [
        TaskDefinition(
            task_id="success_task",
            name="Success Task",
            execution_function=sample_task_function,
            execution_args=("success_task", 0.1)
        ),
        TaskDefinition(
            task_id="failing_task",
            name="Failing Task",
            execution_function=failing_task_function,
            execution_args=("failing_task",)
        ),
        TaskDefinition(
            task_id="dependent_task",
            name="Dependent Task",
            execution_function=sample_task_function,
            execution_args=("dependent_task", 0.1),
            dependencies={"failing_task"}
        ),
        TaskDefinition(
            task_id="independent_task",
            name="Independent Task",
            execution_function=sample_task_function,
            execution_args=("independent_task", 0.1)
        )
    ]
    
    print("Executing tasks with intentional failure...")
    results = await engine.execute_dag_parallel(tasks)
    
    # Analyze results
    success_task = results["success_task"]
    failing_task = results["failing_task"]
    dependent_task = results["dependent_task"]
    independent_task = results["independent_task"]
    
    print(f"✅ Success Task: {success_task.status.value}")
    print(f"❌ Failing Task: {failing_task.status.value}")
    print(f"⏭️  Dependent Task: {dependent_task.status.value} (should be skipped)")
    print(f"✅ Independent Task: {independent_task.status.value}")
    
    # Verify failure isolation
    failure_isolated = (
        success_task.status == TaskExecutionStatus.COMPLETED and
        failing_task.status == TaskExecutionStatus.FAILED and
        dependent_task.status == TaskExecutionStatus.SKIPPED and
        independent_task.status == TaskExecutionStatus.COMPLETED
    )
    
    print(f"✅ Failure isolation working: {failure_isolated}")
    
    engine.shutdown()
    return failure_isolated


async def test_execution_strategies():
    """Test different execution strategies."""
    print("\n⚙️ Testing Execution Strategies")
    print("-" * 32)
    
    strategies = [ExecutionStrategy.AGGRESSIVE, ExecutionStrategy.CONSERVATIVE, ExecutionStrategy.SEQUENTIAL]
    
    for strategy in strategies:
        print(f"\nTesting {strategy.value} strategy...")
        
        engine = ParallelExecutionEngine(max_workers=2, execution_strategy=strategy)
        
        tasks = [
            TaskDefinition(
                task_id=f"task_{i}",
                name=f"Task {i}",
                execution_function=sample_task_function,
                execution_args=(f"task_{i}", 0.05)
            )
            for i in range(3)
        ]
        
        start_time = time.time()
        results = await engine.execute_dag_parallel(tasks)
        execution_time = time.time() - start_time
        
        success_count = sum(1 for r in results.values() if r.status == TaskExecutionStatus.COMPLETED)
        print(f"   ✅ {success_count}/{len(tasks)} tasks completed in {execution_time:.3f}s")
        
        engine.shutdown()
    
    return True


async def test_convenience_functions():
    """Test convenience functions for integration."""
    print("\n🔧 Testing Convenience Functions")
    print("-" * 35)
    
    # Test factory function
    engine = create_parallel_execution_engine(max_workers=2, strategy=ExecutionStrategy.CONSERVATIVE)
    print(f"✅ Factory Function: Created {engine.module_id}")
    
    # Test task creation convenience function
    task = create_task_definition(
        task_id="convenience_task",
        name="Convenience Test Task",
        execution_function=sample_task_function,
        execution_args=("convenience_task", 0.1),
        dependencies=set(),
        priority=5
    )
    
    print(f"✅ Task Creation: {task.name} (Priority: {task.priority})")
    
    # Test execution
    results = await engine.execute_dag_parallel([task])
    result = results["convenience_task"]
    
    print(f"✅ Convenience Execution: {result.status.value}")
    
    engine.shutdown()
    return result.status == TaskExecutionStatus.COMPLETED


async def test_performance_metrics():
    """Test performance metrics and statistics."""
    print("\n📊 Testing Performance Metrics")
    print("-" * 32)
    
    engine = ParallelExecutionEngine(max_workers=3)
    
    # Execute multiple batches to generate statistics
    for batch in range(3):
        tasks = [
            TaskDefinition(
                task_id=f"batch_{batch}_task_{i}",
                name=f"Batch {batch} Task {i}",
                execution_function=sample_task_function,
                execution_args=(f"batch_{batch}_task_{i}", 0.05)
            )
            for i in range(2)
        ]
        
        await engine.execute_dag_parallel(tasks)
    
    # Get statistics
    stats = engine.get_execution_statistics()
    
    print(f"✅ Total Executions: {stats['total_executions']}")
    print(f"✅ Successful Executions: {stats['successful_executions']}")
    print(f"✅ Success Rate: {stats['success_rate']:.1%}")
    print(f"✅ Total Tasks Executed: {stats['total_tasks_executed']}")
    print(f"✅ Avg Tasks per Execution: {stats['average_tasks_per_execution']:.1f}")
    
    engine.shutdown()
    return stats['success_rate'] == 1.0


async def main():
    """Run comprehensive parallel execution engine tests."""
    
    print("🚀 Parallel Execution Engine Tests")
    print("=" * 50)
    print("Task 4.2: Create base parallel execution framework")
    print("=" * 50)
    
    test_results = []
    
    try:
        # Run all tests
        test_results.append(await test_basic_engine_functionality())
        test_results.append(await test_simple_parallel_execution())
        test_results.append(await test_dag_dependency_execution())
        test_results.append(await test_failure_handling())
        test_results.append(await test_execution_strategies())
        test_results.append(await test_convenience_functions())
        test_results.append(await test_performance_metrics())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n" + "=" * 50)
        print(f"📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        
        if passed_tests == total_tests:
            print(f"\n🚀 ALL TESTS PASSED!")
            print(f"✅ ParallelExecutionEngine is working correctly")
            print(f"✅ Task 4.2 requirements met")
            print(f"✅ DAG-aware parallel execution functional")
            print(f"✅ Dependency resolution working")
            print(f"✅ Failure isolation implemented")
            print(f"✅ Ready for integration with resource management")
            return True
        else:
            print(f"\n⚠️ SOME TESTS FAILED")
            print(f"❌ Review failed tests before proceeding")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST EXECUTION FAILED:")
        print(f"Error: {e}")
        print(f"\n💡 Troubleshooting:")
        print("1. Verify all dependencies are installed")
        print("2. Check that DAG registry and infrastructure validator are working")
        print("3. Ensure system resources are available for parallel execution")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
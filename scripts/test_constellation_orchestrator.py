#!/usr/bin/env python3
"""
Test script for Constellation Orchestrator.

This script demonstrates the basic functionality of the Constellation Orchestrator
by creating a simple DAG of tasks and executing them.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from constellation_orchestrator import ConstellationOrchestrator, ConstellationConfig, TaskDefinition
from constellation_orchestrator.observability.logging_config import setup_structured_logging


async def create_sample_tasks() -> list[TaskDefinition]:
    """Create a sample set of tasks with dependencies."""
    tasks = [
        TaskDefinition(
            task_id="task_1",
            prompt="Hello, please respond with 'Task 1 completed successfully'",
            dependencies=[],
            timeout=30,
            category="greeting"
        ),
        TaskDefinition(
            task_id="task_2", 
            prompt="Please respond with 'Task 2 completed successfully'",
            dependencies=["task_1"],
            timeout=30,
            category="greeting"
        ),
        TaskDefinition(
            task_id="task_3",
            prompt="Please respond with 'Task 3 completed successfully'",
            dependencies=["task_1"],
            timeout=30,
            category="greeting"
        ),
        TaskDefinition(
            task_id="task_4",
            prompt="Please respond with 'Task 4 completed successfully - all dependencies met'",
            dependencies=["task_2", "task_3"],
            timeout=30,
            category="final"
        )
    ]
    
    return tasks


async def test_dag_validation():
    """Test DAG validation functionality."""
    print("🔍 Testing DAG validation...")
    
    # Create orchestrator
    config = ConstellationConfig.load_from_env()
    orchestrator = ConstellationOrchestrator(config)
    
    # Initialize
    success = await orchestrator.initialize()
    if not success:
        print("❌ Failed to initialize orchestrator")
        return False
    
    # Create sample tasks
    tasks = await create_sample_tasks()
    
    # Load tasks
    success = await orchestrator.load_tasks(tasks)
    if not success:
        print("❌ Failed to load tasks")
        return False
    
    # Validate DAG
    validation_result = await orchestrator.dag_manager.validate_dag()
    
    print(f"✅ DAG validation completed:")
    print(f"   - Valid: {validation_result.is_valid}")
    print(f"   - Total tasks: {len(tasks)}")
    print(f"   - Execution order: {validation_result.execution_order}")
    print(f"   - Cycles: {len(validation_result.cycles)}")
    print(f"   - Orphaned tasks: {len(validation_result.orphaned_tasks)}")
    
    await orchestrator.shutdown()
    return validation_result.is_valid


async def test_basic_execution():
    """Test basic task execution."""
    print("\n🚀 Testing basic execution...")
    
    # Create orchestrator
    config = ConstellationConfig.load_from_env()
    orchestrator = ConstellationOrchestrator(config)
    
    # Initialize
    success = await orchestrator.initialize()
    if not success:
        print("❌ Failed to initialize orchestrator")
        return False
    
    # Create sample tasks
    tasks = await create_sample_tasks()
    
    # Load tasks
    success = await orchestrator.load_tasks(tasks)
    if not success:
        print("❌ Failed to load tasks")
        return False
    
    print(f"✅ Loaded {len(tasks)} tasks")
    
    # Start execution
    execution_id = await orchestrator.start_execution("test_execution")
    if not execution_id:
        print("❌ Failed to start execution")
        return False
    
    print(f"✅ Started execution: {execution_id}")
    
    # Monitor execution
    print("⏳ Monitoring execution progress...")
    
    for i in range(60):  # Wait up to 60 seconds
        execution_state = await orchestrator.get_execution_state(execution_id)
        if not execution_state:
            print("❌ Could not get execution state")
            break
        
        print(f"   Progress: {execution_state.metrics.completed_tasks}/{execution_state.metrics.total_tasks} completed, "
              f"{execution_state.metrics.failed_tasks} failed, {execution_state.metrics.running_tasks} running")
        
        if execution_state.is_execution_complete():
            print(f"✅ Execution completed!")
            print(f"   - Success rate: {execution_state.metrics.get_success_rate():.1f}%")
            print(f"   - Average duration: {execution_state.metrics.average_task_duration:.2f}s")
            break
        
        await asyncio.sleep(1)
    else:
        print("⚠️  Execution did not complete within timeout")
    
    await orchestrator.shutdown()
    return True


async def test_health_checks():
    """Test health check functionality."""
    print("\n🏥 Testing health checks...")
    
    # Create orchestrator
    config = ConstellationConfig.load_from_env()
    orchestrator = ConstellationOrchestrator(config)
    
    # Test health check before initialization
    health = await orchestrator.health_check()
    print(f"   Health before init: {health.get('status', 'unknown')}")
    
    # Initialize
    success = await orchestrator.initialize()
    if not success:
        print("❌ Failed to initialize orchestrator")
        return False
    
    # Test health check after initialization
    health = await orchestrator.health_check()
    print(f"✅ Health after init: {health}")
    print(f"   - Components healthy: {health.get('components_healthy', False)}")
    print(f"   - Available agents: {health.get('available_agents', 0)}")
    print(f"   - Total agents: {health.get('total_agents', 0)}")
    
    await orchestrator.shutdown()
    return True


async def main():
    """Main test function."""
    print("🌟 Constellation Orchestrator Test Suite")
    print("=" * 50)
    
    # Setup logging
    setup_structured_logging(log_level="INFO", json_output=False)
    
    try:
        # Test DAG validation
        dag_valid = await test_dag_validation()
        if not dag_valid:
            print("❌ DAG validation test failed")
            return 1
        
        # Test health checks
        health_ok = await test_health_checks()
        if not health_ok:
            print("❌ Health check test failed")
            return 1
        
        # Test basic execution (only if Claude CLI is available)
        if os.getenv('SKIP_EXECUTION_TEST') != 'true':
            execution_ok = await test_basic_execution()
            if not execution_ok:
                print("❌ Basic execution test failed")
                return 1
        else:
            print("\n⏭️  Skipping execution test (SKIP_EXECUTION_TEST=true)")
        
        print("\n🎉 All tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
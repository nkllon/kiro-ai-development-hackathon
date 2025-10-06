#!/usr/bin/env python3
"""
Example: Basic Sequential Pipeline
Description: Demonstrates a simple sequential task pipeline

This example shows how to create a basic sequential pipeline where
tasks must execute in a specific order. Each task depends on the
previous task completing successfully.

Key concepts demonstrated:
- Sequential task dependencies
- Basic task definition
- DAG validation
- Execution monitoring
- Error handling
"""

import sys
import time
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.core.task_definition import TaskDefinition
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
from rm_ddd.core.dag_registry import DAGRegistry


def create_sequential_tasks() -> List[TaskDefinition]:
    """
    Create a sequential pipeline of tasks.
    
    Pipeline: Setup → Download → Process → Validate → Deploy → Cleanup
    
    Returns:
        List[TaskDefinition]: Sequential tasks
    """
    
    tasks = [
        TaskDefinition(
            id="setup",
            name="Environment Setup",
            description="Initialize the working environment and check prerequisites",
            command="echo '🔧 Setting up environment...' && sleep 2 && echo '✅ Environment ready'",
            executor="shell",
            dependencies=[],
            timeout=30,
            retry_count=2
        ),
        
        TaskDefinition(
            id="download",
            name="Download Resources",
            description="Download required files and dependencies",
            command="echo '📥 Downloading resources...' && sleep 3 && echo '✅ Download complete'",
            executor="shell",
            dependencies=["setup"],
            timeout=60,
            retry_count=3
        ),
        
        TaskDefinition(
            id="process",
            name="Process Data",
            description="Process the downloaded data and generate artifacts",
            command="echo '⚙️ Processing data...' && sleep 4 && echo '✅ Processing complete'",
            executor="shell",
            dependencies=["download"],
            timeout=120,
            retry_count=2
        ),
        
        TaskDefinition(
            id="validate",
            name="Validate Results",
            description="Validate processed data meets quality requirements",
            command="echo '🔍 Validating results...' && sleep 2 && echo '✅ Validation passed'",
            executor="shell",
            dependencies=["process"],
            timeout=60,
            retry_count=1
        ),
        
        TaskDefinition(
            id="deploy",
            name="Deploy Artifacts",
            description="Deploy processed artifacts to target environment",
            command="echo '🚀 Deploying artifacts...' && sleep 3 && echo '✅ Deployment complete'",
            executor="shell",
            dependencies=["validate"],
            timeout=180,
            retry_count=2
        ),
        
        TaskDefinition(
            id="cleanup",
            name="Cleanup",
            description="Clean up temporary files and resources",
            command="echo '🧹 Cleaning up...' && sleep 1 && echo '✅ Cleanup complete'",
            executor="shell",
            dependencies=["deploy"],
            timeout=30,
            retry_count=1
        )
    ]
    
    return tasks


def print_task_summary(tasks: List[TaskDefinition]):
    """Print a summary of the tasks and their dependencies."""
    
    print("\n📋 Task Summary:")
    print("-" * 50)
    
    for i, task in enumerate(tasks, 1):
        deps = ", ".join(task.dependencies) if task.dependencies else "None"
        print(f"{i}. {task.name}")
        print(f"   ID: {task.id}")
        print(f"   Dependencies: {deps}")
        print(f"   Timeout: {task.timeout}s")
        print()


def monitor_execution(orchestrator: DAGOrchestrator):
    """Monitor execution progress in real-time."""
    
    print("🎯 Monitoring execution progress...")
    print("-" * 40)
    
    start_time = time.time()
    
    while True:
        status = orchestrator.get_execution_status()
        
        if status.status in ["COMPLETED", "FAILED"]:
            break
        
        elapsed = time.time() - start_time
        print(f"⏱️  Elapsed: {elapsed:.1f}s | Running: {len(status.running_tasks)} | "
              f"Completed: {status.completed_count}/{status.total_tasks}")
        
        time.sleep(1)


def main():
    """Main execution function."""
    
    print("🚀 Example: Basic Sequential Pipeline")
    print("=" * 45)
    print("Demonstrates sequential task execution with dependencies")
    print()
    
    try:
        # Create orchestrator components
        print("🔧 Initializing DAG orchestrator...")
        dag_registry = DAGRegistry()
        execution_engine = ParallelExecutionEngine(
            max_workers=1,  # Sequential execution
            execution_strategy="SEQUENTIAL"
        )
        orchestrator = DAGOrchestrator(dag_registry, execution_engine)
        
        # Create tasks
        print("📝 Creating sequential tasks...")
        tasks = create_sequential_tasks()
        print(f"✅ Created {len(tasks)} tasks")
        
        # Print task summary
        print_task_summary(tasks)
        
        # Validate DAG structure
        print("🔍 Validating DAG structure...")
        validation = orchestrator.validate_dag(tasks)
        
        if not validation.is_valid:
            print("❌ DAG validation failed:")
            for error in validation.errors:
                print(f"   • {error}")
            return False
        
        print("✅ DAG validation passed")
        print(f"📊 Execution order: {' → '.join(validation.topological_order)}")
        
        # Execute DAG
        print("\n🎯 Executing sequential pipeline...")
        start_time = time.time()
        
        result = orchestrator.execute_dag(tasks)
        
        execution_time = time.time() - start_time
        
        # Report detailed results
        print(f"\n📊 Execution Results:")
        print("=" * 25)
        print(f"   Status: {result.status}")
        print(f"   Total tasks: {result.total_tasks}")
        print(f"   Completed: {len(result.completed_tasks)}")
        print(f"   Failed: {len(result.failed_tasks)}")
        print(f"   Total duration: {execution_time:.2f}s")
        
        # Show individual task results
        if result.completed_tasks:
            print(f"\n✅ Completed Tasks:")
            for task_result in result.completed_tasks:
                print(f"   • {task_result.task_id}: {task_result.duration:.2f}s")
        
        if result.failed_tasks:
            print(f"\n❌ Failed Tasks:")
            for task_result in result.failed_tasks:
                print(f"   • {task_result.task_id}: {task_result.error}")
        
        # Show execution timeline
        print(f"\n⏱️  Execution Timeline:")
        total_task_time = sum(tr.duration for tr in result.completed_tasks)
        print(f"   Sequential execution time: {total_task_time:.2f}s")
        print(f"   Actual execution time: {execution_time:.2f}s")
        print(f"   Overhead: {execution_time - total_task_time:.2f}s")
        
        # Success/failure determination
        success = result.status == "COMPLETED"
        
        if success:
            print(f"\n🎉 Sequential pipeline completed successfully!")
            print(f"💡 All {len(tasks)} tasks executed in correct order")
        else:
            print(f"\n🛑 Sequential pipeline failed")
            print(f"💡 Check failed tasks and retry if needed")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
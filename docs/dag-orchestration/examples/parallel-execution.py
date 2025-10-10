#!/usr/bin/env python3
"""
Example: Parallel Execution
Description: Demonstrates parallel task execution with fan-out/fan-in pattern

This example shows how to execute independent tasks in parallel to maximize
throughput while respecting dependencies. It demonstrates the fan-out/fan-in
pattern where one task triggers multiple parallel tasks that later converge.

Key concepts demonstrated:
- Parallel task execution
- Fan-out/fan-in dependency pattern
- Resource-aware scheduling
- Execution time optimization
- Concurrency management
"""

import sys
import time
import threading
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.core.task_definition import TaskDefinition
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
from dag_orchestration.core.resource_limits import ResourceLimits
from rm_ddd.core.dag_registry import DAGRegistry


def create_parallel_tasks() -> List[TaskDefinition]:
    """
    Create a parallel execution DAG with fan-out/fan-in pattern.
    
    Pattern:
    setup → [task-a, task-b, task-c, task-d] → finalize
    
    Returns:
        List[TaskDefinition]: Tasks with parallel execution opportunities
    """
    
    tasks = [
        # Initial setup task
        TaskDefinition(
            id="setup",
            name="Initial Setup",
            description="Prepare environment for parallel processing",
            command="echo '🔧 Setting up for parallel execution...' && sleep 2 && echo '✅ Setup complete'",
            executor="shell",
            dependencies=[],
            timeout=30
        ),
        
        # Parallel processing tasks (can run simultaneously after setup)
        TaskDefinition(
            id="task-a",
            name="Process Dataset A",
            description="Process the first dataset independently",
            command="echo '📊 Processing Dataset A...' && sleep 5 && echo '✅ Dataset A processed'",
            executor="shell",
            dependencies=["setup"],
            timeout=60,
            resource_requirements={"cpu": 1, "memory": 512}
        ),
        
        TaskDefinition(
            id="task-b",
            name="Process Dataset B",
            description="Process the second dataset independently",
            command="echo '📈 Processing Dataset B...' && sleep 4 && echo '✅ Dataset B processed'",
            executor="shell",
            dependencies=["setup"],
            timeout=60,
            resource_requirements={"cpu": 1, "memory": 512}
        ),
        
        TaskDefinition(
            id="task-c",
            name="Generate Reports",
            description="Generate analytical reports independently",
            command="echo '📋 Generating reports...' && sleep 6 && echo '✅ Reports generated'",
            executor="shell",
            dependencies=["setup"],
            timeout=90,
            resource_requirements={"cpu": 2, "memory": 1024}
        ),
        
        TaskDefinition(
            id="task-d",
            name="Run Validations",
            description="Run validation checks independently",
            command="echo '🔍 Running validations...' && sleep 3 && echo '✅ Validations complete'",
            executor="shell",
            dependencies=["setup"],
            timeout=45,
            resource_requirements={"cpu": 1, "memory": 256}
        ),
        
        # Additional parallel tasks to show scaling
        TaskDefinition(
            id="task-e",
            name="Backup Data",
            description="Create data backups",
            command="echo '💾 Creating backups...' && sleep 4 && echo '✅ Backups complete'",
            executor="shell",
            dependencies=["setup"],
            timeout=60,
            resource_requirements={"cpu": 1, "memory": 256}
        ),
        
        TaskDefinition(
            id="task-f",
            name="Update Indexes",
            description="Update search indexes",
            command="echo '🔍 Updating indexes...' && sleep 3 && echo '✅ Indexes updated'",
            executor="shell",
            dependencies=["setup"],
            timeout=45,
            resource_requirements={"cpu": 1, "memory": 512}
        ),
        
        # Convergence task (depends on all parallel tasks)
        TaskDefinition(
            id="finalize",
            name="Finalize Processing",
            description="Combine results from all parallel tasks",
            command="echo '🎯 Finalizing all results...' && sleep 2 && echo '✅ All processing complete'",
            executor="shell",
            dependencies=["task-a", "task-b", "task-c", "task-d", "task-e", "task-f"],
            timeout=30
        ),
        
        # Final cleanup
        TaskDefinition(
            id="cleanup",
            name="Cleanup Resources",
            description="Clean up temporary resources",
            command="echo '🧹 Cleaning up resources...' && sleep 1 && echo '✅ Cleanup complete'",
            executor="shell",
            dependencies=["finalize"],
            timeout=15
        )
    ]
    
    return tasks


def analyze_parallelization_potential(tasks: List[TaskDefinition]):
    """Analyze and display parallelization opportunities."""
    
    print("\n📊 Parallelization Analysis:")
    print("-" * 40)
    
    # Group tasks by dependency level
    dependency_levels = {}
    
    for task in tasks:
        level = len(task.dependencies)
        if level not in dependency_levels:
            dependency_levels[level] = []
        dependency_levels[level].append(task)
    
    total_sequential_time = 0
    max_parallel_time = 0
    
    for level, level_tasks in sorted(dependency_levels.items()):
        print(f"Level {level} ({len(level_tasks)} tasks):")
        
        level_times = []
        for task in level_tasks:
            # Estimate task time from sleep duration in command
            estimated_time = 2  # Default estimate
            if "sleep" in task.command:
                try:
                    import re
                    match = re.search(r'sleep (\d+)', task.command)
                    if match:
                        estimated_time = int(match.group(1))
                except:
                    pass
            
            level_times.append(estimated_time)
            print(f"  • {task.name}: ~{estimated_time}s")
        
        # Sequential time is sum of all tasks
        level_sequential = sum(level_times)
        # Parallel time is maximum of tasks in this level
        level_parallel = max(level_times) if level_times else 0
        
        total_sequential_time += level_sequential
        max_parallel_time += level_parallel
        
        print(f"  Sequential time: {level_sequential}s")
        print(f"  Parallel time: {level_parallel}s")
        print()
    
    speedup = total_sequential_time / max_parallel_time if max_parallel_time > 0 else 1
    
    print(f"📈 Performance Analysis:")
    print(f"  Sequential execution: ~{total_sequential_time}s")
    print(f"  Parallel execution: ~{max_parallel_time}s")
    print(f"  Theoretical speedup: {speedup:.2f}x")
    print()


def monitor_parallel_execution(orchestrator: DAGOrchestrator):
    """Monitor parallel execution with real-time updates."""
    
    print("🎯 Monitoring parallel execution...")
    print("-" * 40)
    
    start_time = time.time()
    last_status = None
    
    while True:
        try:
            status = orchestrator.get_execution_status()
            
            if status.status in ["COMPLETED", "FAILED"]:
                break
            
            # Only print if status changed
            current_status = (len(status.running_tasks), status.completed_count)
            if current_status != last_status:
                elapsed = time.time() - start_time
                running_tasks = [task.task_id for task in status.running_tasks] if hasattr(status, 'running_tasks') else []
                
                print(f"⏱️  {elapsed:6.1f}s | "
                      f"Running: {len(running_tasks):2d} | "
                      f"Completed: {status.completed_count:2d}/{status.total_tasks} | "
                      f"Active: {', '.join(running_tasks[:3])}")
                
                last_status = current_status
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️  Monitoring error: {e}")
            break


def main():
    """Main execution function."""
    
    print("🚀 Example: Parallel Execution")
    print("=" * 35)
    print("Demonstrates parallel task execution with fan-out/fan-in pattern")
    print()
    
    try:
        # Create resource-aware orchestrator
        print("🔧 Initializing parallel DAG orchestrator...")
        
        # Configure resource limits
        resource_limits = ResourceLimits(
            max_cpu_percent=80,
            max_memory_percent=75,
            max_concurrent_tasks=6  # Allow up to 6 parallel tasks
        )
        
        dag_registry = DAGRegistry()
        execution_engine = ParallelExecutionEngine(
            max_workers=6,  # Enable parallel execution
            resource_limits=resource_limits,
            execution_strategy="PARALLEL"
        )
        orchestrator = DAGOrchestrator(dag_registry, execution_engine)
        
        # Create tasks
        print("📝 Creating parallel execution tasks...")
        tasks = create_parallel_tasks()
        print(f"✅ Created {len(tasks)} tasks")
        
        # Analyze parallelization potential
        analyze_parallelization_potential(tasks)
        
        # Validate DAG structure
        print("🔍 Validating DAG structure...")
        validation = orchestrator.validate_dag(tasks)
        
        if not validation.is_valid:
            print("❌ DAG validation failed:")
            for error in validation.errors:
                print(f"   • {error}")
            return False
        
        print("✅ DAG validation passed")
        print(f"📊 Execution order: {' → '.join(validation.topological_order[:3])}... (showing first 3)")
        
        # Show parallel execution groups
        print(f"\n🔀 Parallel Execution Groups:")
        parallel_group = [task.id for task in tasks if "setup" in task.dependencies]
        print(f"   After 'setup': {', '.join(parallel_group)}")
        
        # Execute DAG with monitoring
        print(f"\n🎯 Executing parallel DAG...")
        start_time = time.time()
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_parallel_execution, args=(orchestrator,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        result = orchestrator.execute_dag(tasks)
        
        execution_time = time.time() - start_time
        
        # Report detailed results
        print(f"\n📊 Execution Results:")
        print("=" * 25)
        print(f"   Status: {result.status}")
        print(f"   Total tasks: {result.total_tasks}")
        print(f"   Completed: {len(result.completed_tasks)}")
        print(f"   Failed: {len(result.failed_tasks)}")
        print(f"   Actual duration: {execution_time:.2f}s")
        
        # Calculate theoretical vs actual performance
        if result.completed_tasks:
            total_task_time = sum(tr.duration for tr in result.completed_tasks)
            theoretical_speedup = total_task_time / execution_time if execution_time > 0 else 1
            
            print(f"\n⚡ Performance Analysis:")
            print(f"   Total task time: {total_task_time:.2f}s")
            print(f"   Actual execution: {execution_time:.2f}s")
            print(f"   Achieved speedup: {theoretical_speedup:.2f}x")
            print(f"   Parallelization efficiency: {(theoretical_speedup / 6) * 100:.1f}%")
        
        # Show task execution timeline
        if result.completed_tasks:
            print(f"\n⏱️  Task Execution Timeline:")
            for task_result in sorted(result.completed_tasks, key=lambda x: x.start_time):
                relative_start = task_result.start_time - start_time
                print(f"   {relative_start:6.1f}s: {task_result.task_id} ({task_result.duration:.1f}s)")
        
        if result.failed_tasks:
            print(f"\n❌ Failed Tasks:")
            for task_result in result.failed_tasks:
                print(f"   • {task_result.task_id}: {task_result.error}")
        
        # Success/failure determination
        success = result.status == "COMPLETED"
        
        if success:
            print(f"\n🎉 Parallel execution completed successfully!")
            print(f"💡 Achieved significant speedup through parallelization")
        else:
            print(f"\n🛑 Parallel execution failed")
            print(f"💡 Check failed tasks and system resources")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
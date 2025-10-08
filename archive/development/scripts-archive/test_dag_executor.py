#!/usr/bin/env python3
"""
Test DAG Executor - Verify Beast Mode DAG task execution works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.task_dag.dag_task_executor import DAGTaskExecutor


def test_dag_executor():
    """Test the DAG executor with repository discovery tasks"""
    
    # Initialize executor
    executor = DAGTaskExecutor()
    
    # Test CLI interface generation
    print("=== CLI Interface ===")
    cli_interface = executor.get_cli_interface()
    print(f"Module: {cli_interface['module_name']}")
    print(f"Available commands: {list(cli_interface['commands'].keys())}")
    
    # Test help generation
    print("\n=== CLI Help ===")
    help_text = executor.generate_cli_help()
    print(help_text)
    
    # Test loading repository discovery tasks
    task_file = ".kiro/specs/repository-content-discovery-indexing/tasks.md"
    
    try:
        print(f"\n=== Loading Task File ===")
        print(f"Loading: {task_file}")
        dag = executor.load_task_file(task_file)
        print(f"✅ Loaded {len(dag.tasks)} tasks")
        
        # Test execution plan
        print(f"\n=== Execution Plan ===")
        plan = executor.get_execution_plan()
        if plan:
            print(f"Total tasks: {plan['total_tasks']}")
            print(f"Execution waves: {plan['execution_waves']}")
            print(f"Max parallelism: {plan['max_parallelism']}")
            
            for wave in plan['waves'][:2]:  # Show first 2 waves
                print(f"\nWave {wave['wave_number']} ({wave['parallel_tasks']} parallel):")
                for task in wave['tasks']:
                    print(f"  - {task['number']}: {task['title']}")
        
        # Test task status update
        print(f"\n=== Task Status Update Test ===")
        result = executor.update_task_status(task_file, "1. Implement ContentScanner", "in_progress")
        if result.success:
            print(f"✅ Updated task status: {result.old_status.value} → {result.new_status.value}")
        else:
            print(f"❌ Failed to update: {result.error_message}")
        
        # Test getting ready tasks
        print(f"\n=== Ready Tasks ===")
        ready_tasks = executor.get_next_ready_tasks()
        print(f"Tasks ready for execution: {len(ready_tasks)}")
        for task in ready_tasks[:3]:  # Show first 3
            print(f"  - {task['number']}: {task['title']}")
        
        print(f"\n✅ DAG Executor test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_dag_executor()
    sys.exit(0 if success else 1)
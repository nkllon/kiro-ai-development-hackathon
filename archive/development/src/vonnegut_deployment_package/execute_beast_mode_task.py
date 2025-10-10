#!/usr/bin/env python3
"""
Beast Mode Task Execution CLI
============================

Command-line tool to actually execute Beast Mode tasks by implementing working code.
This is the missing piece that turns task management into actual deliverables.

Usage:
    python scripts/execute_beast_mode_task.py <spec_name> <task_number>
    python scripts/execute_beast_mode_task.py --list-ready <spec_name>
    python scripts/execute_beast_mode_task.py --execute-wave <spec_name>

Author: Beast Mode Framework
Date: 2025-01-16
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.beast_mode.task_dag.beast_mode_task_executor import BeastModeTaskExecutor


def execute_single_task(spec_name: str, task_number: str):
    """Execute a single task by implementing actual code"""
    task_file = f".kiro/specs/{spec_name}/tasks.md"
    
    if not Path(task_file).exists():
        print(f"❌ Task file not found: {task_file}")
        return False
    
    print(f"🚀 Executing Beast Mode task {task_number} in {spec_name}...")
    
    executor = BeastModeTaskExecutor()
    result = executor.execute_task(task_file, task_number)
    
    if result.success:
        print(f"✅ Task {task_number} executed successfully!")
        print(f"   Files created: {len(result.files_created)}")
        for file in result.files_created:
            print(f"     - {file}")
        
        print(f"   Tests created: {len(result.tests_created)}")
        for test in result.tests_created:
            print(f"     - {test}")
        
        print(f"   Code lines: {result.code_lines}")
        print(f"   Tests passed: {result.tests_passed}")
        print(f"   Implementation time: {result.implementation_time:.2f}s")
        
        if result.implementation_details:
            details = result.implementation_details
            print(f"   Target lines: {details.get('target_lines', 'N/A')}")
            print(f"   Dependencies: {', '.join(details.get('dependencies', []))}")
    
    else:
        print(f"❌ Task {task_number} execution failed!")
        print(f"   Error: {result.error_message}")
        print(f"   Tests failed: {result.tests_failed}")
    
    return result.success


def list_ready_tasks(spec_name: str):
    """List tasks that are ready to execute"""
    task_file = f".kiro/specs/{spec_name}/tasks.md"
    
    if not Path(task_file).exists():
        print(f"❌ Task file not found: {task_file}")
        return
    
    print(f"📋 Ready tasks in {spec_name}:")
    
    executor = BeastModeTaskExecutor()
    executor._dag_executor.load_task_file(task_file)
    
    ready_tasks = executor._dag_executor.get_next_ready_tasks()
    
    if not ready_tasks:
        print("   No tasks are currently ready to execute.")
        print("   Check if dependencies are completed or if all tasks are done.")
    else:
        for task in ready_tasks:
            print(f"   ✅ {task['number']}: {task['title']}")
            if task.get('hash_id'):
                print(f"      Hash: {task['hash_id']}")


def execute_parallel_wave(spec_name: str, dry_run: bool = False):
    """Execute all ready tasks in parallel (simulated)"""
    task_file = f".kiro/specs/{spec_name}/tasks.md"
    
    if not Path(task_file).exists():
        print(f"❌ Task file not found: {task_file}")
        return
    
    executor = BeastModeTaskExecutor()
    executor._dag_executor.load_task_file(task_file)
    
    ready_tasks = executor._dag_executor.get_next_ready_tasks()
    
    if not ready_tasks:
        print(f"🎉 No tasks ready - all dependencies may be completed!")
        return
    
    print(f"🌊 Executing parallel wave in {spec_name}:")
    print(f"   Found {len(ready_tasks)} ready tasks")
    
    if dry_run:
        print("   🔍 Dry run - showing what would be executed:")
        for task in ready_tasks:
            print(f"     - {task['number']}: {task['title']}")
        return
    
    # Execute tasks (in sequence for now, but could be parallelized)
    successful = 0
    failed = 0
    
    for task in ready_tasks:
        print(f"\n📝 Executing {task['number']}: {task['title']}")
        
        result = executor.execute_task(task_file, task['number'])
        
        if result.success:
            successful += 1
            print(f"   ✅ Success - {result.code_lines} lines, {result.tests_passed} tests passed")
        else:
            failed += 1
            print(f"   ❌ Failed - {result.error_message}")
    
    print(f"\n🎯 Wave execution complete:")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {successful/(successful+failed)*100:.1f}%")


def show_execution_plan(spec_name: str):
    """Show the complete execution plan for a spec"""
    task_file = f".kiro/specs/{spec_name}/tasks.md"
    
    if not Path(task_file).exists():
        print(f"❌ Task file not found: {task_file}")
        return
    
    executor = BeastModeTaskExecutor()
    executor._dag_executor.load_task_file(task_file)
    
    plan = executor._dag_executor.get_execution_plan()
    
    if not plan:
        print(f"❌ Could not generate execution plan for {spec_name}")
        return
    
    print(f"📊 Execution Plan for {spec_name}:")
    print(f"   Total tasks: {plan['total_tasks']}")
    print(f"   Execution waves: {plan['execution_waves']}")
    print(f"   Max parallelism: {plan['max_parallelism']}")
    
    for wave in plan['waves']:
        wave_num = wave['wave_number']
        parallel_count = wave['parallel_tasks']
        
        if parallel_count > 1:
            print(f"\n   🌊 Wave {wave_num}: {parallel_count} parallel tasks")
        else:
            print(f"\n   🔄 Wave {wave_num}: {parallel_count} sequential task")
        
        for task in wave['tasks']:
            status_icon = {
                'not_started': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'failed': '❌',
                'blocked': '🚫'
            }.get(task['status'], '❓')
            
            print(f"     {status_icon} {task['number']}: {task['title']}")


def main():
    parser = argparse.ArgumentParser(
        description="Execute Beast Mode tasks by implementing actual working code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute single task
  python scripts/execute_beast_mode_task.py repository-content-discovery-indexing 1.1
  
  # List ready tasks
  python scripts/execute_beast_mode_task.py --list-ready repository-content-discovery-indexing
  
  # Execute parallel wave (dry run)
  python scripts/execute_beast_mode_task.py --execute-wave repository-content-discovery-indexing --dry-run
  
  # Execute parallel wave (actual)
  python scripts/execute_beast_mode_task.py --execute-wave repository-content-discovery-indexing
  
  # Show execution plan
  python scripts/execute_beast_mode_task.py --plan repository-content-discovery-indexing
        """
    )
    
    parser.add_argument('spec_name', nargs='?', help='Specification name (directory name in .kiro/specs/)')
    parser.add_argument('task_number', nargs='?', help='Task number to execute (e.g., 1.1, 2.3)')
    parser.add_argument('--list-ready', metavar='SPEC', help='List tasks ready to execute')
    parser.add_argument('--execute-wave', metavar='SPEC', help='Execute all ready tasks in parallel wave')
    parser.add_argument('--plan', metavar='SPEC', help='Show execution plan for spec')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be executed without making changes')
    
    args = parser.parse_args()
    
    if args.list_ready:
        list_ready_tasks(args.list_ready)
    elif args.execute_wave:
        execute_parallel_wave(args.execute_wave, dry_run=args.dry_run)
    elif args.plan:
        show_execution_plan(args.plan)
    elif args.spec_name and args.task_number:
        execute_single_task(args.spec_name, args.task_number)
    elif args.spec_name:
        # Default to showing ready tasks if only spec provided
        list_ready_tasks(args.spec_name)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
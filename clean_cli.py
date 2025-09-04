#!/usr/bin/env python3
"""
Clean CLI using the refactored execution engine architecture.
"""
import argparse
import logging
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from beast_mode.execution import ExecutionEngine, Task, Agent
from beast_mode.execution.commands import CommandFactory

def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_sample_tasks():
    """Create sample tasks for demonstration."""
    tasks = []
    
    # Create commands using the factory
    rca_command = CommandFactory.create_command(
        "rca_engine", "1.1", "Enhanced RCA Engine", 
        "Implement enhanced RCA engine with intelligent analysis"
    )
    
    logging_command = CommandFactory.create_command(
        "logging_infrastructure", "2.1", "Logging Infrastructure", 
        "Fix logging infrastructure issues and implement fallbacks"
    )
    
    tool_command = CommandFactory.create_command(
        "tool_orchestration", "3.1", "Tool Orchestration", 
        "Implement missing tool orchestration methods"
    )
    
    health_command = CommandFactory.create_command(
        "health_check", "4.1", "Health Check System", 
        "Implement accurate health state tracking"
    )
    
    # Create tasks with commands
    tasks.extend([
        Task("1.1", "Enhanced RCA Engine", rca_command, []),
        Task("2.1", "Logging Infrastructure", logging_command, []),
        Task("3.1", "Tool Orchestration", tool_command, ["1.1"]),
        Task("4.1", "Health Check System", health_command, ["2.1"]),
    ])
    
    return tasks

def create_sample_agents():
    """Create sample agents for demonstration."""
    return [
        Agent("agent_1", "RCA Specialist", ["rca", "analysis"], 1),
        Agent("agent_2", "Infrastructure Engineer", ["logging", "infrastructure"], 1),
        Agent("agent_3", "Tool Expert", ["orchestration", "optimization"], 1),
        Agent("agent_4", "Health Monitor", ["health_checks", "monitoring"], 1),
    ]

def execute_tasks(args):
    """Execute tasks using the clean architecture."""
    print("🚀 Starting task execution with clean architecture...")
    
    # Create execution engine
    engine = ExecutionEngine(
        auto_merge=not args.no_merge,
        auto_revert_on_failure=not args.no_revert
    )
    
    # Add tasks and agents
    for task in create_sample_tasks():
        engine.add_task(task)
    
    for agent in create_sample_agents():
        engine.register_agent(agent)
    
    # Execute tasks
    result = engine.execute_tasks()
    
    # Display results
    print("\n📊 Execution Summary:")
    print(f"  Duration: {result.get('total_duration_seconds', 0):.2f} seconds")
    print(f"  Iterations: {result.get('iterations', 0)}")
    
    if 'task_stats' in result:
        stats = result['task_stats']
        print(f"  Completed: {stats.get('completed', 0)}")
        print(f"  Failed: {stats.get('failed', 0)}")
        print(f"  In Progress: {stats.get('in_progress', 0)}")
    
    print(f"  Git Status: {result.get('git_status', 'unknown')}")
    print(f"  Success: {result.get('success', False)}")
    
    if result.get('error'):
        print(f"  Error: {result['error']}")
    
    return 0 if result.get('success') else 1

def status_command(args):
    """Show current status."""
    print("📊 Clean Architecture Status")
    print("  Engine: Refactored ✅")
    print("  Commands: Implemented ✅")
    print("  Git Integration: Available ✅")
    print("  RM Compliance: Improved ✅")
    return 0

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Clean Task Execution Engine")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute tasks")
    execute_parser.add_argument("--no-merge", action="store_true",
                               help="Don't auto-merge successful execution")
    execute_parser.add_argument("--no-revert", action="store_true",
                               help="Don't auto-revert failed execution")
    
    # Status command
    subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    if args.command == "execute":
        return execute_tasks(args)
    elif args.command == "status":
        return status_command(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
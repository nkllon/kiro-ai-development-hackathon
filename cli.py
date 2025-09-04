#!/usr/bin/env python3
"""
Beast Mode Framework - Task Execution CLI
Command-line interface for task dependency analysis and execution
"""

import click
import json
import sys
from datetime import datetime
from pathlib import Path

# Import our task execution engine
try:
    from task_execution_engine import TaskExecutionEngine
except ImportError:
    # Handle the case where the module name has hyphens
    import importlib.util
    spec = importlib.util.spec_from_file_location("task_execution_engine", "task-execution-engine.py")
    task_execution_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(task_execution_engine)
    TaskExecutionEngine = task_execution_engine.TaskExecutionEngine

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """🦁 Beast Mode Framework - Task Execution Engine
    
    Recursive descent task execution with dependency resolution
    """
    pass

@cli.command()
@click.option('--output', '-o', help='Output file for dependency analysis')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'yaml', 'text']), 
              help='Output format')
def analyze(output, output_format):
    """🔍 Analyze task dependencies and create execution DAG"""
    click.echo("🔍 Analyzing task dependencies...")
    
    engine = TaskExecutionEngine()
    
    # Print execution plan to console
    engine.print_execution_plan()
    
    # Generate analysis data
    tiers = engine._calculate_task_tiers()
    analysis_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tasks": len(engine.tasks),
        "tier_count": len(tiers),
        "tiers": {str(k): v for k, v in tiers.items()},
        "critical_path_length": max(tiers.keys()) if tiers else 0,
        "max_parallelism": max(len(tasks) for tasks in tiers.values()) if tiers else 0,
        "task_details": {
            task_id: {
                "name": task.name,
                "dependencies": task.dependencies,
                "estimated_hours": task.estimated_duration_hours,
                "priority": task.priority,
                "requirements": task.requirements
            }
            for task_id, task in engine.tasks.items()
        }
    }
    
    # Save to file if specified
    if output:
        output_path = Path(output)
        if output_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
        elif output_format == 'yaml':
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(analysis_data, f, default_flow_style=False)
        else:  # text
            with open(output_path, 'w') as f:
                f.write("Task Dependency Analysis\n")
                f.write("=" * 50 + "\n\n")
                for tier_num in sorted(tiers.keys()):
                    f.write(f"TIER {tier_num}: {len(tiers[tier_num])} tasks\n")
                    for task_id in tiers[tier_num]:
                        task = engine.tasks[task_id]
                        f.write(f"  - {task_id}: {task.name}\n")
                    f.write("\n")
        
        click.echo(f"💾 Analysis saved to: {output_path}")
    else:
        # Default output file
        default_file = f"task-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(default_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        click.echo(f"💾 Analysis saved to: {default_file}")

@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be executed without actually running')
@click.option('--max-agents', default=7, help='Maximum number of concurrent agents')
@click.option('--output', '-o', help='Output file for execution results')
@click.option('--simulate', is_flag=True, help='Simulate task completion for testing')
def execute(dry_run, max_agents, output, simulate):
    """🚀 Execute tasks using recursive descent with dependency resolution"""
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - Showing execution plan without running tasks")
    else:
        click.echo("🚀 Starting task execution with dependency resolution...")
    
    engine = TaskExecutionEngine()
    
    # Limit agents if specified
    if max_agents < len(engine.agents):
        agent_ids = list(engine.agents.keys())[:max_agents]
        engine.agents = {aid: engine.agents[aid] for aid in agent_ids}
        click.echo(f"🔧 Limited to {max_agents} agents")
    
    if dry_run:
        # Show what would be executed
        engine.print_execution_plan()
        
        ready_tasks = engine.get_ready_tasks()
        available_agents = engine.get_available_agents()
        
        click.echo(f"\n🎯 READY FOR EXECUTION")
        click.echo("-" * 30)
        click.echo(f"Ready tasks: {len(ready_tasks)}")
        click.echo(f"Available agents: {len(available_agents)}")
        
        if ready_tasks and available_agents:
            click.echo(f"\nNext assignments would be:")
            for i, task in enumerate(ready_tasks[:len(available_agents)]):
                agent = available_agents[i]
                click.echo(f"  • {task.id} ({task.name}) → {agent.name}")
        
        return
    
    # Execute tasks
    if simulate:
        # Simulate task completion for demonstration
        summary = simulate_task_execution(engine)
    else:
        summary = engine.recursive_task_execution()
    
    # Display results
    click.echo(f"\n📈 EXECUTION RESULTS")
    click.echo("-" * 30)
    click.echo(f"Total Duration: {summary['total_duration_seconds']:.2f} seconds")
    click.echo(f"Iterations: {summary['iterations']}")
    click.echo(f"Completion Rate: {summary['completion_rate']:.1f}%")
    click.echo(f"Tasks Assigned: {len([log for log in summary['execution_log'] if log['action'] == 'task_assigned'])}")
    
    # Show current status
    status = engine.get_execution_status()
    click.echo(f"\n📊 FINAL STATUS")
    click.echo("-" * 30)
    for key, value in status.items():
        click.echo(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Save results
    output_file = output or f"execution-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    click.echo(f"\n💾 Results saved to: {output_file}")

@cli.command()
def status():
    """📊 Show current task execution status"""
    engine = TaskExecutionEngine()
    
    status = engine.get_execution_status()
    ready_tasks = engine.get_ready_tasks()
    
    click.echo("📊 TASK EXECUTION STATUS")
    click.echo("=" * 40)
    
    for key, value in status.items():
        click.echo(f"  {key.replace('_', ' ').title()}: {value}")
    
    if ready_tasks:
        click.echo(f"\n🎯 READY TASKS ({len(ready_tasks)})")
        click.echo("-" * 20)
        for task in ready_tasks[:5]:  # Show first 5
            click.echo(f"  • {task.id}: {task.name}")
        
        if len(ready_tasks) > 5:
            click.echo(f"  ... and {len(ready_tasks) - 5} more")

@cli.command()
@click.argument('task_id')
def task_info(task_id):
    """📋 Show detailed information about a specific task"""
    engine = TaskExecutionEngine()
    
    if task_id not in engine.tasks:
        click.echo(f"❌ Task {task_id} not found")
        return
    
    task = engine.tasks[task_id]
    
    click.echo(f"📋 TASK INFORMATION: {task_id}")
    click.echo("=" * 40)
    click.echo(f"Name: {task.name}")
    click.echo(f"Status: {task.status.value}")
    click.echo(f"Priority: {task.priority}")
    click.echo(f"Estimated Duration: {task.estimated_duration_hours} hours")
    click.echo(f"Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
    click.echo(f"Requirements: {', '.join(task.requirements) if task.requirements else 'None'}")
    click.echo(f"\nDescription:")
    click.echo(f"  {task.description}")
    
    if task.assigned_agent:
        agent = engine.agents[task.assigned_agent]
        click.echo(f"\nAssigned Agent: {agent.name} ({task.assigned_agent})")
    
    if task.start_time:
        click.echo(f"Start Time: {task.start_time}")
    
    if task.completion_time:
        duration = (task.completion_time - task.start_time).total_seconds() / 3600
        click.echo(f"Completion Time: {task.completion_time}")
        click.echo(f"Actual Duration: {duration:.2f} hours")

def simulate_task_execution(engine):
    """Simulate task execution for demonstration purposes"""
    import time
    import random
    
    click.echo("🎭 SIMULATION MODE - Tasks will complete automatically")
    
    start_time = datetime.now()
    iteration = 0
    
    while True:
        iteration += 1
        
        # Get ready tasks and assign them
        ready_tasks = engine.get_ready_tasks()
        available_agents = engine.get_available_agents()
        
        if not ready_tasks:
            remaining_tasks = [t for t in engine.tasks.values() 
                             if t.status.value in ['not_started', 'in_progress']]
            if not remaining_tasks:
                break
            
            # Complete some in-progress tasks randomly
            in_progress = [t for t in engine.tasks.values() if t.status.value == 'in_progress']
            if in_progress:
                # Randomly complete 1-3 tasks
                to_complete = random.sample(in_progress, min(3, len(in_progress)))
                for task in to_complete:
                    engine.complete_task(task.id, success=True)
                    click.echo(f"✅ Completed: {task.id} ({task.name})")
            continue
        
        # Assign tasks to agents
        assignments = 0
        for task in ready_tasks:
            if not available_agents:
                break
            
            agent = available_agents.pop(0)
            if engine.assign_task_to_agent(task, agent):
                assignments += 1
                click.echo(f"🔄 Assigned: {task.id} ({task.name}) → {agent.name}")
        
        if assignments == 0:
            break
        
        # Small delay for visualization
        time.sleep(0.1)
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    return {
        "execution_start": start_time.isoformat(),
        "execution_end": end_time.isoformat(),
        "total_duration_seconds": total_duration,
        "iterations": iteration,
        "total_tasks": len(engine.tasks),
        "completed_tasks": len(engine.completed_tasks),
        "failed_tasks": len(engine.failed_tasks),
        "completion_rate": len(engine.completed_tasks) / len(engine.tasks) * 100,
        "execution_log": engine.execution_log
    }

if __name__ == '__main__':
    cli()
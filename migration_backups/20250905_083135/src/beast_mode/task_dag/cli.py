#!/usr/bin/env python3
"""
Beast Mode Framework - Task DAG CLI
Standard CLI for task dependency analysis and execution
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime

from .task_dag_rm import TaskDAGRM, TaskStatus


@click.group()
@click.version_option(version='1.0.0')
@click.option('--spec-path', '-s', help='Path to spec directory containing tasks.md')
@click.pass_context
def cli(ctx, spec_path):
    """🦁 Beast Mode Framework - Task DAG Analysis and Execution
    
    Standard CLI for analyzing task dependencies and executing tasks
    across all specs with recursive descent dependency resolution.
    """
    ctx.ensure_object(dict)
    ctx.obj['spec_path'] = spec_path or "."


@cli.command()
@click.option('--output', '-o', help='Output file for analysis results')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'text']), help='Output format')
@click.pass_context
def analyze(ctx, output, output_format):
    """🔍 Analyze task dependencies and create DAG"""
    spec_path = ctx.obj['spec_path']
    
    click.echo(f"🔍 Analyzing task dependencies in: {spec_path}")
    
    # Initialize Task DAG RM
    dag_rm = TaskDAGRM(spec_path)
    
    if not dag_rm.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    # Print analysis to console
    dag_rm.print_dag_analysis()
    
    # Export analysis if requested
    if output:
        output_file = dag_rm.export_dag_analysis(output)
        click.echo(f"\n💾 Analysis exported to: {output_file}")
    else:
        # Default export
        output_file = dag_rm.export_dag_analysis()
        click.echo(f"\n💾 Analysis exported to: {output_file}")


@cli.command()
@click.option('--dry-run', is_flag=True, help='Show execution plan without running')
@click.option('--simulate', is_flag=True, help='Simulate task execution')
@click.option('--output', '-o', help='Output file for execution results')
@click.pass_context
def execute(ctx, dry_run, simulate, output):
    """🚀 Execute tasks using recursive descent dependency resolution"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize Task DAG RM
    dag_rm = TaskDAGRM(spec_path)
    
    if not dag_rm.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - Showing execution plan")
        dag_rm.print_dag_analysis()
        
        ready_tasks = dag_rm.get_ready_tasks()
        available_agents = [a for a in dag_rm.agents.values() if a.is_available]
        
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
    click.echo(f"🚀 Starting task execution in: {spec_path}")
    
    if simulate:
        click.echo("🎭 SIMULATION MODE - Tasks will complete automatically")
    
    summary = dag_rm.execute_recursive_descent(simulate=simulate)
    
    # Display results
    click.echo(f"\n📈 EXECUTION RESULTS")
    click.echo("-" * 30)
    click.echo(f"Total Duration: {summary['total_duration_seconds']:.2f} seconds")
    click.echo(f"Iterations: {summary['iterations']}")
    
    dag_analysis = summary['dag_analysis']
    click.echo(f"Completion Rate: {dag_analysis['completion_rate']:.1f}%")
    click.echo(f"Tasks Completed: {dag_analysis['completed_tasks']}/{dag_analysis['total_tasks']}")
    click.echo(f"Tasks Failed: {dag_analysis['failed_tasks']}")
    
    # Save results
    if output:
        output_file = output
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_file = f"execution-results-{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    click.echo(f"\n💾 Results saved to: {output_file}")


@cli.command()
@click.pass_context
def status(ctx):
    """📊 Show current task execution status"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize Task DAG RM
    dag_rm = TaskDAGRM(spec_path)
    
    if not dag_rm.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    analysis = dag_rm.analyze_dag()
    
    click.echo("📊 TASK EXECUTION STATUS")
    click.echo("=" * 40)
    click.echo(f"  Spec Path: {spec_path}")
    click.echo(f"  Total Tasks: {analysis.total_tasks}")
    click.echo(f"  Completed: {len(dag_rm.completed_tasks)}")
    click.echo(f"  Failed: {len(dag_rm.failed_tasks)}")
    click.echo(f"  Ready: {len(analysis.ready_tasks)}")
    click.echo(f"  Blocked: {len(analysis.blocked_tasks)}")
    click.echo(f"  Completion Rate: {analysis.completion_rate:.1f}%")
    
    if analysis.ready_tasks:
        click.echo(f"\n🎯 READY TASKS ({len(analysis.ready_tasks)})")
        click.echo("-" * 20)
        for task_id in analysis.ready_tasks[:5]:  # Show first 5
            task = dag_rm.tasks[task_id]
            click.echo(f"  • {task.id}: {task.name}")
        
        if len(analysis.ready_tasks) > 5:
            click.echo(f"  ... and {len(analysis.ready_tasks) - 5} more")


@cli.command()
@click.argument('task_id')
@click.pass_context
def task_info(ctx, task_id):
    """📋 Show detailed information about a specific task"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize Task DAG RM
    dag_rm = TaskDAGRM(spec_path)
    
    if not dag_rm.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    if task_id not in dag_rm.tasks:
        click.echo(f"❌ Task {task_id} not found")
        available_tasks = list(dag_rm.tasks.keys())[:10]
        click.echo(f"Available tasks: {', '.join(available_tasks)}")
        if len(dag_rm.tasks) > 10:
            click.echo(f"... and {len(dag_rm.tasks) - 10} more")
        sys.exit(1)
    
    task = dag_rm.tasks[task_id]
    
    click.echo(f"📋 TASK INFORMATION: {task_id}")
    click.echo("=" * 40)
    click.echo(f"Name: {task.name}")
    click.echo(f"Status: {task.status.value}")
    click.echo(f"Tier: {task.tier}")
    click.echo(f"Priority: {task.priority}")
    click.echo(f"Estimated Hours: {task.estimated_hours}")
    click.echo(f"Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
    click.echo(f"Requirements: {', '.join(task.requirements) if task.requirements else 'None'}")
    
    if task.description:
        click.echo(f"\nDescription:")
        click.echo(f"  {task.description}")


@cli.command()
@click.pass_context
def health(ctx):
    """🏥 Show Task DAG RM health status"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize Task DAG RM
    dag_rm = TaskDAGRM(spec_path)
    
    module_status = dag_rm.get_module_status()
    health_indicators = dag_rm.get_health_indicators()
    
    click.echo("🏥 TASK DAG RM HEALTH STATUS")
    click.echo("=" * 40)
    
    # Module status
    click.echo(f"Module Status: {module_status['status']}")
    click.echo(f"Spec Path: {module_status['spec_path']}")
    click.echo(f"Total Tasks: {module_status['total_tasks']}")
    click.echo(f"Available Agents: {module_status['available_agents']}")
    
    # Health indicators
    task_analysis = health_indicators['task_analysis']
    click.echo(f"\n📊 Task Analysis Health:")
    click.echo(f"  Tier Count: {task_analysis['tier_count']}")
    click.echo(f"  Critical Path Length: {task_analysis['critical_path_length']}")
    click.echo(f"  Max Parallelism: {task_analysis['max_parallelism']}")
    click.echo(f"  Completion Rate: {task_analysis['completion_rate']:.1f}%")
    
    system_health = health_indicators['system_health']
    click.echo(f"\n🔧 System Health:")
    click.echo(f"  Spec Loaded: {'✅' if system_health['spec_loaded'] else '❌'}")
    click.echo(f"  Agents Available: {'✅' if system_health['agents_available'] else '❌'}")
    click.echo(f"  DAG Valid: {'✅' if system_health['dag_valid'] else '❌'}")


@cli.command()
@click.option('--tier', type=int, help='Show tasks in specific tier')
@click.option('--status', type=click.Choice(['not_started', 'in_progress', 'completed', 'failed', 'blocked']),
              help='Filter by task status')
@click.pass_context
def list_tasks(ctx, tier, status):
    """📋 List all tasks with optional filtering"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize Task DAG RM
    dag_rm = TaskDAGRM(spec_path)
    
    if not dag_rm.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    # Filter tasks
    filtered_tasks = []
    for task in dag_rm.tasks.values():
        if tier is not None and task.tier != tier:
            continue
        if status and task.status.value != status:
            continue
        filtered_tasks.append(task)
    
    # Sort by tier, then by ID
    filtered_tasks.sort(key=lambda t: (t.tier, t.id))
    
    click.echo(f"📋 TASK LIST ({len(filtered_tasks)} tasks)")
    if tier is not None:
        click.echo(f"Filtered by tier: {tier}")
    if status:
        click.echo(f"Filtered by status: {status}")
    click.echo("=" * 40)
    
    current_tier = None
    for task in filtered_tasks:
        if current_tier != task.tier:
            current_tier = task.tier
            click.echo(f"\n📋 TIER {current_tier}")
            click.echo("-" * 20)
        
        status_icon = dag_rm._get_status_icon(task.status)
        deps_str = f" (deps: {len(task.dependencies)})" if task.dependencies else ""
        click.echo(f"  {status_icon} {task.id}: {task.name}{deps_str}")


if __name__ == '__main__':
    cli()
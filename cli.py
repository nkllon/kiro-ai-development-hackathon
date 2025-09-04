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
    
    Recursive descent task execution with dependency resolution and RM compliance
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
@click.option('--branch', '-b', help='Specify branch name (otherwise generates random session branch)')
@click.option('--no-merge', is_flag=True, help='Do not auto-merge successful execution')
@click.option('--no-revert', is_flag=True, help='Do not auto-revert failed execution')
def execute(dry_run, max_agents, output, simulate, branch, no_merge, no_revert):
    """🚀 Execute tasks using recursive descent with dependency resolution
    
    Git Integration:
    - Creates a session branch for all changes
    - Commits progress after each task completion
    - Auto-merges on successful execution (80%+ completion)
    - Auto-reverts on failed execution (unless --no-revert)
    - Pushes session branch to remote for backup
    """
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - Showing execution plan without running tasks")
    else:
        click.echo("🚀 Starting task execution with dependency resolution...")
    
    engine = TaskExecutionEngine(branch_name=branch)
    
    # Configure Git session behavior
    engine.auto_merge = not no_merge
    engine.auto_revert_on_failure = not no_revert
    
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
    
    # Show Git session info
    if 'git_session' in summary:
        git_info = summary['git_session']
        click.echo(f"\n🌿 GIT SESSION")
        click.echo("-" * 30)
        click.echo(f"  Branch: {git_info.get('branch_name', 'N/A')}")
        click.echo(f"  Original Branch: {git_info.get('original_branch', 'N/A')}")
        click.echo(f"  Status: {git_info.get('status', 'N/A')}")
        click.echo(f"  Changes Made: {git_info.get('changes_made', False)}")
    
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
    
    # Show RM compliance status
    click.echo(f"\n🏛️  RM COMPLIANCE STATUS")
    click.echo("-" * 20)
    module_status = engine.get_module_status()
    click.echo(f"  Module: {module_status['module_name']}")
    click.echo(f"  Status: {module_status['status']}")
    click.echo(f"  Healthy: {engine.is_healthy()}")
    
    health_indicators = engine.get_health_indicators()
    healthy_count = sum(1 for indicator in health_indicators.values() 
                       if indicator.get('status') == 'healthy')
    click.echo(f"  Health Indicators: {healthy_count}/{len(health_indicators)} healthy")
    
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

@cli.command()
def rm_compliance():
    """🏛️  Check RM (Reflective Module) compliance status"""
    click.echo("🏛️  RM COMPLIANCE CHECK")
    click.echo("=" * 40)
    
    engine = TaskExecutionEngine()
    
    # Check ReflectiveModule implementation
    required_methods = ['get_module_status', 'is_healthy', 'get_health_indicators']
    implemented_methods = [method for method in required_methods if hasattr(engine, method)]
    
    click.echo(f"ReflectiveModule Interface: {len(implemented_methods)}/{len(required_methods)} methods")
    for method in required_methods:
        status = "✅" if hasattr(engine, method) else "❌"
        click.echo(f"  {status} {method}")
    
    # Show module status
    click.echo(f"\nModule Status:")
    module_status = engine.get_module_status()
    click.echo(f"  Name: {module_status['module_name']}")
    click.echo(f"  Status: {module_status['status']}")
    click.echo(f"  Healthy: {engine.is_healthy()}")
    
    # Show health indicators
    click.echo(f"\nHealth Indicators:")
    health_indicators = engine.get_health_indicators()
    for name, indicator in health_indicators.items():
        status_icon = "✅" if indicator.get('status') == 'healthy' else "⚠️" if indicator.get('status') == 'degraded' else "❌"
        click.echo(f"  {status_icon} {name}: {indicator.get('status', 'unknown')}")
        if indicator.get('message'):
            click.echo(f"    {indicator['message']}")
    
    # Overall assessment
    compliance_score = len(implemented_methods) / len(required_methods)
    healthy_indicators = sum(1 for indicator in health_indicators.values() 
                           if indicator.get('status') == 'healthy')
    health_score = healthy_indicators / len(health_indicators) if health_indicators else 0
    
    overall_score = (compliance_score + health_score) / 2
    
    click.echo(f"\nOverall RM Compliance Score: {overall_score:.2f}")
    if overall_score >= 0.8:
        click.echo("✅ RM compliance acceptable")
    else:
        click.echo("❌ RM compliance needs improvement")

@cli.command()
@click.option('--output', '-o', help='Output file for audit results')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'yaml', 'text']), 
              help='Output format')
@click.option('--spec', help='Audit specific spec (otherwise audits all specs)')
def requirements_audit(output, output_format, spec):
    """🔍 Perform requirements consistency audit across specs"""
    click.echo("🔍 REQUIREMENTS CONSISTENCY AUDIT")
    click.echo("=" * 50)
    
    from pathlib import Path
    import re
    import glob
    
    # Discover all spec directories
    specs_dir = Path('.kiro/specs')
    if not specs_dir.exists():
        click.echo("❌ No .kiro/specs directory found")
        return
    
    spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir()]
    if spec:
        spec_dirs = [d for d in spec_dirs if d.name == spec]
        if not spec_dirs:
            click.echo(f"❌ Spec '{spec}' not found")
            return
    
    click.echo(f"📋 Found {len(spec_dirs)} specs to audit")
    
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "total_specs": len(spec_dirs),
        "specs_audited": [],
        "requirement_busts": [],
        "consistency_issues": [],
        "summary": {}
    }
    
    all_requirements = {}  # requirement_id -> [spec_name, ...]
    requirement_definitions = {}  # requirement_id -> definition
    
    for spec_dir in spec_dirs:
        click.echo(f"\n🔍 Auditing spec: {spec_dir.name}")
        
        spec_audit = audit_spec_requirements(spec_dir)
        audit_results["specs_audited"].append(spec_audit)
        
        # Collect requirements for cross-spec consistency check
        for req_id in spec_audit.get("requirements_found", []):
            if req_id not in all_requirements:
                all_requirements[req_id] = []
            all_requirements[req_id].append(spec_dir.name)
    
    # Check for requirement busts and inconsistencies
    click.echo(f"\n🔍 Analyzing cross-spec consistency...")
    
    # Find orphaned requirements (referenced but not defined)
    orphaned_reqs = []
    duplicate_reqs = []
    
    for req_id, specs in all_requirements.items():
        if len(specs) > 1:
            # Check if it's the same definition across specs
            definitions = []
            for spec_name in specs:
                spec_data = next((s for s in audit_results["specs_audited"] if s["spec_name"] == spec_name), None)
                if spec_data and req_id in spec_data.get("requirement_details", {}):
                    definitions.append(spec_data["requirement_details"][req_id])
            
            if len(set(definitions)) > 1:
                duplicate_reqs.append({
                    "requirement_id": req_id,
                    "specs": specs,
                    "definitions": definitions
                })
    
    # Find missing requirements (tasks reference requirements that don't exist)
    missing_reqs = find_missing_requirements(spec_dirs)
    
    # Compile results
    audit_results["requirement_busts"] = missing_reqs
    audit_results["consistency_issues"] = duplicate_reqs
    audit_results["summary"] = {
        "total_requirements": len(all_requirements),
        "orphaned_requirements": len(orphaned_reqs),
        "duplicate_requirements": len(duplicate_reqs),
        "missing_requirements": len(missing_reqs)
    }
    
    # Calculate consistency score after summary is populated
    audit_results["summary"]["consistency_score"] = calculate_consistency_score(audit_results)
    
    # Display results
    display_audit_results(audit_results)
    
    # Save results
    output_file = output or f"requirements-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    save_audit_results(audit_results, output_file, output_format)
    
    click.echo(f"\n💾 Audit results saved to: {output_file}")

def audit_spec_requirements(spec_dir):
    """Audit requirements in a single spec directory"""
    import re
    
    spec_audit = {
        "spec_name": spec_dir.name,
        "files_found": [],
        "requirements_found": [],
        "requirement_details": {},
        "issues": []
    }
    
    # Look for common spec files
    spec_files = []
    for pattern in ['*.md', 'tasks.md', 'design.md', 'requirements.md']:
        spec_files.extend(spec_dir.glob(pattern))
    
    spec_audit["files_found"] = [f.name for f in spec_files]
    
    # Parse requirements from files
    requirement_pattern = re.compile(r'(?:_Requirements:|Requirements:)\s*([^_\n]+)', re.IGNORECASE)
    requirement_ref_pattern = re.compile(r'\b([A-Z]+[-.]?\d+(?:\.\d+)*)\b')
    
    for file_path in spec_files:
        try:
            content = file_path.read_text()
            
            # Find requirement definitions
            for match in requirement_pattern.finditer(content):
                req_text = match.group(1).strip()
                # Extract individual requirement IDs
                req_ids = requirement_ref_pattern.findall(req_text)
                for req_id in req_ids:
                    if req_id not in spec_audit["requirements_found"]:
                        spec_audit["requirements_found"].append(req_id)
                        spec_audit["requirement_details"][req_id] = req_text
            
            # Find requirement references in task descriptions
            task_pattern = re.compile(r'- \[.\] .+?_Requirements: ([^_\n]+)', re.MULTILINE | re.DOTALL)
            for match in task_pattern.finditer(content):
                req_text = match.group(1).strip()
                req_ids = requirement_ref_pattern.findall(req_text)
                for req_id in req_ids:
                    if req_id not in spec_audit["requirements_found"]:
                        spec_audit["requirements_found"].append(req_id)
                        spec_audit["requirement_details"][req_id] = f"Referenced in task: {req_text}"
                        
        except Exception as e:
            spec_audit["issues"].append(f"Error reading {file_path.name}: {str(e)}")
    
    return spec_audit

def find_missing_requirements(spec_dirs):
    """Find requirements that are referenced but not defined"""
    import re
    
    missing_reqs = []
    all_defined_reqs = set()
    all_referenced_reqs = set()
    
    requirement_ref_pattern = re.compile(r'\b([A-Z]+[-.]?\d+(?:\.\d+)*)\b')
    
    for spec_dir in spec_dirs:
        spec_files = list(spec_dir.glob('*.md'))
        
        for file_path in spec_files:
            try:
                content = file_path.read_text()
                
                # Find all requirement references
                refs = requirement_ref_pattern.findall(content)
                all_referenced_reqs.update(refs)
                
                # Check if this file defines requirements (has Requirements: sections)
                if 'Requirements:' in content or '_Requirements:' in content:
                    all_defined_reqs.update(refs)
                    
            except Exception:
                continue
    
    # Find requirements that are referenced but not defined
    for req_id in all_referenced_reqs:
        if req_id not in all_defined_reqs:
            # Check if it looks like a real requirement ID (not just a random match)
            if re.match(r'^[A-Z]{1,3}[-.]?\d+(?:\.\d+)*$', req_id):
                missing_reqs.append({
                    "requirement_id": req_id,
                    "status": "referenced_but_not_defined"
                })
    
    return missing_reqs

def calculate_consistency_score(audit_results):
    """Calculate overall consistency score"""
    total_issues = (
        len(audit_results["requirement_busts"]) +
        len(audit_results["consistency_issues"])
    )
    
    total_requirements = audit_results["summary"]["total_requirements"]
    
    if total_requirements == 0:
        return 0.0
    
    # Score based on issue ratio
    issue_ratio = total_issues / total_requirements
    consistency_score = max(0.0, 1.0 - issue_ratio)
    
    return round(consistency_score, 3)

def display_audit_results(audit_results):
    """Display audit results in console"""
    summary = audit_results["summary"]
    
    click.echo(f"\n📊 AUDIT SUMMARY")
    click.echo("-" * 30)
    click.echo(f"Total Requirements: {summary['total_requirements']}")
    click.echo(f"Missing Requirements: {summary['missing_requirements']}")
    click.echo(f"Duplicate Requirements: {summary['duplicate_requirements']}")
    click.echo(f"Consistency Score: {summary['consistency_score']}")
    
    # Show requirement busts
    if audit_results["requirement_busts"]:
        click.echo(f"\n❌ REQUIREMENT BUSTS ({len(audit_results['requirement_busts'])})")
        click.echo("-" * 30)
        for bust in audit_results["requirement_busts"][:10]:  # Show first 10
            click.echo(f"  • {bust['requirement_id']}: {bust['status']}")
        
        if len(audit_results["requirement_busts"]) > 10:
            click.echo(f"  ... and {len(audit_results['requirement_busts']) - 10} more")
    
    # Show consistency issues
    if audit_results["consistency_issues"]:
        click.echo(f"\n⚠️  CONSISTENCY ISSUES ({len(audit_results['consistency_issues'])})")
        click.echo("-" * 30)
        for issue in audit_results["consistency_issues"][:5]:  # Show first 5
            click.echo(f"  • {issue['requirement_id']} appears in: {', '.join(issue['specs'])}")
        
        if len(audit_results["consistency_issues"]) > 5:
            click.echo(f"  ... and {len(audit_results['consistency_issues']) - 5} more")
    
    # Overall assessment
    score = summary['consistency_score']
    if score >= 0.9:
        click.echo(f"\n✅ Requirements consistency: EXCELLENT ({score})")
    elif score >= 0.7:
        click.echo(f"\n⚠️  Requirements consistency: GOOD ({score})")
    elif score >= 0.5:
        click.echo(f"\n⚠️  Requirements consistency: NEEDS IMPROVEMENT ({score})")
    else:
        click.echo(f"\n❌ Requirements consistency: POOR ({score})")

def save_audit_results(audit_results, output_file, output_format):
    """Save audit results to file"""
    output_path = Path(output_file)
    
    if output_format == 'json':
        with open(output_path, 'w') as f:
            json.dump(audit_results, f, indent=2)
    elif output_format == 'yaml':
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(audit_results, f, default_flow_style=False)
    else:  # text
        with open(output_path, 'w') as f:
            f.write("Requirements Consistency Audit Report\n")
            f.write("=" * 50 + "\n\n")
            
            summary = audit_results["summary"]
            f.write(f"Audit Summary:\n")
            f.write(f"  Total Requirements: {summary['total_requirements']}\n")
            f.write(f"  Missing Requirements: {summary['missing_requirements']}\n")
            f.write(f"  Duplicate Requirements: {summary['duplicate_requirements']}\n")
            f.write(f"  Consistency Score: {summary['consistency_score']}\n\n")
            
            if audit_results["requirement_busts"]:
                f.write("Requirement Busts:\n")
                for bust in audit_results["requirement_busts"]:
                    f.write(f"  - {bust['requirement_id']}: {bust['status']}\n")
                f.write("\n")
            
            if audit_results["consistency_issues"]:
                f.write("Consistency Issues:\n")
                for issue in audit_results["consistency_issues"]:
                    f.write(f"  - {issue['requirement_id']} appears in: {', '.join(issue['specs'])}\n")
                f.write("\n")

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
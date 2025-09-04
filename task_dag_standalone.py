#!/usr/bin/env python3
"""
Beast Mode Framework - Standalone Task DAG CLI
Self-contained version that doesn't require module installation
"""

import click
import json
import sys
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    """Represents a task in the DAG"""
    id: str
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    estimated_hours: float = 4.0
    priority: int = 1  # 1=highest, 10=lowest
    status: TaskStatus = TaskStatus.NOT_STARTED
    tier: int = 0  # Calculated dependency depth


@dataclass
class Agent:
    """Represents an available agent/worker"""
    id: str
    name: str
    capabilities: List[str] = field(default_factory=list)
    is_available: bool = True
    current_task: Optional[str] = None


@dataclass
class DAGAnalysis:
    """Results of DAG analysis"""
    total_tasks: int
    tier_count: int
    critical_path_length: int
    max_parallelism: int
    tiers: Dict[int, List[str]]
    ready_tasks: List[str]
    blocked_tasks: List[str]
    completion_rate: float


class TaskDAGAnalyzer:
    """Standalone Task DAG Analyzer"""
    
    def __init__(self, spec_path: str = "."):
        self.spec_path = Path(spec_path)
        self.tasks: Dict[str, TaskNode] = {}
        self.agents: Dict[str, Agent] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.execution_log: List[Dict] = []
        
        # Initialize default agents
        self._initialize_default_agents()
        
        # Load tasks
        self.load_tasks_from_spec()
    
    def load_tasks_from_spec(self) -> bool:
        """Load tasks from tasks.md file"""
        tasks_file = self.spec_path / "tasks.md"
        
        if not tasks_file.exists():
            print(f"❌ Tasks file not found: {tasks_file}")
            return False
        
        try:
            content = tasks_file.read_text()
            self.tasks = self._parse_tasks_markdown(content)
            self._calculate_task_tiers()
            return True
        except Exception as e:
            print(f"❌ Failed to load tasks: {e}")
            return False
    
    def _parse_tasks_markdown(self, content: str) -> Dict[str, TaskNode]:
        """Parse tasks from markdown content"""
        tasks = {}
        current_task = None
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Match task headers: - [ ] 1.1 Task Name
            task_match = re.match(r'^-\s*\[\s*[x\s]\s*\]\s*(\d+(?:\.\d+)*)\s+(.+)$', line)
            if task_match:
                task_id = task_match.group(1)
                task_name = task_match.group(2)
                
                current_task = TaskNode(
                    id=task_id,
                    name=task_name,
                    description="",
                    dependencies=self._extract_dependencies(task_id),
                    requirements=[],
                    estimated_hours=4.0,
                    priority=1
                )
                tasks[task_id] = current_task
                continue
            
            # Match requirements: _Requirements: req1, req2_
            req_match = re.match(r'^_Requirements:\s*(.+)_$', line)
            if req_match and current_task:
                reqs = [r.strip() for r in req_match.group(1).split(',')]
                current_task.requirements = reqs
                continue
            
            # Add description lines
            if current_task and line and not line.startswith('-') and not line.startswith('_'):
                if current_task.description:
                    current_task.description += " " + line
                else:
                    current_task.description = line
        
        return tasks
    
    def _extract_dependencies(self, task_id: str) -> List[str]:
        """Extract dependencies based on task ID hierarchy"""
        dependencies = []
        
        # Handle hierarchical dependencies
        if '.' in task_id:
            # Subtask depends on parent
            parent_id = '.'.join(task_id.split('.')[:-1])
            dependencies.append(parent_id)
        
        return dependencies
    
    def _resolve_parent_dependencies(self):
        """Resolve parent task dependencies on their subtasks"""
        for task_id, task in self.tasks.items():
            if '.' not in task_id:  # Parent task
                subtasks = [tid for tid in self.tasks.keys() if tid.startswith(f"{task_id}.")]
                if subtasks:
                    task.dependencies = subtasks
    
    def _calculate_task_tiers(self):
        """Calculate tier (dependency depth) for each task"""
        # First resolve parent dependencies
        self._resolve_parent_dependencies()
        
        # Calculate tiers using topological sort
        visited = set()
        
        def calculate_tier(task_id: str) -> int:
            if task_id in visited:
                return 0  # Avoid cycles
            
            visited.add(task_id)
            
            if task_id not in self.tasks:
                return 0
            
            task = self.tasks[task_id]
            
            if not task.dependencies:
                task.tier = 0
                return 0
            
            max_dep_tier = 0
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_tier = calculate_tier(dep_id)
                    max_dep_tier = max(max_dep_tier, dep_tier)
            
            task.tier = max_dep_tier + 1
            return task.tier
        
        for task_id in self.tasks:
            visited.clear()
            calculate_tier(task_id)
    
    def _initialize_default_agents(self):
        """Initialize default agents for task execution"""
        default_agents = [
            Agent("agent_1", "Full-Stack Developer", ["development", "testing", "integration"]),
            Agent("agent_2", "Infrastructure Engineer", ["infrastructure", "deployment", "monitoring"]),
            Agent("agent_3", "Quality Assurance Engineer", ["testing", "validation", "documentation"]),
            Agent("agent_4", "DevOps Specialist", ["automation", "deployment", "optimization"]),
            Agent("agent_5", "System Architect", ["design", "architecture", "integration"]),
        ]
        
        for agent in default_agents:
            self.agents[agent.id] = agent
    
    def analyze_dag(self) -> DAGAnalysis:
        """Analyze the task DAG and return comprehensive analysis"""
        if not self.tasks:
            return DAGAnalysis(0, 0, 0, 0, {}, [], [], 0.0)
        
        # Group tasks by tier
        tiers = {}
        for task in self.tasks.values():
            tier = task.tier
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(task.id)
        
        # Calculate metrics
        total_tasks = len(self.tasks)
        tier_count = len(tiers)
        critical_path_length = max(tiers.keys()) if tiers else 0
        max_parallelism = max(len(task_list) for task_list in tiers.values()) if tiers else 0
        
        # Get ready and blocked tasks
        ready_tasks = self.get_ready_tasks()
        blocked_tasks = self.get_blocked_tasks()
        
        # Calculate completion rate
        completion_rate = len(self.completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0.0
        
        return DAGAnalysis(
            total_tasks=total_tasks,
            tier_count=tier_count,
            critical_path_length=critical_path_length,
            max_parallelism=max_parallelism,
            tiers=tiers,
            ready_tasks=[t.id for t in ready_tasks],
            blocked_tasks=blocked_tasks,
            completion_rate=completion_rate
        )
    
    def get_ready_tasks(self) -> List[TaskNode]:
        """Get all tasks that are ready to execute (dependencies met)"""
        ready_tasks = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.NOT_STARTED and 
                self._dependencies_met(task)):
                ready_tasks.append(task)
        
        # Sort by priority and tier
        ready_tasks.sort(key=lambda t: (t.priority, t.tier, -t.estimated_hours))
        return ready_tasks
    
    def get_blocked_tasks(self) -> List[str]:
        """Get tasks that are blocked by failed dependencies"""
        blocked_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.NOT_STARTED:
                # Check if any dependencies failed
                for dep_id in task.dependencies:
                    if dep_id in self.failed_tasks:
                        blocked_tasks.append(task.id)
                        break
        
        return blocked_tasks
    
    def _dependencies_met(self, task: TaskNode) -> bool:
        """Check if all dependencies for a task are completed"""
        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)
    
    def print_dag_analysis(self):
        """Print comprehensive DAG analysis"""
        analysis = self.analyze_dag()
        
        print("\n🚀 TASK DAG ANALYSIS")
        print("=" * 50)
        
        # Print tiers
        for tier_num in sorted(analysis.tiers.keys()):
            tasks_in_tier = analysis.tiers[tier_num]
            print(f"\n📋 TIER {tier_num} - {len(tasks_in_tier)} tasks")
            print("-" * 30)
            
            for task_id in tasks_in_tier:
                task = self.tasks[task_id]
                deps_str = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else " (no dependencies)"
                status_icon = self._get_status_icon(task.status)
                print(f"  {status_icon} {task.id}: {task.name}{deps_str}")
        
        # Print summary
        print(f"\n📊 DAG SUMMARY")
        print("-" * 30)
        print(f"  Total Tasks: {analysis.total_tasks}")
        print(f"  Tier Count: {analysis.tier_count}")
        print(f"  Critical Path Length: {analysis.critical_path_length}")
        print(f"  Max Parallelism: {analysis.max_parallelism}")
        print(f"  Completion Rate: {analysis.completion_rate:.1f}%")
        print(f"  Ready Tasks: {len(analysis.ready_tasks)}")
        print(f"  Blocked Tasks: {len(analysis.blocked_tasks)}")
    
    def _get_status_icon(self, status: TaskStatus) -> str:
        """Get icon for task status"""
        icons = {
            TaskStatus.NOT_STARTED: "⚪",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "🚫"
        }
        return icons.get(status, "❓")


@click.group()
@click.version_option(version='1.0.0')
@click.option('--spec-path', '-s', default='.', help='Path to spec directory containing tasks.md')
@click.pass_context
def cli(ctx, spec_path):
    """🦁 Beast Mode Framework - Standalone Task DAG Analysis
    
    Analyze task dependencies and execution order for any spec.
    """
    ctx.ensure_object(dict)
    ctx.obj['spec_path'] = spec_path


@cli.command()
@click.option('--output', '-o', help='Output file for analysis results')
@click.pass_context
def analyze(ctx, output):
    """🔍 Analyze task dependencies and create DAG"""
    spec_path = ctx.obj['spec_path']
    
    click.echo(f"🔍 Analyzing task dependencies in: {spec_path}")
    
    # Initialize analyzer
    analyzer = TaskDAGAnalyzer(spec_path)
    
    if not analyzer.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    # Print analysis to console
    analyzer.print_dag_analysis()
    
    # Export analysis if requested
    if output:
        analysis = analyzer.analyze_dag()
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "spec_path": spec_path,
            "dag_analysis": {
                "total_tasks": analysis.total_tasks,
                "tier_count": analysis.tier_count,
                "critical_path_length": analysis.critical_path_length,
                "max_parallelism": analysis.max_parallelism,
                "completion_rate": analysis.completion_rate,
                "tiers": analysis.tiers,
                "ready_tasks": analysis.ready_tasks,
                "blocked_tasks": analysis.blocked_tasks
            },
            "tasks": {
                task_id: {
                    "name": task.name,
                    "description": task.description,
                    "dependencies": task.dependencies,
                    "requirements": task.requirements,
                    "estimated_hours": task.estimated_hours,
                    "priority": task.priority,
                    "status": task.status.value,
                    "tier": task.tier
                }
                for task_id, task in analyzer.tasks.items()
            }
        }
        
        with open(output, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        click.echo(f"\n💾 Analysis exported to: {output}")


@cli.command()
@click.pass_context
def status(ctx):
    """📊 Show current task execution status"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize analyzer
    analyzer = TaskDAGAnalyzer(spec_path)
    
    if not analyzer.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    analysis = analyzer.analyze_dag()
    
    click.echo("📊 TASK EXECUTION STATUS")
    click.echo("=" * 40)
    click.echo(f"  Spec Path: {spec_path}")
    click.echo(f"  Total Tasks: {analysis.total_tasks}")
    click.echo(f"  Completed: {len(analyzer.completed_tasks)}")
    click.echo(f"  Failed: {len(analyzer.failed_tasks)}")
    click.echo(f"  Ready: {len(analysis.ready_tasks)}")
    click.echo(f"  Blocked: {len(analysis.blocked_tasks)}")
    click.echo(f"  Completion Rate: {analysis.completion_rate:.1f}%")
    
    if analysis.ready_tasks:
        click.echo(f"\n🎯 READY TASKS ({len(analysis.ready_tasks)})")
        click.echo("-" * 20)
        for task_id in analysis.ready_tasks[:5]:  # Show first 5
            task = analyzer.tasks[task_id]
            click.echo(f"  • {task.id}: {task.name}")
        
        if len(analysis.ready_tasks) > 5:
            click.echo(f"  ... and {len(analysis.ready_tasks) - 5} more")


@cli.command()
@click.argument('task_id')
@click.pass_context
def task_info(ctx, task_id):
    """📋 Show detailed information about a specific task"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize analyzer
    analyzer = TaskDAGAnalyzer(spec_path)
    
    if not analyzer.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    if task_id not in analyzer.tasks:
        click.echo(f"❌ Task {task_id} not found")
        available_tasks = list(analyzer.tasks.keys())[:10]
        click.echo(f"Available tasks: {', '.join(available_tasks)}")
        if len(analyzer.tasks) > 10:
            click.echo(f"... and {len(analyzer.tasks) - 10} more")
        sys.exit(1)
    
    task = analyzer.tasks[task_id]
    
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
@click.option('--tier', type=int, help='Show tasks in specific tier')
@click.option('--status', type=click.Choice(['not_started', 'in_progress', 'completed', 'failed', 'blocked']),
              help='Filter by task status')
@click.pass_context
def list_tasks(ctx, tier, status):
    """📋 List all tasks with optional filtering"""
    spec_path = ctx.obj['spec_path']
    
    # Initialize analyzer
    analyzer = TaskDAGAnalyzer(spec_path)
    
    if not analyzer.tasks:
        click.echo("❌ No tasks found. Make sure tasks.md exists in the spec directory.")
        sys.exit(1)
    
    # Filter tasks
    filtered_tasks = []
    for task in analyzer.tasks.values():
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
        
        status_icon = analyzer._get_status_icon(task.status)
        deps_str = f" (deps: {len(task.dependencies)})" if task.dependencies else ""
        click.echo(f"  {status_icon} {task.id}: {task.name}{deps_str}")


if __name__ == '__main__':
    cli()
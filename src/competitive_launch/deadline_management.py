"""
Deadline Management Core Core Core

This module was extracted from deadline_management_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Deadline_Management - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for deadline_management.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/competitive_launch/deadline_management_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.502929
"""



import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from .models import MarketConditions, CompetitiveThreat

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    OPTIONAL = 5

class TaskStatus(Enum):
    """Task status levels."""
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    BLOCKED = 'blocked'
    CANCELLED = 'cancelled'

@dataclass
class HackathonTask:
    """Individual hackathon task."""
    task_id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    estimated_hours: float
    actual_hours: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    competitive_impact: float = 0.0
    technical_debt_risk: float = 0.0

@dataclass
class CriticalPath:
    """Critical path analysis result."""
    path_tasks: List[str]
    total_duration_hours: float
    slack_time_hours: float
    risk_factors: List[str]
    acceleration_opportunities: List[str]

@dataclass
class DeadlineStatus:
    """Current deadline status."""
    days_remaining: int
    hours_remaining: float
    completion_percentage: float
    critical_path_remaining: float
    risk_level: str
    acceleration_required: bool
    scope_optimization_needed: bool

def __init__(self, hackathon_deadline: datetime=None):
    """Initialize deadline manager."""
    self.hackathon_deadline = hackathon_deadline or datetime(2025, 9, 15, 23, 59, 59)
    self.tasks: List[HackathonTask] = []
    self.critical_path: Optional[CriticalPath] = None
    self.emergency_protocols_active = False
    self._load_default_tasks()
    logger.info(f'Hackathon deadline manager initialized for {self.hackathon_deadline}')

def add_task(self, task: HackathonTask) -> bool:
    """Add a task to the hackathon plan."""
    try:
        if any((t.task_id == task.task_id for t in self.tasks)):
            logger.warning(f'Task {task.task_id} already exists')
            return False
        self.tasks.append(task)
        logger.info(f'Task added: {task.task_id} - {task.title}')
        return True
    except Exception as e:
        logger.error(f'Failed to add task {task.task_id}: {e}')
        return False

def update_task_status(self, task_id: str, status: TaskStatus, **kwargs) -> bool:
    """Update task status and progress."""
    try:
        task = self._find_task(task_id)
        if not task:
            logger.error(f'Task {task_id} not found')
            return False
        old_status = task.status
        task.status = status
        if status == TaskStatus.IN_PROGRESS and (not task.started_at):
            task.started_at = datetime.now()
        elif status == TaskStatus.COMPLETED and (not task.completed_at):
            task.completed_at = datetime.now()
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        logger.info(f'Task {task_id} status updated: {old_status.value} -> {status.value}')
        return True
    except Exception as e:
        logger.error(f'Failed to update task {task_id}: {e}')
        return False

def calculate_critical_path(self) -> CriticalPath:
    """Calculate critical path for remaining tasks."""
    logger.info('Calculating critical path')
    try:
        incomplete_tasks = [t for t in self.tasks if t.status != TaskStatus.COMPLETED]
        if not incomplete_tasks:
            return CriticalPath([], 0.0, 0.0, [], [])
        dependency_graph = self._build_dependency_graph(incomplete_tasks)
        critical_path_tasks = self._find_critical_path(dependency_graph, incomplete_tasks)
        total_duration = sum((task.estimated_hours for task in critical_path_tasks))
        time_remaining = (self.hackathon_deadline - datetime.now()).total_seconds() / 3600
        slack_time = max(0, time_remaining - total_duration)
        risk_factors = self._identify_risk_factors(critical_path_tasks, time_remaining)
        acceleration_opportunities = self._find_acceleration_opportunities(critical_path_tasks)
        self.critical_path = CriticalPath(path_tasks=[task.task_id for task in critical_path_tasks], total_duration_hours=total_duration, slack_time_hours=slack_time, risk_factors=risk_factors, acceleration_opportunities=acceleration_opportunities)
        logger.info(f'Critical path calculated: {len(critical_path_tasks)} tasks, {total_duration:.1f} hours')
        return self.critical_path
    except Exception as e:
        logger.error(f'Failed to calculate critical path: {e}')
        return CriticalPath([], 0.0, 0.0, [str(e)], [])

def get_deadline_status(self) -> DeadlineStatus:
    """Get current deadline status and recommendations."""
    logger.info('Calculating deadline status')
    try:
        time_remaining = self.hackathon_deadline - datetime.now()
        days_remaining = time_remaining.days
        hours_remaining = time_remaining.total_seconds() / 3600
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
        completion_percentage = completed_tasks / total_tasks * 100 if total_tasks > 0 else 0
        if not self.critical_path:
            self.critical_path = self.calculate_critical_path()
        critical_path_remaining = self.critical_path.total_duration_hours
        if hours_remaining < critical_path_remaining * 1.2:
            risk_level = 'critical'
        elif hours_remaining < critical_path_remaining * 1.5:
            risk_level = 'high'
        elif hours_remaining < critical_path_remaining * 2.0:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        acceleration_required = risk_level in ['critical', 'high']
        scope_optimization_needed = risk_level == 'critical' or completion_percentage < 50
        return DeadlineStatus(days_remaining=days_remaining, hours_remaining=hours_remaining, completion_percentage=completion_percentage, critical_path_remaining=critical_path_remaining, risk_level=risk_level, acceleration_required=acceleration_required, scope_optimization_needed=scope_optimization_needed)
    except Exception as e:
        logger.error(f'Failed to calculate deadline status: {e}')
        return DeadlineStatus(0, 0.0, 0.0, 0.0, 'critical', True, True)

def trigger_emergency_acceleration(self) -> Dict[str, Any]:
    """Trigger emergency acceleration protocols."""
    logger.warning('Triggering emergency acceleration protocols')
    try:
        self.emergency_protocols_active = True
        status = self.get_deadline_status()
        acceleration_strategies = []
        if status.risk_level == 'critical':
            acceleration_strategies.extend(['Activate 24/7 development mode', 'Reassign all resources to critical path', 'Eliminate non-essential features', 'Implement parallel development streams', 'Reduce quality gates temporarily'])
        elif status.risk_level == 'high':
            acceleration_strategies.extend(['Increase daily work hours', 'Add additional team members', 'Prioritize critical path tasks only', 'Implement aggressive parallelization'])
        else:
            acceleration_strategies.extend(['Optimize task sequencing', 'Remove low-priority features', 'Increase task parallelization'])
        self._update_priorities_for_acceleration()
        acceleration_plan = {'emergency_protocols_active': True, 'risk_level': status.risk_level, 'acceleration_strategies': acceleration_strategies, 'critical_path_tasks': self.critical_path.path_tasks if self.critical_path else [], 'estimated_time_saved': self._estimate_time_savings(acceleration_strategies), 'activated_at': datetime.now().isoformat()}
        logger.warning(f'Emergency acceleration activated: {len(acceleration_strategies)} strategies')
        return acceleration_plan
    except Exception as e:
        logger.error(f'Failed to trigger emergency acceleration: {e}')
        return {'emergency_protocols_active': False, 'error': str(e)}

def optimize_scope_for_deadline(self) -> Dict[str, Any]:
    """Optimize project scope to meet deadline."""
    logger.info('Optimizing scope for deadline')
    try:
        status = self.get_deadline_status()
        if not status.scope_optimization_needed:
            return {'optimization_needed': False, 'message': 'Current scope is manageable'}
        tasks_to_remove = []
        tasks_to_defer = []
        tasks_to_simplify = []
        for task in self.tasks:
            if task.status == TaskStatus.COMPLETED:
                continue
            if task.priority in [TaskPriority.LOW, TaskPriority.OPTIONAL] and task.competitive_impact < 0.3:
                tasks_to_remove.append(task.task_id)
            elif task.priority == TaskPriority.MEDIUM and task.technical_debt_risk > 0.7:
                tasks_to_defer.append(task.task_id)
            elif task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH] and task.estimated_hours > 20:
                tasks_to_simplify.append(task.task_id)
        optimization_actions = []
        for task_id in tasks_to_remove:
            self.update_task_status(task_id, TaskStatus.CANCELLED)
            optimization_actions.append(f'Removed task: {task_id}')
        for task_id in tasks_to_defer:
            task = self._find_task(task_id)
            if task:
                task.deadline = self.hackathon_deadline + timedelta(days=7)
                optimization_actions.append(f'Deferred task: {task_id}')
        for task_id in tasks_to_simplify:
            task = self._find_task(task_id)
            if task:
                task.estimated_hours *= 0.7
                optimization_actions.append(f'Simplified task: {task_id}')
        self.critical_path = self.calculate_critical_path()
        optimization_result = {'optimization_completed': True, 'tasks_removed': len(tasks_to_remove), 'tasks_deferred': len(tasks_to_defer), 'tasks_simplified': len(tasks_to_simplify), 'actions_taken': optimization_actions, 'new_critical_path_hours': self.critical_path.total_duration_hours, 'optimized_at': datetime.now().isoformat()}
        logger.info(f'Scope optimization completed: {len(optimization_actions)} actions taken')
        return optimization_result
    except Exception as e:
        logger.error(f'Failed to optimize scope: {e}')
        return {'optimization_completed': False, 'error': str(e)}

def get_progress_report(self) -> Dict[str, Any]:
    """Get comprehensive progress report."""
    try:
        status = self.get_deadline_status()
        critical_path = self.calculate_critical_path()
        task_breakdown = {}
        for task_status in TaskStatus:
            count = len([t for t in self.tasks if t.status == task_status])
            task_breakdown[task_status.value] = count
        priority_breakdown = {}
        for priority in TaskPriority:
            count = len([t for t in self.tasks if t.priority == priority])
            priority_breakdown[priority.value] = count
        high_impact_tasks = [t for t in self.tasks if t.competitive_impact > 0.7]
        medium_impact_tasks = [t for t in self.tasks if 0.3 <= t.competitive_impact <= 0.7]
        low_impact_tasks = [t for t in self.tasks if t.competitive_impact < 0.3]
        return {'deadline_status': {'days_remaining': status.days_remaining, 'hours_remaining': status.hours_remaining, 'completion_percentage': status.completion_percentage, 'risk_level': status.risk_level, 'acceleration_required': status.acceleration_required, 'scope_optimization_needed': status.scope_optimization_needed}, 'critical_path': {'total_tasks': len(critical_path.path_tasks), 'total_duration_hours': critical_path.total_duration_hours, 'slack_time_hours': critical_path.slack_time_hours, 'risk_factors': critical_path.risk_factors, 'acceleration_opportunities': critical_path.acceleration_opportunities}, 'task_breakdown': task_breakdown, 'priority_breakdown': priority_breakdown, 'competitive_impact': {'high_impact_tasks': len(high_impact_tasks), 'medium_impact_tasks': len(medium_impact_tasks), 'low_impact_tasks': len(low_impact_tasks)}, 'emergency_protocols': {'active': self.emergency_protocols_active, 'hackathon_deadline': self.hackathon_deadline.isoformat()}}
    except Exception as e:
        logger.error(f'Failed to generate progress report: {e}')
        return {'error': str(e)}

def _find_task(self, task_id: str) -> Optional[HackathonTask]:
    """Find task by ID."""
    return next((t for t in self.tasks if t.task_id == task_id), None)

def _build_dependency_graph(self, tasks: List[HackathonTask]) -> Dict[str, List[str]]:
    """Build dependency graph from tasks."""
    graph = {}
    for task in tasks:
        graph[task.task_id] = task.dependencies
    return graph

def _find_critical_path(self, dependency_graph: Dict[str, List[str]], tasks: List[HackathonTask]) -> List[HackathonTask]:
    """Find critical path using topological sort."""
    sorted_tasks = sorted(tasks, key=lambda t: (t.priority.value, -t.estimated_hours))
    return sorted_tasks[:min(5, len(sorted_tasks))]

def _identify_risk_factors(self, critical_tasks: List[HackathonTask], time_remaining: float) -> List[str]:
    """Identify risk factors for critical path."""
    risks = []
    if time_remaining < 48:
        risks.append('Critical time shortage')
    high_debt_tasks = [t for t in critical_tasks if t.technical_debt_risk > 0.7]
    if high_debt_tasks:
        risks.append(f'High technical debt risk in {len(high_debt_tasks)} critical tasks')
    blocked_tasks = [t for t in critical_tasks if t.status == TaskStatus.BLOCKED]
    if blocked_tasks:
        risks.append(f'{len(blocked_tasks)} critical tasks are blocked')
    long_tasks = [t for t in critical_tasks if t.estimated_hours > 16]
    if long_tasks:
        risks.append(f'{len(long_tasks)} critical tasks exceed 16 hours')
    return risks

def _find_acceleration_opportunities(self, critical_tasks: List[HackathonTask]) -> List[str]:
    """Find opportunities to accelerate critical path."""
    opportunities = []
    independent_tasks = [t for t in critical_tasks if not t.dependencies]
    if len(independent_tasks) > 1:
        opportunities.append(f'Parallel execution of {len(independent_tasks)} independent tasks')
    high_priority_tasks = [t for t in critical_tasks if t.priority == TaskPriority.CRITICAL]
    if high_priority_tasks:
        opportunities.append(f'Focus all resources on {len(high_priority_tasks)} critical tasks')
    low_impact_tasks = [t for t in critical_tasks if t.competitive_impact < 0.5]
    if low_impact_tasks:
        opportunities.append(f'Reduce scope of {len(low_impact_tasks)} low-impact tasks')
    return opportunities

def _update_priorities_for_acceleration(self):
    """Update task priorities for emergency acceleration."""
    for task in self.tasks:
        if task.status == TaskStatus.COMPLETED:
            continue
        if task.competitive_impact > 0.8:
            task.priority = TaskPriority.CRITICAL
        elif task.competitive_impact < 0.3:
            task.priority = TaskPriority.LOW

def _estimate_time_savings(self, strategies: List[str]) -> float:
    """Estimate time savings from acceleration strategies."""
    time_savings = 0.0
    for strategy in strategies:
        if '24/7' in strategy:
            time_savings += 8.0
        elif 'parallel' in strategy.lower():
            time_savings += 4.0
        elif 'eliminate' in strategy.lower():
            time_savings += 2.0
        elif 'simplify' in strategy.lower():
            time_savings += 1.0
    return min(time_savings, 24.0)

def _load_default_tasks(self):
    """Load default hackathon tasks."""
    default_tasks = [HackathonTask(task_id='devpost_integration', title='DevPost Integration Complete', description='Complete DevPost platform integration with API client, authentication, and project management', priority=TaskPriority.CRITICAL, status=TaskStatus.COMPLETED, estimated_hours=16.0, actual_hours=16.0, competitive_impact=0.9, technical_debt_risk=0.0, completed_at=datetime.now()), HackathonTask(task_id='competitive_intelligence', title='Competitive Intelligence System', description='Implement real-time competitor monitoring and response automation', priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS, estimated_hours=12.0, competitive_impact=0.8, technical_debt_risk=0.2), HackathonTask(task_id='deadline_management', title='Deadline Management System', description='Deploy hackathon deadline orchestration with critical path analysis', priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS, estimated_hours=8.0, competitive_impact=0.7, technical_debt_risk=0.1), HackathonTask(task_id='demo_preparation', title='Demo and Presentation Preparation', description='Prepare comprehensive demo and presentation materials', priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED, estimated_hours=6.0, competitive_impact=0.6, technical_debt_risk=0.0), HackathonTask(task_id='documentation', title='Documentation and README', description='Create comprehensive documentation and README files', priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED, estimated_hours=4.0, competitive_impact=0.4, technical_debt_risk=0.0)]
    for task in default_tasks:
        self.tasks.append(task)

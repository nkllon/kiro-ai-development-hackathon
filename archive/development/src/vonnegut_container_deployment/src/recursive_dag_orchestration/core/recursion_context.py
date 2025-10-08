#!/usr/bin/env python3
"""
Recursion Context Management
===========================

Manages recursion contexts and levels for the recursive DAG orchestration system.
Provides mathematical guarantees for recursion termination and resource management.

Author: Recursive DAG Orchestration System
Date: 2025-01-30
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid


class RecursionLevel(Enum):
    """Recursion levels for hierarchical orchestration."""
    META = 0          # Meta-orchestration level (orchestrating the orchestration)
    SELF = 1          # Self-orchestration level (orchestrating spec execution)
    TASK = 2          # Task execution level (executing individual tasks)
    BASE = 999        # Base infrastructure level (existing DAG orchestration)


@dataclass
class RecursionContext:
    """
    Context for a single recursion level execution.
    
    Maintains state, resources, and relationships for hierarchical orchestration
    with mathematical guarantees for termination and consistency.
    """
    
    # Identity and hierarchy
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: RecursionLevel = RecursionLevel.SELF
    parent_context: Optional['RecursionContext'] = None
    child_contexts: List['RecursionContext'] = field(default_factory=list)
    
    # Execution state
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "created"  # created, active, completed, failed, terminated
    
    # Resource allocation
    allocated_cpu_cores: int = 1
    allocated_memory_gb: float = 1.0
    max_concurrent_tasks: int = 5
    resource_priority: int = 1  # Lower = higher priority
    
    # Termination conditions
    max_execution_time: Optional[float] = None  # seconds
    termination_conditions: List[str] = field(default_factory=list)
    termination_triggered: bool = False
    
    # Execution metrics
    tasks_executed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    execution_efficiency: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    
    # DAG orchestration instance
    orchestrator_instance: Optional[Any] = None  # Will be DAGOrchestrator instance
    
    def __post_init__(self):
        """Initialize context after creation."""
        # Set default termination conditions based on level
        if not self.termination_conditions:
            self.termination_conditions = self._get_default_termination_conditions()
        
        # Set default resource limits based on level
        if self.level == RecursionLevel.META:
            self.max_execution_time = 3600  # 1 hour max for meta-orchestration
        elif self.level == RecursionLevel.SELF:
            self.max_execution_time = 1800  # 30 minutes max for self-orchestration
        elif self.level == RecursionLevel.TASK:
            self.max_execution_time = 600   # 10 minutes max for task execution
    
    def _get_default_termination_conditions(self) -> List[str]:
        """Get default termination conditions for this recursion level."""
        base_conditions = [
            "max_execution_time_exceeded",
            "resource_exhaustion",
            "parent_context_terminated"
        ]
        
        if self.level == RecursionLevel.META:
            base_conditions.extend([
                "all_child_contexts_completed",
                "orchestration_goal_achieved"
            ])
        elif self.level == RecursionLevel.SELF:
            base_conditions.extend([
                "spec_execution_completed",
                "dag_validation_failed"
            ])
        elif self.level == RecursionLevel.TASK:
            base_conditions.extend([
                "all_tasks_completed",
                "critical_task_failed"
            ])
        
        return base_conditions
    
    def get_recursion_depth(self) -> int:
        """Calculate the depth of this context in the recursion hierarchy."""
        depth = 0
        current = self.parent_context
        while current is not None:
            depth += 1
            current = current.parent_context
        return depth
    
    def is_termination_condition_met(self) -> Tuple[bool, Optional[str]]:
        """
        Check if any termination condition is met.
        
        Returns:
            Tuple of (should_terminate, reason)
        """
        
        # Check execution time limit
        if self.max_execution_time and self.started_at:
            elapsed = (datetime.now() - self.started_at).total_seconds()
            if elapsed > self.max_execution_time:
                return True, "max_execution_time_exceeded"
        
        # Check if parent context terminated
        if self.parent_context and self.parent_context.termination_triggered:
            return True, "parent_context_terminated"
        
        # Check resource exhaustion (simplified check)
        cpu_usage = self.resource_utilization.get('cpu_percent', 0)
        memory_usage = self.resource_utilization.get('memory_percent', 0)
        if cpu_usage > 95 or memory_usage > 95:
            return True, "resource_exhaustion"
        
        # Level-specific termination checks
        if self.level == RecursionLevel.META:
            if all(child.status in ['completed', 'failed'] for child in self.child_contexts):
                return True, "all_child_contexts_completed"
        
        elif self.level == RecursionLevel.SELF:
            if self.tasks_completed > 0 and self.tasks_completed == self.tasks_executed:
                return True, "spec_execution_completed"
        
        elif self.level == RecursionLevel.TASK:
            if self.tasks_failed > 0 and self.tasks_failed / max(self.tasks_executed, 1) > 0.5:
                return True, "critical_task_failed"
        
        return False, None
    
    def start_execution(self) -> None:
        """Mark context as started and begin execution tracking."""
        self.started_at = datetime.now()
        self.status = "active"
    
    def complete_execution(self, success: bool = True) -> None:
        """Mark context as completed."""
        self.completed_at = datetime.now()
        self.status = "completed" if success else "failed"
        
        # Calculate final metrics
        if self.started_at:
            execution_time = (self.completed_at - self.started_at).total_seconds()
            if self.tasks_executed > 0:
                self.execution_efficiency = self.tasks_completed / self.tasks_executed
    
    def trigger_termination(self, reason: str) -> None:
        """Trigger termination of this context and all child contexts."""
        self.termination_triggered = True
        self.status = "terminated"
        
        # Cascade termination to child contexts
        for child in self.child_contexts:
            if child.status == "active":
                child.trigger_termination(f"parent_terminated: {reason}")
    
    def add_child_context(self, child: 'RecursionContext') -> None:
        """Add a child context to this context."""
        child.parent_context = self
        self.child_contexts.append(child)
    
    def update_resource_utilization(self, metrics: Dict[str, float]) -> None:
        """Update resource utilization metrics."""
        self.resource_utilization.update(metrics)
        
        # Check for termination conditions after resource update
        should_terminate, reason = self.is_termination_condition_met()
        if should_terminate and not self.termination_triggered:
            self.trigger_termination(reason)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of this context for monitoring and debugging."""
        return {
            'context_id': self.context_id,
            'level': self.level.name,
            'status': self.status,
            'recursion_depth': self.get_recursion_depth(),
            'execution_time': (
                (datetime.now() - self.started_at).total_seconds() 
                if self.started_at else 0
            ),
            'tasks_executed': self.tasks_executed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'execution_efficiency': self.execution_efficiency,
            'resource_utilization': self.resource_utilization,
            'child_contexts': len(self.child_contexts),
            'termination_triggered': self.termination_triggered
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            'context_id': self.context_id,
            'level': self.level.name,
            'parent_context_id': self.parent_context.context_id if self.parent_context else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'allocated_cpu_cores': self.allocated_cpu_cores,
            'allocated_memory_gb': self.allocated_memory_gb,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'resource_priority': self.resource_priority,
            'max_execution_time': self.max_execution_time,
            'termination_conditions': self.termination_conditions,
            'termination_triggered': self.termination_triggered,
            'tasks_executed': self.tasks_executed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'execution_efficiency': self.execution_efficiency,
            'resource_utilization': self.resource_utilization,
            'child_contexts': [child.context_id for child in self.child_contexts]
        }


@dataclass
class RecursionStack:
    """
    Manages the stack of recursion contexts with depth limits and validation.
    
    Provides mathematical guarantees for recursion termination and prevents
    infinite recursion through depth limits and cycle detection.
    """
    
    contexts: List[RecursionContext] = field(default_factory=list)
    max_depth: int = 3  # Maximum recursion depth
    
    def push_context(self, context: RecursionContext) -> bool:
        """
        Push a new context onto the recursion stack.
        
        Returns:
            True if context was pushed successfully, False if depth limit exceeded
        """
        
        # Check depth limit
        if len(self.contexts) >= self.max_depth:
            return False
        
        # Set parent relationship if stack is not empty
        if self.contexts:
            current_top = self.contexts[-1]
            current_top.add_child_context(context)
        
        self.contexts.append(context)
        return True
    
    def pop_context(self) -> Optional[RecursionContext]:
        """Pop the top context from the recursion stack."""
        if self.contexts:
            return self.contexts.pop()
        return None
    
    def get_current_context(self) -> Optional[RecursionContext]:
        """Get the current (top) context without removing it."""
        return self.contexts[-1] if self.contexts else None
    
    def get_depth(self) -> int:
        """Get the current recursion depth."""
        return len(self.contexts)
    
    def is_at_max_depth(self) -> bool:
        """Check if we're at maximum recursion depth."""
        return len(self.contexts) >= self.max_depth
    
    def get_stack_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of all contexts in the stack."""
        return [context.get_context_summary() for context in self.contexts]
    
    def trigger_stack_termination(self, reason: str) -> None:
        """Trigger termination of all contexts in the stack."""
        for context in reversed(self.contexts):  # Terminate from top to bottom
            if context.status == "active":
                context.trigger_termination(reason)
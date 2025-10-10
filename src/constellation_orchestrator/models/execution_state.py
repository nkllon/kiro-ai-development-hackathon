"""Execution state models for Constellation Orchestrator."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .task_definition import TaskStatus


class ExecutionResult(BaseModel):
    """Result of task execution."""
    
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Execution status")
    
    # Execution details
    start_time: Optional[datetime] = Field(None, description="Task start time")
    end_time: Optional[datetime] = Field(None, description="Task completion time")
    duration: Optional[float] = Field(None, description="Execution duration in seconds")
    
    # Output and results
    output: Optional[str] = Field(None, description="Task output")
    error: Optional[str] = Field(None, description="Error message if failed")
    exit_code: Optional[int] = Field(None, description="Process exit code")
    
    # Execution context
    agent_id: Optional[str] = Field(None, description="Agent that executed the task")
    retry_count: int = Field(0, description="Number of retries attempted")
    
    # Performance metrics
    memory_usage_mb: Optional[float] = Field(None, description="Peak memory usage in MB")
    cpu_time: Optional[float] = Field(None, description="CPU time used in seconds")
    
    # Metadata
    execution_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
    
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if execution failed."""
        return self.status == TaskStatus.FAILED
    
    def get_duration_seconds(self) -> float:
        """Get duration in seconds, calculating if not set."""
        if self.duration is not None:
            return self.duration
        
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        
        return 0.0
    
    def to_summary(self) -> Dict[str, Any]:
        """Get summary representation."""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'duration': self.get_duration_seconds(),
            'agent_id': self.agent_id,
            'retry_count': self.retry_count,
            'has_output': bool(self.output),
            'has_error': bool(self.error)
        }


class ExecutionMetrics(BaseModel):
    """Detailed execution metrics and statistics."""
    
    # Task counts
    total_tasks: int = Field(0, description="Total number of tasks")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    failed_tasks: int = Field(0, description="Number of failed tasks")
    running_tasks: int = Field(0, description="Number of currently running tasks")
    pending_tasks: int = Field(0, description="Number of pending tasks")
    cancelled_tasks: int = Field(0, description="Number of cancelled tasks")
    
    # Timing metrics
    start_time: Optional[datetime] = Field(None, description="Execution start time")
    last_update: datetime = Field(default_factory=datetime.utcnow, description="Last metrics update")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    # Performance metrics
    average_task_duration: float = Field(0.0, description="Average task duration in seconds")
    tasks_per_minute: float = Field(0.0, description="Tasks completed per minute")
    peak_concurrent_tasks: int = Field(0, description="Peak number of concurrent tasks")
    
    # Agent metrics
    agent_utilization: Dict[str, float] = Field(default_factory=dict, description="Agent utilization percentages")
    total_agents: int = Field(0, description="Total number of agents")
    active_agents: int = Field(0, description="Number of active agents")
    
    # Error tracking
    error_rate: float = Field(0.0, description="Error rate (0.0 to 1.0)")
    retry_rate: float = Field(0.0, description="Retry rate (0.0 to 1.0)")
    timeout_count: int = Field(0, description="Number of timeout errors")
    
    # Resource metrics
    peak_memory_usage_mb: float = Field(0.0, description="Peak memory usage in MB")
    average_cpu_utilization: float = Field(0.0, description="Average CPU utilization percentage")
    
    def get_completion_percentage(self) -> float:
        """Get completion percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100.0
    
    def get_success_rate(self) -> float:
        """Get success rate (completed / (completed + failed))."""
        total_finished = self.completed_tasks + self.failed_tasks
        if total_finished == 0:
            return 0.0
        return (self.completed_tasks / total_finished) * 100.0
    
    def is_execution_complete(self) -> bool:
        """Check if execution is complete."""
        return (self.completed_tasks + self.failed_tasks + self.cancelled_tasks) >= self.total_tasks
    
    def get_remaining_tasks(self) -> int:
        """Get number of remaining tasks."""
        return self.total_tasks - (self.completed_tasks + self.failed_tasks + self.cancelled_tasks)
    
    def estimate_completion_time(self) -> Optional[datetime]:
        """Estimate completion time based on current progress."""
        if self.tasks_per_minute <= 0 or self.get_remaining_tasks() <= 0:
            return None
        
        remaining_minutes = self.get_remaining_tasks() / self.tasks_per_minute
        from datetime import timedelta
        return datetime.utcnow() + timedelta(minutes=remaining_minutes)


class ExecutionState(BaseModel):
    """Complete execution state for persistence and recovery."""
    
    execution_id: str = Field(..., description="Unique execution identifier")
    status: str = Field("initializing", description="Execution status")
    
    # Task tracking
    task_states: Dict[str, TaskStatus] = Field(default_factory=dict, description="Current state of each task")
    task_results: Dict[str, ExecutionResult] = Field(default_factory=dict, description="Results for completed tasks")
    
    # Execution metrics
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics, description="Execution metrics")
    
    # Configuration
    max_concurrent_agents: int = Field(5, description="Maximum concurrent agents")
    execution_config: Dict[str, Any] = Field(default_factory=dict, description="Execution configuration")
    
    # Recovery information
    last_checkpoint: datetime = Field(default_factory=datetime.utcnow, description="Last checkpoint time")
    recovery_data: Dict[str, Any] = Field(default_factory=dict, description="Data for execution recovery")
    
    # Execution history
    execution_log: List[Dict[str, Any]] = Field(default_factory=list, description="Execution event log")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
    
    def update_task_state(self, task_id: str, status: TaskStatus, result: Optional[ExecutionResult] = None) -> None:
        """Update task state and metrics."""
        old_status = self.task_states.get(task_id)
        self.task_states[task_id] = status
        
        if result:
            self.task_results[task_id] = result
        
        # Update metrics based on status change
        self._update_metrics_for_status_change(task_id, old_status, status)
        
        # Add to execution log
        self.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'task_status_change',
            'task_id': task_id,
            'old_status': old_status.value if old_status else None,
            'new_status': status.value,
            'has_result': result is not None
        })
        
        # Update checkpoint
        self.last_checkpoint = datetime.utcnow()
    
    def _update_metrics_for_status_change(self, task_id: str, old_status: Optional[TaskStatus], new_status: TaskStatus) -> None:
        """Update metrics based on task status change."""
        # Decrement old status count
        if old_status:
            if old_status == TaskStatus.PENDING:
                self.metrics.pending_tasks = max(0, self.metrics.pending_tasks - 1)
            elif old_status == TaskStatus.RUNNING:
                self.metrics.running_tasks = max(0, self.metrics.running_tasks - 1)
        
        # Increment new status count
        if new_status == TaskStatus.PENDING:
            self.metrics.pending_tasks += 1
        elif new_status == TaskStatus.RUNNING:
            self.metrics.running_tasks += 1
            # Update peak concurrent tasks
            if self.metrics.running_tasks > self.metrics.peak_concurrent_tasks:
                self.metrics.peak_concurrent_tasks = self.metrics.running_tasks
        elif new_status == TaskStatus.COMPLETED:
            self.metrics.completed_tasks += 1
        elif new_status == TaskStatus.FAILED:
            self.metrics.failed_tasks += 1
        elif new_status == TaskStatus.CANCELLED:
            self.metrics.cancelled_tasks += 1
        
        # Update last update time
        self.metrics.last_update = datetime.utcnow()
        
        # Recalculate derived metrics
        self._recalculate_derived_metrics()
    
    def _recalculate_derived_metrics(self) -> None:
        """Recalculate derived metrics."""
        # Calculate error rate
        total_finished = self.metrics.completed_tasks + self.metrics.failed_tasks
        if total_finished > 0:
            self.metrics.error_rate = self.metrics.failed_tasks / total_finished
        
        # Calculate tasks per minute
        if self.metrics.start_time:
            elapsed_minutes = (datetime.utcnow() - self.metrics.start_time).total_seconds() / 60
            if elapsed_minutes > 0:
                self.metrics.tasks_per_minute = self.metrics.completed_tasks / elapsed_minutes
        
        # Calculate average task duration
        completed_results = [r for r in self.task_results.values() if r.is_successful() and r.duration]
        if completed_results:
            total_duration = sum(r.duration for r in completed_results)
            self.metrics.average_task_duration = total_duration / len(completed_results)
        
        # Update estimated completion
        self.metrics.estimated_completion = self.metrics.estimate_completion_time()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[str]:
        """Get list of task IDs with given status."""
        return [task_id for task_id, task_status in self.task_states.items() if task_status == status]
    
    def get_completed_tasks(self) -> set:
        """Get set of completed task IDs."""
        return {task_id for task_id, status in self.task_states.items() if status == TaskStatus.COMPLETED}
    
    def get_failed_tasks(self) -> List[str]:
        """Get list of failed task IDs."""
        return self.get_tasks_by_status(TaskStatus.FAILED)
    
    def get_running_tasks(self) -> List[str]:
        """Get list of running task IDs."""
        return self.get_tasks_by_status(TaskStatus.RUNNING)
    
    def get_pending_tasks(self) -> List[str]:
        """Get list of pending task IDs."""
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def is_execution_complete(self) -> bool:
        """Check if execution is complete."""
        return self.metrics.is_execution_complete()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            'execution_id': self.execution_id,
            'status': self.status,
            'total_tasks': self.metrics.total_tasks,
            'completed_tasks': self.metrics.completed_tasks,
            'failed_tasks': self.metrics.failed_tasks,
            'running_tasks': self.metrics.running_tasks,
            'pending_tasks': self.metrics.pending_tasks,
            'completion_percentage': self.metrics.get_completion_percentage(),
            'success_rate': self.metrics.get_success_rate(),
            'average_duration': self.metrics.average_task_duration,
            'tasks_per_minute': self.metrics.tasks_per_minute,
            'error_rate': self.metrics.error_rate,
            'estimated_completion': self.metrics.estimated_completion.isoformat() if self.metrics.estimated_completion else None,
            'last_checkpoint': self.last_checkpoint.isoformat()
        }
    
    def can_resume(self) -> bool:
        """Check if execution can be resumed."""
        return (
            self.status in ['paused', 'interrupted', 'running'] and
            self.metrics.get_remaining_tasks() > 0
        )
    
    def add_execution_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Add event to execution log."""
        self.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_type,
            **details
        })
        
        # Keep log size manageable
        if len(self.execution_log) > 10000:
            self.execution_log = self.execution_log[-5000:]  # Keep last 5000 events
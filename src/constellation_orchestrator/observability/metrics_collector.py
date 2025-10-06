"""Metrics collection for Constellation Orchestrator."""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import structlog


@dataclass
class TaskMetrics:
    """Metrics for individual task execution."""
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "pending"
    agent_id: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None


@dataclass
class ExecutionMetrics:
    """Metrics for entire execution."""
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    running_tasks: int = 0
    pending_tasks: int = 0
    
    # Performance metrics
    average_task_duration: float = 0.0
    tasks_per_minute: float = 0.0
    agent_utilization: Dict[str, float] = field(default_factory=dict)
    
    # Error tracking
    error_rate: float = 0.0
    retry_rate: float = 0.0
    timeout_count: int = 0
    
    # Resource metrics
    peak_concurrent_tasks: int = 0
    memory_usage_mb: float = 0.0
    cpu_utilization: float = 0.0


class MetricsCollector:
    """Comprehensive metrics collection for orchestrator execution."""
    
    def __init__(self, max_history_size: int = 10000):
        """Initialize metrics collector."""
        self.max_history_size = max_history_size
        self.logger = structlog.get_logger(__name__)
        
        # Current execution metrics
        self.current_execution: Optional[ExecutionMetrics] = None
        self.task_metrics: Dict[str, TaskMetrics] = {}
        
        # Historical data
        self.execution_history: deque = deque(maxlen=max_history_size)
        self.task_history: deque = deque(maxlen=max_history_size)
        
        # Real-time counters
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.timers = defaultdict(list)
        
        # Performance tracking
        self.performance_samples = deque(maxlen=1000)
        
        self.logger.info("metrics_collector_initialized", max_history_size=max_history_size)
    
    def start_execution(self, execution_id: str, total_tasks: int) -> None:
        """Start tracking metrics for a new execution."""
        self.current_execution = ExecutionMetrics(
            execution_id=execution_id,
            start_time=datetime.utcnow(),
            total_tasks=total_tasks,
            pending_tasks=total_tasks
        )
        
        # Reset task metrics
        self.task_metrics.clear()
        
        # Update counters
        self.counters['executions_started'] += 1
        self.gauges['current_total_tasks'] = total_tasks
        
        self.logger.info(
            "execution_metrics_started",
            execution_id=execution_id,
            total_tasks=total_tasks
        )
    
    def start_task(self, task_id: str, agent_id: Optional[str] = None) -> None:
        """Start tracking metrics for a task."""
        if not self.current_execution:
            self.logger.warning("task_metrics_started_without_execution", task_id=task_id)
            return
        
        task_metrics = TaskMetrics(
            task_id=task_id,
            start_time=datetime.utcnow(),
            agent_id=agent_id,
            status="running"
        )
        
        self.task_metrics[task_id] = task_metrics
        
        # Update execution metrics
        self.current_execution.running_tasks += 1
        self.current_execution.pending_tasks -= 1
        
        # Track peak concurrency
        if self.current_execution.running_tasks > self.current_execution.peak_concurrent_tasks:
            self.current_execution.peak_concurrent_tasks = self.current_execution.running_tasks
        
        # Update counters
        self.counters['tasks_started'] += 1
        self.gauges['current_running_tasks'] = self.current_execution.running_tasks
        
        self.logger.debug(
            "task_metrics_started",
            execution_id=self.current_execution.execution_id,
            task_id=task_id,
            agent_id=agent_id
        )
    
    def complete_task(self, task_id: str, status: str, error_message: Optional[str] = None) -> None:
        """Complete task metrics tracking."""
        if not self.current_execution:
            self.logger.warning("task_metrics_completed_without_execution", task_id=task_id)
            return
        
        if task_id not in self.task_metrics:
            self.logger.warning("task_metrics_completed_without_start", task_id=task_id)
            return
        
        task_metrics = self.task_metrics[task_id]
        task_metrics.end_time = datetime.utcnow()
        task_metrics.status = status
        task_metrics.error_message = error_message
        
        # Calculate duration
        if task_metrics.start_time and task_metrics.end_time:
            duration = (task_metrics.end_time - task_metrics.start_time).total_seconds()
            task_metrics.duration = duration
            
            # Add to performance samples
            self.performance_samples.append({
                'task_id': task_id,
                'duration': duration,
                'status': status,
                'timestamp': task_metrics.end_time,
                'agent_id': task_metrics.agent_id
            })
        
        # Update execution metrics
        self.current_execution.running_tasks -= 1
        
        if status == "completed":
            self.current_execution.completed_tasks += 1
            self.counters['tasks_completed'] += 1
        elif status == "failed":
            self.current_execution.failed_tasks += 1
            self.counters['tasks_failed'] += 1
            if error_message and 'timeout' in error_message.lower():
                self.current_execution.timeout_count += 1
        
        # Update gauges
        self.gauges['current_running_tasks'] = self.current_execution.running_tasks
        self.gauges['current_completed_tasks'] = self.current_execution.completed_tasks
        self.gauges['current_failed_tasks'] = self.current_execution.failed_tasks
        
        # Add to task history
        self.task_history.append(task_metrics)
        
        self.logger.debug(
            "task_metrics_completed",
            execution_id=self.current_execution.execution_id,
            task_id=task_id,
            status=status,
            duration=task_metrics.duration
        )
    
    def record_retry(self, task_id: str) -> None:
        """Record a task retry."""
        if task_id in self.task_metrics:
            self.task_metrics[task_id].retry_count += 1
        
        self.counters['task_retries'] += 1
        
        if self.current_execution:
            # Update retry rate
            total_attempts = self.current_execution.completed_tasks + self.current_execution.failed_tasks
            if total_attempts > 0:
                self.current_execution.retry_rate = self.counters['task_retries'] / total_attempts
    
    def update_agent_utilization(self, agent_utilization: Dict[str, float]) -> None:
        """Update agent utilization metrics."""
        if self.current_execution:
            self.current_execution.agent_utilization = agent_utilization.copy()
        
        # Update gauges
        for agent_id, utilization in agent_utilization.items():
            self.gauges[f'agent_utilization_{agent_id}'] = utilization
        
        if agent_utilization:
            self.gauges['average_agent_utilization'] = sum(agent_utilization.values()) / len(agent_utilization)
    
    def update_resource_metrics(self, memory_mb: float, cpu_percent: float) -> None:
        """Update system resource metrics."""
        if self.current_execution:
            self.current_execution.memory_usage_mb = memory_mb
            self.current_execution.cpu_utilization = cpu_percent
        
        self.gauges['memory_usage_mb'] = memory_mb
        self.gauges['cpu_utilization_percent'] = cpu_percent
    
    def complete_execution(self, status: str = "completed") -> ExecutionMetrics:
        """Complete execution metrics tracking."""
        if not self.current_execution:
            raise RuntimeError("No active execution to complete")
        
        self.current_execution.end_time = datetime.utcnow()
        
        # Calculate final metrics
        if self.current_execution.start_time and self.current_execution.end_time:
            total_duration = (self.current_execution.end_time - self.current_execution.start_time).total_seconds()
            
            # Calculate tasks per minute
            if total_duration > 0:
                self.current_execution.tasks_per_minute = (self.current_execution.completed_tasks * 60) / total_duration
        
        # Calculate average task duration
        completed_durations = [
            task.duration for task in self.task_metrics.values() 
            if task.duration is not None and task.status == "completed"
        ]
        
        if completed_durations:
            self.current_execution.average_task_duration = sum(completed_durations) / len(completed_durations)
        
        # Calculate error rate
        total_finished = self.current_execution.completed_tasks + self.current_execution.failed_tasks
        if total_finished > 0:
            self.current_execution.error_rate = self.current_execution.failed_tasks / total_finished
        
        # Add to execution history
        self.execution_history.append(self.current_execution)
        
        # Update counters
        if status == "completed":
            self.counters['executions_completed'] += 1
        else:
            self.counters['executions_failed'] += 1
        
        self.logger.info(
            "execution_metrics_completed",
            execution_id=self.current_execution.execution_id,
            status=status,
            total_tasks=self.current_execution.total_tasks,
            completed_tasks=self.current_execution.completed_tasks,
            failed_tasks=self.current_execution.failed_tasks,
            average_duration=self.current_execution.average_task_duration,
            tasks_per_minute=self.current_execution.tasks_per_minute,
            error_rate=self.current_execution.error_rate
        )
        
        completed_execution = self.current_execution
        self.current_execution = None
        
        return completed_execution
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current execution metrics."""
        if not self.current_execution:
            return {}
        
        return {
            'execution_id': self.current_execution.execution_id,
            'total_tasks': self.current_execution.total_tasks,
            'completed_tasks': self.current_execution.completed_tasks,
            'failed_tasks': self.current_execution.failed_tasks,
            'running_tasks': self.current_execution.running_tasks,
            'pending_tasks': self.current_execution.pending_tasks,
            'peak_concurrent_tasks': self.current_execution.peak_concurrent_tasks,
            'average_task_duration': self.current_execution.average_task_duration,
            'tasks_per_minute': self.current_execution.tasks_per_minute,
            'error_rate': self.current_execution.error_rate,
            'retry_rate': self.current_execution.retry_rate,
            'timeout_count': self.current_execution.timeout_count,
            'agent_utilization': self.current_execution.agent_utilization,
            'memory_usage_mb': self.current_execution.memory_usage_mb,
            'cpu_utilization': self.current_execution.cpu_utilization
        }
    
    def get_prometheus_metrics(self) -> Dict[str, Any]:
        """Get metrics in Prometheus format."""
        metrics = {}
        
        # Add counters
        for name, value in self.counters.items():
            metrics[f'constellation_{name}_total'] = value
        
        # Add gauges
        for name, value in self.gauges.items():
            metrics[f'constellation_{name}'] = value
        
        # Add current execution metrics
        if self.current_execution:
            current_metrics = self.get_current_metrics()
            for name, value in current_metrics.items():
                if isinstance(value, (int, float)):
                    metrics[f'constellation_current_{name}'] = value
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance analysis summary."""
        if not self.performance_samples:
            return {}
        
        # Analyze recent performance samples
        recent_samples = list(self.performance_samples)[-100:]  # Last 100 tasks
        
        durations = [sample['duration'] for sample in recent_samples if sample['duration']]
        completed_samples = [sample for sample in recent_samples if sample['status'] == 'completed']
        failed_samples = [sample for sample in recent_samples if sample['status'] == 'failed']
        
        summary = {
            'total_samples': len(recent_samples),
            'completed_count': len(completed_samples),
            'failed_count': len(failed_samples),
            'success_rate': len(completed_samples) / len(recent_samples) if recent_samples else 0
        }
        
        if durations:
            summary.update({
                'average_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'median_duration': sorted(durations)[len(durations) // 2]
            })
        
        return summary
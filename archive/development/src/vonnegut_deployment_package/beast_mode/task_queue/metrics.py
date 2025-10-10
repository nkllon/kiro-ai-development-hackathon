"""
Prometheus metrics integration for TaskQueueManager

This module provides comprehensive metrics collection and Prometheus
integration for the task queue system.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Info,
        generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .models import TaskState, ConversationState


class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    INFO = "info"


@dataclass
class MetricDefinition:
    """Definition of a Prometheus metric."""
    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = None


class TaskQueueMetrics:
    """
    Prometheus metrics collector for TaskQueueManager.

    Provides comprehensive metrics for task processing, queue status,
    state transitions, and system health.
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._logger = logging.getLogger(f"{__name__}.TaskQueueMetrics")

        # Track if Prometheus is available
        self.prometheus_enabled = PROMETHEUS_AVAILABLE

        if not self.prometheus_enabled:
            self._logger.warning("Prometheus client not available - metrics collection disabled")
            return

        # Initialize all metrics
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize all Prometheus metrics."""
        if not self.prometheus_enabled:
            return

        # Task processing metrics
        self.tasks_processed_total = Counter(
            'task_queue_tasks_processed_total',
            'Total number of tasks processed',
            ['queue_name', 'task_type', 'status'],
            registry=self.registry
        )

        self.task_processing_duration = Histogram(
            'task_queue_processing_duration_seconds',
            'Time spent processing tasks',
            ['queue_name', 'task_type'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )

        # Queue status metrics
        self.queue_size = Gauge(
            'task_queue_size',
            'Current number of tasks in queue',
            ['queue_name'],
            registry=self.registry
        )

        self.queue_processing_rate = Gauge(
            'task_queue_processing_rate_per_minute',
            'Rate of task processing per minute',
            ['queue_name'],
            registry=self.registry
        )

        # State machine metrics
        self.conversation_state_transitions = Counter(
            'task_queue_conversation_state_transitions_total',
            'Total conversation state transitions',
            ['from_state', 'to_state', 'trigger'],
            registry=self.registry
        )

        self.current_conversation_state = Gauge(
            'task_queue_current_conversation_state',
            'Current conversation state (encoded as integer)',
            ['conversation_id'],
            registry=self.registry
        )

        # System health metrics
        self.manager_health_score = Gauge(
            'task_queue_manager_health_score',
            'Current health score of TaskQueueManager (0.0 to 1.0)',
            registry=self.registry
        )

        self.consecutive_failures = Gauge(
            'task_queue_consecutive_failures',
            'Number of consecutive failures',
            registry=self.registry
        )

        self.redis_connection_status = Gauge(
            'task_queue_redis_connection_status',
            'Redis connection status (1=healthy, 0=unhealthy)',
            registry=self.registry
        )

        # Performance metrics
        self.hook_execution_duration = Histogram(
            'task_queue_hook_execution_duration_seconds',
            'Time spent in hook execution',
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=self.registry
        )

        self.state_persistence_operations = Counter(
            'task_queue_state_persistence_operations_total',
            'State persistence operations',
            ['operation_type', 'storage_layer', 'status'],
            registry=self.registry
        )

        # Resource usage metrics
        self.memory_usage = Gauge(
            'task_queue_memory_usage_bytes',
            'Memory usage of task queue components',
            ['component'],
            registry=self.registry
        )

        self.active_connections = Gauge(
            'task_queue_active_connections',
            'Number of active Redis connections',
            registry=self.registry
        )

        # Security metrics
        self.security_validations = Counter(
            'task_queue_security_validations_total',
            'Security validation attempts',
            ['validation_type', 'result'],
            registry=self.registry
        )

        # System info
        self.system_info = Info(
            'task_queue_system_info',
            'System information',
            registry=self.registry
        )

        # Set initial system info
        self.system_info.info({
            'version': '1.0.0',
            'prometheus_enabled': 'true',
            'initialized_at': datetime.now().isoformat()
        })

    def record_task_processed(self, queue_name: str, task_type: str,
                             status: str, duration_seconds: float):
        """Record a processed task."""
        if not self.prometheus_enabled:
            return

        self.tasks_processed_total.labels(
            queue_name=queue_name,
            task_type=task_type,
            status=status
        ).inc()

        self.task_processing_duration.labels(
            queue_name=queue_name,
            task_type=task_type
        ).observe(duration_seconds)

    def update_queue_size(self, queue_name: str, size: int):
        """Update current queue size."""
        if not self.prometheus_enabled:
            return

        self.queue_size.labels(queue_name=queue_name).set(size)

    def update_processing_rate(self, queue_name: str, rate: float):
        """Update task processing rate per minute."""
        if not self.prometheus_enabled:
            return

        self.queue_processing_rate.labels(queue_name=queue_name).set(rate)

    def record_state_transition(self, from_state: ConversationState,
                               to_state: ConversationState, trigger: str):
        """Record a conversation state transition."""
        if not self.prometheus_enabled:
            return

        self.conversation_state_transitions.labels(
            from_state=from_state.value,
            to_state=to_state.value,
            trigger=trigger
        ).inc()

    def update_conversation_state(self, conversation_id: str, state: ConversationState):
        """Update current conversation state."""
        if not self.prometheus_enabled:
            return

        # Encode state as integer for Prometheus gauge
        state_value = list(ConversationState).index(state)
        self.current_conversation_state.labels(
            conversation_id=conversation_id
        ).set(state_value)

    def update_health_score(self, score: float):
        """Update manager health score."""
        if not self.prometheus_enabled:
            return

        self.manager_health_score.set(score)

    def update_consecutive_failures(self, count: int):
        """Update consecutive failures count."""
        if not self.prometheus_enabled:
            return

        self.consecutive_failures.set(count)

    def update_redis_connection_status(self, healthy: bool):
        """Update Redis connection status."""
        if not self.prometheus_enabled:
            return

        self.redis_connection_status.set(1 if healthy else 0)

    def record_hook_execution(self, duration_seconds: float):
        """Record hook execution duration."""
        if not self.prometheus_enabled:
            return

        self.hook_execution_duration.observe(duration_seconds)

    def record_persistence_operation(self, operation_type: str,
                                   storage_layer: str, status: str):
        """Record state persistence operation."""
        if not self.prometheus_enabled:
            return

        self.state_persistence_operations.labels(
            operation_type=operation_type,
            storage_layer=storage_layer,
            status=status
        ).inc()

    def update_memory_usage(self, component: str, bytes_used: int):
        """Update memory usage for component."""
        if not self.prometheus_enabled:
            return

        self.memory_usage.labels(component=component).set(bytes_used)

    def update_active_connections(self, count: int):
        """Update active Redis connections count."""
        if not self.prometheus_enabled:
            return

        self.active_connections.set(count)

    def record_security_validation(self, validation_type: str, result: str):
        """Record security validation attempt."""
        if not self.prometheus_enabled:
            return

        self.security_validations.labels(
            validation_type=validation_type,
            result=result
        ).inc()

    def get_metrics_output(self) -> tuple[str, str]:
        """
        Get Prometheus metrics output.

        Returns:
            Tuple of (metrics_content, content_type)
        """
        if not self.prometheus_enabled:
            return "# Prometheus metrics not available\n", "text/plain"

        metrics_content = generate_latest(self.registry).decode('utf-8')
        return metrics_content, CONTENT_TYPE_LATEST

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current metrics for JSON endpoints.

        Returns:
            Dictionary containing metric summaries
        """
        if not self.prometheus_enabled:
            return {"error": "Prometheus metrics not available"}

        try:
            # Collect current values from metrics
            summary = {
                "prometheus_enabled": True,
                "timestamp": datetime.now().isoformat(),
                "metrics": {}
            }

            # Add metric summaries here
            # Note: This is a simplified version - full implementation would
            # extract current values from all metrics

            return summary

        except Exception as e:
            self._logger.error(f"Error getting metrics summary: {e}")
            return {"error": str(e)}


class MetricsCollector:
    """
    High-level metrics collection coordinator.

    Integrates with TaskQueueManager to automatically collect and
    report metrics throughout the system lifecycle.
    """

    def __init__(self, metrics: TaskQueueMetrics):
        self.metrics = metrics
        self._logger = logging.getLogger(f"{__name__}.MetricsCollector")

        # Collection state
        self._last_collection_time = datetime.now()
        self._collection_count = 0

    def collect_system_metrics(self, task_queue_manager):
        """Collect comprehensive system metrics from TaskQueueManager."""
        try:
            current_time = datetime.now()

            # Update health metrics
            health_status = task_queue_manager.get_health_status()
            self.metrics.update_health_score(health_status.health_score)
            self.metrics.update_consecutive_failures(task_queue_manager._consecutive_failures)
            self.metrics.update_redis_connection_status(task_queue_manager._redis_connection_healthy)

            # Update conversation state
            if task_queue_manager.conversation_state_machine:
                context = task_queue_manager.conversation_state_machine.context
                self.metrics.update_conversation_state(
                    context.conversation_id,
                    context.current_state
                )

            # Update queue size if Redis operations available
            if task_queue_manager.redis_ops:
                # This would need to be called asynchronously in practice
                # queue_size = await task_queue_manager.redis_ops.get_queue_size(...)
                pass

            self._collection_count += 1
            self._last_collection_time = current_time

            self._logger.debug(f"Collected metrics (collection #{self._collection_count})")

        except Exception as e:
            self._logger.error(f"Error collecting system metrics: {e}")

    def get_collector_info(self) -> Dict[str, Any]:
        """Get information about the metrics collector."""
        return {
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "metrics_enabled": self.metrics.prometheus_enabled,
            "collection_count": self._collection_count,
            "last_collection_time": self._last_collection_time.isoformat(),
            "registry_metrics_count": len(self.metrics.registry._collector_to_names) if self.metrics.prometheus_enabled else 0
        }
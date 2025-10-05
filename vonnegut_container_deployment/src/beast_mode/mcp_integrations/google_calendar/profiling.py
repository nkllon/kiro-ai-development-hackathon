"""Performance profiling utilities for Google Calendar MCP integration.

This module provides comprehensive profiling capabilities including timing decorators,
memory tracking, and performance analysis tools following Beast Mode framework patterns.
"""

import cProfile
import functools
import io
import pstats
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from uuid import uuid4

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    memory_peak_mb: float
    memory_current_mb: float
    cpu_time_ms: float
    call_count: int = 1
    error_count: int = 0
    correlation_id: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.duration_ms / 1000.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.call_count == 0:
            return 0.0
        return ((self.call_count - self.error_count) / self.call_count) * 100.0


@dataclass
class AggregatedMetrics:
    """Aggregated performance metrics for multiple operations."""
    operation_name: str
    total_calls: int = 0
    total_errors: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    peak_memory_mb: float = 0.0
    durations: List[float] = field(default_factory=list)
    
    def add_measurement(self, metrics: PerformanceMetrics):
        """Add a new measurement to the aggregated metrics."""
        self.total_calls += metrics.call_count
        self.total_errors += metrics.error_count
        self.total_duration_ms += metrics.duration_ms
        self.min_duration_ms = min(self.min_duration_ms, metrics.duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, metrics.duration_ms)
        self.peak_memory_mb = max(self.peak_memory_mb, metrics.memory_peak_mb)
        self.durations.append(metrics.duration_ms)
        
        # Recalculate averages and percentiles
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """Calculate statistical metrics."""
        if self.durations:
            self.avg_duration_ms = sum(self.durations) / len(self.durations)
            sorted_durations = sorted(self.durations)
            
            # Calculate percentiles
            if len(sorted_durations) >= 20:  # Only calculate percentiles with sufficient data
                p95_index = int(0.95 * len(sorted_durations))
                p99_index = int(0.99 * len(sorted_durations))
                self.p95_duration_ms = sorted_durations[p95_index]
                self.p99_duration_ms = sorted_durations[p99_index]


class PerformanceProfiler:
    """Comprehensive performance profiler for MCP operations."""
    
    def __init__(self, enable_memory_tracking: bool = True):
        """Initialize the performance profiler.
        
        Args:
            enable_memory_tracking: Whether to enable memory usage tracking
        """
        self.enable_memory_tracking = enable_memory_tracking
        self.metrics_history: List[PerformanceMetrics] = []
        self.aggregated_metrics: Dict[str, AggregatedMetrics] = {}
        self.active_profiles: Dict[str, cProfile.Profile] = {}
        
        if self.enable_memory_tracking:
            tracemalloc.start()
    
    def profile_operation(self, operation_name: Optional[str] = None):
        """Decorator to profile function execution.
        
        Args:
            operation_name: Optional custom name for the operation
            
        Returns:
            Decorated function with profiling capabilities
        """
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.profile_context(op_name) as metrics:
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        metrics.error_count += 1
                        raise
            
            return wrapper
        return decorator
    
    @contextmanager
    def profile_context(self, operation_name: str, correlation_id: Optional[str] = None):
        """Context manager for profiling code blocks.
        
        Args:
            operation_name: Name of the operation being profiled
            correlation_id: Optional correlation ID for tracing
            
        Yields:
            PerformanceMetrics object that gets populated during execution
        """
        if correlation_id is None:
            correlation_id = str(uuid4())
        
        # Initialize metrics
        start_time = datetime.utcnow()
        start_perf = time.perf_counter()
        start_cpu = time.process_time()
        
        # Memory tracking
        memory_start = 0.0
        if self.enable_memory_tracking:
            current, peak = tracemalloc.get_traced_memory()
            memory_start = current / 1024 / 1024  # Convert to MB
        
        # Create metrics object
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=start_time,
            end_time=start_time,  # Will be updated
            duration_ms=0.0,
            memory_peak_mb=0.0,
            memory_current_mb=memory_start,
            cpu_time_ms=0.0,
            correlation_id=correlation_id
        )
        
        try:
            yield metrics
        finally:
            # Calculate final metrics
            end_time = datetime.utcnow()
            end_perf = time.perf_counter()
            end_cpu = time.process_time()
            
            metrics.end_time = end_time
            metrics.duration_ms = (end_perf - start_perf) * 1000
            metrics.cpu_time_ms = (end_cpu - start_cpu) * 1000
            
            # Memory tracking
            if self.enable_memory_tracking:
                current, peak = tracemalloc.get_traced_memory()
                metrics.memory_current_mb = current / 1024 / 1024
                metrics.memory_peak_mb = peak / 1024 / 1024
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Update aggregated metrics
            if operation_name not in self.aggregated_metrics:
                self.aggregated_metrics[operation_name] = AggregatedMetrics(operation_name)
            
            self.aggregated_metrics[operation_name].add_measurement(metrics)
    
    def start_detailed_profiling(self, operation_name: str) -> str:
        """Start detailed CPU profiling for an operation.
        
        Args:
            operation_name: Name of the operation to profile
            
        Returns:
            Profile ID for stopping the profiling session
        """
        profile_id = f"{operation_name}_{uuid4()}"
        profiler = cProfile.Profile()
        profiler.enable()
        
        self.active_profiles[profile_id] = profiler
        return profile_id
    
    def stop_detailed_profiling(self, profile_id: str) -> str:
        """Stop detailed CPU profiling and return results.
        
        Args:
            profile_id: ID of the profiling session to stop
            
        Returns:
            Formatted profiling results as string
        """
        if profile_id not in self.active_profiles:
            return "Profile ID not found"
        
        profiler = self.active_profiles.pop(profile_id)
        profiler.disable()
        
        # Generate profiling report
        output = io.StringIO()
        stats = pstats.Stats(profiler, stream=output)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        return output.getvalue()
    
    def get_operation_metrics(self, operation_name: str) -> Optional[AggregatedMetrics]:
        """Get aggregated metrics for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Aggregated metrics or None if operation not found
        """
        return self.aggregated_metrics.get(operation_name)
    
    def get_all_metrics(self) -> Dict[str, AggregatedMetrics]:
        """Get all aggregated metrics.
        
        Returns:
            Dictionary of all aggregated metrics by operation name
        """
        return self.aggregated_metrics.copy()
    
    def get_recent_metrics(self, limit: int = 100) -> List[PerformanceMetrics]:
        """Get recent performance metrics.
        
        Args:
            limit: Maximum number of recent metrics to return
            
        Returns:
            List of recent performance metrics
        """
        return self.metrics_history[-limit:]
    
    def get_slow_operations(self, threshold_ms: float = 1000.0) -> List[PerformanceMetrics]:
        """Get operations that exceeded the specified duration threshold.
        
        Args:
            threshold_ms: Duration threshold in milliseconds
            
        Returns:
            List of slow operations
        """
        return [
            metrics for metrics in self.metrics_history
            if metrics.duration_ms > threshold_ms
        ]
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report.
        
        Returns:
            Dictionary containing performance analysis
        """
        total_operations = len(self.metrics_history)
        total_errors = sum(m.error_count for m in self.metrics_history)
        
        if total_operations == 0:
            return {"message": "No operations recorded"}
        
        # Calculate overall statistics
        durations = [m.duration_ms for m in self.metrics_history]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        # Find bottlenecks
        slow_operations = self.get_slow_operations(avg_duration * 2)  # 2x average
        
        # Memory statistics
        memory_peaks = [m.memory_peak_mb for m in self.metrics_history if m.memory_peak_mb > 0]
        max_memory = max(memory_peaks) if memory_peaks else 0
        
        return {
            "summary": {
                "total_operations": total_operations,
                "total_errors": total_errors,
                "error_rate_percent": (total_errors / total_operations) * 100,
                "avg_duration_ms": avg_duration,
                "min_duration_ms": min_duration,
                "max_duration_ms": max_duration,
                "max_memory_mb": max_memory
            },
            "bottlenecks": {
                "slow_operations_count": len(slow_operations),
                "slowest_operation": max(self.metrics_history, key=lambda m: m.duration_ms).__dict__ if self.metrics_history else None
            },
            "operations": {
                name: {
                    "total_calls": metrics.total_calls,
                    "avg_duration_ms": metrics.avg_duration_ms,
                    "p95_duration_ms": metrics.p95_duration_ms,
                    "error_rate_percent": (metrics.total_errors / metrics.total_calls) * 100 if metrics.total_calls > 0 else 0
                }
                for name, metrics in self.aggregated_metrics.items()
            }
        }
    
    def clear_metrics(self):
        """Clear all stored metrics."""
        self.metrics_history.clear()
        self.aggregated_metrics.clear()
    
    def export_metrics_csv(self, filename: str):
        """Export metrics to CSV file.
        
        Args:
            filename: Path to the CSV file to create
        """
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'operation_name', 'start_time', 'duration_ms', 'memory_peak_mb',
                'cpu_time_ms', 'call_count', 'error_count', 'correlation_id'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for metrics in self.metrics_history:
                writer.writerow({
                    'operation_name': metrics.operation_name,
                    'start_time': metrics.start_time.isoformat(),
                    'duration_ms': metrics.duration_ms,
                    'memory_peak_mb': metrics.memory_peak_mb,
                    'cpu_time_ms': metrics.cpu_time_ms,
                    'call_count': metrics.call_count,
                    'error_count': metrics.error_count,
                    'correlation_id': metrics.correlation_id
                })


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance.
    
    Returns:
        Global PerformanceProfiler instance
    """
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def profile(operation_name: Optional[str] = None):
    """Convenience decorator for profiling functions.
    
    Args:
        operation_name: Optional custom name for the operation
        
    Returns:
        Decorated function with profiling
    """
    return get_profiler().profile_operation(operation_name)


@contextmanager
def profile_block(operation_name: str, correlation_id: Optional[str] = None):
    """Convenience context manager for profiling code blocks.
    
    Args:
        operation_name: Name of the operation being profiled
        correlation_id: Optional correlation ID for tracing
        
    Yields:
        PerformanceMetrics object
    """
    with get_profiler().profile_context(operation_name, correlation_id) as metrics:
        yield metrics
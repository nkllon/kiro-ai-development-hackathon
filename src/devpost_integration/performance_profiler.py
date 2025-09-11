"""
Performance Profiler Module

Provides comprehensive performance profiling and monitoring capabilities.
Implements R9.2: Performance Profiling requirements.
"""

import time
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from functools import wraps

from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus
from .logging_infrastructure import get_logging_infrastructure, log_performance, LogLevel


@dataclass
class ProfilingContext:
    """Profiling context for tracking operation performance"""
    operation_id: str
    operation_name: str
    start_time: datetime
    start_memory: int
    start_cpu: float
    metadata: Dict[str, Any]


@dataclass
class ProfilingResult:
    """Profiling result with performance metrics"""
    operation_id: str
    operation_name: str
    duration: float  # seconds
    memory_delta: int  # bytes
    cpu_delta: float  # percentage
    end_time: datetime
    metadata: Dict[str, Any]


@dataclass
class PerformanceMetrics:
    """Performance metrics for a module or operation"""
    total_operations: int
    total_duration: float
    average_duration: float
    min_duration: float
    max_duration: float
    memory_usage: int
    cpu_usage: float
    error_count: int
    success_rate: float


class MetricsStore:
    """In-memory metrics store for performance data"""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.operation_history: List[ProfilingResult] = []
        self.lock = threading.Lock()
    
    def add_result(self, result: ProfilingResult) -> None:
        """Add profiling result to store"""
        with self.lock:
            self.operation_history.append(result)
            
            # Update metrics for operation
            operation_name = result.operation_name
            if operation_name not in self.metrics:
                self.metrics[operation_name] = PerformanceMetrics(
                    total_operations=0,
                    total_duration=0.0,
                    average_duration=0.0,
                    min_duration=float('inf'),
                    max_duration=0.0,
                    memory_usage=0,
                    cpu_usage=0.0,
                    error_count=0,
                    success_rate=0.0
                )
            
            metrics = self.metrics[operation_name]
            metrics.total_operations += 1
            metrics.total_duration += result.duration
            metrics.average_duration = metrics.total_duration / metrics.total_operations
            metrics.min_duration = min(metrics.min_duration, result.duration)
            metrics.max_duration = max(metrics.max_duration, result.duration)
            metrics.memory_usage = result.memory_delta
            metrics.cpu_usage = result.cpu_delta
    
    def get_metrics(self, operation_name: Optional[str] = None) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics"""
        with self.lock:
            if operation_name:
                return {operation_name: self.metrics.get(operation_name)}
            return self.metrics.copy()
    
    def get_operation_history(self, operation_name: Optional[str] = None) -> List[ProfilingResult]:
        """Get operation history"""
        with self.lock:
            if operation_name:
                return [r for r in self.operation_history if r.operation_name == operation_name]
            return self.operation_history.copy()
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        with self.lock:
            self.metrics.clear()
            self.operation_history.clear()


class PerformanceProfiler(ReflectiveModule):
    """
    Performance Profiler for DevPost Integration
    
    Provides comprehensive performance profiling and monitoring capabilities.
    Implements R9.2: Performance Profiling.
    """
    
    def __init__(self, metrics_store: Optional[MetricsStore] = None):
        """Initialize performance profiler"""
        super().__init__(module_id="performance_profiler", version="1.0.0")
        self.metrics_store = metrics_store or MetricsStore()
        self.active_profiles: Dict[str, ProfilingContext] = {}
        self.logging = get_logging_infrastructure()
        register_module(self)
    
    def start_profiling(self, operation_name: str, metadata: Dict[str, Any] = None) -> ProfilingContext:
        """Start profiling an operation"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        # Get current system metrics
        process = psutil.Process()
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        
        context = ProfilingContext(
            operation_id=operation_id,
            operation_name=operation_name,
            start_time=datetime.now(),
            start_memory=start_memory,
            start_cpu=start_cpu,
            metadata=metadata or {}
        )
        
        self.active_profiles[operation_id] = context
        
        self.logging.log_event(
            LogLevel.DEBUG,
            f"Started profiling: {operation_name}",
            {"operation_id": operation_id, "metadata": metadata}
        )
        
        return context
    
    def end_profiling(self, context: ProfilingContext) -> ProfilingResult:
        """End profiling and return results"""
        if context.operation_id not in self.active_profiles:
            raise ValueError(f"Profiling context not found: {context.operation_id}")
        
        # Get current system metrics
        process = psutil.Process()
        end_memory = process.memory_info().rss
        end_cpu = process.cpu_percent()
        
        # Calculate deltas
        duration = (datetime.now() - context.start_time).total_seconds()
        memory_delta = end_memory - context.start_memory
        cpu_delta = end_cpu - context.start_cpu
        
        result = ProfilingResult(
            operation_id=context.operation_id,
            operation_name=context.operation_name,
            duration=duration,
            memory_delta=memory_delta,
            cpu_delta=cpu_delta,
            end_time=datetime.now(),
            metadata=context.metadata
        )
        
        # Store result
        self.metrics_store.add_result(result)
        
        # Remove from active profiles
        del self.active_profiles[context.operation_id]
        
        # Log performance
        self.logging.log_performance(
            context.operation_name,
            duration,
            {
                "memory_delta": memory_delta,
                "cpu_delta": cpu_delta,
                "operation_id": context.operation_id
            }
        )
        
        return result
    
    @contextmanager
    def profile_operation(self, operation_name: str, metadata: Dict[str, Any] = None):
        """Context manager for profiling operations"""
        context = self.start_profiling(operation_name, metadata)
        try:
            yield context
        finally:
            self.end_profiling(context)
    
    def measure_execution_time(self, operation_name: str = None):
        """Decorator to measure function execution time"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                name = operation_name or f"{func.__module__}.{func.__name__}"
                with self.profile_operation(name, {"function": func.__name__}):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_performance_metrics(self, operation_name: Optional[str] = None) -> Dict[str, PerformanceMetrics]:
        """Get comprehensive performance metrics"""
        return self.metrics_store.get_metrics(operation_name)
    
    def get_operation_history(self, operation_name: Optional[str] = None) -> List[ProfilingResult]:
        """Get operation history"""
        return self.metrics_store.get_operation_history(operation_name)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        process = psutil.Process()
        return {
            "memory_usage": process.memory_info().rss,
            "cpu_percent": process.cpu_percent(),
            "thread_count": process.num_threads(),
            "open_files": len(process.open_files()),
            "active_profiles": len(self.active_profiles)
        }
    
    def clear_metrics(self) -> None:
        """Clear all performance metrics"""
        self.metrics_store.clear_metrics()
        self.logging.log_event(
            LogLevel.INFO,
            "Performance metrics cleared",
            {"module": self.module_id}
        )
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to file"""
        import json
        
        data = {
            "metrics": {k: asdict(v) for k, v in self.metrics_store.get_metrics().items()},
            "operation_history": [asdict(r) for r in self.metrics_store.get_operation_history()],
            "export_time": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, default=str, indent=2)
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information"""
        return {
            "module_id": self.module_id,
            "version": self.version,
            "type": "PerformanceProfiler",
            "active_profiles": len(self.active_profiles),
            "total_operations": len(self.metrics_store.operation_history),
            "metrics_count": len(self.metrics_store.metrics)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.PERFORMANCE_MONITORING,
            ModuleCapability.METRICS_COLLECTION,
            ModuleCapability.EXECUTION_TIMING,
            ModuleCapability.RESOURCE_MONITORING
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ["reflective_module", "logging_infrastructure"]
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check"""
        issues = []
        
        # Check active profiles
        if len(self.active_profiles) > 100:  # Arbitrary threshold
            issues.append("Too many active profiles, possible memory leak")
        
        # Check metrics store
        if len(self.metrics_store.operation_history) > 100000:  # Arbitrary threshold
            issues.append("Too many operations in history, consider clearing")
        
        # Check system resources
        try:
            system_metrics = self.get_system_metrics()
            if system_metrics["memory_usage"] > 1024 * 1024 * 1024:  # 1GB
                issues.append("High memory usage detected")
        except Exception as e:
            issues.append(f"Failed to get system metrics: {str(e)}")
        
        status = ModuleStatus.HEALTHY if not issues else ModuleStatus.DEGRADED
        score = 100 - len(issues) * 15
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=max(0, score) / 100.0,  # Convert to 0.0-1.0 range
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration"""
        return {
            "active_profiles": len(self.active_profiles),
            "metrics_store_size": len(self.metrics_store.operation_history),
            "dependencies": self.get_dependencies()
        }
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update module configuration"""
        # Update configuration as needed
        self.logging.log_event(
            LogLevel.INFO,
            "Performance profiler configuration updated",
            {"config": config}
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        return {
            "active_profiles": len(self.active_profiles),
            "total_operations": len(self.metrics_store.operation_history),
            "metrics_count": len(self.metrics_store.metrics),
            "system_metrics": self.get_system_metrics()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self.clear_metrics()
        self.logging.log_event(
            LogLevel.INFO,
            "Performance profiler metrics reset",
            {"module": self.module_id}
        )


# Global performance profiler instance
_performance_profiler: Optional[PerformanceProfiler] = None


def get_performance_profiler() -> PerformanceProfiler:
    """Get global performance profiler instance"""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler


def profile_operation(operation_name: str, metadata: Dict[str, Any] = None):
    """Profile operation using global profiler"""
    return get_performance_profiler().profile_operation(operation_name, metadata)


def measure_execution_time(operation_name: str = None):
    """Measure execution time using global profiler"""
    return get_performance_profiler().measure_execution_time(operation_name)

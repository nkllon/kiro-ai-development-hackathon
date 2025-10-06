"""Performance monitoring and analysis for Constellation Orchestrator."""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from functools import wraps
import structlog


@dataclass
class PerformanceSnapshot:
    """Point-in-time performance snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    active_tasks: int
    agent_count: int
    throughput: float  # tasks per minute


class PerformanceMonitor:
    """Comprehensive performance monitoring and analysis."""
    
    def __init__(self, snapshot_interval: int = 30):
        """Initialize performance monitor."""
        self.snapshot_interval = snapshot_interval
        self.logger = structlog.get_logger(__name__)
        
        # Performance data
        self.snapshots: List[PerformanceSnapshot] = []
        self.operation_timings: Dict[str, List[float]] = {}
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.cpu_threshold = 80.0  # CPU usage percentage
        self.memory_threshold = 80.0  # Memory usage percentage
        self.response_time_threshold = 5.0  # seconds
        
        # Callbacks for performance alerts
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        self.logger.info("performance_monitor_initialized", snapshot_interval=snapshot_interval)
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self) -> None:
        """Start continuous performance monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("performance_monitoring_started")
    
    async def stop_monitoring(self) -> None:
        """Stop continuous performance monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None
        
        self.logger.info("performance_monitoring_stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        try:
            while self.is_monitoring:
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)
                
                # Keep only last 24 hours of snapshots
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
                
                # Check for performance issues
                await self._check_performance_alerts(snapshot)
                
                await asyncio.sleep(self.snapshot_interval)
                
        except asyncio.CancelledError:
            self.logger.info("performance_monitoring_cancelled")
        except Exception as e:
            self.logger.error(
                "performance_monitoring_error",
                error=str(e),
                error_type=type(e).__name__
            )
    
    def _take_snapshot(self, active_tasks: int = 0, agent_count: int = 0) -> PerformanceSnapshot:
        """Take a performance snapshot."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            memory_percent = memory.percent
            
            # Calculate throughput (tasks per minute)
            throughput = 0.0
            if len(self.snapshots) > 0:
                # Calculate based on recent snapshots
                recent_snapshots = [s for s in self.snapshots[-10:] if s.active_tasks > 0]
                if recent_snapshots:
                    time_span = (datetime.utcnow() - recent_snapshots[0].timestamp).total_seconds()
                    if time_span > 0:
                        total_tasks = sum(s.active_tasks for s in recent_snapshots)
                        throughput = (total_tasks * 60) / time_span
            
            snapshot = PerformanceSnapshot(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                active_tasks=active_tasks,
                agent_count=agent_count,
                throughput=throughput
            )
            
            self.logger.debug(
                "performance_snapshot_taken",
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                active_tasks=active_tasks,
                throughput=throughput
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.error(
                "performance_snapshot_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Return default snapshot
            return PerformanceSnapshot(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_mb=0.0,
                memory_percent=0.0,
                active_tasks=active_tasks,
                agent_count=agent_count,
                throughput=0.0
            )
    
    async def _check_performance_alerts(self, snapshot: PerformanceSnapshot) -> None:
        """Check for performance issues and trigger alerts."""
        alerts = []
        
        # CPU usage alert
        if snapshot.cpu_percent > self.cpu_threshold:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f'CPU usage is {snapshot.cpu_percent:.1f}%, exceeding threshold of {self.cpu_threshold}%',
                'value': snapshot.cpu_percent,
                'threshold': self.cpu_threshold
            })
        
        # Memory usage alert
        if snapshot.memory_percent > self.memory_threshold:
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f'Memory usage is {snapshot.memory_percent:.1f}%, exceeding threshold of {self.memory_threshold}%',
                'value': snapshot.memory_percent,
                'threshold': self.memory_threshold
            })
        
        # Low throughput alert
        if len(self.snapshots) > 5 and snapshot.throughput < 1.0 and snapshot.active_tasks > 0:
            alerts.append({
                'type': 'low_throughput',
                'severity': 'info',
                'message': f'Low throughput detected: {snapshot.throughput:.2f} tasks/minute',
                'value': snapshot.throughput,
                'threshold': 1.0
            })
        
        # Trigger alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert['type'], alert)
                except Exception as e:
                    self.logger.error(
                        "performance_alert_callback_failed",
                        alert_type=alert['type'],
                        error=str(e),
                        error_type=type(e).__name__
                    )
    
    def record_operation_timing(self, operation: str, duration: float) -> None:
        """Record timing for an operation."""
        if operation not in self.operation_timings:
            self.operation_timings[operation] = []
        
        self.operation_timings[operation].append(duration)
        
        # Keep only last 1000 timings per operation
        if len(self.operation_timings[operation]) > 1000:
            self.operation_timings[operation] = self.operation_timings[operation][-1000:]
        
        # Check for slow operations
        if duration > self.response_time_threshold:
            self.logger.warning(
                "slow_operation_detected",
                operation=operation,
                duration=duration,
                threshold=self.response_time_threshold
            )
    
    def time_operation(self, operation: str):
        """Decorator to time operation execution."""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        duration = time.time() - start_time
                        self.record_operation_timing(operation, duration)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        duration = time.time() - start_time
                        self.record_operation_timing(operation, duration)
                return sync_wrapper
        return decorator
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        
        # Calculate averages over last hour
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_snapshots = [s for s in self.snapshots if s.timestamp > hour_ago]
        
        metrics = {
            'current_cpu_percent': latest.cpu_percent,
            'current_memory_mb': latest.memory_mb,
            'current_memory_percent': latest.memory_percent,
            'current_throughput': latest.throughput,
            'snapshot_count': len(self.snapshots)
        }
        
        if recent_snapshots:
            metrics.update({
                'avg_cpu_percent_1h': sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots),
                'avg_memory_percent_1h': sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots),
                'avg_throughput_1h': sum(s.throughput for s in recent_snapshots) / len(recent_snapshots),
                'max_cpu_percent_1h': max(s.cpu_percent for s in recent_snapshots),
                'max_memory_percent_1h': max(s.memory_percent for s in recent_snapshots)
            })
        
        return metrics
    
    def get_operation_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for recorded operations."""
        stats = {}
        
        for operation, timings in self.operation_timings.items():
            if not timings:
                continue
            
            stats[operation] = {
                'count': len(timings),
                'average': sum(timings) / len(timings),
                'min': min(timings),
                'max': max(timings),
                'median': sorted(timings)[len(timings) // 2],
                'p95': sorted(timings)[int(len(timings) * 0.95)] if len(timings) > 20 else max(timings)
            }
        
        return stats
    
    def get_performance_recommendations(self) -> List[str]:
        """Analyze performance data and provide optimization recommendations."""
        recommendations = []
        
        if not self.snapshots:
            return recommendations
        
        # Analyze recent performance
        recent_snapshots = self.snapshots[-10:] if len(self.snapshots) >= 10 else self.snapshots
        
        if recent_snapshots:
            avg_cpu = sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots)
            avg_memory = sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots)
            avg_throughput = sum(s.throughput for s in recent_snapshots) / len(recent_snapshots)
            
            # CPU recommendations
            if avg_cpu > 80:
                recommendations.append("High CPU usage detected. Consider reducing max_concurrent_agents.")
            elif avg_cpu < 20 and avg_throughput < 5:
                recommendations.append("Low CPU usage with low throughput. Consider increasing max_concurrent_agents.")
            
            # Memory recommendations
            if avg_memory > 80:
                recommendations.append("High memory usage detected. Consider reducing max_memory_tasks or implementing more aggressive cleanup.")
            
            # Throughput recommendations
            if avg_throughput < 1 and any(s.active_tasks > 0 for s in recent_snapshots):
                recommendations.append("Low throughput detected. Check for agent communication issues or task complexity.")
        
        # Operation timing recommendations
        operation_stats = self.get_operation_statistics()
        for operation, stats in operation_stats.items():
            if stats['average'] > self.response_time_threshold:
                recommendations.append(f"Slow {operation} operations detected (avg: {stats['average']:.2f}s). Consider optimization.")
        
        return recommendations
    
    def export_performance_data(self) -> Dict[str, Any]:
        """Export all performance data for analysis."""
        return {
            'snapshots': [
                {
                    'timestamp': s.timestamp.isoformat(),
                    'cpu_percent': s.cpu_percent,
                    'memory_mb': s.memory_mb,
                    'memory_percent': s.memory_percent,
                    'active_tasks': s.active_tasks,
                    'agent_count': s.agent_count,
                    'throughput': s.throughput
                }
                for s in self.snapshots
            ],
            'operation_timings': self.operation_timings,
            'operation_statistics': self.get_operation_statistics(),
            'performance_metrics': self.get_performance_metrics(),
            'recommendations': self.get_performance_recommendations()
        }
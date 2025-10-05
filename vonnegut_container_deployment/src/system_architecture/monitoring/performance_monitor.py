#!/usr/bin/env python3
"""
Performance Monitor - Phase 5 Task 5.4

Monitors documentation generation performance and resource usage
with optimization strategies and scalability thresholds.
"""

import asyncio
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
import statistics

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class PerformanceMetric:
    """Represents a performance measurement."""
    metric_id: str
    component: str
    operation: str
    timestamp: datetime
    execution_time: float  # seconds
    cpu_usage: float      # percentage
    memory_usage: float   # MB
    disk_io: Dict[str, float]  # read/write bytes
    network_io: Dict[str, float]  # sent/received bytes
    custom_metrics: Dict[str, Any] = None


@dataclass
class PerformanceThreshold:
    """Defines performance thresholds for monitoring."""
    component: str
    operation: str
    max_execution_time: float  # seconds
    max_cpu_usage: float      # percentage
    max_memory_usage: float   # MB
    alert_threshold: float = 0.8  # Trigger alert at 80% of max
    critical_threshold: float = 0.95  # Critical at 95% of max


@dataclass
class PerformanceAlert:
    """Represents a performance alert."""
    alert_id: str
    component: str
    operation: str
    metric_type: str  # 'execution_time', 'cpu_usage', 'memory_usage'
    current_value: float
    threshold_value: float
    severity: str  # 'warning', 'critical'
    timestamp: datetime
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


class PerformanceMonitor(ReflectiveModule):
    """
    Performance monitoring and optimization system.
    
    Monitors documentation generation performance, tracks resource usage,
    and provides optimization recommendations with scalability analysis.
    """
    
    def __init__(self, history_size: int = 10000):
        super().__init__()
        self.history_size = history_size
        self.performance_metrics: deque = deque(maxlen=history_size)
        self.performance_thresholds: Dict[str, PerformanceThreshold] = {}
        self.performance_alerts: List[PerformanceAlert] = []
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # System baseline
        self.system_baseline: Optional[Dict[str, float]] = None
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        # Register capabilities
        self.register_capability('performance_monitoring', {
            'description': 'Performance monitoring and optimization for documentation generation',
            'thresholds_configured': len(self.performance_thresholds),
            'monitoring_active': self.monitoring_active
        })    

    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds."""
        default_thresholds = [
            # Discovery component thresholds
            PerformanceThreshold(
                component='InfrastructureDiscoverer',
                operation='discover_services',
                max_execution_time=300.0,  # 5 minutes
                max_cpu_usage=50.0,        # 50%
                max_memory_usage=512.0     # 512 MB
            ),
            PerformanceThreshold(
                component='ServiceDiscoveryScanner',
                operation='scan_services',
                max_execution_time=240.0,  # 4 minutes
                max_cpu_usage=40.0,        # 40%
                max_memory_usage=256.0     # 256 MB
            ),
            PerformanceThreshold(
                component='ObservatoryWebSocketClient',
                operation='connect_websocket',
                max_execution_time=30.0,   # 30 seconds
                max_cpu_usage=20.0,        # 20%
                max_memory_usage=128.0     # 128 MB
            ),
            
            # Analysis component thresholds
            PerformanceThreshold(
                component='RelationshipMapper',
                operation='map_relationships',
                max_execution_time=360.0,  # 6 minutes
                max_cpu_usage=60.0,        # 60%
                max_memory_usage=1024.0    # 1 GB
            ),
            PerformanceThreshold(
                component='DataFlowMapper',
                operation='map_data_flows',
                max_execution_time=300.0,  # 5 minutes
                max_cpu_usage=50.0,        # 50%
                max_memory_usage=512.0     # 512 MB
            ),
            PerformanceThreshold(
                component='AutomationChainAnalyzer',
                operation='analyze_chains',
                max_execution_time=420.0,  # 7 minutes
                max_cpu_usage=45.0,        # 45%
                max_memory_usage=768.0     # 768 MB
            ),
            
            # Generation component thresholds
            PerformanceThreshold(
                component='DiagramGenerator',
                operation='generate_diagrams',
                max_execution_time=480.0,  # 8 minutes
                max_cpu_usage=70.0,        # 70%
                max_memory_usage=2048.0    # 2 GB
            ),
            PerformanceThreshold(
                component='SequenceDiagramGenerator',
                operation='generate_sequences',
                max_execution_time=360.0,  # 6 minutes
                max_cpu_usage=60.0,        # 60%
                max_memory_usage=1024.0    # 1 GB
            ),
            PerformanceThreshold(
                component='NetworkTopologyVisualizer',
                operation='visualize_topology',
                max_execution_time=300.0,  # 5 minutes
                max_cpu_usage=55.0,        # 55%
                max_memory_usage=1536.0    # 1.5 GB
            ),
            
            # Orchestration component thresholds
            PerformanceThreshold(
                component='DocumentationOrchestrator',
                operation='orchestrate_generation',
                max_execution_time=1800.0, # 30 minutes
                max_cpu_usage=80.0,        # 80%
                max_memory_usage=4096.0    # 4 GB
            ),
            PerformanceThreshold(
                component='RealTimeValidator',
                operation='validate_documentation',
                max_execution_time=240.0,  # 4 minutes
                max_cpu_usage=40.0,        # 40%
                max_memory_usage=512.0     # 512 MB
            )
        ]
        
        for threshold in default_thresholds:
            key = f"{threshold.component}:{threshold.operation}"
            self.performance_thresholds[key] = threshold
    
    async def start_monitoring(self, interval_seconds: int = 60) -> Dict[str, Any]:
        """Start performance monitoring."""
        try:
            if self.monitoring_active:
                return {'status': 'already_running'}
            
            # Establish system baseline
            await self._establish_system_baseline()
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(
                self._monitoring_loop(interval_seconds)
            )
            
            self.logger.info(f"Performance monitoring started with {interval_seconds}s intervals")
            
            return {
                'status': 'started',
                'interval_seconds': interval_seconds,
                'thresholds_configured': len(self.performance_thresholds),
                'system_baseline': self.system_baseline
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start performance monitoring: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop performance monitoring."""
        try:
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                self.monitoring_task = None
            
            self.logger.info("Performance monitoring stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            self.logger.error(f"Error stopping performance monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _establish_system_baseline(self):
        """Establish system performance baseline."""
        try:
            # Collect baseline metrics over a short period
            baseline_samples = []
            
            for _ in range(5):  # 5 samples over 10 seconds
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                baseline_samples.append({
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.used / (1024 * 1024),  # MB
                    'memory_percent': memory.percent,
                    'disk_read': disk_io.read_bytes if disk_io else 0,
                    'disk_write': disk_io.write_bytes if disk_io else 0,
                    'network_sent': network_io.bytes_sent if network_io else 0,
                    'network_recv': network_io.bytes_recv if network_io else 0
                })
                
                await asyncio.sleep(2)
            
            # Calculate baseline averages
            self.system_baseline = {
                'cpu_usage': statistics.mean([s['cpu_usage'] for s in baseline_samples]),
                'memory_usage': statistics.mean([s['memory_usage'] for s in baseline_samples]),
                'memory_percent': statistics.mean([s['memory_percent'] for s in baseline_samples]),
                'disk_read_rate': 0,  # Will be calculated during monitoring
                'disk_write_rate': 0,
                'network_sent_rate': 0,
                'network_recv_rate': 0
            }
            
            self.logger.info(f"System baseline established: CPU={self.system_baseline['cpu_usage']:.1f}%, "
                           f"Memory={self.system_baseline['memory_usage']:.1f}MB")
            
        except Exception as e:
            self.logger.error(f"Error establishing system baseline: {e}")
            self.system_baseline = {
                'cpu_usage': 10.0,
                'memory_usage': 1024.0,
                'memory_percent': 20.0,
                'disk_read_rate': 0,
                'disk_write_rate': 0,
                'network_sent_rate': 0,
                'network_recv_rate': 0
            }
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Main performance monitoring loop."""
        last_disk_io = None
        last_network_io = None
        last_timestamp = None
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                # Calculate rates if we have previous data
                disk_rates = {'read_rate': 0, 'write_rate': 0}
                network_rates = {'sent_rate': 0, 'recv_rate': 0}
                
                if last_disk_io and last_timestamp and disk_io:
                    time_delta = current_time - last_timestamp
                    disk_rates['read_rate'] = (disk_io.read_bytes - last_disk_io.read_bytes) / time_delta
                    disk_rates['write_rate'] = (disk_io.write_bytes - last_disk_io.write_bytes) / time_delta
                
                if last_network_io and last_timestamp and network_io:
                    time_delta = current_time - last_timestamp
                    network_rates['sent_rate'] = (network_io.bytes_sent - last_network_io.bytes_sent) / time_delta
                    network_rates['recv_rate'] = (network_io.bytes_recv - last_network_io.bytes_recv) / time_delta
                
                # Create system performance metric
                system_metric = PerformanceMetric(
                    metric_id=f"system_{int(current_time)}",
                    component='System',
                    operation='baseline_monitoring',
                    timestamp=datetime.now(),
                    execution_time=0.0,
                    cpu_usage=cpu_percent,
                    memory_usage=memory.used / (1024 * 1024),  # MB
                    disk_io=disk_rates,
                    network_io=network_rates,
                    custom_metrics={
                        'memory_percent': memory.percent,
                        'memory_available': memory.available / (1024 * 1024),
                        'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                    }
                )
                
                # Add to metrics history
                self.performance_metrics.append(system_metric)
                
                # Check for performance alerts
                await self._check_performance_alerts(system_metric)
                
                # Update for next iteration
                last_disk_io = disk_io
                last_network_io = network_io
                last_timestamp = current_time
                
                # Wait for next monitoring cycle
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def record_operation_performance(self, component: str, operation: str,
                                         execution_time: float,
                                         custom_metrics: Optional[Dict[str, Any]] = None) -> str:
        """Record performance metrics for a specific operation."""
        try:
            # Collect current system metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            metric_id = f"{component}_{operation}_{int(time.time())}"
            
            metric = PerformanceMetric(
                metric_id=metric_id,
                component=component,
                operation=operation,
                timestamp=datetime.now(),
                execution_time=execution_time,
                cpu_usage=cpu_percent,
                memory_usage=memory.used / (1024 * 1024),  # MB
                disk_io={
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                network_io={
                    'sent_bytes': network_io.bytes_sent if network_io else 0,
                    'recv_bytes': network_io.bytes_recv if network_io else 0
                },
                custom_metrics=custom_metrics or {}
            )
            
            # Add to metrics history
            self.performance_metrics.append(metric)
            
            # Check against thresholds
            await self._check_operation_thresholds(metric)
            
            self.logger.debug(f"Recorded performance for {component}.{operation}: {execution_time:.2f}s")
            
            return metric_id
            
        except Exception as e:
            self.logger.error(f"Error recording operation performance: {e}")
            return ""
    
    async def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check system performance against baseline and generate alerts."""
        if not self.system_baseline:
            return
        
        # Check CPU usage
        cpu_threshold = self.system_baseline['cpu_usage'] * 3  # Alert if 3x baseline
        if metric.cpu_usage > cpu_threshold:
            await self._create_performance_alert(
                component='System',
                operation='cpu_usage',
                metric_type='cpu_usage',
                current_value=metric.cpu_usage,
                threshold_value=cpu_threshold,
                severity='warning' if metric.cpu_usage < cpu_threshold * 1.5 else 'critical'
            )
        
        # Check memory usage
        memory_threshold = self.system_baseline['memory_usage'] * 2  # Alert if 2x baseline
        if metric.memory_usage > memory_threshold:
            await self._create_performance_alert(
                component='System',
                operation='memory_usage',
                metric_type='memory_usage',
                current_value=metric.memory_usage,
                threshold_value=memory_threshold,
                severity='warning' if metric.memory_usage < memory_threshold * 1.5 else 'critical'
            )
    
    async def _check_operation_thresholds(self, metric: PerformanceMetric):
        """Check operation performance against configured thresholds."""
        threshold_key = f"{metric.component}:{metric.operation}"
        
        if threshold_key not in self.performance_thresholds:
            return
        
        threshold = self.performance_thresholds[threshold_key]
        
        # Check execution time
        if metric.execution_time > threshold.max_execution_time * threshold.alert_threshold:
            severity = 'critical' if metric.execution_time > threshold.max_execution_time * threshold.critical_threshold else 'warning'
            await self._create_performance_alert(
                component=metric.component,
                operation=metric.operation,
                metric_type='execution_time',
                current_value=metric.execution_time,
                threshold_value=threshold.max_execution_time,
                severity=severity
            )
        
        # Check CPU usage
        if metric.cpu_usage > threshold.max_cpu_usage * threshold.alert_threshold:
            severity = 'critical' if metric.cpu_usage > threshold.max_cpu_usage * threshold.critical_threshold else 'warning'
            await self._create_performance_alert(
                component=metric.component,
                operation=metric.operation,
                metric_type='cpu_usage',
                current_value=metric.cpu_usage,
                threshold_value=threshold.max_cpu_usage,
                severity=severity
            )
        
        # Check memory usage
        if metric.memory_usage > threshold.max_memory_usage * threshold.alert_threshold:
            severity = 'critical' if metric.memory_usage > threshold.max_memory_usage * threshold.critical_threshold else 'warning'
            await self._create_performance_alert(
                component=metric.component,
                operation=metric.operation,
                metric_type='memory_usage',
                current_value=metric.memory_usage,
                threshold_value=threshold.max_memory_usage,
                severity=severity
            )
    
    async def _create_performance_alert(self, component: str, operation: str,
                                      metric_type: str, current_value: float,
                                      threshold_value: float, severity: str):
        """Create a performance alert."""
        try:
            alert_id = f"{component}_{operation}_{metric_type}_{int(time.time())}"
            
            # Check for recent similar alerts to avoid spam
            recent_alerts = [
                alert for alert in self.performance_alerts[-10:]
                if alert.component == component and 
                   alert.operation == operation and
                   alert.metric_type == metric_type and
                   alert.timestamp > datetime.now() - timedelta(minutes=15) and
                   not alert.resolved
            ]
            
            if recent_alerts:
                return  # Don't create duplicate alerts
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                component=component,
                operation=operation,
                metric_type=metric_type,
                current_value=current_value,
                threshold_value=threshold_value,
                severity=severity,
                timestamp=datetime.now()
            )
            
            self.performance_alerts.append(alert)
            
            # Log the alert
            log_level = 'error' if severity == 'critical' else 'warning'
            getattr(self.logger, log_level)(
                f"Performance alert [{severity.upper()}]: {component}.{operation} "
                f"{metric_type}={current_value:.2f} exceeds threshold {threshold_value:.2f}"
            )
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
            
            # Trim alerts history if needed
            if len(self.performance_alerts) > 1000:
                self.performance_alerts = self.performance_alerts[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error creating performance alert: {e}")
    
    def get_performance_summary(self, component: Optional[str] = None,
                              hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics by time and component
        filtered_metrics = [
            metric for metric in self.performance_metrics
            if metric.timestamp > cutoff_time and
               (component is None or metric.component == component)
        ]
        
        if not filtered_metrics:
            return {
                'component': component or 'All',
                'time_period_hours': hours,
                'total_operations': 0,
                'summary': 'No data available'
            }
        
        # Calculate statistics
        execution_times = [m.execution_time for m in filtered_metrics if m.execution_time > 0]
        cpu_usages = [m.cpu_usage for m in filtered_metrics]
        memory_usages = [m.memory_usage for m in filtered_metrics]
        
        # Operation breakdown
        operation_stats = {}
        for metric in filtered_metrics:
            op_key = f"{metric.component}.{metric.operation}"
            if op_key not in operation_stats:
                operation_stats[op_key] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_cpu': 0,
                    'avg_memory': 0
                }
            
            stats = operation_stats[op_key]
            stats['count'] += 1
            stats['total_time'] += metric.execution_time
            stats['avg_cpu'] = (stats['avg_cpu'] * (stats['count'] - 1) + metric.cpu_usage) / stats['count']
            stats['avg_memory'] = (stats['avg_memory'] * (stats['count'] - 1) + metric.memory_usage) / stats['count']
        
        # Recent alerts
        recent_alerts = [
            alert for alert in self.performance_alerts
            if alert.timestamp > cutoff_time and
               (component is None or alert.component == component)
        ]
        
        return {
            'component': component or 'All',
            'time_period_hours': hours,
            'total_operations': len(filtered_metrics),
            'execution_time_stats': {
                'count': len(execution_times),
                'mean': statistics.mean(execution_times) if execution_times else 0,
                'median': statistics.median(execution_times) if execution_times else 0,
                'min': min(execution_times) if execution_times else 0,
                'max': max(execution_times) if execution_times else 0,
                'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            },
            'resource_usage_stats': {
                'avg_cpu_usage': statistics.mean(cpu_usages) if cpu_usages else 0,
                'max_cpu_usage': max(cpu_usages) if cpu_usages else 0,
                'avg_memory_usage': statistics.mean(memory_usages) if memory_usages else 0,
                'max_memory_usage': max(memory_usages) if memory_usages else 0
            },
            'operation_breakdown': operation_stats,
            'alerts_count': len(recent_alerts),
            'critical_alerts': len([a for a in recent_alerts if a.severity == 'critical']),
            'system_baseline': self.system_baseline
        }
    
    def get_scalability_analysis(self, component: str, operation: str) -> Dict[str, Any]:
        """Analyze scalability characteristics for a component operation."""
        # Get metrics for the specific component/operation
        component_metrics = [
            metric for metric in self.performance_metrics
            if metric.component == component and metric.operation == operation
        ]
        
        if len(component_metrics) < 5:
            return {
                'component': component,
                'operation': operation,
                'analysis': 'Insufficient data for scalability analysis',
                'recommendations': ['Collect more performance data']
            }
        
        # Sort by timestamp to analyze trends
        component_metrics.sort(key=lambda x: x.timestamp)
        
        # Analyze trends
        execution_times = [m.execution_time for m in component_metrics]
        memory_usages = [m.memory_usage for m in component_metrics]
        
        # Simple trend analysis
        time_trend = 'stable'
        memory_trend = 'stable'
        
        if len(execution_times) >= 10:
            first_half_time = statistics.mean(execution_times[:len(execution_times)//2])
            second_half_time = statistics.mean(execution_times[len(execution_times)//2:])
            
            if second_half_time > first_half_time * 1.2:
                time_trend = 'increasing'
            elif second_half_time < first_half_time * 0.8:
                time_trend = 'decreasing'
            
            first_half_memory = statistics.mean(memory_usages[:len(memory_usages)//2])
            second_half_memory = statistics.mean(memory_usages[len(memory_usages)//2:])
            
            if second_half_memory > first_half_memory * 1.2:
                memory_trend = 'increasing'
            elif second_half_memory < first_half_memory * 0.8:
                memory_trend = 'decreasing'
        
        # Performance characteristics
        avg_execution_time = statistics.mean(execution_times)
        max_execution_time = max(execution_times)
        avg_memory_usage = statistics.mean(memory_usages)
        max_memory_usage = max(memory_usages)
        
        # Scalability assessment
        scalability_score = 1.0
        bottlenecks = []
        recommendations = []
        
        # Check execution time scalability
        if max_execution_time > avg_execution_time * 3:
            scalability_score -= 0.2
            bottlenecks.append('Execution time variance')
            recommendations.append('Investigate performance spikes')
        
        # Check memory usage scalability
        if max_memory_usage > avg_memory_usage * 2:
            scalability_score -= 0.2
            bottlenecks.append('Memory usage spikes')
            recommendations.append('Optimize memory usage patterns')
        
        # Check trends
        if time_trend == 'increasing':
            scalability_score -= 0.3
            bottlenecks.append('Increasing execution time trend')
            recommendations.append('Performance degradation over time - investigate causes')
        
        if memory_trend == 'increasing':
            scalability_score -= 0.2
            bottlenecks.append('Increasing memory usage trend')
            recommendations.append('Memory leak or inefficient memory usage')
        
        # Threshold analysis
        threshold_key = f"{component}:{operation}"
        if threshold_key in self.performance_thresholds:
            threshold = self.performance_thresholds[threshold_key]
            
            time_utilization = avg_execution_time / threshold.max_execution_time
            memory_utilization = avg_memory_usage / threshold.max_memory_usage
            
            if time_utilization > 0.7:
                recommendations.append(f'Execution time near threshold ({time_utilization:.1%} utilization)')
            
            if memory_utilization > 0.7:
                recommendations.append(f'Memory usage near threshold ({memory_utilization:.1%} utilization)')
        
        return {
            'component': component,
            'operation': operation,
            'scalability_score': max(0.0, scalability_score),
            'performance_characteristics': {
                'avg_execution_time': avg_execution_time,
                'max_execution_time': max_execution_time,
                'avg_memory_usage': avg_memory_usage,
                'max_memory_usage': max_memory_usage,
                'execution_time_trend': time_trend,
                'memory_usage_trend': memory_trend
            },
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'data_points': len(component_metrics)
        }
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add a callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Remove an alert callback."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def set_performance_threshold(self, component: str, operation: str,
                                max_execution_time: float, max_cpu_usage: float,
                                max_memory_usage: float):
        """Set performance threshold for a component operation."""
        threshold = PerformanceThreshold(
            component=component,
            operation=operation,
            max_execution_time=max_execution_time,
            max_cpu_usage=max_cpu_usage,
            max_memory_usage=max_memory_usage
        )
        
        key = f"{component}:{operation}"
        self.performance_thresholds[key] = threshold
        
        self.logger.info(f"Set performance threshold for {key}")
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'monitoring_active': self.monitoring_active,
            'metrics_collected': len(self.performance_metrics),
            'thresholds_configured': len(self.performance_thresholds),
            'active_alerts': len([a for a in self.performance_alerts if not a.resolved]),
            'system_baseline_established': self.system_baseline is not None
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'monitoring_available': True,
            'thresholds_configured': len(self.performance_thresholds) > 0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance monitoring metrics."""
        recent_metrics = [
            m for m in self.performance_metrics
            if m.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        active_alerts = len([a for a in self.performance_alerts if not a.resolved])
        
        return {
            'performance_monitor_metrics_collected': len(self.performance_metrics),
            'performance_monitor_recent_metrics_1h': len(recent_metrics),
            'performance_monitor_active_alerts': active_alerts,
            'performance_monitor_monitoring_active': 1 if self.monitoring_active else 0,
            'performance_monitor_thresholds_configured': len(self.performance_thresholds)
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create performance monitor
        monitor = PerformanceMonitor()
        
        # Add alert callback
        async def handle_alert(alert: PerformanceAlert):
            print(f"PERFORMANCE ALERT [{alert.severity}]: {alert.component}.{alert.operation} "
                  f"{alert.metric_type}={alert.current_value:.2f}")
        
        monitor.add_alert_callback(handle_alert)
        
        # Start monitoring
        result = await monitor.start_monitoring(interval_seconds=30)
        print(f"Monitoring started: {result}")
        
        # Simulate some operations
        await monitor.record_operation_performance('TestComponent', 'test_operation', 2.5)
        await monitor.record_operation_performance('TestComponent', 'test_operation', 5.2)
        
        # Wait a bit
        await asyncio.sleep(5)
        
        # Get performance summary
        summary = monitor.get_performance_summary('TestComponent')
        print(f"Performance summary: {summary}")
        
        # Get scalability analysis
        analysis = monitor.get_scalability_analysis('TestComponent', 'test_operation')
        print(f"Scalability analysis: {analysis}")
        
        # Stop monitoring
        await monitor.stop_monitoring()
    
    asyncio.run(main())
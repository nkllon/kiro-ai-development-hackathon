#!/usr/bin/env python3
"""
Performance Monitoring System
============================

Advanced performance monitoring system for the Beast Mode framework.
Provides real-time performance tracking, resource monitoring, and
intelligent alerting for optimal system performance.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Advanced performance monitoring and metrics collection
"""

import sys
import os
import time
import json
import logging
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import weakref


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types for monitoring."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    id: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold_value: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemResourceUsage:
    """System resource usage snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: Tuple[float, float, float]
    process_count: int
    thread_count: int


@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: datetime
    active_operations: int
    completed_operations: int
    failed_operations: int
    average_response_time_ms: float
    throughput_ops_per_second: float
    cache_hit_rate: float
    error_rate: float
    queue_size: int
    active_threads: int


class PerformanceMonitoringSystem:
    """
    Advanced performance monitoring system.
    
    Provides comprehensive performance tracking, resource monitoring,
    intelligent alerting, and performance optimization recommendations.
    """
    
    def __init__(self, 
                 monitoring_interval: float = 5.0,
                 retention_hours: int = 24,
                 enable_alerts: bool = True):
        """Initialize the performance monitoring system."""
        self.monitoring_interval = monitoring_interval
        self.retention_hours = retention_hours
        self.enable_alerts = enable_alerts
        
        self.logger = self._setup_logging()
        
        # Data storage
        self.metrics: List[PerformanceMetric] = []
        self.system_usage: List[SystemResourceUsage] = []
        self.application_metrics: List[ApplicationMetrics] = []
        self.alerts: List[PerformanceAlert] = []
        
        # Threading and synchronization
        self.monitoring_active = False
        self.monitoring_thread = None
        self.data_lock = threading.RLock()
        
        # Alert thresholds
        self.alert_thresholds = self._initialize_alert_thresholds()
        
        # Performance baselines
        self.baselines = self._initialize_baselines()
        
        # Callbacks for external monitoring
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        self.metric_callbacks: List[Callable[[PerformanceMetric], None]] = []
        
        # Prometheus integration
        self._prometheus_exporter = None
        self._enable_prometheus = self._should_enable_prometheus()
        if self._enable_prometheus:
            self._initialize_prometheus_integration()
        
        # Start monitoring
        self.start_monitoring()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for performance monitoring."""
        logger = logging.getLogger('performance_monitoring_system')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _should_enable_prometheus(self) -> bool:
        """Check if Prometheus metrics should be enabled."""
        import os
        return os.getenv('BEAST_MODE_PROMETHEUS_ENABLED', 'true').lower() == 'true'
    
    def _initialize_prometheus_integration(self):
        """Initialize Prometheus integration."""
        try:
            from beast_mode.monitoring.prometheus_exporter import PrometheusExporter
            import os
            self._prometheus_exporter = PrometheusExporter(
                port=int(os.getenv('BEAST_MODE_PROMETHEUS_PORT', '8000')),
                enable_http_server=True
            )
            self.logger.info("Prometheus integration enabled for PerformanceMonitoringSystem")
        except ImportError:
            self.logger.warning("Prometheus client not available. Install with: pip install prometheus-client")
            self._enable_prometheus = False
        except Exception as e:
            self.logger.error(f"Failed to initialize Prometheus integration: {e}")
            self._enable_prometheus = False
    
    def _initialize_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize alert thresholds for different metrics."""
        return {
            'cpu_percent': {
                'warning': 70.0,
                'error': 85.0,
                'critical': 95.0
            },
            'memory_percent': {
                'warning': 75.0,
                'error': 85.0,
                'critical': 95.0
            },
            'disk_usage_percent': {
                'warning': 80.0,
                'error': 90.0,
                'critical': 95.0
            },
            'response_time_ms': {
                'warning': 1000.0,
                'error': 5000.0,
                'critical': 10000.0
            },
            'error_rate': {
                'warning': 5.0,
                'error': 10.0,
                'critical': 20.0
            },
            'cache_hit_rate': {
                'warning': 80.0,
                'error': 70.0,
                'critical': 60.0
            }
        }
    
    def _initialize_baselines(self) -> Dict[str, float]:
        """Initialize performance baselines."""
        return {
            'cpu_percent': 20.0,
            'memory_percent': 30.0,
            'response_time_ms': 100.0,
            'throughput_ops_per_second': 10.0,
            'cache_hit_rate': 90.0,
            'error_rate': 1.0
        }
    
    def start_monitoring(self):
        """Start performance monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect application metrics
                self._collect_application_metrics()
                
                # Check for alerts
                if self.enable_alerts:
                    self._check_alerts()
                
                # Export to Prometheus if enabled
                if self._enable_prometheus and self._prometheus_exporter:
                    self._export_to_prometheus()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    def _export_to_prometheus(self):
        """Export performance metrics to Prometheus."""
        try:
            if not self._prometheus_exporter:
                return
            
            # Get current metrics
            current_metrics = self.get_current_metrics()
            
            # Export system metrics
            system_usage = current_metrics.get('system_usage', {})
            if system_usage:
                self._prometheus_exporter._export_system_metrics()
            
            # Export application metrics
            app_metrics = current_metrics.get('application_metrics', {})
            if app_metrics:
                self._prometheus_exporter._export_application_metrics()
            
            # Export performance metrics
            perf_metrics = current_metrics.get('performance_metrics', {})
            if perf_metrics:
                self._prometheus_exporter._export_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Failed to export to Prometheus: {e}")
    
    def _collect_system_metrics(self):
        """Collect system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network usage
            network = psutil.net_io_counters()
            
            # Load average
            load_avg = psutil.getloadavg()
            
            # Process and thread counts
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
            
            # Create system usage snapshot
            system_usage = SystemResourceUsage(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                load_average=load_avg,
                process_count=process_count,
                thread_count=thread_count
            )
            
            with self.data_lock:
                self.system_usage.append(system_usage)
                
                # Store individual metrics
                self._store_metric('cpu_percent', cpu_percent, MetricType.GAUGE)
                self._store_metric('memory_percent', memory.percent, MetricType.GAUGE)
                self._store_metric('memory_used_mb', system_usage.memory_used_mb, MetricType.GAUGE)
                self._store_metric('disk_usage_percent', disk.percent, MetricType.GAUGE)
                self._store_metric('disk_free_gb', system_usage.disk_free_gb, MetricType.GAUGE)
                self._store_metric('process_count', process_count, MetricType.GAUGE)
                self._store_metric('thread_count', thread_count, MetricType.GAUGE)
            
        except Exception as e:
            self.logger.error(f"System metrics collection failed: {e}")
    
    def _collect_application_metrics(self):
        """Collect application-specific metrics."""
        try:
            # This would be populated by application components
            # For now, we'll use placeholder values
            app_metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                active_operations=0,
                completed_operations=0,
                failed_operations=0,
                average_response_time_ms=0.0,
                throughput_ops_per_second=0.0,
                cache_hit_rate=0.0,
                error_rate=0.0,
                queue_size=0,
                active_threads=threading.active_count()
            )
            
            with self.data_lock:
                self.application_metrics.append(app_metrics)
                
                # Store application metrics
                self._store_metric('active_operations', app_metrics.active_operations, MetricType.GAUGE)
                self._store_metric('completed_operations', app_metrics.completed_operations, MetricType.COUNTER)
                self._store_metric('failed_operations', app_metrics.failed_operations, MetricType.COUNTER)
                self._store_metric('response_time_ms', app_metrics.average_response_time_ms, MetricType.TIMER)
                self._store_metric('throughput_ops_per_second', app_metrics.throughput_ops_per_second, MetricType.GAUGE)
                self._store_metric('cache_hit_rate', app_metrics.cache_hit_rate, MetricType.GAUGE)
                self._store_metric('error_rate', app_metrics.error_rate, MetricType.GAUGE)
                self._store_metric('queue_size', app_metrics.queue_size, MetricType.GAUGE)
                self._store_metric('active_threads', app_metrics.active_threads, MetricType.GAUGE)
            
        except Exception as e:
            self.logger.error(f"Application metrics collection failed: {e}")
    
    def _store_metric(self, name: str, value: float, metric_type: MetricType, 
                     tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Store a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # Notify callbacks
        for callback in self.metric_callbacks:
            try:
                callback(metric)
            except Exception as e:
                self.logger.error(f"Metric callback error: {e}")
    
    def _check_alerts(self):
        """Check for performance alerts."""
        current_time = datetime.now()
        
        # Get recent metrics
        recent_metrics = [
            m for m in self.metrics
            if (current_time - m.timestamp).total_seconds() < self.monitoring_interval * 2
        ]
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in recent_metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)
        
        # Check each metric against thresholds
        for metric_name, metrics in metrics_by_name.items():
            if metric_name in self.alert_thresholds:
                # Get latest value
                latest_metric = max(metrics, key=lambda m: m.timestamp)
                current_value = latest_metric.value
                
                # Check thresholds
                thresholds = self.alert_thresholds[metric_name]
                
                alert_level = None
                if current_value >= thresholds.get('critical', float('inf')):
                    alert_level = AlertLevel.CRITICAL
                elif current_value >= thresholds.get('error', float('inf')):
                    alert_level = AlertLevel.ERROR
                elif current_value >= thresholds.get('warning', float('inf')):
                    alert_level = AlertLevel.WARNING
                
                # Create alert if threshold exceeded
                if alert_level:
                    self._create_alert(
                        metric_name, current_value, 
                        thresholds.get(alert_level.value, 0),
                        alert_level
                    )
    
    def _create_alert(self, metric_name: str, current_value: float, 
                     threshold_value: float, level: AlertLevel):
        """Create a performance alert."""
        alert_id = f"{metric_name}_{int(time.time())}"
        
        # Check if similar alert already exists
        existing_alerts = [
            a for a in self.alerts
            if (a.metric_name == metric_name and 
                a.level == level and 
                not a.resolved and
                (datetime.now() - a.timestamp).total_seconds() < 300)  # 5 minutes
        ]
        
        if existing_alerts:
            return  # Don't create duplicate alerts
        
        alert = PerformanceAlert(
            id=alert_id,
            level=level,
            message=f"{metric_name} threshold exceeded: {current_value:.2f} >= {threshold_value:.2f}",
            metric_name=metric_name,
            threshold_value=threshold_value,
            current_value=current_value,
            timestamp=datetime.now()
        )
        
        with self.data_lock:
            self.alerts.append(alert)
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        self.logger.warning(f"Performance alert: {alert.message}")
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=self.retention_hours)
        
        with self.data_lock:
            # Clean up metrics
            self.metrics = [
                m for m in self.metrics
                if m.timestamp > cutoff_time
            ]
            
            # Clean up system usage
            self.system_usage = [
                s for s in self.system_usage
                if s.timestamp > cutoff_time
            ]
            
            # Clean up application metrics
            self.application_metrics = [
                a for a in self.application_metrics
                if a.timestamp > cutoff_time
            ]
            
            # Clean up resolved alerts older than 24 hours
            self.alerts = [
                a for a in self.alerts
                if not (a.resolved and a.resolved_at and a.resolved_at < cutoff_time)
            ]
    
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a custom performance metric."""
        self._store_metric(name, value, metric_type, tags, metadata)
    
    def record_timing(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timing metric."""
        self._store_metric(name, duration_ms, MetricType.TIMER, tags)
    
    def increment_counter(self, name: str, increment: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        self._store_metric(name, increment, MetricType.COUNTER, tags)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric value."""
        self._store_metric(name, value, MetricType.GAUGE, tags)
    
    def resolve_alert(self, alert_id: str):
        """Resolve a performance alert."""
        with self.data_lock:
            for alert in self.alerts:
                if alert.id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    self.logger.info(f"Alert resolved: {alert_id}")
                    break
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add alert callback function."""
        self.alert_callbacks.append(callback)
    
    def add_metric_callback(self, callback: Callable[[PerformanceMetric], None]):
        """Add metric callback function."""
        self.metric_callbacks.append(callback)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        current_time = datetime.now()
        
        with self.data_lock:
            # Get latest system usage
            latest_system = self.system_usage[-1] if self.system_usage else None
            
            # Get latest application metrics
            latest_app = self.application_metrics[-1] if self.application_metrics else None
            
            # Get recent metrics (last 5 minutes)
            recent_metrics = [
                m for m in self.metrics
                if (current_time - m.timestamp).total_seconds() < 300
            ]
            
            # Get active alerts
            active_alerts = [
                a for a in self.alerts
                if not a.resolved
            ]
            
            return {
                'timestamp': current_time.isoformat(),
                'system_usage': {
                    'cpu_percent': latest_system.cpu_percent if latest_system else 0,
                    'memory_percent': latest_system.memory_percent if latest_system else 0,
                    'memory_used_mb': latest_system.memory_used_mb if latest_system else 0,
                    'disk_usage_percent': latest_system.disk_usage_percent if latest_system else 0,
                    'disk_free_gb': latest_system.disk_free_gb if latest_system else 0,
                    'load_average': latest_system.load_average if latest_system else (0, 0, 0),
                    'process_count': latest_system.process_count if latest_system else 0,
                    'thread_count': latest_system.thread_count if latest_system else 0
                },
                'application_metrics': {
                    'active_operations': latest_app.active_operations if latest_app else 0,
                    'completed_operations': latest_app.completed_operations if latest_app else 0,
                    'failed_operations': latest_app.failed_operations if latest_app else 0,
                    'average_response_time_ms': latest_app.average_response_time_ms if latest_app else 0,
                    'throughput_ops_per_second': latest_app.throughput_ops_per_second if latest_app else 0,
                    'cache_hit_rate': latest_app.cache_hit_rate if latest_app else 0,
                    'error_rate': latest_app.error_rate if latest_app else 0,
                    'queue_size': latest_app.queue_size if latest_app else 0,
                    'active_threads': latest_app.active_threads if latest_app else 0
                },
                'recent_metrics_count': len(recent_metrics),
                'active_alerts_count': len(active_alerts),
                'total_metrics_stored': len(self.metrics),
                'monitoring_uptime_hours': (current_time - self.start_time).total_seconds() / 3600 if hasattr(self, 'start_time') else 0
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary with trends and recommendations."""
        current_time = datetime.now()
        
        with self.data_lock:
            # Calculate time ranges
            last_hour = current_time - timedelta(hours=1)
            last_day = current_time - timedelta(days=1)
            
            # Filter recent data
            recent_system = [s for s in self.system_usage if s.timestamp > last_hour]
            recent_app = [a for a in self.application_metrics if a.timestamp > last_hour]
            recent_metrics = [m for m in self.metrics if m.timestamp > last_hour]
            
            # Calculate averages
            avg_cpu = sum(s.cpu_percent for s in recent_system) / len(recent_system) if recent_system else 0
            avg_memory = sum(s.memory_percent for s in recent_system) / len(recent_system) if recent_system else 0
            avg_response_time = sum(a.average_response_time_ms for a in recent_app) / len(recent_app) if recent_app else 0
            
            # Calculate trends
            cpu_trend = self._calculate_trend([s.cpu_percent for s in recent_system])
            memory_trend = self._calculate_trend([s.memory_percent for s in recent_system])
            response_trend = self._calculate_trend([a.average_response_time_ms for a in recent_app])
            
            # Generate recommendations
            recommendations = self._generate_recommendations(avg_cpu, avg_memory, avg_response_time)
            
            return {
                'summary_period': 'last_hour',
                'averages': {
                    'cpu_percent': avg_cpu,
                    'memory_percent': avg_memory,
                    'response_time_ms': avg_response_time
                },
                'trends': {
                    'cpu_trend': cpu_trend,
                    'memory_trend': memory_trend,
                    'response_trend': response_trend
                },
                'recommendations': recommendations,
                'data_points': {
                    'system_samples': len(recent_system),
                    'application_samples': len(recent_app),
                    'metric_samples': len(recent_metrics)
                }
            }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        change_percent = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
        
        if change_percent > 10:
            return 'increasing'
        elif change_percent < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_recommendations(self, avg_cpu: float, avg_memory: float, avg_response_time: float) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        if avg_cpu > 80:
            recommendations.append("High CPU usage detected. Consider optimizing CPU-intensive operations or scaling horizontally.")
        
        if avg_memory > 80:
            recommendations.append("High memory usage detected. Consider implementing memory optimization strategies or increasing available memory.")
        
        if avg_response_time > 1000:
            recommendations.append("High response times detected. Consider implementing caching, database optimization, or async processing.")
        
        if avg_cpu < 20 and avg_memory < 30:
            recommendations.append("System resources are underutilized. Consider increasing workload or reducing resource allocation.")
        
        if not recommendations:
            recommendations.append("System performance is within acceptable ranges. Continue monitoring for trends.")
        
        return recommendations
    
    def generate_monitoring_report(self) -> str:
        """Generate comprehensive monitoring report."""
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE MONITORING SYSTEM REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        current_metrics = self.get_current_metrics()
        performance_summary = self.get_performance_summary()
        
        # Current status
        report.append("CURRENT STATUS:")
        system_usage = current_metrics['system_usage']
        report.append(f"  CPU Usage: {system_usage['cpu_percent']:.1f}%")
        report.append(f"  Memory Usage: {system_usage['memory_percent']:.1f}%")
        report.append(f"  Memory Used: {system_usage['memory_used_mb']:.1f}MB")
        report.append(f"  Disk Usage: {system_usage['disk_usage_percent']:.1f}%")
        report.append(f"  Disk Free: {system_usage['disk_free_gb']:.1f}GB")
        report.append(f"  Load Average: {system_usage['load_average'][0]:.2f}")
        report.append("")
        
        # Application metrics
        app_metrics = current_metrics['application_metrics']
        report.append("APPLICATION METRICS:")
        report.append(f"  Active Operations: {app_metrics['active_operations']}")
        report.append(f"  Completed Operations: {app_metrics['completed_operations']}")
        report.append(f"  Failed Operations: {app_metrics['failed_operations']}")
        report.append(f"  Average Response Time: {app_metrics['average_response_time_ms']:.2f}ms")
        report.append(f"  Throughput: {app_metrics['throughput_ops_per_second']:.2f} ops/sec")
        report.append(f"  Cache Hit Rate: {app_metrics['cache_hit_rate']:.1f}%")
        report.append(f"  Error Rate: {app_metrics['error_rate']:.1f}%")
        report.append("")
        
        # Performance summary
        report.append("PERFORMANCE SUMMARY (Last Hour):")
        averages = performance_summary['averages']
        report.append(f"  Average CPU: {averages['cpu_percent']:.1f}%")
        report.append(f"  Average Memory: {averages['memory_percent']:.1f}%")
        report.append(f"  Average Response Time: {averages['response_time_ms']:.2f}ms")
        report.append("")
        
        # Trends
        report.append("TRENDS:")
        trends = performance_summary['trends']
        report.append(f"  CPU Trend: {trends['cpu_trend']}")
        report.append(f"  Memory Trend: {trends['memory_trend']}")
        report.append(f"  Response Time Trend: {trends['response_trend']}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        for i, rec in enumerate(performance_summary['recommendations'], 1):
            report.append(f"  {i}. {rec}")
        report.append("")
        
        # System information
        report.append("SYSTEM INFORMATION:")
        report.append(f"  Monitoring Uptime: {current_metrics['monitoring_uptime_hours']:.1f} hours")
        report.append(f"  Total Metrics Stored: {current_metrics['total_metrics_stored']}")
        report.append(f"  Active Alerts: {current_metrics['active_alerts_count']}")
        report.append(f"  Monitoring Interval: {self.monitoring_interval}s")
        report.append("")
        
        return "\n".join(report)
    
    def __del__(self):
        """Cleanup on destruction."""
        self.stop_monitoring()


def main():
    """Main function for testing the performance monitoring system."""
    monitor = PerformanceMonitoringSystem(
        monitoring_interval=2.0,
        enable_alerts=True
    )
    
    print("Testing Performance Monitoring System...")
    
    # Test custom metrics
    print("\nRecording custom metrics...")
    monitor.record_metric('custom_gauge', 42.5, tags={'component': 'test'})
    monitor.record_timing('custom_timer', 150.0, tags={'operation': 'test_op'})
    monitor.increment_counter('custom_counter', 1.0, tags={'event': 'test_event'})
    monitor.set_gauge('custom_gauge_2', 100.0, tags={'status': 'active'})
    
    # Wait for monitoring to collect data
    print("Waiting for monitoring data collection...")
    time.sleep(10)
    
    # Get current metrics
    print("\nCurrent metrics:")
    current = monitor.get_current_metrics()
    print(f"  CPU: {current['system_usage']['cpu_percent']:.1f}%")
    print(f"  Memory: {current['system_usage']['memory_percent']:.1f}%")
    print(f"  Active Alerts: {current['active_alerts_count']}")
    
    # Get performance summary
    print("\nPerformance summary:")
    summary = monitor.get_performance_summary()
    print(f"  Average CPU: {summary['averages']['cpu_percent']:.1f}%")
    print(f"  CPU Trend: {summary['trends']['cpu_trend']}")
    print(f"  Recommendations: {len(summary['recommendations'])}")
    
    # Generate report
    print("\n" + monitor.generate_monitoring_report())
    
    # Stop monitoring
    monitor.stop_monitoring()


if __name__ == "__main__":
    main()

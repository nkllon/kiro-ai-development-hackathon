#!/usr/bin/env python3
"""
Prometheus Metrics Exporter
===========================

Integrates existing Beast Mode monitoring infrastructure with Prometheus
for real-time metrics visibility and alerting. Exposes metrics via HTTP
endpoint for Prometheus scraping.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Prometheus integration for real-time monitoring visibility
"""

import sys
import os
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path

# Prometheus client library
try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Summary,
        Info,
        Enum as PromEnum,
        start_http_server,
        generate_latest,
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        REGISTRY,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

    # Create dummy classes for when Prometheus is not available
    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def dec(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Summary:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self


# Import existing monitoring systems
try:
    from src.beast_mode.performance.performance_monitoring_system import (
        PerformanceMonitoringSystem,
    )
except ImportError:
    # Fallback if performance monitoring system not available
    PerformanceMonitoringSystem = None


class PrometheusExporter:
    """
    Prometheus metrics exporter for Beast Mode framework.
    
    DEPRECATED: This class now serves as a backward compatibility wrapper
    around the new daemon-based monitoring system. New code should use
    MonitoringClient directly.

    Integrates with existing monitoring infrastructure to expose metrics
    via Prometheus format for real-time visibility and alerting.
    
    Implements singleton pattern to prevent duplicate metric registration.
    """
    
    _instance = None
    _initialized = False
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to prevent duplicate instances."""
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(PrometheusExporter, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        port: int = 8000,
        monitoring_interval: float = 5.0,
        enable_http_server: bool = True,
    ):
        """Initialize Prometheus exporter (singleton)."""
        # Thread-safe initialization check
        with self._instance_lock:
            # Prevent re-initialization
            if self._initialized:
                return
                
            self.port = port
            self.monitoring_interval = monitoring_interval
            self.enable_http_server = enable_http_server

            self.logger = self._setup_logging()
            
            # Initialize thread safety attributes
            self.export_thread = None
            self.export_active = False
            self.performance_monitor = None
            
            # Import the new monitoring client
            # Check if daemon mode is explicitly disabled
            disable_daemon = os.environ.get('BEAST_MODE_DISABLE_DAEMON', '0') == '1'

            if disable_daemon:
                self.logger.info("Daemon mode explicitly disabled via BEAST_MODE_DISABLE_DAEMON")
                self._use_daemon = False
            else:
                try:
                    from .client import MonitoringClient
                    # Try to check if daemon is actually running before committing to daemon mode
                    try:
                        import socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex(('localhost', port))
                        sock.close()
                        daemon_running = (result == 0)
                    except:
                        daemon_running = False

                    if not daemon_running:
                        self.logger.warning(f"Monitoring daemon not running on port {port}, falling back to legacy mode")
                        self._use_daemon = False
                    else:
                        self.monitoring_client = MonitoringClient(
                            client_id="prometheus_exporter_legacy",
                            daemon_port=port,
                            fallback_mode=True
                        )
                        self.logger.info("Using new daemon-based monitoring system")
                        self._use_daemon = True
                except ImportError:
                    self.logger.warning("New monitoring client not available, falling back to legacy mode")
                    self._use_daemon = False
                except Exception as e:
                    self.logger.warning(f"Failed to connect to monitoring daemon: {e}, falling back to legacy mode")
                    self._use_daemon = False

            if not PROMETHEUS_AVAILABLE and not self._use_daemon:
                self.logger.warning(
                    "Prometheus client not available. Install with: pip install prometheus-client"
                )
                self._initialized = True
                return

            # Initialize monitoring system
            if self._use_daemon:
                self._initialize_daemon_metrics()
                # When using daemon mode, we don't start our own HTTP server
                # The daemon handles the HTTP endpoint
                self.logger.info(f"Using daemon HTTP server, not starting local server")
            else:
                # Legacy initialization
                try:
                    self._initialize_prometheus_metrics()
                except Exception as e:
                    self.logger.error(f"Failed to initialize Prometheus metrics: {e}")
                    self._initialized = True
                    return

                # Connect to existing monitoring systems
                self.performance_monitor = PerformanceMonitoringSystem(
                    monitoring_interval=monitoring_interval, enable_alerts=True
                )

                # HTTP server for metrics endpoint (only in legacy mode)
                self.http_server = None

                # Start HTTP server and metrics export (only once, only in legacy mode)
                if self.enable_http_server:
                    self.start_http_server()

                self.start_metrics_export()
            
            # Mark as initialized
            self._initialized = True

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Prometheus exporter."""
        logger = logging.getLogger("prometheus_exporter")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        # Clear existing metrics to prevent duplicates
        try:
            # Create a new registry to avoid conflicts
            self.registry = CollectorRegistry()
        except Exception:
            # Use default registry if custom registry fails
            self.registry = REGISTRY

        # System metrics
        self.system_cpu_percent = Gauge(
            "beast_mode_system_cpu_percent", "System CPU usage percentage", ["host"], registry=self.registry
        )

        self.system_memory_percent = Gauge(
            "beast_mode_system_memory_percent",
            "System memory usage percentage",
            ["host"],
            registry=self.registry
        )

        self.system_memory_used_bytes = Gauge(
            "beast_mode_system_memory_used_bytes",
            "System memory used in bytes",
            ["host"],
            registry=self.registry
        )

        self.system_disk_usage_percent = Gauge(
            "beast_mode_system_disk_usage_percent",
            "System disk usage percentage",
            ["host", "mountpoint"],
            registry=self.registry
        )

        self.system_load_average = Gauge(
            "beast_mode_system_load_average",
            "System load average",
            ["host", "period"],  # period: 1m, 5m, 15m
            registry=self.registry
        )

        # Application metrics
        self.app_operations_total = Counter(
            "beast_mode_app_operations_total",
            "Total number of operations",
            ["operation_type", "status"],  # status: completed, failed
            registry=self.registry
        )

        self.app_operation_duration_seconds = Histogram(
            "beast_mode_app_operation_duration_seconds",
            "Operation duration in seconds",
            ["operation_type"],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0),
            registry=self.registry
        )

        self.app_throughput_ops_per_second = Gauge(
            "beast_mode_app_throughput_ops_per_second",
            "Application throughput in operations per second",
            ["operation_type"],
            registry=self.registry
        )

        self.app_error_rate = Gauge(
            "beast_mode_app_error_rate",
            "Application error rate percentage",
            ["component"],
            registry=self.registry
        )

        self.app_cache_hit_rate = Gauge(
            "beast_mode_app_cache_hit_rate", "Cache hit rate percentage", ["cache_name"],
            registry=self.registry
        )

        self.app_active_operations = Gauge(
            "beast_mode_app_active_operations",
            "Number of active operations",
            ["operation_type"],
            registry=self.registry
        )

        self.app_queue_size = Gauge(
            "beast_mode_app_queue_size", "Queue size", ["queue_name"],
            registry=self.registry
        )

        # Module-specific metrics
        self.module_health_score = Gauge(
            "beast_mode_module_health_score",
            "Module health score (0-100)",
            ["module_id", "class_name"],
            registry=self.registry
        )

        self.module_status = Gauge(
            "beast_mode_module_status",
            "Module status (1=healthy, 0=unhealthy)",
            ["module_id", "class_name", "status"],
            registry=self.registry
        )

        self.module_error_count = Counter(
            "beast_mode_module_errors_total",
            "Total number of module errors",
            ["module_id", "class_name"],
            registry=self.registry
        )

        self.module_warning_count = Counter(
            "beast_mode_module_warnings_total",
            "Total number of module warnings",
            ["module_id", "class_name"],
            registry=self.registry
        )

        self.module_uptime_seconds = Gauge(
            "beast_mode_module_uptime_seconds",
            "Module uptime in seconds",
            ["module_id", "class_name"],
            registry=self.registry
        )

        self.module_last_activity = Gauge(
            "beast_mode_module_last_activity_timestamp",
            "Module last activity timestamp",
            ["module_id", "class_name"],
            registry=self.registry
        )

        self.module_capabilities_count = Gauge(
            "beast_mode_module_capabilities_count",
            "Number of module capabilities",
            ["module_id", "class_name"],
            registry=self.registry
        )

        self.module_version_info = Info(
            "beast_mode_module_version",
            "Module version information",
            ["module_id", "class_name"],
            registry=self.registry
        )

        # Health metrics
        self.component_health_status = Gauge(
            "beast_mode_component_health_status",
            "Component health status (1=healthy, 0=unhealthy)",
            ["component_name", "component_type"],
            registry=self.registry
        )

        self.component_health_score = Gauge(
            "beast_mode_component_health_score",
            "Component health score (0-100)",
            ["component_name", "component_type"],
            registry=self.registry
        )

        self.alert_count = Counter(
            "beast_mode_alerts_total",
            "Total number of alerts",
            ["alert_level", "alert_type"],
            registry=self.registry
        )

        # Performance optimization metrics
        self.optimization_improvement_factor = Gauge(
            "beast_mode_optimization_improvement_factor",
            "Performance improvement factor from optimization",
            ["optimization_strategy"],
            registry=self.registry
        )

        self.cache_operations_total = Counter(
            "beast_mode_cache_operations_total",
            "Total cache operations",
            ["cache_name", "operation"],  # operation: hit, miss, eviction
            registry=self.registry
        )

        self.cache_size_bytes = Gauge(
            "beast_mode_cache_size_bytes", "Cache size in bytes", ["cache_name"],
            registry=self.registry
        )

        # Framework info
        self.framework_info = Info(
            "beast_mode_framework_info", "Beast Mode framework information",
            registry=self.registry
        )

        # Set framework info
        self.framework_info.info(
            {
                "version": "2.0.0",
                "phase": "Phase 4 - Performance Optimization",
                "monitoring_enabled": "true",
                "prometheus_integration": "true",
            }
        )

        self.logger.info("Prometheus metrics initialized")

    def _initialize_daemon_metrics(self):
        """Initialize metrics using the new daemon-based system."""
        if not self._use_daemon:
            return

        try:
            # Register all the metrics that were previously created directly
            # System metrics
            self.monitoring_client.register_gauge(
                "beast_mode_system_cpu_percent", 
                "System CPU usage percentage", 
                ["host"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_system_memory_percent",
                "System memory usage percentage",
                ["host"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_system_memory_used_bytes",
                "System memory used in bytes",
                ["host"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_system_disk_usage_percent",
                "System disk usage percentage",
                ["host", "mountpoint"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_system_load_average",
                "System load average",
                ["host", "period"]
            )

            # Application metrics
            self.monitoring_client.register_counter(
                "beast_mode_app_operations_total",
                "Total number of operations",
                ["operation_type", "status"]
            )
            self.monitoring_client.register_histogram(
                "beast_mode_app_operation_duration_seconds",
                "Operation duration in seconds",
                ["operation_type"],
                [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_app_throughput_ops_per_second",
                "Application throughput in operations per second",
                ["operation_type"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_app_error_rate",
                "Application error rate percentage",
                ["component"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_app_cache_hit_rate", 
                "Cache hit rate percentage", 
                ["cache_name"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_app_active_operations",
                "Number of active operations",
                ["operation_type"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_app_queue_size", 
                "Queue size", 
                ["queue_name"]
            )

            # Module-specific metrics
            self.monitoring_client.register_gauge(
                "beast_mode_module_health_score",
                "Module health score (0-100)",
                ["module_id", "class_name"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_module_status",
                "Module status (1=healthy, 0=unhealthy)",
                ["module_id", "class_name", "status"]
            )
            self.monitoring_client.register_counter(
                "beast_mode_module_errors_total",
                "Total number of module errors",
                ["module_id", "class_name"]
            )
            self.monitoring_client.register_counter(
                "beast_mode_module_warnings_total",
                "Total number of module warnings",
                ["module_id", "class_name"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_module_uptime_seconds",
                "Module uptime in seconds",
                ["module_id", "class_name"]
            )

            # Health metrics
            self.monitoring_client.register_gauge(
                "beast_mode_component_health_status",
                "Component health status (1=healthy, 0=unhealthy)",
                ["component_name", "component_type"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_component_health_score",
                "Component health score (0-100)",
                ["component_name", "component_type"]
            )
            self.monitoring_client.register_counter(
                "beast_mode_alerts_total",
                "Total number of alerts",
                ["alert_level", "alert_type"]
            )

            # Performance optimization metrics
            self.monitoring_client.register_gauge(
                "beast_mode_optimization_improvement_factor",
                "Performance improvement factor from optimization",
                ["optimization_strategy"]
            )
            self.monitoring_client.register_counter(
                "beast_mode_cache_operations_total",
                "Total cache operations",
                ["cache_name", "operation"]
            )
            self.monitoring_client.register_gauge(
                "beast_mode_cache_size_bytes", 
                "Cache size in bytes", 
                ["cache_name"]
            )

            self.logger.info("Daemon-based metrics initialized")
            
            # Connect to existing monitoring systems for data collection
            # DISABLED: This creates recursive monitoring loops
            # self.performance_monitor = PerformanceMonitoringSystem(
            #     monitoring_interval=self.monitoring_interval, enable_alerts=True
            # )
            self.performance_monitor = None

            # Start metrics export thread for daemon-based system
            self.export_thread = None
            self.export_active = False
            self.start_metrics_export()

        except Exception as e:
            self.logger.error(f"Failed to initialize daemon-based metrics: {e}")
            # Fall back to legacy mode
            self._use_daemon = False
            self._initialize_prometheus_metrics()

    def start_http_server(self):
        """Start HTTP server for metrics endpoint."""
        if not PROMETHEUS_AVAILABLE or not self.enable_http_server:
            return

        try:
            start_http_server(self.port, registry=self.registry)
            self.logger.info(f"Prometheus metrics server started on port {self.port}")
            self.logger.info(
                f"Metrics available at: http://localhost:{self.port}/metrics"
            )
        except Exception as e:
            self.logger.error(f"Failed to start Prometheus HTTP server: {e}")

    def start_metrics_export(self):
        """Start metrics export thread."""
        if not self.export_active:
            self.export_active = True
            self.export_thread = threading.Thread(
                target=self._export_metrics_loop, daemon=True
            )
            self.export_thread.start()
            self.logger.info("Metrics export started")

    def stop_metrics_export(self):
        """Stop metrics export thread."""
        self.export_active = False
        if hasattr(self, "export_thread") and self.export_thread and self.export_thread.is_alive():
            self.export_thread.join(timeout=5)
            if self.export_thread.is_alive():
                self.logger.warning("Export thread did not stop gracefully")
        self.logger.info("Metrics export stopped")

    def shutdown(self):
        """Shutdown the exporter and clean up resources."""
        with self._instance_lock:
            if not self._initialized:
                return
                
            self.logger.info("Shutting down Prometheus exporter")
            
            # Stop metrics export
            self.stop_metrics_export()
            
            # Shutdown monitoring client if using daemon
            if self._use_daemon and hasattr(self, 'monitoring_client'):
                self.monitoring_client.shutdown()
            
            # Reset singleton state for testing
            PrometheusExporter._instance = None
            PrometheusExporter._initialized = False
            
            self.logger.info("Prometheus exporter shutdown complete")

    @classmethod
    def reset_singleton(cls):
        """Reset singleton state for testing purposes."""
        with cls._instance_lock:
            if cls._instance and hasattr(cls._instance, 'export_active'):
                cls._instance.export_active = False
                if hasattr(cls._instance, 'export_thread') and cls._instance.export_thread:
                    cls._instance.export_thread.join(timeout=2)
            cls._instance = None
            cls._initialized = False

    def _export_metrics_loop(self):
        """Main metrics export loop."""
        while self.export_active:
            try:
                self._export_system_metrics()
                self._export_application_metrics()
                self._export_health_metrics()
                self._export_performance_metrics()

                time.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Metrics export error: {e}")

    def _export_system_metrics(self):
        """Export system metrics to Prometheus."""
        if not PROMETHEUS_AVAILABLE and not self._use_daemon:
            return

        try:
            import psutil
            import socket
            import platform

            hostname = socket.gethostname()
            system = platform.system().lower()

            # Skip system metrics on macOS if restricted
            if (
                system == "darwin"
                and os.getenv("BEAST_MODE_RESTRICTED_MODE", "false").lower() == "true"
            ):
                self.logger.debug(
                    "Skipping system metrics collection on restricted macOS"
                )
                return

            # CPU metrics
            try:
                cpu_percent = psutil.cpu_percent(
                    interval=0.1
                )  # Reduced interval for macOS
                
                if self._use_daemon:
                    self.monitoring_client.set_gauge(
                        "beast_mode_system_cpu_percent", 
                        cpu_percent, 
                        {"host": hostname}
                    )
                else:
                    self.system_cpu_percent.labels(host=hostname).set(cpu_percent)
            except (PermissionError, OSError) as e:
                self.logger.debug(f"CPU metrics collection failed on macOS: {e}")

            # Memory metrics
            try:
                memory = psutil.virtual_memory()
                
                if self._use_daemon:
                    self.monitoring_client.set_gauge(
                        "beast_mode_system_memory_percent", 
                        memory.percent, 
                        {"host": hostname}
                    )
                    self.monitoring_client.set_gauge(
                        "beast_mode_system_memory_used_bytes", 
                        memory.used, 
                        {"host": hostname}
                    )
                else:
                    self.system_memory_percent.labels(host=hostname).set(memory.percent)
                    self.system_memory_used_bytes.labels(host=hostname).set(memory.used)
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Memory metrics collection failed on macOS: {e}")

            # Disk metrics
            disk = psutil.disk_usage("/")
            if self._use_daemon:
                self.monitoring_client.set_gauge(
                    "beast_mode_system_disk_usage_percent", 
                    disk.percent, 
                    {"host": hostname, "mountpoint": "/"}
                )
            else:
                self.system_disk_usage_percent.labels(host=hostname, mountpoint="/").set(
                    disk.percent
                )

            # Load average
            load_avg = psutil.getloadavg()
            if self._use_daemon:
                self.monitoring_client.set_gauge(
                    "beast_mode_system_load_average", 
                    load_avg[0], 
                    {"host": hostname, "period": "1m"}
                )
                self.monitoring_client.set_gauge(
                    "beast_mode_system_load_average", 
                    load_avg[1], 
                    {"host": hostname, "period": "5m"}
                )
                self.monitoring_client.set_gauge(
                    "beast_mode_system_load_average", 
                    load_avg[2], 
                    {"host": hostname, "period": "15m"}
                )
            else:
                self.system_load_average.labels(host=hostname, period="1m").set(load_avg[0])
                self.system_load_average.labels(host=hostname, period="5m").set(load_avg[1])
                self.system_load_average.labels(host=hostname, period="15m").set(
                    load_avg[2]
                )

        except Exception as e:
            self.logger.error(f"Failed to export system metrics: {e}")

    def _export_application_metrics(self):
        """Export application metrics to Prometheus."""
        if not PROMETHEUS_AVAILABLE or not self.performance_monitor:
            return

        try:
            # Get current metrics from performance monitor
            current_metrics = self.performance_monitor.get_current_metrics()

            app_metrics = current_metrics.get("application_metrics", {})

            # Operation metrics
            completed_ops = app_metrics.get("completed_operations", 0)
            failed_ops = app_metrics.get("failed_operations", 0)

            self.app_operations_total.labels(
                operation_type="general", status="completed"
            )._value._value = completed_ops

            self.app_operations_total.labels(
                operation_type="general", status="failed"
            )._value._value = failed_ops

            # Performance metrics
            response_time = (
                app_metrics.get("average_response_time_ms", 0) / 1000
            )  # Convert to seconds
            self.app_operation_duration_seconds.labels(
                operation_type="general"
            ).observe(response_time)

            throughput = app_metrics.get("throughput_ops_per_second", 0)
            self.app_throughput_ops_per_second.labels(operation_type="general").set(
                throughput
            )

            error_rate = app_metrics.get("error_rate", 0)
            self.app_error_rate.labels(component="general").set(error_rate)

            cache_hit_rate = app_metrics.get("cache_hit_rate", 0)
            self.app_cache_hit_rate.labels(cache_name="general").set(cache_hit_rate)

            active_ops = app_metrics.get("active_operations", 0)
            self.app_active_operations.labels(operation_type="general").set(active_ops)

            queue_size = app_metrics.get("queue_size", 0)
            self.app_queue_size.labels(queue_name="general").set(queue_size)

        except Exception as e:
            self.logger.error(f"Failed to export application metrics: {e}")

    def _export_health_metrics(self):
        """Export health metrics to Prometheus."""
        if not PROMETHEUS_AVAILABLE or not self.performance_monitor:
            return

        try:
            # Get current metrics for health information
            current_metrics = self.performance_monitor.get_current_metrics()

            # Export basic health status based on performance metrics
            system_usage = current_metrics.get("system_usage", {})
            cpu_percent = system_usage.get("cpu_percent", 0)
            memory_percent = system_usage.get("memory_percent", 0)

            # Simple health status based on resource usage
            cpu_healthy = cpu_percent < 80
            memory_healthy = memory_percent < 80

            self.component_health_status.labels(
                component_name="system_cpu", component_type="system"
            ).set(1 if cpu_healthy else 0)

            self.component_health_status.labels(
                component_name="system_memory", component_type="system"
            ).set(1 if memory_healthy else 0)

            self.component_health_score.labels(
                component_name="system_cpu", component_type="system"
            ).set(100 - cpu_percent)

            self.component_health_score.labels(
                component_name="system_memory", component_type="system"
            ).set(100 - memory_percent)

            # Export alerts from performance monitor
            active_alerts = current_metrics.get("active_alerts_count", 0)
            if active_alerts > 0:
                self.alert_count.labels(
                    alert_level="warning", alert_type="performance"
                ).inc()

        except Exception as e:
            self.logger.error(f"Failed to export health metrics: {e}")

    def _export_performance_metrics(self):
        """Export performance optimization metrics to Prometheus."""
        if not PROMETHEUS_AVAILABLE or not self.performance_monitor:
            return

        try:
            # Get performance summary
            performance_summary = self.performance_monitor.get_performance_summary()

            # Export optimization improvements (placeholder - would come from optimizer)
            optimization_strategies = [
                "caching",
                "concurrent_processing",
                "memory_optimization",
            ]
            for strategy in optimization_strategies:
                # This would be populated by actual optimization results
                improvement_factor = 1.0  # Placeholder
                self.optimization_improvement_factor.labels(
                    optimization_strategy=strategy
                ).set(improvement_factor)

            # Export cache metrics (placeholder - would come from cache systems)
            cache_names = ["domain_cache", "performance_cache"]
            for cache_name in cache_names:
                # These would be populated by actual cache statistics
                cache_hits = 0  # Placeholder
                cache_misses = 0  # Placeholder
                cache_evictions = 0  # Placeholder
                cache_size = 0  # Placeholder

                self.cache_operations_total.labels(
                    cache_name=cache_name, operation="hit"
                )._value._value = cache_hits

                self.cache_operations_total.labels(
                    cache_name=cache_name, operation="miss"
                )._value._value = cache_misses

                self.cache_operations_total.labels(
                    cache_name=cache_name, operation="eviction"
                )._value._value = cache_evictions

                self.cache_size_bytes.labels(cache_name=cache_name).set(cache_size)

        except Exception as e:
            self.logger.error(f"Failed to export performance metrics: {e}")

    def record_module_health(
        self,
        module_id: str,
        status: str,
        health_score: float,
        error_count: int,
        warning_count: int,
        uptime_seconds: float,
    ):
        """Record module health metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        try:
            class_name = module_id.split("_")[0] if "_" in module_id else module_id

            # Record health score
            self.module_health_score.labels(
                module_id=module_id, class_name=class_name
            ).set(health_score)

            # Record status (1=healthy, 0=unhealthy)
            status_value = 1 if status == "healthy" else 0
            self.module_status.labels(
                module_id=module_id, class_name=class_name, status=status
            ).set(status_value)

            # Record error count
            self.module_error_count.labels(
                module_id=module_id, class_name=class_name
            )._value._value = error_count

            # Record warning count
            self.module_warning_count.labels(
                module_id=module_id, class_name=class_name
            )._value._value = warning_count

            # Record uptime
            self.module_uptime_seconds.labels(
                module_id=module_id, class_name=class_name
            ).set(uptime_seconds)

        except Exception as e:
            self.logger.error(f"Failed to record module health metrics: {e}")

    def record_module_performance(
        self,
        module_id: str,
        class_name: str,
        version: str,
        capabilities: List[str],
        last_activity: datetime,
    ):
        """Record module performance metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        try:
            # Record last activity timestamp
            self.module_last_activity.labels(
                module_id=module_id, class_name=class_name
            ).set(last_activity.timestamp())

            # Record capabilities count
            self.module_capabilities_count.labels(
                module_id=module_id, class_name=class_name
            ).set(len(capabilities))

            # Record version info
            self.module_version_info.labels(
                module_id=module_id, class_name=class_name
            ).info({"version": version, "capabilities": ",".join(capabilities)})

        except Exception as e:
            self.logger.error(f"Failed to record module performance metrics: {e}")

    def get_module_metrics(self, module_id: str) -> Dict[str, Any]:
        """Get metrics for a specific module."""
        if not PROMETHEUS_AVAILABLE:
            return {}

        try:
            class_name = module_id.split("_")[0] if "_" in module_id else module_id

            return {
                "module_id": module_id,
                "class_name": class_name,
                "health_score": self.module_health_score.labels(
                    module_id=module_id, class_name=class_name
                )._value._value,
                "error_count": self.module_error_count.labels(
                    module_id=module_id, class_name=class_name
                )._value._value,
                "warning_count": self.module_warning_count.labels(
                    module_id=module_id, class_name=class_name
                )._value._value,
                "uptime_seconds": self.module_uptime_seconds.labels(
                    module_id=module_id, class_name=class_name
                )._value._value,
                "capabilities_count": self.module_capabilities_count.labels(
                    module_id=module_id, class_name=class_name
                )._value._value,
            }
        except Exception as e:
            self.logger.error(f"Failed to get module metrics: {e}")
            return {}

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for monitoring."""
        return {
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "http_server_running": self.http_server is not None,
            "metrics_port": self.port,
            "export_active": self.export_active,
            "monitoring_interval": self.monitoring_interval,
            "metrics_endpoint": (
                f"http://localhost:{self.port}/metrics"
                if PROMETHEUS_AVAILABLE
                else None
            ),
        }

    def generate_prometheus_report(self) -> str:
        """Generate Prometheus integration report."""
        report = []
        report.append("=" * 80)
        report.append("PROMETHEUS METRICS EXPORTER REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        summary = self.get_metrics_summary()

        report.append("PROMETHEUS INTEGRATION STATUS:")
        report.append(
            f"  Prometheus Client Available: {'Yes' if summary['prometheus_available'] else 'No'}"
        )
        report.append(
            f"  HTTP Server Running: {'Yes' if summary['http_server_running'] else 'No'}"
        )
        report.append(f"  Metrics Port: {summary['metrics_port']}")
        report.append(f"  Export Active: {'Yes' if summary['export_active'] else 'No'}")
        report.append(f"  Monitoring Interval: {summary['monitoring_interval']}s")
        report.append("")

        if summary["metrics_endpoint"]:
            report.append("METRICS ENDPOINT:")
            report.append(f"  URL: {summary['metrics_endpoint']}")
            report.append("  Format: Prometheus exposition format")
            report.append("  Scraping: Configure Prometheus to scrape this endpoint")
            report.append("")

        report.append("EXPORTED METRICS:")
        report.append("  System Metrics:")
        report.append("    - beast_mode_system_cpu_percent")
        report.append("    - beast_mode_system_memory_percent")
        report.append("    - beast_mode_system_memory_used_bytes")
        report.append("    - beast_mode_system_disk_usage_percent")
        report.append("    - beast_mode_system_load_average")
        report.append("")
        report.append("  Application Metrics:")
        report.append("    - beast_mode_app_operations_total")
        report.append("    - beast_mode_app_operation_duration_seconds")
        report.append("    - beast_mode_app_throughput_ops_per_second")
        report.append("    - beast_mode_app_error_rate")
        report.append("    - beast_mode_app_cache_hit_rate")
        report.append("    - beast_mode_app_active_operations")
        report.append("    - beast_mode_app_queue_size")
        report.append("")
        report.append("  Health Metrics:")
        report.append("    - beast_mode_component_health_status")
        report.append("    - beast_mode_component_health_score")
        report.append("    - beast_mode_alerts_total")
        report.append("")
        report.append("  Performance Metrics:")
        report.append("    - beast_mode_optimization_improvement_factor")
        report.append("    - beast_mode_cache_operations_total")
        report.append("    - beast_mode_cache_size_bytes")
        report.append("    - beast_mode_framework_info")
        report.append("")

        if not summary["prometheus_available"]:
            report.append("INSTALLATION INSTRUCTIONS:")
            report.append("  Install Prometheus client library:")
            report.append("    pip install prometheus-client")
            report.append("")
            report.append(
                "  Then restart the exporter to enable Prometheus integration."
            )
            report.append("")

        return "\n".join(report)

    def __del__(self):
        """Cleanup on destruction."""
        self.stop_metrics_export()


def main() -> None:
    """Main function for testing Prometheus exporter."""
    print("Testing Prometheus Metrics Exporter...")

    # Initialize exporter
    exporter = PrometheusExporter(port=8000, monitoring_interval=2.0)

    # Wait for metrics to be collected and exported
    print("Collecting and exporting metrics...")
    time.sleep(10)

    # Generate report
    print("\n" + exporter.generate_prometheus_report())

    if PROMETHEUS_AVAILABLE:
        print(f"\n✅ Prometheus metrics available at: http://localhost:8000/metrics")
        print(
            "   Configure Prometheus to scrape this endpoint for real-time monitoring"
        )
    else:
        print(f"\n⚠️  Install prometheus-client to enable Prometheus integration:")
        print("   pip install prometheus-client")


if __name__ == "__main__":
    main()

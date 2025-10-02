"""
Health Monitoring Coordinator for Node B Management

Provides comprehensive health monitoring and diagnostics for Node B instances
including Redis connectivity monitoring, performance metrics collection,
and diagnostic reporting with Beast Mode framework integration.
"""

import os
import asyncio
import psutil
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from ..core.node_b_component import NodeBComponent
from ..core.interfaces import IHealthMonitoring, HealthMetrics


@dataclass
class PerformanceSnapshot:
    """Performance metrics snapshot"""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    disk_io_read: int
    disk_io_write: int
    process_count: int


@dataclass
class AlertThresholds:
    """Alert thresholds for health monitoring"""
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0
    memory_warning: float = 70.0
    memory_critical: float = 90.0
    response_time_warning: float = 1000.0  # milliseconds
    response_time_critical: float = 5000.0  # milliseconds
    error_rate_warning: float = 5.0  # errors per minute
    error_rate_critical: float = 20.0  # errors per minute


class HealthMonitoringCoordinator(NodeBComponent, IHealthMonitoring):
    """
    Health Monitoring Coordinator for Node B instances
    
    Provides comprehensive health monitoring capabilities including:
    - Standard health endpoints (/health, /ready, /metrics)
    - Redis connectivity monitoring
    - Message processing rate tracking
    - Performance metrics collection (CPU, memory, network)
    - Alert generation for performance degradation
    
    Requirements: 3.1, 3.2, 3.3, 3.6, 6.3
    """

    def __init__(self, node_id: str = None):
        """
        Initialize Health Monitoring Coordinator
        
        Args:
            node_id: Optional Node B instance ID to monitor
        """
        super().__init__("health_monitoring", node_id)
        
        # Health monitoring state
        self._monitored_nodes: Dict[str, Dict[str, Any]] = {}
        self._performance_history: Dict[str, List[PerformanceSnapshot]] = {}
        self._alert_thresholds = AlertThresholds()
        self._monitoring_interval = 30.0  # seconds
        self._history_retention_hours = 24
        
        # Message processing tracking
        self._message_processing_stats: Dict[str, Dict[str, Any]] = {}
        
        # Health check state
        self._last_health_check: Dict[str, datetime] = {}
        self._health_check_failures: Dict[str, int] = {}
        
        # Performance monitoring
        self._performance_monitor_task = None
        self._monitoring_active = False
        
        self._logger.info(f"HealthMonitoringCoordinator initialized for monitoring")

    async def start_monitoring(self, node_ids: List[str] = None):
        """
        Start health monitoring for specified nodes
        
        Args:
            node_ids: List of node IDs to monitor, defaults to self.node_id
        """
        if node_ids is None:
            node_ids = [self.node_id] if self.node_id else []
        
        # Initialize monitoring state for each node
        for node_id in node_ids:
            self._monitored_nodes[node_id] = {
                'status': 'monitoring',
                'started_at': datetime.now().isoformat(),
                'last_check': None,
                'consecutive_failures': 0
            }
            self._performance_history[node_id] = []
            self._message_processing_stats[node_id] = {
                'messages_processed': 0,
                'messages_sent': 0,
                'processing_rate': 0.0,
                'last_activity': None,
                'error_count': 0
            }
        
        # Start performance monitoring task
        if not self._monitoring_active:
            self._monitoring_active = True
            self._performance_monitor_task = asyncio.create_task(self._performance_monitor_loop())
            self._logger.info(f"Started health monitoring for nodes: {node_ids}")

    async def stop_monitoring(self):
        """Stop health monitoring and cleanup resources"""
        self._monitoring_active = False
        
        if self._performance_monitor_task:
            self._performance_monitor_task.cancel()
            try:
                await self._performance_monitor_task
            except asyncio.CancelledError:
                pass
        
        self._logger.info("Health monitoring stopped")

    async def get_health_status(self, node_id: str) -> HealthMetrics:
        """
        Get comprehensive health metrics for a node
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            HealthMetrics: Complete health status and metrics
            
        Requirements: 3.1, 3.2, 3.3, 3.6
        """
        try:
            self.increment_health_checks()
            
            # Check Redis connectivity
            redis_connected = await self.check_redis_connectivity(node_id)
            
            # Get performance metrics
            performance_metrics = await self.monitor_performance(node_id)
            
            # Get message processing stats
            msg_stats = self._message_processing_stats.get(node_id, {})
            
            # Calculate response time average
            response_time_avg = performance_metrics.get('response_time_avg', 0.0)
            
            # Get network status
            network_status = "healthy" if redis_connected else "degraded"
            
            # Get last heartbeat
            last_heartbeat = datetime.now().isoformat()
            
            # Count errors and warnings
            error_count = msg_stats.get('error_count', 0)
            warning_count = self._health_check_failures.get(node_id, 0)
            
            # Calculate uptime
            node_info = self._monitored_nodes.get(node_id, {})
            started_at_str = node_info.get('started_at')
            uptime_seconds = 0.0
            if started_at_str:
                started_at = datetime.fromisoformat(started_at_str)
                uptime_seconds = (datetime.now() - started_at).total_seconds()
            
            # Create health metrics
            health_metrics = HealthMetrics(
                redis_connectivity=redis_connected,
                message_processing_rate=msg_stats.get('processing_rate', 0.0),
                response_time_avg=response_time_avg,
                memory_usage_mb=performance_metrics.get('memory_mb', 0.0),
                cpu_usage_percent=performance_metrics.get('cpu_percent', 0.0),
                network_status=network_status,
                last_heartbeat=last_heartbeat,
                error_count=error_count,
                warning_count=warning_count,
                uptime_seconds=uptime_seconds
            )
            
            # Update last health check
            self._last_health_check[node_id] = datetime.now()
            
            # Reset consecutive failures on successful check
            if node_id in self._health_check_failures:
                self._health_check_failures[node_id] = 0
            
            self._logger.debug(f"Health status retrieved for node {node_id}")
            return health_metrics
            
        except Exception as e:
            self._increment_error_count()
            self._health_check_failures[node_id] = self._health_check_failures.get(node_id, 0) + 1
            self._logger.error(f"Failed to get health status for node {node_id}: {e}")
            
            # Return degraded health metrics
            return HealthMetrics(
                redis_connectivity=False,
                message_processing_rate=0.0,
                response_time_avg=999999.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                network_status="error",
                last_heartbeat=datetime.now().isoformat(),
                error_count=1,
                warning_count=1,
                uptime_seconds=0.0
            )

    async def generate_diagnostic_report(self, node_id: str) -> Dict[str, Any]:
        """
        Generate detailed diagnostic information
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict[str, Any]: Comprehensive diagnostic report
            
        Requirements: 3.4, 3.5, 3.7
        """
        try:
            report_timestamp = datetime.now().isoformat()
            
            # Get current health status
            health_status = await self.get_health_status(node_id)
            
            # Get performance history
            performance_history = self._performance_history.get(node_id, [])
            recent_performance = performance_history[-10:] if performance_history else []
            
            # Get Redis connection info
            redis_info = {}
            try:
                redis_manager = await self.get_redis_manager()
                redis_info = redis_manager.get_connection_info()
            except Exception as e:
                redis_info = {"error": str(e)}
            
            # Get system information
            system_info = {
                "platform": os.name,
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "process_id": os.getpid(),
                "working_directory": os.getcwd(),
                "environment_variables": {
                    k: v for k, v in os.environ.items() 
                    if k.startswith(('NODE_B_', 'REDIS_')) and 'PASSWORD' not in k
                }
            }
            
            # Get conversation history and network participation
            conversation_history = await self._get_conversation_history(node_id)
            network_participation = await self._get_network_participation(node_id)
            
            # Generate alerts
            alerts = await self._generate_alerts(node_id, health_status)
            
            # Resource utilization summary
            resource_utilization = await self._get_resource_utilization_summary(node_id)
            
            # Compile comprehensive diagnostic report
            diagnostic_report = {
                "report_metadata": {
                    "node_id": node_id,
                    "generated_at": report_timestamp,
                    "report_version": "1.0.0",
                    "coordinator_id": self.module_id
                },
                "health_status": asdict(health_status),
                "performance_metrics": {
                    "current": await self.monitor_performance(node_id),
                    "recent_history": [asdict(snapshot) for snapshot in recent_performance],
                    "history_count": len(performance_history)
                },
                "redis_connectivity": {
                    "status": health_status.redis_connectivity,
                    "connection_info": redis_info,
                    "last_test": self._last_health_check.get(node_id, datetime.now()).isoformat()
                },
                "message_processing": self._message_processing_stats.get(node_id, {}),
                "system_information": system_info,
                "conversation_history": conversation_history,
                "network_participation": network_participation,
                "alerts": alerts,
                "resource_utilization": resource_utilization,
                "monitoring_configuration": {
                    "monitoring_interval": self._monitoring_interval,
                    "history_retention_hours": self._history_retention_hours,
                    "alert_thresholds": asdict(self._alert_thresholds)
                }
            }
            
            self._logger.info(f"Generated diagnostic report for node {node_id}")
            return diagnostic_report
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to generate diagnostic report for node {node_id}: {e}")
            
            # Return minimal error report
            return {
                "report_metadata": {
                    "node_id": node_id,
                    "generated_at": datetime.now().isoformat(),
                    "error": str(e)
                },
                "status": "error",
                "message": f"Failed to generate diagnostic report: {e}"
            }

    async def check_redis_connectivity(self, node_id: str) -> bool:
        """
        Validate Redis connection health
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if Redis connection is healthy, False otherwise
            
        Requirements: 3.1, 3.2
        """
        try:
            redis_manager = await self.get_redis_manager()
            is_connected = await redis_manager.test_connection()
            
            if is_connected:
                self.increment_redis_operations()
                self._logger.debug(f"Redis connectivity check passed for node {node_id}")
            else:
                self._increment_warning_count()
                self._logger.warning(f"Redis connectivity check failed for node {node_id}")
            
            return is_connected
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Redis connectivity check error for node {node_id}: {e}")
            return False

    async def monitor_performance(self, node_id: str) -> Dict[str, float]:
        """
        Monitor performance metrics and resource utilization
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict[str, float]: Performance metrics including CPU, memory, network
            
        Requirements: 3.6, 3.7
        """
        try:
            # Get system performance metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            disk = psutil.disk_io_counters()
            
            # Get process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Calculate response time (simulate based on system load)
            response_time_avg = max(100.0, cpu_percent * 10)  # Base response time on CPU load
            
            performance_metrics = {
                "cpu_percent": cpu_percent,
                "memory_mb": memory.used / (1024 * 1024),
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "network_bytes_sent": network.bytes_sent if network else 0,
                "network_bytes_recv": network.bytes_recv if network else 0,
                "disk_read_bytes": disk.read_bytes if disk else 0,
                "disk_write_bytes": disk.write_bytes if disk else 0,
                "process_memory_mb": process_memory.rss / (1024 * 1024),
                "process_cpu_percent": process_cpu,
                "response_time_avg": response_time_avg,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            }
            
            # Store performance snapshot
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_mb=memory.used / (1024 * 1024),
                memory_percent=memory.percent,
                network_bytes_sent=network.bytes_sent if network else 0,
                network_bytes_recv=network.bytes_recv if network else 0,
                disk_io_read=disk.read_bytes if disk else 0,
                disk_io_write=disk.write_bytes if disk else 0,
                process_count=len(psutil.pids())
            )
            
            # Add to history
            if node_id not in self._performance_history:
                self._performance_history[node_id] = []
            
            self._performance_history[node_id].append(snapshot)
            
            # Cleanup old history
            await self._cleanup_performance_history(node_id)
            
            self._logger.debug(f"Performance metrics collected for node {node_id}")
            return performance_metrics
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to monitor performance for node {node_id}: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "memory_percent": 0.0,
                "response_time_avg": 999999.0,
                "error": str(e)
            }

    async def update_message_processing_stats(self, node_id: str, messages_processed: int = 0, messages_sent: int = 0, errors: int = 0):
        """
        Update message processing statistics
        
        Args:
            node_id: Node identifier
            messages_processed: Number of messages processed
            messages_sent: Number of messages sent
            errors: Number of errors encountered
        """
        if node_id not in self._message_processing_stats:
            self._message_processing_stats[node_id] = {
                'messages_processed': 0,
                'messages_sent': 0,
                'processing_rate': 0.0,
                'last_activity': None,
                'error_count': 0,
                'last_rate_calculation': datetime.now()
            }
        
        stats = self._message_processing_stats[node_id]
        
        # Update counters
        stats['messages_processed'] += messages_processed
        stats['messages_sent'] += messages_sent
        stats['error_count'] += errors
        stats['last_activity'] = datetime.now().isoformat()
        
        # Calculate processing rate (messages per minute)
        now = datetime.now()
        last_calc = stats.get('last_rate_calculation', now)
        time_diff = (now - last_calc).total_seconds()
        
        if time_diff >= 60:  # Calculate rate every minute
            total_messages = messages_processed + messages_sent
            stats['processing_rate'] = total_messages / (time_diff / 60)
            stats['last_rate_calculation'] = now

    async def _performance_monitor_loop(self):
        """Background task for continuous performance monitoring"""
        while self._monitoring_active:
            try:
                for node_id in self._monitored_nodes.keys():
                    await self.monitor_performance(node_id)
                
                await asyncio.sleep(self._monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Performance monitoring loop error: {e}")
                await asyncio.sleep(self._monitoring_interval)

    async def _cleanup_performance_history(self, node_id: str):
        """Clean up old performance history data"""
        if node_id not in self._performance_history:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=self._history_retention_hours)
        
        # Filter out old snapshots
        self._performance_history[node_id] = [
            snapshot for snapshot in self._performance_history[node_id]
            if datetime.fromisoformat(snapshot.timestamp) > cutoff_time
        ]

    async def _get_conversation_history(self, node_id: str) -> Dict[str, Any]:
        """Get conversation history for diagnostic report"""
        # This would integrate with actual conversation tracking
        # For now, return placeholder data
        return {
            "total_conversations": 0,
            "active_conversations": 0,
            "last_conversation": None,
            "conversation_topics": [],
            "note": "Conversation history tracking not yet implemented"
        }

    async def _get_network_participation(self, node_id: str) -> Dict[str, Any]:
        """Get network participation metrics for diagnostic report"""
        # This would integrate with actual network participation tracking
        # For now, return placeholder data based on message stats
        msg_stats = self._message_processing_stats.get(node_id, {})
        
        return {
            "messages_processed": msg_stats.get('messages_processed', 0),
            "messages_sent": msg_stats.get('messages_sent', 0),
            "last_activity": msg_stats.get('last_activity'),
            "processing_rate": msg_stats.get('processing_rate', 0.0),
            "network_events": self._node_b_metrics.get('network_events', 0),
            "redis_operations": self._node_b_metrics.get('redis_operations', 0)
        }

    async def _generate_alerts(self, node_id: str, health_status: HealthMetrics) -> List[Dict[str, Any]]:
        """Generate alerts based on health status and thresholds"""
        alerts = []
        
        # CPU alerts
        if health_status.cpu_usage_percent >= self._alert_thresholds.cpu_critical:
            alerts.append({
                "type": "critical",
                "category": "performance",
                "metric": "cpu_usage",
                "value": health_status.cpu_usage_percent,
                "threshold": self._alert_thresholds.cpu_critical,
                "message": f"Critical CPU usage: {health_status.cpu_usage_percent:.1f}%"
            })
        elif health_status.cpu_usage_percent >= self._alert_thresholds.cpu_warning:
            alerts.append({
                "type": "warning",
                "category": "performance",
                "metric": "cpu_usage",
                "value": health_status.cpu_usage_percent,
                "threshold": self._alert_thresholds.cpu_warning,
                "message": f"High CPU usage: {health_status.cpu_usage_percent:.1f}%"
            })
        
        # Memory alerts
        memory_percent = (health_status.memory_usage_mb / psutil.virtual_memory().total) * 100
        if memory_percent >= self._alert_thresholds.memory_critical:
            alerts.append({
                "type": "critical",
                "category": "performance",
                "metric": "memory_usage",
                "value": memory_percent,
                "threshold": self._alert_thresholds.memory_critical,
                "message": f"Critical memory usage: {memory_percent:.1f}%"
            })
        elif memory_percent >= self._alert_thresholds.memory_warning:
            alerts.append({
                "type": "warning",
                "category": "performance",
                "metric": "memory_usage",
                "value": memory_percent,
                "threshold": self._alert_thresholds.memory_warning,
                "message": f"High memory usage: {memory_percent:.1f}%"
            })
        
        # Response time alerts
        if health_status.response_time_avg >= self._alert_thresholds.response_time_critical:
            alerts.append({
                "type": "critical",
                "category": "performance",
                "metric": "response_time",
                "value": health_status.response_time_avg,
                "threshold": self._alert_thresholds.response_time_critical,
                "message": f"Critical response time: {health_status.response_time_avg:.1f}ms"
            })
        elif health_status.response_time_avg >= self._alert_thresholds.response_time_warning:
            alerts.append({
                "type": "warning",
                "category": "performance",
                "metric": "response_time",
                "value": health_status.response_time_avg,
                "threshold": self._alert_thresholds.response_time_warning,
                "message": f"High response time: {health_status.response_time_avg:.1f}ms"
            })
        
        # Redis connectivity alerts
        if not health_status.redis_connectivity:
            alerts.append({
                "type": "critical",
                "category": "connectivity",
                "metric": "redis_connectivity",
                "value": False,
                "threshold": True,
                "message": "Redis connectivity lost"
            })
        
        # Error count alerts
        if health_status.error_count >= self._alert_thresholds.error_rate_critical:
            alerts.append({
                "type": "critical",
                "category": "errors",
                "metric": "error_count",
                "value": health_status.error_count,
                "threshold": self._alert_thresholds.error_rate_critical,
                "message": f"Critical error rate: {health_status.error_count} errors"
            })
        elif health_status.error_count >= self._alert_thresholds.error_rate_warning:
            alerts.append({
                "type": "warning",
                "category": "errors",
                "metric": "error_count",
                "value": health_status.error_count,
                "threshold": self._alert_thresholds.error_rate_warning,
                "message": f"High error rate: {health_status.error_count} errors"
            })
        
        return alerts

    async def _get_resource_utilization_summary(self, node_id: str) -> Dict[str, Any]:
        """Get resource utilization summary for diagnostic report"""
        try:
            # Get current system resources
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get historical averages
            history = self._performance_history.get(node_id, [])
            if history:
                recent_history = history[-10:]  # Last 10 snapshots
                avg_cpu = sum(s.cpu_percent for s in recent_history) / len(recent_history)
                avg_memory = sum(s.memory_percent for s in recent_history) / len(recent_history)
            else:
                avg_cpu = cpu_percent
                avg_memory = memory.percent
            
            return {
                "current": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "memory_used_gb": memory.used / (1024**3),
                    "memory_total_gb": memory.total / (1024**3)
                },
                "averages": {
                    "cpu_percent_avg": avg_cpu,
                    "memory_percent_avg": avg_memory
                },
                "limits": {
                    "cpu_cores": psutil.cpu_count(),
                    "memory_total_gb": memory.total / (1024**3),
                    "disk_total_gb": disk.total / (1024**3)
                }
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get resource utilization summary: {e}")
            return {"error": str(e)}

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status and configuration"""
        return {
            "monitoring_active": self._monitoring_active,
            "monitored_nodes": list(self._monitored_nodes.keys()),
            "monitoring_interval": self._monitoring_interval,
            "history_retention_hours": self._history_retention_hours,
            "alert_thresholds": asdict(self._alert_thresholds),
            "performance_history_counts": {
                node_id: len(history) 
                for node_id, history in self._performance_history.items()
            }
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_monitoring()
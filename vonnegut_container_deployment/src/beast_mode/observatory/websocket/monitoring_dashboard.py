"""
WebSocket Monitoring Dashboard and Metrics Visualization

Provides real-time dashboard capabilities for WebSocket connectivity monitoring
with comprehensive metrics visualization and status tracking.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
import time

from .comprehensive_monitor import ComprehensiveWebSocketMonitor, MonitoringMetrics, WebSocketAlert, AlertSeverity
from .alerting_rules import WebSocketAlertingSystem

logger = logging.getLogger(__name__)


class DashboardWidget(Enum):
    """Dashboard widget types."""
    CONNECTION_STATUS = "connection_status"
    LATENCY_CHART = "latency_chart"
    ERROR_RATE_CHART = "error_rate_chart"
    THROUGHPUT_CHART = "throughput_chart"
    ALERT_SUMMARY = "alert_summary"
    HEALTH_SCORE = "health_score"
    TUNNEL_STATUS = "tunnel_status"
    ENDPOINT_STATUS = "endpoint_status"


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    refresh_interval_seconds: int = 30
    max_data_points: int = 100
    enable_real_time: bool = True
    widgets: List[DashboardWidget] = field(default_factory=lambda: list(DashboardWidget))
    theme: str = "dark"
    auto_refresh: bool = True


@dataclass
class DashboardData:
    """Dashboard data structure."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    connection_status: Dict[str, Any] = field(default_factory=dict)
    latency_data: List[Dict[str, Any]] = field(default_factory=list)
    error_rate_data: List[Dict[str, Any]] = field(default_factory=list)
    throughput_data: List[Dict[str, Any]] = field(default_factory=list)
    alert_summary: Dict[str, Any] = field(default_factory=dict)
    health_scores: Dict[str, float] = field(default_factory=dict)
    tunnel_status: Dict[str, Any] = field(default_factory=dict)
    endpoint_status: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'connection_status': self.connection_status,
            'latency_data': self.latency_data,
            'error_rate_data': self.error_rate_data,
            'throughput_data': self.throughput_data,
            'alert_summary': self.alert_summary,
            'health_scores': self.health_scores,
            'tunnel_status': self.tunnel_status,
            'endpoint_status': self.endpoint_status
        }


class WebSocketMonitoringDashboard:
    """
    Comprehensive WebSocket monitoring dashboard with real-time updates
    and interactive visualization capabilities.
    """
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        """Initialize monitoring dashboard."""
        self.config = config or DashboardConfig()
        self.monitor: Optional[ComprehensiveWebSocketMonitor] = None
        self.alerting_system: Optional[WebSocketAlertingSystem] = None
        
        # Dashboard state
        self._dashboard_active = False
        self._dashboard_task: Optional[asyncio.Task] = None
        self._dashboard_data_history: List[DashboardData] = []
        self._subscribers: Set[Callable[[DashboardData], None]] = set()
        
        # Data aggregation
        self._latency_history: List[float] = []
        self._error_rate_history: List[float] = []
        self._throughput_history: List[float] = []
        
        self._log_action("dashboard_initialized", {
            "config": {
                "refresh_interval_seconds": self.config.refresh_interval_seconds,
                "max_data_points": self.config.max_data_points,
                "enable_real_time": self.config.enable_real_time,
                "widgets": [w.value for w in self.config.widgets],
                "theme": self.config.theme
            }
        })
    
    async def initialize(self, monitor: ComprehensiveWebSocketMonitor, alerting_system: WebSocketAlertingSystem) -> None:
        """Initialize dashboard with monitoring components."""
        self.monitor = monitor
        self.alerting_system = alerting_system
        
        self._log_action("dashboard_components_initialized", {
            "monitor_available": self.monitor is not None,
            "alerting_system_available": self.alerting_system is not None
        })
    
    async def start_dashboard(self) -> None:
        """Start dashboard with real-time updates."""
        if self._dashboard_active:
            self._log_action("dashboard_already_active", {})
            return
        
        if not self.monitor or not self.alerting_system:
            raise RuntimeError("Dashboard not initialized with monitoring components")
        
        self._dashboard_active = True
        self._dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        
        self._log_action("dashboard_started", {
            "refresh_interval_seconds": self.config.refresh_interval_seconds,
            "real_time_enabled": self.config.enable_real_time
        })
    
    async def stop_dashboard(self) -> None:
        """Stop dashboard updates."""
        if not self._dashboard_active:
            self._log_action("dashboard_not_active", {})
            return
        
        self._dashboard_active = False
        
        if self._dashboard_task:
            self._dashboard_task.cancel()
            try:
                await self._dashboard_task
            except asyncio.CancelledError:
                pass
        
        self._log_action("dashboard_stopped", {})
    
    async def get_dashboard_data(self) -> DashboardData:
        """Get current dashboard data."""
        if not self.monitor or not self.alerting_system:
            raise RuntimeError("Dashboard not initialized")
        
        # Get current metrics
        current_metrics = await self.monitor.get_current_metrics()
        
        # Get alert summary
        alert_summary = await self.monitor.get_alert_summary()
        
        # Get health summary
        health_summary = self.monitor.health_validator.get_health_summary()
        
        # Build dashboard data
        dashboard_data = DashboardData(
            connection_status=self._build_connection_status(current_metrics),
            latency_data=self._build_latency_data(current_metrics),
            error_rate_data=self._build_error_rate_data(current_metrics),
            throughput_data=self._build_throughput_data(current_metrics),
            alert_summary=alert_summary,
            health_scores=self._build_health_scores(current_metrics),
            tunnel_status=self._build_tunnel_status(current_metrics),
            endpoint_status=self._build_endpoint_status(health_summary)
        )
        
        return dashboard_data
    
    async def get_historical_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get historical dashboard data."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter historical data
        historical_data = [
            data for data in self._dashboard_data_history
            if data.timestamp >= cutoff_time
        ]
        
        # Extract time series data
        timestamps = [data.timestamp.isoformat() for data in historical_data]
        
        latency_series = []
        error_rate_series = []
        throughput_series = []
        health_score_series = []
        
        for data in historical_data:
            latency_series.append(data.connection_status.get('average_latency_ms', 0))
            error_rate_series.append(data.connection_status.get('error_rate', 0))
            throughput_series.append(data.connection_status.get('throughput_msgs_per_sec', 0))
            health_score_series.append(data.health_scores.get('overall', 0))
        
        return {
            "timestamps": timestamps,
            "latency_series": latency_series,
            "error_rate_series": error_rate_series,
            "throughput_series": throughput_series,
            "health_score_series": health_score_series,
            "data_points": len(historical_data),
            "time_range_hours": hours
        }
    
    async def get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for specific widget."""
        dashboard_data = await self.get_dashboard_data()
        
        if widget == DashboardWidget.CONNECTION_STATUS:
            return dashboard_data.connection_status
        elif widget == DashboardWidget.LATENCY_CHART:
            return {"data": dashboard_data.latency_data}
        elif widget == DashboardWidget.ERROR_RATE_CHART:
            return {"data": dashboard_data.error_rate_data}
        elif widget == DashboardWidget.THROUGHPUT_CHART:
            return {"data": dashboard_data.throughput_data}
        elif widget == DashboardWidget.ALERT_SUMMARY:
            return dashboard_data.alert_summary
        elif widget == DashboardWidget.HEALTH_SCORE:
            return {"scores": dashboard_data.health_scores}
        elif widget == DashboardWidget.TUNNEL_STATUS:
            return dashboard_data.tunnel_status
        elif widget == DashboardWidget.ENDPOINT_STATUS:
            return dashboard_data.endpoint_status
        else:
            return {}
    
    def subscribe_to_updates(self, callback: Callable[[DashboardData], None]) -> None:
        """Subscribe to dashboard updates."""
        self._subscribers.add(callback)
    
    def unsubscribe_from_updates(self, callback: Callable[[DashboardData], None]) -> None:
        """Unsubscribe from dashboard updates."""
        self._subscribers.discard(callback)
    
    async def _dashboard_update_loop(self) -> None:
        """Main dashboard update loop."""
        self._log_action("dashboard_update_loop_started", {})
        
        try:
            while self._dashboard_active:
                start_time = time.time()
                
                # Get current dashboard data
                dashboard_data = await self.get_dashboard_data()
                
                # Store in history
                self._dashboard_data_history.append(dashboard_data)
                if len(self._dashboard_data_history) > self.config.max_data_points:
                    self._dashboard_data_history = self._dashboard_data_history[-self.config.max_data_points:]
                
                # Update data series
                self._update_data_series(dashboard_data)
                
                # Notify subscribers
                await self._notify_subscribers(dashboard_data)
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.refresh_interval_seconds - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            self._log_action("dashboard_update_loop_cancelled", {})
            raise
        except Exception as e:
            self._log_action("dashboard_update_loop_error", {
                "error": str(e)
            })
            raise
    
    def _build_connection_status(self, metrics: MonitoringMetrics) -> Dict[str, Any]:
        """Build connection status data."""
        return {
            "total_endpoints": metrics.active_connections + metrics.failed_connections,
            "healthy_endpoints": metrics.active_connections,
            "failed_endpoints": metrics.failed_connections,
            "success_rate": metrics.connection_success_rate,
            "average_latency_ms": metrics.average_latency_ms,
            "error_rate": metrics.error_rate,
            "throughput_msgs_per_sec": metrics.throughput_msgs_per_sec,
            "status": "healthy" if metrics.connection_success_rate > 0.9 else "degraded" if metrics.connection_success_rate > 0.7 else "critical"
        }
    
    def _build_latency_data(self, metrics: MonitoringMetrics) -> List[Dict[str, Any]]:
        """Build latency chart data."""
        return [
            {
                "timestamp": metrics.timestamp.isoformat(),
                "latency_ms": metrics.average_latency_ms,
                "threshold_ms": 5000.0,
                "status": "good" if metrics.average_latency_ms < 1000 else "warning" if metrics.average_latency_ms < 5000 else "critical"
            }
        ]
    
    def _build_error_rate_data(self, metrics: MonitoringMetrics) -> List[Dict[str, Any]]:
        """Build error rate chart data."""
        return [
            {
                "timestamp": metrics.timestamp.isoformat(),
                "error_rate": metrics.error_rate,
                "threshold": 0.10,
                "status": "good" if metrics.error_rate < 0.05 else "warning" if metrics.error_rate < 0.10 else "critical"
            }
        ]
    
    def _build_throughput_data(self, metrics: MonitoringMetrics) -> List[Dict[str, Any]]:
        """Build throughput chart data."""
        return [
            {
                "timestamp": metrics.timestamp.isoformat(),
                "throughput_msgs_per_sec": metrics.throughput_msgs_per_sec,
                "status": "good" if metrics.throughput_msgs_per_sec > 1.0 else "warning"
            }
        ]
    
    def _build_health_scores(self, metrics: MonitoringMetrics) -> Dict[str, float]:
        """Build health scores."""
        return {
            "overall": (metrics.connection_success_rate + (1.0 - metrics.error_rate) + metrics.tunnel_health_score + metrics.observatory_health_score) / 4,
            "connection": metrics.connection_success_rate,
            "tunnel": metrics.tunnel_health_score,
            "observatory": metrics.observatory_health_score,
            "performance": 1.0 - min(metrics.error_rate, 1.0)
        }
    
    def _build_tunnel_status(self, metrics: MonitoringMetrics) -> Dict[str, Any]:
        """Build tunnel status data."""
        return {
            "health_score": metrics.tunnel_health_score,
            "status": metrics.cloudflare_status,
            "bot_protection_triggers": metrics.bot_protection_triggers,
            "status_color": "green" if metrics.tunnel_health_score > 0.8 else "yellow" if metrics.tunnel_health_score > 0.6 else "red"
        }
    
    def _build_endpoint_status(self, health_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Build endpoint status data."""
        return {
            "total_endpoints": health_summary.get("total_endpoints", 0),
            "healthy_endpoints": health_summary.get("healthy_endpoints", 0),
            "degraded_endpoints": health_summary.get("degraded_endpoints", 0),
            "unhealthy_endpoints": health_summary.get("unhealthy_endpoints", 0),
            "overall_status": health_summary.get("overall_status", "unknown"),
            "endpoint_details": health_summary.get("endpoint_statuses", {})
        }
    
    def _update_data_series(self, dashboard_data: DashboardData) -> None:
        """Update data series for charts."""
        # Update latency series
        self._latency_history.append(dashboard_data.connection_status.get('average_latency_ms', 0))
        if len(self._latency_history) > self.config.max_data_points:
            self._latency_history = self._latency_history[-self.config.max_data_points:]
        
        # Update error rate series
        self._error_rate_history.append(dashboard_data.connection_status.get('error_rate', 0))
        if len(self._error_rate_history) > self.config.max_data_points:
            self._error_rate_history = self._error_rate_history[-self.config.max_data_points:]
        
        # Update throughput series
        self._throughput_history.append(dashboard_data.connection_status.get('throughput_msgs_per_sec', 0))
        if len(self._throughput_history) > self.config.max_data_points:
            self._throughput_history = self._throughput_history[-self.config.max_data_points:]
    
    async def _notify_subscribers(self, dashboard_data: DashboardData) -> None:
        """Notify dashboard subscribers."""
        for callback in self._subscribers:
            try:
                callback(dashboard_data)
            except Exception as e:
                logger.error(f"Dashboard subscriber callback error: {e}")
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return {
            "dashboard_active": self._dashboard_active,
            "data_points_collected": len(self._dashboard_data_history),
            "subscribers": len(self._subscribers),
            "refresh_interval_seconds": self.config.refresh_interval_seconds,
            "widgets_enabled": len(self.config.widgets),
            "real_time_enabled": self.config.enable_real_time,
            "data_series_lengths": {
                "latency_history": len(self._latency_history),
                "error_rate_history": len(self._error_rate_history),
                "throughput_history": len(self._throughput_history)
            }
        }
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '5.0',
            'action': f'dashboard_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))


class WebSocketDashboardAPI:
    """
    REST API for WebSocket monitoring dashboard.
    Provides HTTP endpoints for dashboard data access.
    """
    
    def __init__(self, dashboard: WebSocketMonitoringDashboard):
        """Initialize dashboard API."""
        self.dashboard = dashboard
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        data = await self.dashboard.get_dashboard_data()
        return data.to_dict()
    
    async def get_historical_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get historical dashboard data."""
        return await self.dashboard.get_historical_data(hours)
    
    async def get_widget_data(self, widget_name: str) -> Dict[str, Any]:
        """Get widget data."""
        try:
            widget = DashboardWidget(widget_name)
            return await self.dashboard.get_widget_data(widget)
        except ValueError:
            return {"error": f"Unknown widget: {widget_name}"}
    
    async def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return self.dashboard.get_dashboard_statistics()


# Global dashboard instance
_global_dashboard: Optional[WebSocketMonitoringDashboard] = None


async def get_global_dashboard() -> WebSocketMonitoringDashboard:
    """Get global dashboard instance."""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = WebSocketMonitoringDashboard()
    return _global_dashboard


async def initialize_global_dashboard(monitor: ComprehensiveWebSocketMonitor, alerting_system: WebSocketAlertingSystem) -> None:
    """Initialize global dashboard."""
    dashboard = await get_global_dashboard()
    await dashboard.initialize(monitor, alerting_system)


async def start_global_dashboard() -> None:
    """Start global dashboard."""
    dashboard = await get_global_dashboard()
    await dashboard.start_dashboard()


async def stop_global_dashboard() -> None:
    """Stop global dashboard."""
    dashboard = await get_global_dashboard()
    await dashboard.stop_dashboard()
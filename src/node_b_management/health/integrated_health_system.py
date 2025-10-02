"""
Integrated Health Management System for Node B Management

Combines health monitoring and diagnostic reporting into a unified system
that provides comprehensive health management capabilities for Node B instances.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.node_b_component import NodeBComponent
from ..core.interfaces import IHealthMonitoring, HealthMetrics
from .health_monitoring_coordinator import HealthMonitoringCoordinator
from .diagnostic_reporting_system import DiagnosticReportingSystem, Alert


class IntegratedHealthSystem(NodeBComponent, IHealthMonitoring):
    """
    Integrated Health Management System for Node B instances
    
    Combines health monitoring and diagnostic reporting to provide:
    - Comprehensive health status monitoring
    - Automated alert generation and management
    - Detailed diagnostic reporting
    - Performance tracking and analysis
    - Resource utilization monitoring
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 6.3
    """

    def __init__(self, node_id: str = None):
        """
        Initialize Integrated Health System
        
        Args:
            node_id: Optional Node B instance ID for health management
        """
        super().__init__("integrated_health", node_id)
        
        # Initialize component systems
        self._health_monitor = HealthMonitoringCoordinator(node_id)
        self._diagnostic_reporter = DiagnosticReportingSystem(node_id)
        
        # Integration state
        self._integration_active = False
        self._health_check_interval = 60.0  # seconds
        self._health_check_task = None
        
        # Health status cache
        self._last_health_status: Dict[str, HealthMetrics] = {}
        self._health_status_cache_ttl = 30.0  # seconds
        
        self._logger.info(f"IntegratedHealthSystem initialized for node {node_id}")

    async def start_integrated_monitoring(self, node_ids: List[str] = None):
        """
        Start integrated health monitoring for specified nodes
        
        Args:
            node_ids: List of node IDs to monitor, defaults to self.node_id
        """
        if node_ids is None:
            node_ids = [self.node_id] if self.node_id else []
        
        try:
            # Start health monitoring
            await self._health_monitor.start_monitoring(node_ids)
            
            # Start integrated health check loop
            if not self._integration_active:
                self._integration_active = True
                self._health_check_task = asyncio.create_task(self._integrated_health_check_loop(node_ids))
            
            self._logger.info(f"Started integrated health monitoring for nodes: {node_ids}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to start integrated monitoring: {e}")
            raise

    async def stop_integrated_monitoring(self):
        """Stop integrated health monitoring and cleanup resources"""
        try:
            self._integration_active = False
            
            # Stop health check task
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Stop health monitoring
            await self._health_monitor.stop_monitoring()
            
            self._logger.info("Integrated health monitoring stopped")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to stop integrated monitoring: {e}")

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
            # Check cache first
            if node_id in self._last_health_status:
                cached_status = self._last_health_status[node_id]
                cache_time = datetime.fromisoformat(cached_status.last_heartbeat)
                if (datetime.now() - cache_time).total_seconds() < self._health_status_cache_ttl:
                    return cached_status
            
            # Get fresh health status
            health_status = await self._health_monitor.get_health_status(node_id)
            
            # Cache the result
            self._last_health_status[node_id] = health_status
            
            # Generate alerts based on health status
            await self._diagnostic_reporter.generate_alerts_from_health_metrics(node_id, health_status)
            
            return health_status
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to get integrated health status for node {node_id}: {e}")
            raise

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
            # Get base diagnostic report from health monitor
            base_report = await self._health_monitor.generate_diagnostic_report(node_id)
            
            # Get current performance metrics
            performance_metrics = await self._health_monitor.monitor_performance(node_id)
            
            # Generate resource utilization report
            resource_report = await self._diagnostic_reporter.generate_resource_utilization_report(
                node_id, performance_metrics
            )
            
            # Get alerts and event history
            active_alerts = self._diagnostic_reporter.get_active_alerts(node_id)
            conversation_history = self._diagnostic_reporter.get_conversation_history(node_id, limit=50)
            network_history = self._diagnostic_reporter.get_network_participation_history(node_id, limit=50)
            participation_stats = self._diagnostic_reporter.get_participation_statistics(node_id)
            
            # Combine into integrated report
            integrated_report = {
                **base_report,
                "integrated_diagnostics": {
                    "resource_utilization": resource_report.__dict__,
                    "active_alerts": [alert.__dict__ for alert in active_alerts],
                    "alert_summary": {
                        "total_active": len(active_alerts),
                        "critical_count": len([a for a in active_alerts if a.severity.value == "critical"]),
                        "warning_count": len([a for a in active_alerts if a.severity.value == "warning"])
                    },
                    "conversation_summary": {
                        "total_events": len(conversation_history),
                        "recent_events": [event.__dict__ for event in conversation_history[-10:]],
                        "active_conversations": len(self._diagnostic_reporter._active_conversations.get(node_id, {}))
                    },
                    "network_participation_summary": {
                        "total_events": len(network_history),
                        "recent_events": [event.__dict__ for event in network_history[-10:]],
                        "participation_stats": participation_stats
                    },
                    "integration_status": {
                        "monitoring_active": self._integration_active,
                        "health_check_interval": self._health_check_interval,
                        "last_integrated_check": datetime.now().isoformat()
                    }
                }
            }
            
            self._logger.info(f"Generated integrated diagnostic report for node {node_id}")
            return integrated_report
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to generate integrated diagnostic report for node {node_id}: {e}")
            raise

    async def check_redis_connectivity(self, node_id: str) -> bool:
        """
        Validate Redis connection health
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if Redis connection is healthy, False otherwise
            
        Requirements: 3.1, 3.2
        """
        return await self._health_monitor.check_redis_connectivity(node_id)

    async def monitor_performance(self, node_id: str) -> Dict[str, float]:
        """
        Monitor performance metrics and resource utilization
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict[str, float]: Performance metrics including CPU, memory, network
            
        Requirements: 3.6, 3.7
        """
        return await self._health_monitor.monitor_performance(node_id)

    async def track_conversation_event(self, node_id: str, event_type: str, participant: str, 
                                     content_summary: str, metadata: Dict[str, Any] = None):
        """
        Track conversation events for diagnostic reporting
        
        Args:
            node_id: Node identifier
            event_type: Type of conversation event
            participant: Conversation participant
            content_summary: Summary of conversation content
            metadata: Additional event metadata
        """
        await self._diagnostic_reporter.track_conversation_event(
            node_id, event_type, participant, content_summary, metadata
        )

    async def track_network_participation_event(self, node_id: str, event_type: str, 
                                              details: Dict[str, Any], success: bool, 
                                              response_time_ms: float):
        """
        Track network participation events for diagnostic reporting
        
        Args:
            node_id: Node identifier
            event_type: Type of network event
            details: Event details
            success: Whether the event was successful
            response_time_ms: Response time in milliseconds
        """
        await self._diagnostic_reporter.track_network_participation_event(
            node_id, event_type, details, success, response_time_ms
        )

    async def get_active_alerts(self, node_id: str = None) -> List[Alert]:
        """Get active alerts, optionally filtered by node ID"""
        return self._diagnostic_reporter.get_active_alerts(node_id)

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert"""
        return await self._diagnostic_reporter.acknowledge_alert(alert_id, acknowledged_by)

    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an active alert"""
        return await self._diagnostic_reporter.resolve_alert(alert_id, resolved_by)

    def get_system_status(self) -> Dict[str, Any]:
        """Get integrated system status"""
        health_status = self._health_monitor.get_monitoring_status()
        diagnostic_status = self._diagnostic_reporter.get_diagnostic_summary()
        
        return {
            "integrated_system": {
                "active": self._integration_active,
                "health_check_interval": self._health_check_interval,
                "cached_health_statuses": len(self._last_health_status)
            },
            "health_monitoring": health_status,
            "diagnostic_reporting": diagnostic_status,
            "overall_status": "operational" if self._integration_active else "stopped"
        }

    async def _integrated_health_check_loop(self, node_ids: List[str]):
        """Background task for integrated health checking"""
        while self._integration_active:
            try:
                for node_id in node_ids:
                    # Get health status (this will also generate alerts)
                    health_status = await self.get_health_status(node_id)
                    
                    # Update message processing stats if available
                    msg_stats = self._health_monitor._message_processing_stats.get(node_id, {})
                    if msg_stats:
                        await self._health_monitor.update_message_processing_stats(
                            node_id,
                            messages_processed=msg_stats.get('messages_processed', 0),
                            messages_sent=msg_stats.get('messages_sent', 0),
                            errors=msg_stats.get('error_count', 0)
                        )
                
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Integrated health check loop error: {e}")
                await asyncio.sleep(self._health_check_interval)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_integrated_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_integrated_monitoring()
"""
Health Monitoring Integration for Engagement System

Integrates engagement system health monitoring with Observatory's existing health system.
Provides comprehensive health checks, status reporting, and integration with Observatory health endpoints.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .engagement_metrics import EngagementMetricsCollector
from .prometheus_integration import EngagementPrometheusIntegration

logger = logging.getLogger(__name__)


class EngagementHealthStatus(Enum):
    """Engagement system health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class EngagementHealthCheck:
    """Represents a single health check result."""
    
    def __init__(self, name: str, status: EngagementHealthStatus, 
                 message: str, details: Dict[str, Any] = None,
                 timestamp: datetime = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class EngagementHealthMonitor(ReflectiveModule):
    """
    Monitors engagement system health and integrates with Observatory health monitoring.
    
    Provides comprehensive health checks for all engagement components, calculates
    overall system health scores, and integrates with Observatory's health endpoints.
    """
    
    def __init__(self, metrics_collector: EngagementMetricsCollector,
                 prometheus_integration: EngagementPrometheusIntegration):
        super().__init__()
        self.module_id = "engagement_health_monitor"
        
        self.metrics_collector = metrics_collector
        self.prometheus_integration = prometheus_integration
        
        # Health monitoring state
        self.running = False
        self.last_health_check = datetime.now()
        self.health_check_interval = 30  # seconds
        
        # Health status tracking
        self.current_health_status = EngagementHealthStatus.UNKNOWN
        self.health_score = 0.0
        self.health_checks: List[EngagementHealthCheck] = []
        self.health_history: List[Tuple[datetime, float]] = []
        
        # Component health tracking
        self.component_health: Dict[str, EngagementHealthStatus] = {}
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        
        logger.info("🏥 Engagement Health Monitor initialized")
    
    async def initialize(self) -> bool:
        """Initialize the health monitor."""
        try:
            # Start health monitoring
            self.running = True
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            # Perform initial health check
            await self._perform_health_check()
            
            logger.info("✅ Engagement Health Monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Health Monitor: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the health monitor."""
        logger.info("🛑 Shutting down Engagement Health Monitor...")
        
        self.running = False
        
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Engagement Health Monitor shutdown complete")
    
    async def _health_check_loop(self):
        """Background loop for periodic health checks."""
        logger.info("🏥 Starting engagement health check loop")
        
        while self.running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval * 2)  # Back off on error
    
    async def _perform_health_check(self):
        """Perform comprehensive health check of engagement system."""
        try:
            self.health_checks.clear()
            
            # Check metrics collector health
            await self._check_metrics_collector_health()
            
            # Check Prometheus integration health
            await self._check_prometheus_integration_health()
            
            # Check engagement activity health
            await self._check_engagement_activity_health()
            
            # Check system resource health
            await self._check_system_resource_health()
            
            # Calculate overall health
            self._calculate_overall_health()
            
            # Update health history
            self.health_history.append((datetime.now(), self.health_score))
            
            # Keep only last 24 hours of history
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.health_history = [
                (timestamp, score) for timestamp, score in self.health_history
                if timestamp > cutoff_time
            ]
            
            self.last_health_check = datetime.now()
            
            logger.debug(f"🏥 Health check complete: {self.current_health_status.value} (score: {self.health_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            self._add_health_check("health_check_system", EngagementHealthStatus.CRITICAL,
                                 f"Health check system failed: {e}")
    
    async def _check_metrics_collector_health(self):
        """Check metrics collector health."""
        try:
            collector_health = self.metrics_collector.get_health_status()
            
            if collector_health.get("status") == "healthy":
                # Check if metrics are being collected
                metrics_collected = collector_health.get("metrics_collected", 0)
                active_sessions = collector_health.get("active_sessions", 0)
                
                if metrics_collected > 0:
                    status = EngagementHealthStatus.HEALTHY
                    message = f"Metrics collector healthy: {metrics_collected} metrics collected, {active_sessions} active sessions"
                else:
                    status = EngagementHealthStatus.DEGRADED
                    message = "Metrics collector running but no metrics collected yet"
                
                self.component_health["metrics_collector"] = status
                self._add_health_check("metrics_collector", status, message, collector_health)
                
            else:
                status = EngagementHealthStatus.UNHEALTHY
                message = "Metrics collector not running"
                self.component_health["metrics_collector"] = status
                self._add_health_check("metrics_collector", status, message, collector_health)
                
        except Exception as e:
            status = EngagementHealthStatus.CRITICAL
            message = f"Failed to check metrics collector health: {e}"
            self.component_health["metrics_collector"] = status
            self._add_health_check("metrics_collector", status, message)
    
    async def _check_prometheus_integration_health(self):
        """Check Prometheus integration health."""
        try:
            integration_health = self.prometheus_integration.get_health_status()
            
            if integration_health.get("integration_running"):
                export_errors = integration_health.get("export_errors", 0)
                
                if export_errors == 0:
                    status = EngagementHealthStatus.HEALTHY
                    message = "Prometheus integration healthy"
                elif export_errors < 5:
                    status = EngagementHealthStatus.DEGRADED
                    message = f"Prometheus integration degraded: {export_errors} export errors"
                else:
                    status = EngagementHealthStatus.UNHEALTHY
                    message = f"Prometheus integration unhealthy: {export_errors} export errors"
                
                self.component_health["prometheus_integration"] = status
                self._add_health_check("prometheus_integration", status, message, integration_health)
                
            else:
                status = EngagementHealthStatus.UNHEALTHY
                message = "Prometheus integration not running"
                self.component_health["prometheus_integration"] = status
                self._add_health_check("prometheus_integration", status, message, integration_health)
                
        except Exception as e:
            status = EngagementHealthStatus.CRITICAL
            message = f"Failed to check Prometheus integration health: {e}"
            self.component_health["prometheus_integration"] = status
            self._add_health_check("prometheus_integration", status, message)
    
    async def _check_engagement_activity_health(self):
        """Check engagement activity health."""
        try:
            summary = self.metrics_collector.get_engagement_summary()
            
            active_sessions = summary.get("active_attention_sessions", 0)
            interaction_rate = summary.get("recent_interaction_rate_per_minute", 0)
            avg_session_duration = summary.get("average_session_duration_seconds", 0)
            
            # Determine health based on activity levels
            if active_sessions > 0 and interaction_rate > 0.5:
                status = EngagementHealthStatus.HEALTHY
                message = f"High engagement activity: {active_sessions} sessions, {interaction_rate:.1f} interactions/min"
            elif active_sessions > 0 or interaction_rate > 0.1:
                status = EngagementHealthStatus.DEGRADED
                message = f"Moderate engagement activity: {active_sessions} sessions, {interaction_rate:.1f} interactions/min"
            elif summary.get("completed_sessions", 0) > 0:
                status = EngagementHealthStatus.DEGRADED
                message = "Low current activity but has historical engagement"
            else:
                status = EngagementHealthStatus.UNHEALTHY
                message = "No engagement activity detected"
            
            self.component_health["engagement_activity"] = status
            self._add_health_check("engagement_activity", status, message, {
                "active_sessions": active_sessions,
                "interaction_rate_per_minute": interaction_rate,
                "avg_session_duration_seconds": avg_session_duration
            })
            
        except Exception as e:
            status = EngagementHealthStatus.CRITICAL
            message = f"Failed to check engagement activity health: {e}"
            self.component_health["engagement_activity"] = status
            self._add_health_check("engagement_activity", status, message)
    
    async def _check_system_resource_health(self):
        """Check system resource health for engagement components."""
        try:
            # Check memory usage (simplified check)
            import psutil
            
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if memory_percent < 80 and cpu_percent < 80:
                status = EngagementHealthStatus.HEALTHY
                message = f"System resources healthy: {memory_percent:.1f}% memory, {cpu_percent:.1f}% CPU"
            elif memory_percent < 90 and cpu_percent < 90:
                status = EngagementHealthStatus.DEGRADED
                message = f"System resources degraded: {memory_percent:.1f}% memory, {cpu_percent:.1f}% CPU"
            else:
                status = EngagementHealthStatus.UNHEALTHY
                message = f"System resources unhealthy: {memory_percent:.1f}% memory, {cpu_percent:.1f}% CPU"
            
            self.component_health["system_resources"] = status
            self._add_health_check("system_resources", status, message, {
                "memory_percent": memory_percent,
                "cpu_percent": cpu_percent
            })
            
        except ImportError:
            # psutil not available, skip resource check
            status = EngagementHealthStatus.UNKNOWN
            message = "System resource monitoring not available (psutil not installed)"
            self.component_health["system_resources"] = status
            self._add_health_check("system_resources", status, message)
            
        except Exception as e:
            status = EngagementHealthStatus.CRITICAL
            message = f"Failed to check system resource health: {e}"
            self.component_health["system_resources"] = status
            self._add_health_check("system_resources", status, message)
    
    def _add_health_check(self, name: str, status: EngagementHealthStatus,
                         message: str, details: Dict[str, Any] = None):
        """Add a health check result."""
        health_check = EngagementHealthCheck(name, status, message, details)
        self.health_checks.append(health_check)
    
    def _calculate_overall_health(self):
        """Calculate overall health status and score."""
        if not self.health_checks:
            self.current_health_status = EngagementHealthStatus.UNKNOWN
            self.health_score = 0.0
            return
        
        # Calculate weighted health score
        status_weights = {
            EngagementHealthStatus.HEALTHY: 1.0,
            EngagementHealthStatus.DEGRADED: 0.7,
            EngagementHealthStatus.UNHEALTHY: 0.3,
            EngagementHealthStatus.CRITICAL: 0.0,
            EngagementHealthStatus.UNKNOWN: 0.5
        }
        
        # Component weights (more important components have higher weight)
        component_weights = {
            "metrics_collector": 0.4,
            "prometheus_integration": 0.3,
            "engagement_activity": 0.2,
            "system_resources": 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for check in self.health_checks:
            weight = component_weights.get(check.name, 0.1)
            score = status_weights.get(check.status, 0.0)
            total_score += score * weight
            total_weight += weight
        
        self.health_score = total_score / max(total_weight, 1.0)
        
        # Determine overall status
        if self.health_score >= 0.9:
            self.current_health_status = EngagementHealthStatus.HEALTHY
        elif self.health_score >= 0.7:
            self.current_health_status = EngagementHealthStatus.DEGRADED
        elif self.health_score >= 0.3:
            self.current_health_status = EngagementHealthStatus.UNHEALTHY
        else:
            self.current_health_status = EngagementHealthStatus.CRITICAL
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        return {
            "overall_status": self.current_health_status.value,
            "health_score": self.health_score,
            "last_check": self.last_health_check.isoformat(),
            "component_health": {
                name: status.value for name, status in self.component_health.items()
            },
            "health_checks": [check.to_dict() for check in self.health_checks],
            "health_trend": self._calculate_health_trend()
        }
    
    def _calculate_health_trend(self) -> str:
        """Calculate health trend based on recent history."""
        if len(self.health_history) < 2:
            return "stable"
        
        recent_scores = [score for _, score in self.health_history[-5:]]
        
        if len(recent_scores) < 2:
            return "stable"
        
        # Calculate trend
        first_half = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
        second_half = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
        
        diff = second_half - first_half
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "degrading"
        else:
            return "stable"
    
    async def inject_into_observatory_health(self, observatory_health: Dict[str, Any]):
        """Inject engagement health data into Observatory's health endpoint."""
        try:
            engagement_health = self.get_health_summary()
            
            # Add engagement section to Observatory health
            observatory_health["engagement"] = {
                "status": engagement_health["overall_status"],
                "health_score": engagement_health["health_score"],
                "last_check": engagement_health["last_check"],
                "components": engagement_health["component_health"],
                "trend": engagement_health["health_trend"]
            }
            
            # Add engagement metrics to overall health calculation
            if "health_score" in observatory_health:
                # Weight engagement health into overall score (20% weight)
                overall_score = observatory_health["health_score"]
                engagement_weight = 0.2
                observatory_weight = 0.8
                
                combined_score = (overall_score * observatory_weight + 
                                self.health_score * engagement_weight)
                observatory_health["health_score"] = combined_score
            
            logger.debug("🏥 Injected engagement health into Observatory health")
            
        except Exception as e:
            logger.error(f"Failed to inject engagement health: {e}")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get health monitor capabilities."""
        return [
            "comprehensive_health_monitoring",
            "component_health_tracking",
            "health_score_calculation",
            "health_trend_analysis",
            "observatory_health_integration",
            "automated_health_checks"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health monitor status."""
        return {
            "status": "healthy" if self.running else "stopped",
            "monitoring_running": self.running,
            "last_health_check": self.last_health_check.isoformat(),
            "current_health_status": self.current_health_status.value,
            "health_score": self.health_score,
            "health_checks_performed": len(self.health_checks),
            "health_history_points": len(self.health_history)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get health monitor module information."""
        return {
            "module_id": self.module_id,
            "name": "Engagement Health Monitor",
            "version": "1.0.0",
            "description": "Monitors engagement system health and integrates with Observatory health monitoring"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Engagement Health Monitor entering degradation mode due to: {error}")
            
            # Increase health check interval to reduce load
            self.health_check_interval = min(self.health_check_interval * 2, 300)  # Max 5 minutes
            
            # Mark system as degraded
            self.current_health_status = EngagementHealthStatus.DEGRADED
            self.health_score = 0.5
            
            logger.info(f"Degradation applied: increased health check interval to {self.health_check_interval}s")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False


# Helper functions for Observatory integration

async def create_engagement_health_monitor(
    metrics_collector: EngagementMetricsCollector,
    prometheus_integration: EngagementPrometheusIntegration
) -> EngagementHealthMonitor:
    """Create and initialize engagement health monitor."""
    monitor = EngagementHealthMonitor(metrics_collector, prometheus_integration)
    await monitor.initialize()
    return monitor


async def inject_engagement_health_into_observatory(
    health_monitor: EngagementHealthMonitor,
    observatory_health: Dict[str, Any]
) -> None:
    """Inject engagement health into Observatory's health endpoint."""
    await health_monitor.inject_into_observatory_health(observatory_health)
"""
Health monitoring and alerting system for GitHub synchronization.

This module provides comprehensive health checks, status reporting,
and alerting capabilities for the GitHub sync system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from .monitoring import MetricsCollector, PerformanceMonitor
from .client import GitHubAPIClient
from .auth import AuthenticationManager

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheck]
    uptime_seconds: float
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'overall_status': self.overall_status.value,
            'timestamp': self.timestamp.isoformat(),
            'uptime_seconds': self.uptime_seconds,
            'version': self.version,
            'checks': [
                {
                    'name': check.name,
                    'status': check.status.value,
                    'message': check.message,
                    'timestamp': check.timestamp.isoformat(),
                    'details': check.details,
                    'duration_ms': check.duration_ms
                }
                for check in self.checks
            ]
        }


class HealthMonitor:
    """
    Comprehensive health monitoring system.
    
    This class performs various health checks and provides
    system status reporting and alerting capabilities.
    """
    
    def __init__(self, api_client: GitHubAPIClient, auth_manager: AuthenticationManager,
                 metrics_collector: MetricsCollector):
        """
        Initialize health monitor.
        
        Args:
            api_client: GitHub API client
            auth_manager: Authentication manager
            metrics_collector: Metrics collector
        """
        self.api_client = api_client
        self.auth_manager = auth_manager
        self.metrics_collector = metrics_collector
        self.performance_monitor = PerformanceMonitor(metrics_collector)
        
        self.start_time = datetime.utcnow()
        self.last_health_check = None
        self.health_history: List[SystemHealth] = []
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[SystemHealth], None]] = []
        
        # Health check configuration
        self.check_interval = 60  # seconds
        self.history_retention = 24 * 60  # 24 hours in minutes
        
        self.logger = logging.getLogger(__name__)
    
    def add_alert_callback(self, callback: Callable[[SystemHealth], None]) -> None:
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    async def perform_health_check(self) -> SystemHealth:
        """
        Perform comprehensive health check.
        
        Returns:
            SystemHealth object with all check results
        """
        checks = []
        
        # GitHub API connectivity check
        checks.append(await self._check_github_api())
        
        # Authentication check
        checks.append(await self._check_authentication())
        
        # Rate limit check
        checks.append(await self._check_rate_limits())
        
        # Database connectivity check
        checks.append(await self._check_database())
        
        # Metrics system check
        checks.append(await self._check_metrics_system())
        
        # Performance thresholds check
        checks.append(await self._check_performance_thresholds())
        
        # Webhook health check
        checks.append(await self._check_webhook_health())
        
        # Cache system check
        checks.append(await self._check_cache_system())
        
        # Determine overall status
        overall_status = self._determine_overall_status(checks)
        
        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Create system health object
        system_health = SystemHealth(
            overall_status=overall_status,
            timestamp=datetime.utcnow(),
            checks=checks,
            uptime_seconds=uptime_seconds
        )
        
        # Store in history
        self.health_history.append(system_health)
        self._cleanup_history()
        
        # Update last check time
        self.last_health_check = datetime.utcnow()
        
        # Trigger alerts if needed
        if overall_status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            self._trigger_alerts(system_health)
        
        return system_health
    
    async def _check_github_api(self) -> HealthCheck:
        """Check GitHub API connectivity."""
        start_time = datetime.utcnow()
        
        try:
            # Simple API call to check connectivity
            rate_limit_info = await asyncio.to_thread(self.api_client.get_rate_limit_status)
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if rate_limit_info:
                return HealthCheck(
                    name="github_api_connectivity",
                    status=HealthStatus.HEALTHY,
                    message="GitHub API is accessible",
                    duration_ms=duration_ms,
                    details={
                        'rate_limit_remaining': rate_limit_info.get('remaining', 0),
                        'rate_limit_limit': rate_limit_info.get('limit', 0)
                    }
                )
            else:
                return HealthCheck(
                    name="github_api_connectivity",
                    status=HealthStatus.WARNING,
                    message="GitHub API responded but no rate limit info",
                    duration_ms=duration_ms
                )
                
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="github_api_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"GitHub API connectivity failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_authentication(self) -> HealthCheck:
        """Check GitHub authentication status."""
        start_time = datetime.utcnow()
        
        try:
            # Validate token
            is_valid = await asyncio.to_thread(self.auth_manager.validate_token)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if is_valid:
                # Get token info for additional details
                try:
                    token_info = await asyncio.to_thread(self.auth_manager.get_token_info)
                    return HealthCheck(
                        name="github_authentication",
                        status=HealthStatus.HEALTHY,
                        message="GitHub authentication is valid",
                        duration_ms=duration_ms,
                        details={
                            'user': token_info.get('user', {}).get('login', 'unknown'),
                            'scopes': token_info.get('scopes', [])
                        }
                    )
                except Exception:
                    return HealthCheck(
                        name="github_authentication",
                        status=HealthStatus.HEALTHY,
                        message="GitHub authentication is valid (limited info)",
                        duration_ms=duration_ms
                    )
            else:
                return HealthCheck(
                    name="github_authentication",
                    status=HealthStatus.CRITICAL,
                    message="GitHub authentication is invalid",
                    duration_ms=duration_ms
                )
                
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="github_authentication",
                status=HealthStatus.CRITICAL,
                message=f"Authentication check failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_rate_limits(self) -> HealthCheck:
        """Check GitHub API rate limits."""
        start_time = datetime.utcnow()
        
        try:
            rate_limit_info = await asyncio.to_thread(self.api_client.get_rate_limit_status)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if rate_limit_info:
                remaining = rate_limit_info.get('remaining', 0)
                limit = rate_limit_info.get('limit', 5000)
                usage_percent = ((limit - remaining) / limit) * 100 if limit > 0 else 0
                
                if usage_percent < 80:
                    status = HealthStatus.HEALTHY
                    message = f"Rate limit usage is healthy ({usage_percent:.1f}%)"
                elif usage_percent < 95:
                    status = HealthStatus.WARNING
                    message = f"Rate limit usage is high ({usage_percent:.1f}%)"
                else:
                    status = HealthStatus.CRITICAL
                    message = f"Rate limit usage is critical ({usage_percent:.1f}%)"
                
                return HealthCheck(
                    name="github_rate_limits",
                    status=status,
                    message=message,
                    duration_ms=duration_ms,
                    details={
                        'remaining': remaining,
                        'limit': limit,
                        'usage_percent': usage_percent,
                        'reset_time': rate_limit_info.get('reset')
                    }
                )
            else:
                return HealthCheck(
                    name="github_rate_limits",
                    status=HealthStatus.WARNING,
                    message="Could not retrieve rate limit information",
                    duration_ms=duration_ms
                )
                
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="github_rate_limits",
                status=HealthStatus.WARNING,
                message=f"Rate limit check failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_database(self) -> HealthCheck:
        """Check database connectivity and health."""
        start_time = datetime.utcnow()
        
        try:
            # Test database connection by getting metrics summary
            summary = await asyncio.to_thread(self.metrics_collector.get_metrics_summary, 1)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                name="database_connectivity",
                status=HealthStatus.HEALTHY,
                message="Database is accessible and responsive",
                duration_ms=duration_ms,
                details={
                    'recent_syncs': summary.get('sync_operations', {}).get('total', 0),
                    'recent_api_calls': summary.get('api_usage', {}).get('total_calls', 0)
                }
            )
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="database_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Database connectivity failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_metrics_system(self) -> HealthCheck:
        """Check metrics collection system health."""
        start_time = datetime.utcnow()
        
        try:
            # Check if metrics are being collected
            summary = await asyncio.to_thread(self.metrics_collector.get_metrics_summary, 1)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            recent_activity = (
                summary.get('sync_operations', {}).get('total', 0) +
                summary.get('api_usage', {}).get('total_calls', 0)
            )
            
            if recent_activity > 0:
                status = HealthStatus.HEALTHY
                message = "Metrics system is collecting data"
            else:
                status = HealthStatus.WARNING
                message = "Metrics system is running but no recent activity"
            
            return HealthCheck(
                name="metrics_system",
                status=status,
                message=message,
                duration_ms=duration_ms,
                details={
                    'recent_activity_count': recent_activity,
                    'active_syncs': summary.get('current_state', {}).get('active_syncs', 0)
                }
            )
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="metrics_system",
                status=HealthStatus.CRITICAL,
                message=f"Metrics system check failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_performance_thresholds(self) -> HealthCheck:
        """Check performance thresholds."""
        start_time = datetime.utcnow()
        
        try:
            violations = await asyncio.to_thread(self.performance_monitor.check_thresholds)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if not violations:
                return HealthCheck(
                    name="performance_thresholds",
                    status=HealthStatus.HEALTHY,
                    message="All performance thresholds are within limits",
                    duration_ms=duration_ms
                )
            
            critical_violations = [v for v in violations if v['metric'] in ['sync_failure_rate', 'api_error_rate']]
            
            if critical_violations:
                status = HealthStatus.CRITICAL
                message = f"Critical performance thresholds exceeded: {len(critical_violations)} violations"
            else:
                status = HealthStatus.WARNING
                message = f"Performance thresholds exceeded: {len(violations)} violations"
            
            return HealthCheck(
                name="performance_thresholds",
                status=status,
                message=message,
                duration_ms=duration_ms,
                details={
                    'violations': violations,
                    'violation_count': len(violations),
                    'critical_violations': len(critical_violations)
                }
            )
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="performance_thresholds",
                status=HealthStatus.WARNING,
                message=f"Performance threshold check failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_webhook_health(self) -> HealthCheck:
        """Check webhook system health."""
        start_time = datetime.utcnow()
        
        try:
            # This is a placeholder - in a real implementation, you'd check:
            # - Webhook endpoint accessibility
            # - Recent webhook deliveries
            # - Webhook processing queue health
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                name="webhook_system",
                status=HealthStatus.HEALTHY,
                message="Webhook system is operational",
                duration_ms=duration_ms,
                details={
                    'note': 'Webhook health check is a placeholder implementation'
                }
            )
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="webhook_system",
                status=HealthStatus.WARNING,
                message=f"Webhook health check failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    async def _check_cache_system(self) -> HealthCheck:
        """Check cache system health."""
        start_time = datetime.utcnow()
        
        try:
            # This is a placeholder - in a real implementation, you'd check:
            # - Cache hit rates
            # - Cache size and memory usage
            # - Cache eviction rates
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                name="cache_system",
                status=HealthStatus.HEALTHY,
                message="Cache system is operational",
                duration_ms=duration_ms,
                details={
                    'note': 'Cache health check is a placeholder implementation'
                }
            )
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthCheck(
                name="cache_system",
                status=HealthStatus.WARNING,
                message=f"Cache health check failed: {str(e)}",
                duration_ms=duration_ms,
                details={'error': str(e)}
            )
    
    def _determine_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Determine overall system status from individual checks."""
        if any(check.status == HealthStatus.CRITICAL for check in checks):
            return HealthStatus.CRITICAL
        elif any(check.status == HealthStatus.WARNING for check in checks):
            return HealthStatus.WARNING
        elif all(check.status == HealthStatus.HEALTHY for check in checks):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def _cleanup_history(self) -> None:
        """Clean up old health check history."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.history_retention)
        self.health_history = [
            health for health in self.health_history 
            if health.timestamp >= cutoff_time
        ]
    
    def _trigger_alerts(self, system_health: SystemHealth) -> None:
        """Trigger alert callbacks for unhealthy status."""
        for callback in self.alert_callbacks:
            try:
                callback(system_health)
            except Exception as e:
                self.logger.error(f"Health alert callback failed: {e}")
    
    def get_health_history(self, hours: int = 24) -> List[SystemHealth]:
        """
        Get health check history for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of SystemHealth objects
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            health for health in self.health_history 
            if health.timestamp >= cutoff_time
        ]
    
    def get_current_status(self) -> SystemHealth:
        """Get the most recent health status."""
        if self.health_history:
            return self.health_history[-1]
        else:
            # Return unknown status if no checks have been performed
            return SystemHealth(
                overall_status=HealthStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                checks=[],
                uptime_seconds=(datetime.utcnow() - self.start_time).total_seconds()
            )
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        self.logger.info("Starting health monitoring")
        
        while True:
            try:
                await self.perform_health_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval)


# Default alert callbacks
def log_health_alert(system_health: SystemHealth) -> None:
    """Default health alert callback that logs alerts."""
    failed_checks = [
        check for check in system_health.checks 
        if check.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]
    ]
    
    logger.warning(
        f"HEALTH ALERT: System status is {system_health.overall_status.value}",
        extra={
            'overall_status': system_health.overall_status.value,
            'failed_checks': [check.name for check in failed_checks],
            'timestamp': system_health.timestamp.isoformat()
        }
    )


def json_health_alert(system_health: SystemHealth) -> None:
    """Health alert callback that outputs JSON for external monitoring."""
    alert_data = {
        'alert_type': 'health_status',
        'severity': system_health.overall_status.value,
        'timestamp': system_health.timestamp.isoformat(),
        'system_health': system_health.to_dict()
    }
    
    print(json.dumps(alert_data))  # Output to stdout for external monitoring
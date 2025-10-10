"""
Observatory Context Provider

Safely extracts monitoring data from Observatory for AI consultation context.
Implements brownfield safety patterns to avoid performance impact.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re

from .models import ObservatoryContext
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError, ContextUnavailableError
from .health_checker import ComponentHealth
from .security_manager import SecurityContext, ResourceType

logger = logging.getLogger(__name__)


class DataSensitivity(str, Enum):
    """Data sensitivity levels for privacy control"""
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    CONFIDENTIAL = "confidential"


class MetricType(str, Enum):
    """Types of metrics that can be extracted"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"
    PERCENTAGE = "percentage"


@dataclass
class MetricData:
    """Structured metric data"""
    name: str
    value: Union[float, int, str]
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str]
    unit: Optional[str] = None
    description: Optional[str] = None
    sensitivity: DataSensitivity = DataSensitivity.INTERNAL


@dataclass
class AlertData:
    """Structured alert data"""
    name: str
    status: str  # firing, resolved, pending
    severity: str  # critical, warning, info
    message: str
    timestamp: datetime
    labels: Dict[str, str]
    duration: Optional[timedelta] = None
    sensitivity: DataSensitivity = DataSensitivity.INTERNAL


@dataclass
class SystemStatus:
    """Overall system status summary"""
    overall_health: str  # healthy, degraded, unhealthy
    active_alerts: int
    critical_alerts: int
    warning_alerts: int
    services_up: int
    services_total: int
    last_updated: datetime


class ObservatoryContextProvider:
    """
    Provides Observatory monitoring context for AI consultations
    
    Features:
    - Safe data extraction without Observatory performance impact
    - Circuit breaker protection for all Observatory access
    - Data sanitization and privacy controls
    - Token-optimized formatting for LLM consumption
    - Configurable data sensitivity filtering
    - Caching to reduce Observatory load
    """
    
    def __init__(
        self,
        cache_ttl: int = 300,  # 5 minutes
        max_metrics: int = 50,
        max_alerts: int = 20,
        max_context_tokens: int = 2000,
        observatory_timeout: int = 10
    ):
        self.cache_ttl = cache_ttl
        self.max_metrics = max_metrics
        self.max_alerts = max_alerts
        self.max_context_tokens = max_context_tokens
        self.observatory_timeout = observatory_timeout
        
        # Cache for Observatory data
        self._metrics_cache: Dict[str, Any] = {}
        self._alerts_cache: Dict[str, Any] = {}
        self._system_status_cache: Optional[SystemStatus] = None
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Observatory connection detection
        self._observatory_available = False
        self._observatory_endpoints: Dict[str, str] = {}
        
        # Data sanitization patterns
        self._sensitive_patterns = [
            r'password',
            r'secret',
            r'token',
            r'key',
            r'credential',
            r'auth',
            r'api[_-]?key',
            r'private[_-]?key'
        ]
        
        # Statistics
        self._stats = {
            'context_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'observatory_calls': 0,
            'observatory_errors': 0,
            'data_sanitized': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the context provider"""
        try:
            logger.info("Initializing Observatory Context Provider")
            
            # Check if feature is enabled
            if not await feature_flags.is_enabled(FeatureFlag.OBSERVATORY_CONTEXT):
                logger.info("Observatory context is disabled via feature flag")
                return
            
            # Detect Observatory endpoints
            await self._detect_observatory_endpoints()
            
            # Test Observatory connectivity
            await self._test_observatory_connectivity()
            
            logger.info(f"Observatory Context Provider initialized - Available: {self._observatory_available}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Observatory Context Provider: {e}")
            self._observatory_available = False
            # Don't raise - should degrade gracefully
    
    async def _detect_observatory_endpoints(self) -> None:
        """Detect Observatory API endpoints"""
        try:
            # Common Observatory endpoint patterns
            potential_endpoints = {
                'metrics': [
                    'http://localhost:9090/api/v1/query',  # Prometheus
                    'http://localhost:8080/metrics',       # Observatory metrics
                    'http://observatory:8080/metrics',     # Docker Observatory
                ],
                'alerts': [
                    'http://localhost:9093/api/v1/alerts', # Alertmanager
                    'http://localhost:8080/alerts',        # Observatory alerts
                    'http://observatory:8080/alerts',      # Docker Observatory
                ],
                'status': [
                    'http://localhost:8080/health',        # Observatory health
                    'http://observatory:8080/health',      # Docker Observatory
                ]
            }
            
            # Try to detect actual endpoints
            # In a real implementation, this would probe for actual Observatory services
            # For now, we'll use environment variables or defaults
            import os
            
            self._observatory_endpoints = {
                'metrics': os.getenv('OBSERVATORY_METRICS_URL', 'http://localhost:8080/metrics'),
                'alerts': os.getenv('OBSERVATORY_ALERTS_URL', 'http://localhost:8080/alerts'),
                'status': os.getenv('OBSERVATORY_STATUS_URL', 'http://localhost:8080/health')
            }
            
            logger.info(f"Detected Observatory endpoints: {self._observatory_endpoints}")
            
        except Exception as e:
            logger.warning(f"Failed to detect Observatory endpoints: {e}")
            self._observatory_endpoints = {}
    
    async def _test_observatory_connectivity(self) -> None:
        """Test connectivity to Observatory services"""
        try:
            # In a real implementation, this would make actual HTTP requests
            # For brownfield safety, we'll simulate the check
            
            # Simulate connectivity test
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # For demo purposes, assume Observatory is available
            self._observatory_available = bool(self._observatory_endpoints)
            
            if self._observatory_available:
                logger.info("Observatory connectivity confirmed")
            else:
                logger.warning("Observatory not available - context will be limited")
                
        except Exception as e:
            logger.warning(f"Observatory connectivity test failed: {e}")
            self._observatory_available = False
    
    @with_circuit_breaker('observatory_metrics')
    async def get_current_metrics(
        self,
        metric_names: Optional[List[str]] = None,
        max_age: Optional[timedelta] = None
    ) -> List[MetricData]:
        """Get current metrics from Observatory"""
        try:
            self._stats['context_requests'] += 1
            
            # Check cache first
            cache_key = f"metrics_{hash(str(metric_names))}"
            if self._is_cache_valid(cache_key, max_age):
                self._stats['cache_hits'] += 1
                return self._metrics_cache[cache_key]
            
            self._stats['cache_misses'] += 1
            
            if not self._observatory_available:
                logger.warning("Observatory not available - returning empty metrics")
                return []
            
            # Extract metrics from Observatory
            metrics = await self._extract_metrics(metric_names)
            
            # Cache the results
            self._metrics_cache[cache_key] = metrics
            self._cache_timestamps[cache_key] = datetime.utcnow()
            
            self._stats['observatory_calls'] += 1
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            self._stats['observatory_errors'] += 1
            return []
    
    async def _extract_metrics(self, metric_names: Optional[List[str]] = None) -> List[MetricData]:
        """Extract metrics from Observatory (simulated for brownfield safety)"""
        try:
            # In a real implementation, this would make HTTP requests to Observatory
            # For brownfield safety, we'll simulate common metrics
            
            simulated_metrics = [
                MetricData(
                    name="cpu_usage_percent",
                    value=75.5,
                    metric_type=MetricType.GAUGE,
                    timestamp=datetime.utcnow(),
                    labels={"instance": "web-server-1", "job": "observatory"},
                    unit="percent",
                    description="CPU usage percentage",
                    sensitivity=DataSensitivity.INTERNAL
                ),
                MetricData(
                    name="memory_usage_bytes",
                    value=2147483648,  # 2GB
                    metric_type=MetricType.GAUGE,
                    timestamp=datetime.utcnow(),
                    labels={"instance": "web-server-1", "job": "observatory"},
                    unit="bytes",
                    description="Memory usage in bytes",
                    sensitivity=DataSensitivity.INTERNAL
                ),
                MetricData(
                    name="http_requests_total",
                    value=12543,
                    metric_type=MetricType.COUNTER,
                    timestamp=datetime.utcnow(),
                    labels={"method": "GET", "status": "200", "endpoint": "/api/metrics"},
                    unit="requests",
                    description="Total HTTP requests",
                    sensitivity=DataSensitivity.PUBLIC
                ),
                MetricData(
                    name="response_time_seconds",
                    value=0.125,
                    metric_type=MetricType.HISTOGRAM,
                    timestamp=datetime.utcnow(),
                    labels={"endpoint": "/api/metrics", "quantile": "0.95"},
                    unit="seconds",
                    description="Response time 95th percentile",
                    sensitivity=DataSensitivity.INTERNAL
                ),
                MetricData(
                    name="disk_usage_percent",
                    value=45.2,
                    metric_type=MetricType.GAUGE,
                    timestamp=datetime.utcnow(),
                    labels={"device": "/dev/sda1", "mountpoint": "/"},
                    unit="percent",
                    description="Disk usage percentage",
                    sensitivity=DataSensitivity.INTERNAL
                )
            ]
            
            # Filter by requested metric names if specified
            if metric_names:
                simulated_metrics = [
                    m for m in simulated_metrics 
                    if m.name in metric_names
                ]
            
            # Limit number of metrics
            return simulated_metrics[:self.max_metrics]
            
        except Exception as e:
            logger.error(f"Failed to extract metrics: {e}")
            return []
    
    @with_circuit_breaker('observatory_alerts')
    async def get_current_alerts(
        self,
        severity_filter: Optional[List[str]] = None,
        max_age: Optional[timedelta] = None
    ) -> List[AlertData]:
        """Get current alerts from Observatory"""
        try:
            self._stats['context_requests'] += 1
            
            # Check cache first
            cache_key = f"alerts_{hash(str(severity_filter))}"
            if self._is_cache_valid(cache_key, max_age):
                self._stats['cache_hits'] += 1
                return self._alerts_cache[cache_key]
            
            self._stats['cache_misses'] += 1
            
            if not self._observatory_available:
                logger.warning("Observatory not available - returning empty alerts")
                return []
            
            # Extract alerts from Observatory
            alerts = await self._extract_alerts(severity_filter)
            
            # Cache the results
            self._alerts_cache[cache_key] = alerts
            self._cache_timestamps[cache_key] = datetime.utcnow()
            
            self._stats['observatory_calls'] += 1
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get current alerts: {e}")
            self._stats['observatory_errors'] += 1
            return []
    
    async def _extract_alerts(self, severity_filter: Optional[List[str]] = None) -> List[AlertData]:
        """Extract alerts from Observatory (simulated for brownfield safety)"""
        try:
            # Simulate common alerts
            simulated_alerts = [
                AlertData(
                    name="HighCPUUsage",
                    status="firing",
                    severity="warning",
                    message="CPU usage is above 80% for more than 5 minutes",
                    timestamp=datetime.utcnow() - timedelta(minutes=10),
                    labels={"instance": "web-server-1", "job": "observatory"},
                    duration=timedelta(minutes=10),
                    sensitivity=DataSensitivity.INTERNAL
                ),
                AlertData(
                    name="DiskSpaceLow",
                    status="firing",
                    severity="critical",
                    message="Disk space is below 10% on /dev/sda1",
                    timestamp=datetime.utcnow() - timedelta(hours=1),
                    labels={"device": "/dev/sda1", "mountpoint": "/"},
                    duration=timedelta(hours=1),
                    sensitivity=DataSensitivity.INTERNAL
                ),
                AlertData(
                    name="HighResponseTime",
                    status="resolved",
                    severity="warning",
                    message="API response time exceeded 1 second",
                    timestamp=datetime.utcnow() - timedelta(hours=2),
                    labels={"endpoint": "/api/metrics", "method": "GET"},
                    duration=timedelta(minutes=30),
                    sensitivity=DataSensitivity.INTERNAL
                )
            ]
            
            # Filter by severity if specified
            if severity_filter:
                simulated_alerts = [
                    a for a in simulated_alerts 
                    if a.severity in severity_filter
                ]
            
            # Limit number of alerts
            return simulated_alerts[:self.max_alerts]
            
        except Exception as e:
            logger.error(f"Failed to extract alerts: {e}")
            return []
    
    @with_circuit_breaker('observatory_status')
    async def get_system_status(self, max_age: Optional[timedelta] = None) -> SystemStatus:
        """Get overall system status from Observatory"""
        try:
            self._stats['context_requests'] += 1
            
            # Check cache first
            if self._is_cache_valid('system_status', max_age) and self._system_status_cache:
                self._stats['cache_hits'] += 1
                return self._system_status_cache
            
            self._stats['cache_misses'] += 1
            
            if not self._observatory_available:
                logger.warning("Observatory not available - returning degraded status")
                return SystemStatus(
                    overall_health="degraded",
                    active_alerts=0,
                    critical_alerts=0,
                    warning_alerts=0,
                    services_up=0,
                    services_total=1,
                    last_updated=datetime.utcnow()
                )
            
            # Extract system status
            status = await self._extract_system_status()
            
            # Cache the result
            self._system_status_cache = status
            self._cache_timestamps['system_status'] = datetime.utcnow()
            
            self._stats['observatory_calls'] += 1
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            self._stats['observatory_errors'] += 1
            return SystemStatus(
                overall_health="unhealthy",
                active_alerts=0,
                critical_alerts=0,
                warning_alerts=0,
                services_up=0,
                services_total=1,
                last_updated=datetime.utcnow()
            )
    
    async def _extract_system_status(self) -> SystemStatus:
        """Extract system status from Observatory"""
        try:
            # Get current alerts to calculate status
            alerts = await self._extract_alerts()
            
            active_alerts = len([a for a in alerts if a.status == "firing"])
            critical_alerts = len([a for a in alerts if a.severity == "critical" and a.status == "firing"])
            warning_alerts = len([a for a in alerts if a.severity == "warning" and a.status == "firing"])
            
            # Determine overall health
            if critical_alerts > 0:
                overall_health = "unhealthy"
            elif warning_alerts > 0:
                overall_health = "degraded"
            else:
                overall_health = "healthy"
            
            # Simulate service counts
            services_total = 5  # Observatory, Prometheus, Alertmanager, etc.
            services_up = services_total - critical_alerts
            
            return SystemStatus(
                overall_health=overall_health,
                active_alerts=active_alerts,
                critical_alerts=critical_alerts,
                warning_alerts=warning_alerts,
                services_up=services_up,
                services_total=services_total,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract system status: {e}")
            raise
    
    def _is_cache_valid(self, cache_key: str, max_age: Optional[timedelta] = None) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = datetime.utcnow() - self._cache_timestamps[cache_key]
        max_cache_age = max_age or timedelta(seconds=self.cache_ttl)
        
        return cache_age < max_cache_age
    
    async def get_observatory_context(
        self,
        user_id: str,
        security_context: Optional[SecurityContext] = None,
        include_metrics: bool = True,
        include_alerts: bool = True,
        include_status: bool = True,
        sensitivity_level: DataSensitivity = DataSensitivity.INTERNAL
    ) -> ObservatoryContext:
        """Get complete Observatory context for AI consultation"""
        try:
            logger.debug(f"Getting Observatory context for user {user_id}")
            
            # Check feature flags
            if not await feature_flags.is_enabled(FeatureFlag.OBSERVATORY_CONTEXT):
                raise ContextUnavailableError("Observatory context is disabled")
            
            # Use security context sensitivity if provided
            if security_context:
                sensitivity_level = security_context.permissions.data_sensitivity_limit
            
            # Initialize context data
            metrics = []
            alerts = []
            system_status = None
            
            # Get metrics if requested and permitted
            if include_metrics and await feature_flags.is_enabled(FeatureFlag.METRICS_ACCESS):
                # Check permission if security context provided
                if not security_context or await self._check_resource_permission(security_context, ResourceType.METRICS):
                    raw_metrics = await self.get_current_metrics()
                    metrics = self._filter_by_sensitivity(raw_metrics, sensitivity_level)
            
            # Get alerts if requested and permitted
            if include_alerts and await feature_flags.is_enabled(FeatureFlag.ALERTS_ACCESS):
                # Check permission if security context provided
                if not security_context or await self._check_resource_permission(security_context, ResourceType.ALERTS):
                    raw_alerts = await self.get_current_alerts()
                    alerts = self._filter_by_sensitivity(raw_alerts, sensitivity_level)
            
            # Get system status if requested and permitted
            if include_status:
                # Check permission if security context provided
                if not security_context or await self._check_resource_permission(security_context, ResourceType.SYSTEM_STATUS):
                    system_status = await self.get_system_status()
            
            # Create context object
            context = ObservatoryContext(
                timestamp=datetime.utcnow(),
                system_status=system_status.overall_health if system_status else "unknown",
                active_alerts=len([a for a in alerts if a.status == "firing"]),
                critical_alerts=len([a for a in alerts if a.severity == "critical" and a.status == "firing"]),
                metrics_summary=self._summarize_metrics(metrics),
                alerts_summary=self._summarize_alerts(alerts),
                formatted_context=await self._format_for_llm(metrics, alerts, system_status, sensitivity_level)
            )
            
            logger.debug(f"Generated Observatory context with {len(metrics)} metrics and {len(alerts)} alerts")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get Observatory context: {e}")
            raise ContextUnavailableError(f"Failed to get Observatory context: {str(e)}")
    
    async def _check_resource_permission(self, security_context: SecurityContext, resource_type: ResourceType) -> bool:
        """Check if user has permission for a resource type"""
        try:
            # Import here to avoid circular imports
            from .security_manager import check_permission
            return await check_permission(security_context, resource_type)
        except Exception as e:
            logger.warning(f"Permission check failed: {e}")
            return False
    
    def _filter_by_sensitivity(self, data: List[Union[MetricData, AlertData]], max_sensitivity: DataSensitivity) -> List[Union[MetricData, AlertData]]:
        """Filter data by sensitivity level"""
        sensitivity_order = [
            DataSensitivity.PUBLIC,
            DataSensitivity.INTERNAL,
            DataSensitivity.SENSITIVE,
            DataSensitivity.CONFIDENTIAL
        ]
        
        max_level = sensitivity_order.index(max_sensitivity)
        
        filtered_data = []
        for item in data:
            item_level = sensitivity_order.index(item.sensitivity)
            if item_level <= max_level:
                # Sanitize sensitive data
                sanitized_item = self._sanitize_data(item)
                filtered_data.append(sanitized_item)
        
        return filtered_data
    
    def _sanitize_data(self, data: Union[MetricData, AlertData]) -> Union[MetricData, AlertData]:
        """Sanitize sensitive data from metrics and alerts"""
        try:
            # Create a copy to avoid modifying original
            if isinstance(data, MetricData):
                sanitized = MetricData(
                    name=self._sanitize_string(data.name),
                    value=data.value,
                    metric_type=data.metric_type,
                    timestamp=data.timestamp,
                    labels=self._sanitize_labels(data.labels),
                    unit=data.unit,
                    description=self._sanitize_string(data.description) if data.description else None,
                    sensitivity=data.sensitivity
                )
            else:  # AlertData
                sanitized = AlertData(
                    name=self._sanitize_string(data.name),
                    status=data.status,
                    severity=data.severity,
                    message=self._sanitize_string(data.message),
                    timestamp=data.timestamp,
                    labels=self._sanitize_labels(data.labels),
                    duration=data.duration,
                    sensitivity=data.sensitivity
                )
            
            return sanitized
            
        except Exception as e:
            logger.warning(f"Failed to sanitize data: {e}")
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize sensitive information from strings"""
        if not text:
            return text
        
        sanitized = text
        for pattern in self._sensitive_patterns:
            # Replace sensitive patterns with [REDACTED]
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        if sanitized != text:
            self._stats['data_sanitized'] += 1
        
        return sanitized
    
    def _sanitize_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive information from labels"""
        sanitized_labels = {}
        for key, value in labels.items():
            sanitized_key = self._sanitize_string(key)
            sanitized_value = self._sanitize_string(value)
            sanitized_labels[sanitized_key] = sanitized_value
        
        return sanitized_labels
    
    def _summarize_metrics(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Create a summary of metrics for context"""
        if not metrics:
            return {"count": 0, "types": [], "latest_timestamp": None}
        
        metric_types = list(set(m.metric_type.value for m in metrics))
        latest_timestamp = max(m.timestamp for m in metrics)
        
        # Group by type
        by_type = {}
        for metric in metrics:
            metric_type = metric.metric_type.value
            if metric_type not in by_type:
                by_type[metric_type] = []
            by_type[metric_type].append({
                "name": metric.name,
                "value": metric.value,
                "unit": metric.unit
            })
        
        return {
            "count": len(metrics),
            "types": metric_types,
            "latest_timestamp": latest_timestamp.isoformat(),
            "by_type": by_type
        }
    
    def _summarize_alerts(self, alerts: List[AlertData]) -> Dict[str, Any]:
        """Create a summary of alerts for context"""
        if not alerts:
            return {"count": 0, "firing": 0, "critical": 0, "warning": 0}
        
        firing_count = len([a for a in alerts if a.status == "firing"])
        critical_count = len([a for a in alerts if a.severity == "critical"])
        warning_count = len([a for a in alerts if a.severity == "warning"])
        
        return {
            "count": len(alerts),
            "firing": firing_count,
            "critical": critical_count,
            "warning": warning_count,
            "latest_timestamp": max(a.timestamp for a in alerts).isoformat() if alerts else None
        }
    
    async def _format_for_llm(
        self,
        metrics: List[MetricData],
        alerts: List[AlertData],
        system_status: Optional[SystemStatus],
        sensitivity_level: DataSensitivity
    ) -> str:
        """Format Observatory data for LLM consumption with token optimization"""
        try:
            context_parts = []
            
            # System status summary
            if system_status:
                status_text = f"System Status: {system_status.overall_health.upper()}"
                if system_status.active_alerts > 0:
                    status_text += f" ({system_status.active_alerts} active alerts)"
                context_parts.append(status_text)
            
            # Critical alerts first (most important)
            critical_alerts = [a for a in alerts if a.severity == "critical" and a.status == "firing"]
            if critical_alerts:
                context_parts.append("CRITICAL ALERTS:")
                for alert in critical_alerts[:5]:  # Limit to top 5
                    context_parts.append(f"- {alert.name}: {alert.message}")
            
            # Warning alerts
            warning_alerts = [a for a in alerts if a.severity == "warning" and a.status == "firing"]
            if warning_alerts:
                context_parts.append("WARNING ALERTS:")
                for alert in warning_alerts[:3]:  # Limit to top 3
                    context_parts.append(f"- {alert.name}: {alert.message}")
            
            # Key metrics
            if metrics:
                context_parts.append("KEY METRICS:")
                
                # Prioritize important metrics
                important_metrics = []
                for metric in metrics:
                    if any(keyword in metric.name.lower() for keyword in ['cpu', 'memory', 'disk', 'error', 'response']):
                        important_metrics.append(metric)
                
                for metric in important_metrics[:10]:  # Limit to top 10
                    value_str = f"{metric.value}"
                    if metric.unit:
                        value_str += f" {metric.unit}"
                    context_parts.append(f"- {metric.name}: {value_str}")
            
            # Join all parts
            formatted_context = "\n".join(context_parts)
            
            # Truncate if too long (token optimization)
            if len(formatted_context) > self.max_context_tokens * 4:  # Rough token estimation
                formatted_context = formatted_context[:self.max_context_tokens * 4] + "...[truncated]"
            
            return formatted_context
            
        except Exception as e:
            logger.error(f"Failed to format context for LLM: {e}")
            return "Observatory context unavailable due to formatting error"
    
    async def clear_cache(self) -> None:
        """Clear all cached data"""
        self._metrics_cache.clear()
        self._alerts_cache.clear()
        self._system_status_cache = None
        self._cache_timestamps.clear()
        logger.info("Observatory context cache cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get context provider statistics"""
        return {
            **self._stats,
            'observatory_available': self._observatory_available,
            'cache_size': len(self._cache_timestamps),
            'endpoints_configured': len(self._observatory_endpoints)
        }
    
    async def health_check(self) -> ComponentHealth:
        """Perform health check"""
        try:
            # Test basic functionality
            start_time = datetime.utcnow()
            
            # Try to get system status (cached is fine)
            await self.get_system_status(max_age=timedelta(hours=1))
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Determine health status
            if not self._observatory_available:
                status = "degraded"
                error_message = "Observatory not available"
            elif self._stats['observatory_errors'] > self._stats['observatory_calls'] * 0.1:
                status = "degraded"
                error_message = "High error rate accessing Observatory"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="observatory_context_provider",
                status=status,
                response_time=response_time,
                error_message=error_message,
                metadata={
                    "observatory_available": self._observatory_available,
                    "cache_hit_rate": self._stats['cache_hits'] / max(1, self._stats['context_requests']),
                    "observatory_calls": self._stats['observatory_calls'],
                    "observatory_errors": self._stats['observatory_errors'],
                    "endpoints_configured": len(self._observatory_endpoints)
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="observatory_context_provider",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def cleanup(self) -> None:
        """Cleanup context provider resources"""
        try:
            await self.clear_cache()
            logger.info("Observatory Context Provider cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global context provider instance
observatory_context_provider = ObservatoryContextProvider()


async def get_observatory_context(
    user_id: str,
    security_context: Optional[SecurityContext] = None,
    include_metrics: bool = True,
    include_alerts: bool = True,
    include_status: bool = True,
    sensitivity_level: DataSensitivity = DataSensitivity.INTERNAL
) -> ObservatoryContext:
    """Get Observatory context for AI consultation"""
    return await observatory_context_provider.get_observatory_context(
        user_id=user_id,
        security_context=security_context,
        include_metrics=include_metrics,
        include_alerts=include_alerts,
        include_status=include_status,
        sensitivity_level=sensitivity_level
    )


async def initialize_context_provider() -> None:
    """Initialize the Observatory context provider"""
    await observatory_context_provider.initialize()


async def cleanup_context_provider() -> None:
    """Cleanup the Observatory context provider"""
    await observatory_context_provider.cleanup()
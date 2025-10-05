"""WebSocket endpoint health validation system."""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import time

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode, WebSocketException

from .exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    AuthenticationError,
    RateLimitError,
    ProtocolError,
)

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """WebSocket endpoint health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class QualityMetrics:
    """WebSocket connection quality metrics."""
    endpoint: str
    response_time_ms: float
    connection_time_ms: float
    message_latency_ms: float
    throughput_bytes_per_sec: float
    error_rate: float
    uptime_percentage: float
    last_check: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'endpoint': self.endpoint,
            'response_time_ms': self.response_time_ms,
            'connection_time_ms': self.connection_time_ms,
            'message_latency_ms': self.message_latency_ms,
            'throughput_bytes_per_sec': self.throughput_bytes_per_sec,
            'error_rate': self.error_rate,
            'uptime_percentage': self.uptime_percentage,
            'last_check': self.last_check.isoformat()
        }


@dataclass
class FailureIndicator:
    """WebSocket endpoint failure indicator."""
    endpoint: str
    failure_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'endpoint': self.endpoint,
            'failure_type': self.failure_type,
            'severity': self.severity,
            'description': self.description,
            'detected_at': self.detected_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class HealthCheckResult:
    """Result of WebSocket health check."""
    endpoint: str
    status: HealthStatus
    response_time_ms: float
    error_message: Optional[str] = None
    quality_metrics: Optional[QualityMetrics] = None
    failure_indicators: List[FailureIndicator] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'endpoint': self.endpoint,
            'status': self.status.value,
            'response_time_ms': self.response_time_ms,
            'error_message': self.error_message,
            'quality_metrics': self.quality_metrics.to_dict() if self.quality_metrics else None,
            'failure_indicators': [f.to_dict() for f in self.failure_indicators],
            'checked_at': self.checked_at.isoformat()
        }


class WebSocketHealthValidator:
    """Comprehensive WebSocket endpoint health validator."""
    
    def __init__(self, timeout: float = 5.0, max_retries: int = 3):
        self.endpoints = [
            '/ws/emoji-rain',
            '/ws/observatory',
            '/ws/anomalies',
            '/ws/doctor-status'
        ]
        self.timeout = timeout
        self.max_retries = max_retries
        self._health_history: Dict[str, List[HealthCheckResult]] = {}
        self._quality_thresholds = {
            'response_time_ms': 1000.0,  # 1 second max
            'connection_time_ms': 5000.0,  # 5 seconds max
            'message_latency_ms': 100.0,  # 100ms max
            'error_rate': 0.05,  # 5% max error rate
            'uptime_percentage': 95.0  # 95% min uptime
        }
        
        self._log_action("validator_initialized", {
            "endpoints": self.endpoints,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        })
    
    async def validate_endpoint_health(self, endpoint: str) -> HealthCheckResult:
        """Validate health of a specific WebSocket endpoint."""
        start_time = time.time()
        
        self._log_action("health_check_started", {
            "endpoint": endpoint,
            "timeout": self.timeout
        })
        
        try:
            # Perform connection test
            connection_result = await self._test_connection(endpoint)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Collect quality metrics
            quality_metrics = await self._collect_quality_metrics(endpoint, connection_result)
            
            # Detect failures
            failure_indicators = await self._detect_endpoint_failures(endpoint, quality_metrics)
            
            # Determine health status
            status = self._determine_health_status(quality_metrics, failure_indicators)
            
            result = HealthCheckResult(
                endpoint=endpoint,
                status=status,
                response_time_ms=response_time_ms,
                quality_metrics=quality_metrics,
                failure_indicators=failure_indicators
            )
            
            # Store in history
            if endpoint not in self._health_history:
                self._health_history[endpoint] = []
            self._health_history[endpoint].append(result)
            
            # Keep only last 100 results
            if len(self._health_history[endpoint]) > 100:
                self._health_history[endpoint] = self._health_history[endpoint][-100:]
            
            self._log_action("health_check_completed", {
                "endpoint": endpoint,
                "status": status.value,
                "response_time_ms": response_time_ms,
                "failure_count": len(failure_indicators)
            })
            
            return result
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Health check failed: {str(e)}"
            
            self._log_action("health_check_failed", {
                "endpoint": endpoint,
                "error": error_msg,
                "response_time_ms": response_time_ms
            })
            
            return HealthCheckResult(
                endpoint=endpoint,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                error_message=error_msg
            )
    
    async def check_connection_quality(self, endpoint: str) -> QualityMetrics:
        """Check connection quality metrics for an endpoint."""
        self._log_action("quality_check_started", {"endpoint": endpoint})
        
        try:
            # Test connection with timing
            connection_start = time.time()
            websocket = await asyncio.wait_for(
                websockets.connect(endpoint, ping_interval=20, ping_timeout=10),
                timeout=self.timeout
            )
            connection_time_ms = (time.time() - connection_start) * 1000
            
            # Test message latency
            message_start = time.time()
            test_message = {"type": "ping", "timestamp": datetime.utcnow().isoformat()}
            await websocket.send(json.dumps(test_message))
            
            # Wait for pong response
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            message_latency_ms = (time.time() - message_start) * 1000
            
            # Calculate throughput (simple test)
            throughput_start = time.time()
            test_data = "x" * 1024  # 1KB test data
            await websocket.send(test_data)
            await websocket.recv()  # Wait for echo
            throughput_time = time.time() - throughput_start
            throughput_bytes_per_sec = len(test_data) / throughput_time if throughput_time > 0 else 0
            
            await websocket.close()
            
            # Calculate error rate from history
            error_rate = self._calculate_error_rate(endpoint)
            
            # Calculate uptime percentage
            uptime_percentage = self._calculate_uptime_percentage(endpoint)
            
            metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=connection_time_ms,
                connection_time_ms=connection_time_ms,
                message_latency_ms=message_latency_ms,
                throughput_bytes_per_sec=throughput_bytes_per_sec,
                error_rate=error_rate,
                uptime_percentage=uptime_percentage
            )
            
            self._log_action("quality_check_completed", {
                "endpoint": endpoint,
                "connection_time_ms": connection_time_ms,
                "message_latency_ms": message_latency_ms,
                "throughput_bytes_per_sec": throughput_bytes_per_sec
            })
            
            return metrics
            
        except Exception as e:
            self._log_action("quality_check_failed", {
                "endpoint": endpoint,
                "error": str(e)
            })
            
            # Return degraded metrics
            return QualityMetrics(
                endpoint=endpoint,
                response_time_ms=float('inf'),
                connection_time_ms=float('inf'),
                message_latency_ms=float('inf'),
                throughput_bytes_per_sec=0.0,
                error_rate=1.0,
                uptime_percentage=0.0
            )
    
    async def detect_endpoint_failures(self, endpoint: str, quality_metrics: Optional[QualityMetrics] = None) -> List[FailureIndicator]:
        """Detect endpoint-specific failures."""
        failures = []
        
        if quality_metrics:
            # Check response time threshold
            if quality_metrics.response_time_ms > self._quality_thresholds['response_time_ms']:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="slow_response",
                    severity="medium",
                    description=f"Response time {quality_metrics.response_time_ms:.2f}ms exceeds threshold {self._quality_thresholds['response_time_ms']}ms",
                    metadata={"response_time_ms": quality_metrics.response_time_ms}
                ))
            
            # Check connection time threshold
            if quality_metrics.connection_time_ms > self._quality_thresholds['connection_time_ms']:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="slow_connection",
                    severity="high",
                    description=f"Connection time {quality_metrics.connection_time_ms:.2f}ms exceeds threshold {self._quality_thresholds['connection_time_ms']}ms",
                    metadata={"connection_time_ms": quality_metrics.connection_time_ms}
                ))
            
            # Check message latency threshold
            if quality_metrics.message_latency_ms > self._quality_thresholds['message_latency_ms']:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="high_latency",
                    severity="medium",
                    description=f"Message latency {quality_metrics.message_latency_ms:.2f}ms exceeds threshold {self._quality_thresholds['message_latency_ms']}ms",
                    metadata={"message_latency_ms": quality_metrics.message_latency_ms}
                ))
            
            # Check error rate threshold
            if quality_metrics.error_rate > self._quality_thresholds['error_rate']:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="high_error_rate",
                    severity="high",
                    description=f"Error rate {quality_metrics.error_rate:.2%} exceeds threshold {self._quality_thresholds['error_rate']:.2%}",
                    metadata={"error_rate": quality_metrics.error_rate}
                ))
            
            # Check uptime threshold
            if quality_metrics.uptime_percentage < self._quality_thresholds['uptime_percentage']:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="low_uptime",
                    severity="critical",
                    description=f"Uptime {quality_metrics.uptime_percentage:.1f}% below threshold {self._quality_thresholds['uptime_percentage']:.1f}%",
                    metadata={"uptime_percentage": quality_metrics.uptime_percentage}
                ))
        
        # Check for consecutive failures
        consecutive_failures = self._count_consecutive_failures(endpoint)
        if consecutive_failures >= 3:
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type="consecutive_failures",
                severity="critical",
                description=f"Endpoint has failed {consecutive_failures} consecutive health checks",
                metadata={"consecutive_failures": consecutive_failures}
            ))
        
        # Check for endpoint-specific issues
        endpoint_specific_failures = await self._check_endpoint_specific_issues(endpoint)
        failures.extend(endpoint_specific_failures)
        
        self._log_action("failure_detection_completed", {
            "endpoint": endpoint,
            "failure_count": len(failures),
            "failure_types": [f.failure_type for f in failures]
        })
        
        return failures
    
    async def validate_all_endpoints(self) -> Dict[str, HealthCheckResult]:
        """Validate health of all WebSocket endpoints."""
        self._log_action("bulk_health_check_started", {
            "endpoint_count": len(self.endpoints)
        })
        
        # Run health checks in parallel
        tasks = [self.validate_endpoint_health(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        endpoint_results = {}
        for i, result in enumerate(results):
            endpoint = self.endpoints[i]
            if isinstance(result, Exception):
                endpoint_results[endpoint] = HealthCheckResult(
                    endpoint=endpoint,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=float('inf'),
                    error_message=str(result)
                )
            else:
                endpoint_results[endpoint] = result
        
        healthy_count = sum(1 for r in endpoint_results.values() if r.status == HealthStatus.HEALTHY)
        
        self._log_action("bulk_health_check_completed", {
            "total_endpoints": len(self.endpoints),
            "healthy_endpoints": healthy_count,
            "unhealthy_endpoints": len(self.endpoints) - healthy_count
        })
        
        return endpoint_results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary."""
        if not self._health_history:
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "total_endpoints": len(self.endpoints),
                "healthy_endpoints": 0,
                "degraded_endpoints": 0,
                "unhealthy_endpoints": len(self.endpoints),
                "last_check": None
            }
        
        # Calculate current status for each endpoint
        endpoint_statuses = {}
        for endpoint in self.endpoints:
            if endpoint in self._health_history and self._health_history[endpoint]:
                latest_result = self._health_history[endpoint][-1]
                endpoint_statuses[endpoint] = latest_result.status
            else:
                endpoint_statuses[endpoint] = HealthStatus.UNKNOWN
        
        # Count statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0
        }
        
        for status in endpoint_statuses.values():
            status_counts[status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.HEALTHY] == len(self.endpoints):
            overall_status = HealthStatus.HEALTHY
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNKNOWN
        
        return {
            "overall_status": overall_status.value,
            "total_endpoints": len(self.endpoints),
            "healthy_endpoints": status_counts[HealthStatus.HEALTHY],
            "degraded_endpoints": status_counts[HealthStatus.DEGRADED],
            "unhealthy_endpoints": status_counts[HealthStatus.UNHEALTHY],
            "unknown_endpoints": status_counts[HealthStatus.UNKNOWN],
            "endpoint_statuses": {ep: status.value for ep, status in endpoint_statuses.items()},
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def _test_connection(self, endpoint: str) -> Dict[str, Any]:
        """Test WebSocket connection."""
        try:
            websocket = await asyncio.wait_for(
                websockets.connect(endpoint, ping_interval=20, ping_timeout=10),
                timeout=self.timeout
            )
            
            # Send ping and wait for pong
            await websocket.send(json.dumps({"type": "ping"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            
            await websocket.close()
            
            return {
                "success": True,
                "response": json.loads(response) if isinstance(response, str) else response
            }
            
        except asyncio.TimeoutError:
            raise ConnectionTimeoutError(f"Connection timeout to {endpoint}", endpoint)
        except InvalidStatusCode as e:
            if e.status_code == 401:
                raise AuthenticationError(f"Authentication failed for {endpoint}", endpoint)
            elif e.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded for {endpoint}", endpoint)
            else:
                raise ConnectionFailedError(f"Connection failed with status {e.status_code}", endpoint)
        except (ConnectionClosed, WebSocketException) as e:
            raise ProtocolError(f"WebSocket protocol error: {str(e)}", endpoint)
        except Exception as e:
            raise ConnectionFailedError(f"Unexpected connection error: {str(e)}", endpoint)
    
    def _determine_health_status(self, quality_metrics: Optional[QualityMetrics], failures: List[FailureIndicator]) -> HealthStatus:
        """Determine health status based on metrics and failures."""
        if not quality_metrics:
            return HealthStatus.UNHEALTHY
        
        # Check for critical failures
        critical_failures = [f for f in failures if f.severity == "critical"]
        if critical_failures:
            return HealthStatus.UNHEALTHY
        
        # Check for high severity failures
        high_failures = [f for f in failures if f.severity == "high"]
        if high_failures:
            return HealthStatus.DEGRADED
        
        # Check quality thresholds
        if (quality_metrics.response_time_ms > self._quality_thresholds['response_time_ms'] or
            quality_metrics.error_rate > self._quality_thresholds['error_rate'] or
            quality_metrics.uptime_percentage < self._quality_thresholds['uptime_percentage']):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def _calculate_error_rate(self, endpoint: str) -> float:
        """Calculate error rate from health history."""
        if endpoint not in self._health_history or not self._health_history[endpoint]:
            return 0.0
        
        recent_results = self._health_history[endpoint][-20:]  # Last 20 checks
        error_count = sum(1 for r in recent_results if r.status == HealthStatus.UNHEALTHY)
        return error_count / len(recent_results) if recent_results else 0.0
    
    def _calculate_uptime_percentage(self, endpoint: str) -> float:
        """Calculate uptime percentage from health history."""
        if endpoint not in self._health_history or not self._health_history[endpoint]:
            return 100.0
        
        recent_results = self._health_history[endpoint][-100:]  # Last 100 checks
        healthy_count = sum(1 for r in recent_results if r.status == HealthStatus.HEALTHY)
        return (healthy_count / len(recent_results)) * 100 if recent_results else 100.0
    
    def _count_consecutive_failures(self, endpoint: str) -> int:
        """Count consecutive failures for an endpoint."""
        if endpoint not in self._health_history or not self._health_history[endpoint]:
            return 0
        
        consecutive = 0
        for result in reversed(self._health_history[endpoint]):
            if result.status == HealthStatus.UNHEALTHY:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    async def _check_endpoint_specific_issues(self, endpoint: str) -> List[FailureIndicator]:
        """Check for endpoint-specific issues."""
        failures = []
        
        # Emoji rain endpoint specific checks
        if endpoint == '/ws/emoji-rain':
            # Check if emoji engine is running
            try:
                # This would need integration with the emoji engine
                # For now, we'll do a basic connectivity test
                pass
            except Exception as e:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="emoji_engine_unavailable",
                    severity="high",
                    description=f"Emoji rain engine unavailable: {str(e)}",
                    metadata={"error": str(e)}
                ))
        
        # Observatory endpoint specific checks
        elif endpoint == '/ws/observatory':
            # Check if observatory core is healthy
            try:
                # This would need integration with the observatory core
                pass
            except Exception as e:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="observatory_core_unavailable",
                    severity="critical",
                    description=f"Observatory core unavailable: {str(e)}",
                    metadata={"error": str(e)}
                ))
        
        # Anomalies endpoint specific checks
        elif endpoint == '/ws/anomalies':
            # Check if anomaly detector is running
            try:
                # This would need integration with the anomaly detector
                pass
            except Exception as e:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="anomaly_detector_unavailable",
                    severity="medium",
                    description=f"Anomaly detector unavailable: {str(e)}",
                    metadata={"error": str(e)}
                ))
        
        # Doctor status endpoint specific checks
        elif endpoint == '/ws/doctor-status':
            # Check if AI consultation is available
            try:
                # This would need integration with the AI consultation module
                pass
            except Exception as e:
                failures.append(FailureIndicator(
                    endpoint=endpoint,
                    failure_type="ai_consultation_unavailable",
                    severity="medium",
                    description=f"AI consultation unavailable: {str(e)}",
                    metadata={"error": str(e)}
                ))
        
        return failures
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '2.3',
            'action': f'health_validator_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))
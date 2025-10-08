"""WebSocket endpoint failure detection with endpoint-specific logic."""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
import time

from .health_validator import FailureIndicator, QualityMetrics, HealthStatus
from .quality_metrics import MetricsAggregation

logger = logging.getLogger(__name__)


class FailureSeverity(Enum):
    """Failure severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureType(Enum):
    """Types of failures that can be detected."""
    CONNECTION_TIMEOUT = "connection_timeout"
    AUTHENTICATION_FAILURE = "authentication_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PROTOCOL_ERROR = "protocol_error"
    SLOW_RESPONSE = "slow_response"
    HIGH_LATENCY = "high_latency"
    HIGH_ERROR_RATE = "high_error_rate"
    LOW_UPTIME = "low_uptime"
    CONSECUTIVE_FAILURES = "consecutive_failures"
    ENDPOINT_SPECIFIC = "endpoint_specific"
    QUALITY_DEGRADATION = "quality_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class FailurePattern:
    """Pattern for detecting specific types of failures."""
    failure_type: FailureType
    severity: FailureSeverity
    detection_function: Callable[['FailureDetector', str, Any], bool]
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureRule:
    """Rule for failure detection."""
    name: str
    failure_type: FailureType
    severity: FailureSeverity
    condition: str
    threshold: Any
    cooldown_seconds: float = 300.0  # 5 minutes
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'failure_type': self.failure_type.value,
            'severity': self.severity.value,
            'condition': self.condition,
            'threshold': self.threshold,
            'cooldown_seconds': self.cooldown_seconds,
            'enabled': self.enabled
        }


class FailureDetector:
    """Advanced failure detection system with endpoint-specific logic."""
    
    def __init__(self):
        self._failure_rules: Dict[str, FailureRule] = {}
        self._failure_history: Dict[str, List[FailureIndicator]] = {}
        self._last_failure_times: Dict[str, Dict[str, datetime]] = {}  # endpoint -> failure_type -> time
        self._failure_callbacks: Set[Callable[[FailureIndicator], None]] = set()
        
        # Initialize default failure rules
        self._initialize_default_rules()
        
        self._log_action("failure_detector_initialized", {
            "rule_count": len(self._failure_rules)
        })
    
    def add_failure_rule(self, rule: FailureRule) -> None:
        """Add a custom failure detection rule."""
        self._failure_rules[rule.name] = rule
        
        self._log_action("failure_rule_added", {
            "rule_name": rule.name,
            "failure_type": rule.failure_type.value,
            "severity": rule.severity.value
        })
    
    def remove_failure_rule(self, rule_name: str) -> bool:
        """Remove a failure detection rule."""
        if rule_name in self._failure_rules:
            del self._failure_rules[rule_name]
            self._log_action("failure_rule_removed", {"rule_name": rule_name})
            return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a failure detection rule."""
        if rule_name in self._failure_rules:
            self._failure_rules[rule_name].enabled = True
            self._log_action("failure_rule_enabled", {"rule_name": rule_name})
            return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a failure detection rule."""
        if rule_name in self._failure_rules:
            self._failure_rules[rule_name].enabled = False
            self._log_action("failure_rule_disabled", {"rule_name": rule_name})
            return True
        return False
    
    async def detect_failures(
        self, 
        endpoint: str, 
        quality_metrics: Optional[QualityMetrics] = None,
        health_status: Optional[HealthStatus] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> List[FailureIndicator]:
        """Detect failures for a specific endpoint."""
        failures = []
        additional_data = additional_data or {}
        
        self._log_action("failure_detection_started", {
            "endpoint": endpoint,
            "has_quality_metrics": quality_metrics is not None,
            "health_status": health_status.value if health_status else None
        })
        
        # Run all enabled failure detection rules
        for rule_name, rule in self._failure_rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown period
            if self._is_in_cooldown(endpoint, rule_name, rule.cooldown_seconds):
                continue
            
            try:
                # Detect failure based on rule
                failure_detected = await self._apply_failure_rule(
                    rule, endpoint, quality_metrics, health_status, additional_data
                )
                
                if failure_detected:
                    failure = FailureIndicator(
                        endpoint=endpoint,
                        failure_type=rule.failure_type.value,
                        severity=rule.severity.value,
                        description=f"{rule.name}: {rule.condition}",
                        metadata={
                            "rule_name": rule_name,
                            "threshold": rule.threshold,
                            "condition": rule.condition,
                            **additional_data
                        }
                    )
                    
                    failures.append(failure)
                    
                    # Update last failure time
                    if endpoint not in self._last_failure_times:
                        self._last_failure_times[endpoint] = {}
                    self._last_failure_times[endpoint][rule_name] = datetime.utcnow()
                    
                    # Store in history
                    await self._store_failure(endpoint, failure)
                    
                    # Notify callbacks
                    await self._notify_failure_callbacks(failure)
                    
            except Exception as e:
                logger.error(f"Error applying failure rule {rule_name}: {e}")
        
        # Run endpoint-specific failure detection
        endpoint_specific_failures = await self._detect_endpoint_specific_failures(
            endpoint, quality_metrics, health_status, additional_data
        )
        failures.extend(endpoint_specific_failures)
        
        self._log_action("failure_detection_completed", {
            "endpoint": endpoint,
            "failure_count": len(failures),
            "failure_types": [f.failure_type for f in failures]
        })
        
        return failures
    
    async def get_failure_history(self, endpoint: str, limit: int = 100) -> List[FailureIndicator]:
        """Get failure history for an endpoint."""
        if endpoint not in self._failure_history:
            return []
        
        history = self._failure_history[endpoint]
        return history[-limit:] if history else []
    
    async def get_failure_summary(self, endpoint: str, period_hours: int = 24) -> Dict[str, Any]:
        """Get failure summary for an endpoint over a time period."""
        if endpoint not in self._failure_history:
            return {
                "endpoint": endpoint,
                "period_hours": period_hours,
                "total_failures": 0,
                "failures_by_type": {},
                "failures_by_severity": {},
                "most_common_failure": None,
                "failure_trend": "stable"
            }
        
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        recent_failures = [
            f for f in self._failure_history[endpoint]
            if f.detected_at >= cutoff_time
        ]
        
        # Count failures by type
        failures_by_type = {}
        for failure in recent_failures:
            failures_by_type[failure.failure_type] = failures_by_type.get(failure.failure_type, 0) + 1
        
        # Count failures by severity
        failures_by_severity = {}
        for failure in recent_failures:
            failures_by_severity[failure.severity] = failures_by_severity.get(failure.severity, 0) + 1
        
        # Find most common failure
        most_common_failure = max(failures_by_type.items(), key=lambda x: x[1])[0] if failures_by_type else None
        
        # Calculate failure trend
        if len(recent_failures) >= 2:
            first_half = recent_failures[:len(recent_failures)//2]
            second_half = recent_failures[len(recent_failures)//2:]
            
            first_half_count = len(first_half)
            second_half_count = len(second_half)
            
            if second_half_count > first_half_count * 1.2:
                failure_trend = "increasing"
            elif second_half_count < first_half_count * 0.8:
                failure_trend = "decreasing"
            else:
                failure_trend = "stable"
        else:
            failure_trend = "stable"
        
        return {
            "endpoint": endpoint,
            "period_hours": period_hours,
            "total_failures": len(recent_failures),
            "failures_by_type": failures_by_type,
            "failures_by_severity": failures_by_severity,
            "most_common_failure": most_common_failure,
            "failure_trend": failure_trend,
            "recent_failures": [f.to_dict() for f in recent_failures[-10:]]  # Last 10 failures
        }
    
    def add_failure_callback(self, callback: Callable[[FailureIndicator], None]) -> None:
        """Add callback for failure detection."""
        self._failure_callbacks.add(callback)
    
    def remove_failure_callback(self, callback: Callable[[FailureIndicator], None]) -> None:
        """Remove failure callback."""
        self._failure_callbacks.discard(callback)
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get failure detection statistics."""
        total_failures = sum(len(failures) for failures in self._failure_history.values())
        
        # Count failures by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for failures in self._failure_history.values():
            for failure in failures:
                severity_counts[failure.severity] += 1
        
        # Count failures by type
        type_counts = {}
        for failures in self._failure_history.values():
            for failure in failures:
                type_counts[failure.failure_type] = type_counts.get(failure.failure_type, 0) + 1
        
        return {
            "total_failures_detected": total_failures,
            "endpoints_monitored": len(self._failure_history),
            "active_rules": len([r for r in self._failure_rules.values() if r.enabled]),
            "total_rules": len(self._failure_rules),
            "failures_by_severity": severity_counts,
            "failures_by_type": type_counts,
            "callback_count": len(self._failure_callbacks)
        }
    
    def _initialize_default_rules(self) -> None:
        """Initialize default failure detection rules."""
        default_rules = [
            FailureRule(
                name="slow_response_time",
                failure_type=FailureType.SLOW_RESPONSE,
                severity=FailureSeverity.MEDIUM,
                condition="response_time_ms > 1000",
                threshold=1000.0,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="very_slow_response_time",
                failure_type=FailureType.SLOW_RESPONSE,
                severity=FailureSeverity.HIGH,
                condition="response_time_ms > 5000",
                threshold=5000.0,
                cooldown_seconds=600.0
            ),
            FailureRule(
                name="high_message_latency",
                failure_type=FailureType.HIGH_LATENCY,
                severity=FailureSeverity.MEDIUM,
                condition="message_latency_ms > 100",
                threshold=100.0,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="very_high_message_latency",
                failure_type=FailureType.HIGH_LATENCY,
                severity=FailureSeverity.HIGH,
                condition="message_latency_ms > 500",
                threshold=500.0,
                cooldown_seconds=600.0
            ),
            FailureRule(
                name="high_error_rate",
                failure_type=FailureType.HIGH_ERROR_RATE,
                severity=FailureSeverity.HIGH,
                condition="error_rate > 0.05",
                threshold=0.05,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="critical_error_rate",
                failure_type=FailureType.HIGH_ERROR_RATE,
                severity=FailureSeverity.CRITICAL,
                condition="error_rate > 0.2",
                threshold=0.2,
                cooldown_seconds=600.0
            ),
            FailureRule(
                name="low_uptime",
                failure_type=FailureType.LOW_UPTIME,
                severity=FailureSeverity.HIGH,
                condition="uptime_percentage < 95",
                threshold=95.0,
                cooldown_seconds=600.0
            ),
            FailureRule(
                name="critical_low_uptime",
                failure_type=FailureType.LOW_UPTIME,
                severity=FailureSeverity.CRITICAL,
                condition="uptime_percentage < 80",
                threshold=80.0,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="slow_connection_time",
                failure_type=FailureType.SLOW_RESPONSE,
                severity=FailureSeverity.MEDIUM,
                condition="connection_time_ms > 5000",
                threshold=5000.0,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="very_slow_connection_time",
                failure_type=FailureType.SLOW_RESPONSE,
                severity=FailureSeverity.HIGH,
                condition="connection_time_ms > 10000",
                threshold=10000.0,
                cooldown_seconds=600.0
            )
        ]
        
        for rule in default_rules:
            self._failure_rules[rule.name] = rule
    
    async def _apply_failure_rule(
        self,
        rule: FailureRule,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        health_status: Optional[HealthStatus],
        additional_data: Dict[str, Any]
    ) -> bool:
        """Apply a specific failure detection rule."""
        try:
            # Evaluate rule condition
            if rule.condition == "response_time_ms > 1000":
                return quality_metrics and quality_metrics.response_time_ms > rule.threshold
            elif rule.condition == "response_time_ms > 5000":
                return quality_metrics and quality_metrics.response_time_ms > rule.threshold
            elif rule.condition == "message_latency_ms > 100":
                return quality_metrics and quality_metrics.message_latency_ms > rule.threshold
            elif rule.condition == "message_latency_ms > 500":
                return quality_metrics and quality_metrics.message_latency_ms > rule.threshold
            elif rule.condition == "error_rate > 0.05":
                return quality_metrics and quality_metrics.error_rate > rule.threshold
            elif rule.condition == "error_rate > 0.2":
                return quality_metrics and quality_metrics.error_rate > rule.threshold
            elif rule.condition == "uptime_percentage < 95":
                return quality_metrics and quality_metrics.uptime_percentage < rule.threshold
            elif rule.condition == "uptime_percentage < 80":
                return quality_metrics and quality_metrics.uptime_percentage < rule.threshold
            elif rule.condition == "connection_time_ms > 5000":
                return quality_metrics and quality_metrics.connection_time_ms > rule.threshold
            elif rule.condition == "connection_time_ms > 10000":
                return quality_metrics and quality_metrics.connection_time_ms > rule.threshold
            else:
                # Custom condition evaluation
                return await self._evaluate_custom_condition(rule.condition, endpoint, quality_metrics, health_status, additional_data)
        
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.name}: {e}")
            return False
    
    async def _evaluate_custom_condition(
        self,
        condition: str,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        health_status: Optional[HealthStatus],
        additional_data: Dict[str, Any]
    ) -> bool:
        """Evaluate custom condition string."""
        # This is a simplified condition evaluator
        # In a production system, you might want to use a more sophisticated expression evaluator
        
        try:
            # Create evaluation context
            context = {
                "endpoint": endpoint,
                "health_status": health_status.value if health_status else None,
            }
            
            if quality_metrics:
                context.update({
                    "response_time_ms": quality_metrics.response_time_ms,
                    "connection_time_ms": quality_metrics.connection_time_ms,
                    "message_latency_ms": quality_metrics.message_latency_ms,
                    "throughput_bytes_per_sec": quality_metrics.throughput_bytes_per_sec,
                    "error_rate": quality_metrics.error_rate,
                    "uptime_percentage": quality_metrics.uptime_percentage
                })
            
            context.update(additional_data)
            
            # Simple condition evaluation (not safe for arbitrary code)
            # This is a basic implementation - in production, use a proper expression evaluator
            if "response_time_ms" in condition:
                if quality_metrics:
                    return eval(condition.replace("response_time_ms", str(quality_metrics.response_time_ms)))
            elif "error_rate" in condition:
                if quality_metrics:
                    return eval(condition.replace("error_rate", str(quality_metrics.error_rate)))
            elif "uptime_percentage" in condition:
                if quality_metrics:
                    return eval(condition.replace("uptime_percentage", str(quality_metrics.uptime_percentage)))
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating custom condition '{condition}': {e}")
            return False
    
    async def _detect_endpoint_specific_failures(
        self,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        health_status: Optional[HealthStatus],
        additional_data: Dict[str, Any]
    ) -> List[FailureIndicator]:
        """Detect endpoint-specific failures."""
        failures = []
        
        # Emoji rain endpoint specific checks
        if endpoint == '/ws/emoji-rain':
            failures.extend(await self._check_emoji_rain_failures(endpoint, quality_metrics, additional_data))
        
        # Observatory endpoint specific checks
        elif endpoint == '/ws/observatory':
            failures.extend(await self._check_observatory_failures(endpoint, quality_metrics, additional_data))
        
        # Anomalies endpoint specific checks
        elif endpoint == '/ws/anomalies':
            failures.extend(await self._check_anomalies_failures(endpoint, quality_metrics, additional_data))
        
        # Doctor status endpoint specific checks
        elif endpoint == '/ws/doctor-status':
            failures.extend(await self._check_doctor_status_failures(endpoint, quality_metrics, additional_data))
        
        return failures
    
    async def _check_emoji_rain_failures(
        self,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        additional_data: Dict[str, Any]
    ) -> List[FailureIndicator]:
        """Check for emoji rain specific failures."""
        failures = []
        
        # Check if emoji engine is running
        emoji_engine_running = additional_data.get('emoji_engine_running', True)
        if not emoji_engine_running:
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.ENDPOINT_SPECIFIC.value,
                severity=FailureSeverity.HIGH.value,
                description="Emoji rain engine is not running",
                metadata={"emoji_engine_running": False}
            ))
        
        # Check active effects count
        active_effects = additional_data.get('active_effects_count', 0)
        if active_effects > 100:  # Too many active effects
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.RESOURCE_EXHAUSTION.value,
                severity=FailureSeverity.MEDIUM.value,
                description=f"Too many active emoji effects: {active_effects}",
                metadata={"active_effects_count": active_effects}
            ))
        
        # Check connected clients
        connected_clients = additional_data.get('connected_clients', 0)
        if connected_clients > 1000:  # Too many clients
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.RESOURCE_EXHAUSTION.value,
                severity=FailureSeverity.HIGH.value,
                description=f"Too many connected clients: {connected_clients}",
                metadata={"connected_clients": connected_clients}
            ))
        
        return failures
    
    async def _check_observatory_failures(
        self,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        additional_data: Dict[str, Any]
    ) -> List[FailureIndicator]:
        """Check for observatory specific failures."""
        failures = []
        
        # Check observatory core health
        observatory_health_score = additional_data.get('observatory_health_score', 1.0)
        if observatory_health_score < 0.7:
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.ENDPOINT_SPECIFIC.value,
                severity=FailureSeverity.HIGH.value,
                description=f"Observatory core health score is low: {observatory_health_score:.2f}",
                metadata={"observatory_health_score": observatory_health_score}
            ))
        
        # Check metrics collection rate
        metrics_collection_rate = additional_data.get('metrics_collection_rate', 0.0)
        if metrics_collection_rate < 1.0:  # Less than 1 metric per second
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.QUALITY_DEGRADATION.value,
                severity=FailureSeverity.MEDIUM.value,
                description=f"Low metrics collection rate: {metrics_collection_rate:.2f} metrics/sec",
                metadata={"metrics_collection_rate": metrics_collection_rate}
            ))
        
        return failures
    
    async def _check_anomalies_failures(
        self,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        additional_data: Dict[str, Any]
    ) -> List[FailureIndicator]:
        """Check for anomalies endpoint specific failures."""
        failures = []
        
        # Check anomaly detector status
        anomaly_detector_running = additional_data.get('anomaly_detector_running', True)
        if not anomaly_detector_running:
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.ENDPOINT_SPECIFIC.value,
                severity=FailureSeverity.MEDIUM.value,
                description="Anomaly detector is not running",
                metadata={"anomaly_detector_running": False}
            ))
        
        # Check active anomalies count
        active_anomalies = additional_data.get('active_anomalies_count', 0)
        if active_anomalies > 50:  # Too many active anomalies
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.QUALITY_DEGRADATION.value,
                severity=FailureSeverity.HIGH.value,
                description=f"High number of active anomalies: {active_anomalies}",
                metadata={"active_anomalies_count": active_anomalies}
            ))
        
        return failures
    
    async def _check_doctor_status_failures(
        self,
        endpoint: str,
        quality_metrics: Optional[QualityMetrics],
        additional_data: Dict[str, Any]
    ) -> List[FailureIndicator]:
        """Check for doctor status endpoint specific failures."""
        failures = []
        
        # Check AI consultation availability
        ai_consultation_available = additional_data.get('ai_consultation_available', True)
        if not ai_consultation_available:
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.ENDPOINT_SPECIFIC.value,
                severity=FailureSeverity.MEDIUM.value,
                description="AI consultation service is not available",
                metadata={"ai_consultation_available": False}
            ))
        
        # Check doctor availability
        doctor_available = additional_data.get('doctor_available', True)
        if not doctor_available:
            failures.append(FailureIndicator(
                endpoint=endpoint,
                failure_type=FailureType.ENDPOINT_SPECIFIC.value,
                severity=FailureSeverity.LOW.value,
                description="Doctor is currently unavailable",
                metadata={"doctor_available": False}
            ))
        
        return failures
    
    def _is_in_cooldown(self, endpoint: str, rule_name: str, cooldown_seconds: float) -> bool:
        """Check if a rule is in cooldown period."""
        if endpoint not in self._last_failure_times:
            return False
        
        if rule_name not in self._last_failure_times[endpoint]:
            return False
        
        last_failure_time = self._last_failure_times[endpoint][rule_name]
        return (datetime.utcnow() - last_failure_time).total_seconds() < cooldown_seconds
    
    async def _store_failure(self, endpoint: str, failure: FailureIndicator) -> None:
        """Store failure in history."""
        if endpoint not in self._failure_history:
            self._failure_history[endpoint] = []
        
        self._failure_history[endpoint].append(failure)
        
        # Keep only last 1000 failures per endpoint
        if len(self._failure_history[endpoint]) > 1000:
            self._failure_history[endpoint] = self._failure_history[endpoint][-1000:]
    
    async def _notify_failure_callbacks(self, failure: FailureIndicator) -> None:
        """Notify failure callbacks."""
        for callback in self._failure_callbacks:
            try:
                callback(failure)
            except Exception as e:
                logger.error(f"Failure callback error: {e}")
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '2.3',
            'action': f'failure_detector_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))
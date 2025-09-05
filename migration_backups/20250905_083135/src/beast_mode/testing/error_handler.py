"""
Beast Mode Framework - RCA Integration Error Handling and Graceful Degradation
Implements comprehensive error handling for RCA engine failures in test context
Requirements: 1.1, 1.4, 4.1 - Error handling, fallback reporting, health monitoring, retry logic
"""

import time
import traceback
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager

from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import RCAEngine, Failure, RCAResult
# Import types at runtime to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rca_integration import TestFailureData, TestRCAReportData, TestRCASummaryData


class ErrorSeverity(Enum):
    """Error severity levels for RCA integration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors in RCA integration"""
    RCA_ENGINE_FAILURE = "rca_engine_failure"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PARSING_ERROR = "parsing_error"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class DegradationLevel(Enum):
    """Levels of graceful degradation"""
    NONE = 0
    MINIMAL = 1
    MODERATE = 2
    SEVERE = 3
    EMERGENCY = 4


@dataclass
class ErrorContext:
    """Context information for error handling"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    error_message: str
    stack_trace: Optional[str]
    component: str
    operation: str
    context_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryConfiguration:
    """Configuration for retry logic"""
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_backoff: bool = True
    retry_on_categories: List[ErrorCategory] = field(default_factory=lambda: [
        ErrorCategory.TIMEOUT_EXCEEDED,
        ErrorCategory.RESOURCE_EXHAUSTION,
        ErrorCategory.NETWORK_ERROR
    ])


@dataclass
class FallbackReportData:
    """Fallback report when RCA analysis fails"""
    error_summary: str
    basic_failure_info: List[Dict[str, Any]]
    suggested_actions: List[str]
    health_status: Dict[str, Any]
    timestamp: datetime
    degradation_level: DegradationLevel


@dataclass
class HealthMonitoringMetrics:
    """Health monitoring metrics for RCA system components"""
    component_name: str
    last_check_timestamp: datetime
    is_healthy: bool
    error_count_last_hour: int
    error_count_last_day: int
    success_rate_last_hour: float
    success_rate_last_day: float
    average_response_time_ms: float
    resource_usage: Dict[str, float]
    degradation_level: DegradationLevel


class RCAErrorHandler(ReflectiveModule):
    """
    Comprehensive error handling and graceful degradation for RCA integration
    Provides fallback reporting, health monitoring, and automatic retry logic
    """
    
    def __init__(self, retry_config: Optional[RetryConfiguration] = None):
        super().__init__("rca_error_handler")
        
        # Configuration
        self.retry_config = retry_config or RetryConfiguration()
        
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.component_health: Dict[str, HealthMonitoringMetrics] = {}
        self.degradation_level = DegradationLevel.NONE
        
        # Metrics
        self.total_errors_handled = 0
        self.successful_recoveries = 0
        self.fallback_reports_generated = 0
        self.retry_attempts_made = 0
        self.successful_retries = 0
        
        # Health monitoring intervals
        self.health_check_interval_seconds = 60
        self.last_health_check = datetime.now()
        
        # Component registry
        self.monitored_components = [
            "rca_engine",
            "test_failure_detector", 
            "rca_integration_engine",
            "report_generator",
            "pattern_library"
        ]
        
        # Initialize component health tracking
        self._initialize_component_health()
        
        self._update_health_indicator(
            "rca_error_handler_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "RCA error handler ready for comprehensive error management"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "total_errors_handled": self.total_errors_handled,
            "successful_recoveries": self.successful_recoveries,
            "fallback_reports_generated": self.fallback_reports_generated,
            "retry_success_rate": self.successful_retries / max(1, self.retry_attempts_made),
            "current_degradation_level": self.degradation_level.value,
            "component_health_summary": self._get_component_health_summary(),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for error handling capability"""
        return (not self._degradation_active and 
                self.degradation_level.value <= DegradationLevel.MINIMAL.value and
                self._get_overall_component_health() > 0.7)
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "error_handling_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "errors_handled": self.total_errors_handled,
                "recovery_rate": self.successful_recoveries / max(1, self.total_errors_handled)
            },
            "component_monitoring": {
                "status": "healthy" if self._get_overall_component_health() > 0.7 else "degraded",
                "monitored_components": len(self.monitored_components),
                "healthy_components": len([c for c in self.component_health.values() if c.is_healthy]),
                "overall_health_score": self._get_overall_component_health()
            },
            "degradation_management": {
                "status": "healthy" if self.degradation_level.value <= DegradationLevel.MINIMAL.value else "degraded",
                "current_level": self.degradation_level.value,
                "fallback_reports": self.fallback_reports_generated,
                "graceful_degradation": "active" if self.degradation_level.value > 0 else "inactive"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: RCA integration error handling and recovery"""
        return "rca_integration_error_handling_and_recovery"
        
    @contextmanager
    def handle_rca_operation(self, operation_name: str, component: str = "unknown"):
        """
        Context manager for handling RCA operations with comprehensive error handling
        Requirements: 1.1, 1.4 - Comprehensive error handling with automatic retry
        """
        operation_id = f"{operation_name}_{int(time.time())}"
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting RCA operation: {operation_name} on {component}")
            
            # Pre-operation health check
            self._check_component_health(component)
            
            yield operation_id
            
            # Operation successful
            duration = time.time() - start_time
            self._record_successful_operation(component, operation_name, duration)
            
        except Exception as e:
            # Handle operation failure
            duration = time.time() - start_time
            error_context = self._create_error_context(
                error=e,
                component=component,
                operation=operation_name,
                duration=duration
            )
            
            self._handle_operation_error(error_context)
            self.total_errors_handled += 1  # Increment error count
            raise
            
    def handle_rca_engine_failure(
        self, 
        failure: Failure, 
        error: Exception,
        rca_engine: Optional[RCAEngine] = None
    ) -> Union[RCAResult, FallbackReportData]:
        """
        Handle RCA engine failures with fallback reporting
        Requirements: 1.1, 4.1 - RCA engine failure handling with fallback
        """
        self.total_errors_handled += 1
        
        try:
            self.logger.error(f"RCA engine failure for {failure.failure_id}: {error}")
            
            # Create error context
            error_context = self._create_error_context(
                error=error,
                component="rca_engine",
                operation="systematic_rca",
                context_data={"failure_id": failure.failure_id}
            )
            
            # Attempt recovery with retry logic
            if self._should_retry(error_context):
                recovery_result = self._attempt_recovery_with_retry(
                    operation=lambda: rca_engine.perform_systematic_rca(failure) if rca_engine else None,
                    error_context=error_context,
                    max_retries=self.retry_config.max_retries
                )
                
                if recovery_result is not None:
                    self.successful_recoveries += 1
                    return recovery_result
                    
            # Generate fallback report
            fallback_report = self._generate_fallback_report(failure, error_context)
            self.fallback_reports_generated += 1
            
            return fallback_report
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback handling failed: {fallback_error}")
            return self._generate_emergency_fallback(failure, str(fallback_error))
            
    def generate_fallback_report(
        self, 
        test_failures: List[Any], 
        error: Exception
    ) -> Any:
        """
        Generate fallback report when RCA analysis fails during testing
        Requirements: 1.1, 1.4 - Fallback reporting when RCA analysis fails
        """
        try:
            self.logger.info(f"Generating fallback report for {len(test_failures)} failures due to: {error}")
            
            # Create basic failure analysis
            basic_analysis = self._perform_basic_failure_analysis(test_failures)
            
            # Generate simple recommendations
            recommendations = self._generate_basic_recommendations(test_failures, error)
            
            # Import here to avoid circular import
            from .rca_integration import TestRCASummaryData
            
            # Create fallback summary
            fallback_summary = TestRCASummaryData(
                most_common_root_causes=[],
                systematic_fixes_available=0,
                pattern_matches_found=0,
                estimated_fix_time_minutes=30,  # Conservative estimate
                confidence_score=0.3,  # Low confidence for fallback
                critical_issues=[f"RCA analysis failed: {str(error)[:100]}"]
            )
            
            # Generate next steps
            next_steps = [
                "Check RCA engine health and configuration",
                "Retry analysis with simplified parameters",
                "Review test failure patterns manually",
                "Check system resources and dependencies",
                "Contact support if issues persist"
            ]
            
            # Import here to avoid circular import
            from .rca_integration import TestRCAReportData
            
            return TestRCAReportData(
                analysis_timestamp=datetime.now(),
                total_failures=len(test_failures),
                failures_analyzed=0,
                grouped_failures={"fallback_group": test_failures},
                rca_results=[],
                summary=fallback_summary,
                recommendations=recommendations,
                prevention_patterns=[],
                next_steps=next_steps
            )
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback report generation failed: {fallback_error}")
            return self._generate_emergency_report(test_failures, str(fallback_error))
            
    def monitor_component_health(self, component_name: str, operation_result: bool, response_time_ms: float) -> None:
        """
        Monitor health of RCA system components during test execution
        Requirements: 1.4 - Health monitoring for RCA system components
        """
        try:
            current_time = datetime.now()
            
            # Initialize component health if not exists
            if component_name not in self.component_health:
                self._initialize_component_health_entry(component_name)
                
            health_metrics = self.component_health[component_name]
            
            # Update metrics
            health_metrics.last_check_timestamp = current_time
            health_metrics.average_response_time_ms = (
                (health_metrics.average_response_time_ms * 0.9) + (response_time_ms * 0.1)
            )
            
            # Update error counts and success rates
            if operation_result:
                # Successful operation
                self._update_success_metrics(health_metrics)
            else:
                # Failed operation
                self._update_error_metrics(health_metrics, current_time)
                
            # Determine health status
            health_metrics.is_healthy = self._assess_component_health(health_metrics)
            
            # Check if degradation is needed
            if not health_metrics.is_healthy:
                self._consider_degradation(component_name, health_metrics)
                
        except Exception as e:
            self.logger.error(f"Health monitoring failed for {component_name}: {e}")
            
    def apply_graceful_degradation(self, degradation_level: DegradationLevel, reason: str) -> Dict[str, Any]:
        """
        Apply graceful degradation to RCA integration system
        Requirements: 1.4 - Graceful degradation when RCA analysis exceeds limits
        """
        try:
            self.logger.warning(f"Applying graceful degradation level {degradation_level.value}: {reason}")
            
            previous_level = self.degradation_level
            self.degradation_level = degradation_level
            
            degradation_actions = {
                DegradationLevel.MINIMAL: self._apply_minimal_degradation,
                DegradationLevel.MODERATE: self._apply_moderate_degradation,
                DegradationLevel.SEVERE: self._apply_severe_degradation,
                DegradationLevel.EMERGENCY: self._apply_emergency_degradation
            }
            
            action_result = {}
            if degradation_level in degradation_actions:
                action_result = degradation_actions[degradation_level](reason)
                
            return {
                "success": True,
                "previous_level": previous_level.value,
                "new_level": degradation_level.value,
                "reason": reason,
                "actions_taken": action_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Graceful degradation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def retry_with_simplified_parameters(
        self, 
        operation: Callable,
        original_error: Exception,
        max_retries: int = 3
    ) -> Any:
        """
        Automatic retry logic with simplified parameters on test failures
        Requirements: 1.4 - Automatic retry logic with simplified parameters
        """
        self.retry_attempts_made += 1
        
        try:
            self.logger.info(f"Attempting retry with simplified parameters, max retries: {max_retries}")
            
            for attempt in range(max_retries):
                try:
                    # Calculate delay with exponential backoff
                    if attempt > 0:
                        delay = min(
                            self.retry_config.base_delay_seconds * (2 ** (attempt - 1)),
                            self.retry_config.max_delay_seconds
                        )
                        self.logger.info(f"Retry attempt {attempt + 1} after {delay:.1f}s delay")
                        time.sleep(delay)
                        
                    # Apply simplified parameters based on attempt
                    simplified_operation = self._simplify_operation_parameters(operation, attempt)
                    
                    # Execute simplified operation
                    result = simplified_operation()
                    
                    # Success
                    self.successful_retries += 1
                    self.logger.info(f"Retry successful on attempt {attempt + 1}")
                    return result
                    
                except Exception as retry_error:
                    self.logger.warning(f"Retry attempt {attempt + 1} failed: {retry_error}")
                    
                    # If this is the last attempt, continue to raise final error
                    if attempt == max_retries - 1:
                        continue
                        
            # All retries failed - raise the last error with context
            raise Exception(f"All {max_retries} retry attempts failed. Original error: {original_error}")
            
        except Exception as e:
            self.logger.error(f"Retry logic failed: {e}")
            raise
            
    def get_error_report(self) -> Dict[str, Any]:
        """Get comprehensive error handling report"""
        try:
            recent_errors = [
                {
                    "error_id": error.error_id,
                    "timestamp": error.timestamp.isoformat(),
                    "severity": error.severity.value,
                    "category": error.category.value,
                    "component": error.component,
                    "operation": error.operation,
                    "message": error.error_message[:200]
                }
                for error in self.error_history[-10:]  # Last 10 errors
            ]
            
            return {
                "error_handling_summary": {
                    "total_errors_handled": self.total_errors_handled,
                    "successful_recoveries": self.successful_recoveries,
                    "recovery_rate": self.successful_recoveries / max(1, self.total_errors_handled),
                    "fallback_reports_generated": self.fallback_reports_generated,
                    "current_degradation_level": self.degradation_level.value
                },
                "retry_statistics": {
                    "retry_attempts_made": self.retry_attempts_made,
                    "successful_retries": self.successful_retries,
                    "retry_success_rate": self.successful_retries / max(1, self.retry_attempts_made)
                },
                "component_health": {
                    name: {
                        "is_healthy": metrics.is_healthy,
                        "error_count_last_hour": metrics.error_count_last_hour,
                        "success_rate_last_hour": metrics.success_rate_last_hour,
                        "average_response_time_ms": metrics.average_response_time_ms,
                        "degradation_level": metrics.degradation_level.value
                    }
                    for name, metrics in self.component_health.items()
                },
                "recent_errors": recent_errors,
                "health_indicators": self.get_health_indicators()
            }
            
        except Exception as e:
            self.logger.error(f"Error report generation failed: {e}")
            return {
                "error": f"Error report generation failed: {e}",
                "timestamp": datetime.now().isoformat()
            }
            
    # Private helper methods
    
    def _initialize_component_health(self) -> None:
        """Initialize health tracking for all monitored components"""
        for component in self.monitored_components:
            self._initialize_component_health_entry(component)
            
    def _initialize_component_health_entry(self, component_name: str) -> None:
        """Initialize health tracking for a specific component"""
        self.component_health[component_name] = HealthMonitoringMetrics(
            component_name=component_name,
            last_check_timestamp=datetime.now(),
            is_healthy=True,
            error_count_last_hour=0,
            error_count_last_day=0,
            success_rate_last_hour=1.0,
            success_rate_last_day=1.0,
            average_response_time_ms=0.0,
            resource_usage={},
            degradation_level=DegradationLevel.NONE
        )
        
    def _create_error_context(
        self, 
        error: Exception, 
        component: str, 
        operation: str,
        duration: float = 0.0,
        context_data: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """Create comprehensive error context"""
        error_id = f"error_{int(time.time())}_{component}_{operation}"
        
        # Determine error category and severity
        category = self._categorize_error(error)
        severity = self._assess_error_severity(error, category)
        
        context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            component=component,
            operation=operation,
            context_data=context_data or {}
        )
        
        # Add to error history
        self.error_history.append(context)
        
        # Keep only recent errors (last 100)
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
            
        return context
        
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if "timeout" in error_str or "timeout" in error_type:
            return ErrorCategory.TIMEOUT_EXCEEDED
        elif "memory" in error_str or "resource" in error_str:
            return ErrorCategory.RESOURCE_EXHAUSTION
        elif "permission" in error_str or "access" in error_str:
            return ErrorCategory.PERMISSION_ERROR
        elif "network" in error_str or "connection" in error_str:
            return ErrorCategory.NETWORK_ERROR
        elif "config" in error_str or "setting" in error_str:
            return ErrorCategory.CONFIGURATION_ERROR
        elif "parse" in error_str or "format" in error_str:
            return ErrorCategory.PARSING_ERROR
        elif "rca" in error_str or "analysis" in error_str:
            return ErrorCategory.RCA_ENGINE_FAILURE
        else:
            return ErrorCategory.UNKNOWN_ERROR
            
    def _assess_error_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Assess error severity based on type and category"""
        critical_categories = [
            ErrorCategory.RCA_ENGINE_FAILURE,
            ErrorCategory.RESOURCE_EXHAUSTION
        ]
        
        high_categories = [
            ErrorCategory.TIMEOUT_EXCEEDED,
            ErrorCategory.CONFIGURATION_ERROR
        ]
        
        if category in critical_categories:
            return ErrorSeverity.CRITICAL
        elif category in high_categories:
            return ErrorSeverity.HIGH
        elif "critical" in str(error).lower():
            return ErrorSeverity.CRITICAL
        elif "error" in str(error).lower():
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
            
    def _should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if error should trigger retry logic"""
        return (error_context.category in self.retry_config.retry_on_categories and
                error_context.severity.value in ["low", "medium"])
                
    def _attempt_recovery_with_retry(
        self, 
        operation: Callable,
        error_context: ErrorContext,
        max_retries: int
    ) -> Any:
        """Attempt recovery with retry logic"""
        try:
            return self.retry_with_simplified_parameters(
                operation=operation,
                original_error=Exception(error_context.error_message),
                max_retries=max_retries
            )
        except Exception:
            return None
            
    def _generate_fallback_report(self, failure: Failure, error_context: ErrorContext) -> FallbackReportData:
        """Generate fallback report for single failure"""
        return FallbackReportData(
            error_summary=f"RCA analysis failed: {error_context.error_message[:200]}",
            basic_failure_info=[{
                "failure_id": failure.failure_id,
                "component": failure.component,
                "error_message": failure.error_message[:200],
                "timestamp": failure.timestamp.isoformat()
            }],
            suggested_actions=[
                "Check RCA engine configuration",
                "Verify system resources",
                "Review error logs for details",
                "Retry with simplified parameters"
            ],
            health_status=self.get_health_indicators(),
            timestamp=datetime.now(),
            degradation_level=self.degradation_level
        )
        
    def _generate_emergency_fallback(self, failure: Failure, error_message: str) -> FallbackReportData:
        """Generate emergency fallback when all else fails"""
        return FallbackReportData(
            error_summary=f"Emergency fallback: {error_message}",
            basic_failure_info=[{
                "failure_id": failure.failure_id,
                "error": "Multiple system failures"
            }],
            suggested_actions=[
                "Contact system administrator",
                "Check system health",
                "Review logs immediately"
            ],
            health_status={"emergency": True},
            timestamp=datetime.now(),
            degradation_level=DegradationLevel.EMERGENCY
        )
        
    def _generate_emergency_report(self, test_failures: List[Any], error_message: str) -> Any:
        """Generate emergency report when fallback fails"""
        # Import here to avoid circular import
        from .rca_integration import TestRCAReportData, TestRCASummaryData
        
        return TestRCAReportData(
            analysis_timestamp=datetime.now(),
            total_failures=len(test_failures),
            failures_analyzed=0,
            grouped_failures={},
            rca_results=[],
            summary=TestRCASummaryData(
                most_common_root_causes=[],
                systematic_fixes_available=0,
                pattern_matches_found=0,
                estimated_fix_time_minutes=0,
                confidence_score=0.0,
                critical_issues=[f"Emergency: {error_message}"]
            ),
            recommendations=[f"Emergency situation: {error_message}"],
            prevention_patterns=[],
            next_steps=["Contact system administrator immediately"]
        )
        
    def _perform_basic_failure_analysis(self, test_failures: List[Any]) -> Dict[str, Any]:
        """Perform basic analysis when RCA engine is unavailable"""
        failure_types = {}
        error_patterns = {}
        
        for failure in test_failures:
            # Count failure types
            failure_types[failure.failure_type] = failure_types.get(failure.failure_type, 0) + 1
            
            # Extract common error patterns
            error_words = failure.error_message.lower().split()[:5]
            pattern = " ".join(error_words)
            error_patterns[pattern] = error_patterns.get(pattern, 0) + 1
            
        return {
            "failure_types": failure_types,
            "error_patterns": error_patterns,
            "total_failures": len(test_failures)
        }
        
    def _generate_basic_recommendations(self, test_failures: List[Any], error: Exception) -> List[str]:
        """Generate basic recommendations when RCA is unavailable"""
        recommendations = [
            f"RCA analysis failed due to: {str(error)[:100]}",
            f"Found {len(test_failures)} test failures requiring attention"
        ]
        
        # Add failure-type specific recommendations
        failure_types = set(f.failure_type for f in test_failures)
        
        if "import" in failure_types:
            recommendations.append("Check Python import paths and dependencies")
        if "assertion" in failure_types:
            recommendations.append("Review test assertions and expected values")
        if "timeout" in failure_types:
            recommendations.append("Check test execution timeouts and performance")
            
        recommendations.extend([
            "Review test logs for detailed error information",
            "Check system resources and configuration",
            "Retry RCA analysis when system is stable"
        ])
        
        return recommendations
        
    def _get_component_health_summary(self) -> Dict[str, str]:
        """Get summary of component health status"""
        return {
            name: "healthy" if metrics.is_healthy else "unhealthy"
            for name, metrics in self.component_health.items()
        }
        
    def _get_overall_component_health(self) -> float:
        """Calculate overall component health score"""
        if not self.component_health:
            return 1.0
            
        healthy_count = sum(1 for metrics in self.component_health.values() if metrics.is_healthy)
        return healthy_count / len(self.component_health)
        
    def _check_component_health(self, component: str) -> None:
        """Check health of specific component"""
        if component in self.component_health:
            metrics = self.component_health[component]
            if not metrics.is_healthy:
                self.logger.warning(f"Component {component} is unhealthy")
                
    def _record_successful_operation(self, component: str, operation: str, duration: float) -> None:
        """Record successful operation for health monitoring"""
        self.monitor_component_health(component, True, duration * 1000)  # Convert to ms
        
    def _handle_operation_error(self, error_context: ErrorContext) -> None:
        """Handle operation error and update health metrics"""
        self.monitor_component_health(error_context.component, False, 0.0)
        
    def _update_success_metrics(self, health_metrics: HealthMonitoringMetrics) -> None:
        """Update success metrics for component"""
        # Simple exponential moving average
        health_metrics.success_rate_last_hour = min(1.0, health_metrics.success_rate_last_hour * 1.01)
        health_metrics.success_rate_last_day = min(1.0, health_metrics.success_rate_last_day * 1.001)
        
    def _update_error_metrics(self, health_metrics: HealthMonitoringMetrics, current_time: datetime) -> None:
        """Update error metrics for component"""
        health_metrics.error_count_last_hour += 1
        health_metrics.error_count_last_day += 1
        
        # Decay success rates
        health_metrics.success_rate_last_hour *= 0.95
        health_metrics.success_rate_last_day *= 0.99
        
    def _assess_component_health(self, health_metrics: HealthMonitoringMetrics) -> bool:
        """Assess if component is healthy based on metrics"""
        return (health_metrics.success_rate_last_hour > 0.7 and
                health_metrics.error_count_last_hour < 10 and
                health_metrics.average_response_time_ms < 5000)
                
    def _consider_degradation(self, component_name: str, health_metrics: HealthMonitoringMetrics) -> None:
        """Consider applying degradation based on component health"""
        if health_metrics.error_count_last_hour > 20:
            self.apply_graceful_degradation(
                DegradationLevel.SEVERE,
                f"Component {component_name} has {health_metrics.error_count_last_hour} errors in last hour"
            )
        elif health_metrics.success_rate_last_hour < 0.5:
            self.apply_graceful_degradation(
                DegradationLevel.MODERATE,
                f"Component {component_name} success rate: {health_metrics.success_rate_last_hour:.1%}"
            )
            
    def _apply_minimal_degradation(self, reason: str) -> Dict[str, Any]:
        """Apply minimal degradation - reduce analysis depth"""
        return {
            "analysis_depth": "reduced",
            "pattern_matching": "fast_only",
            "timeout_reduction": "10%",
            "reason": reason
        }
        
    def _apply_moderate_degradation(self, reason: str) -> Dict[str, Any]:
        """Apply moderate degradation - skip non-essential analysis"""
        return {
            "analysis_depth": "basic",
            "pattern_matching": "disabled",
            "timeout_reduction": "25%",
            "comprehensive_analysis": "disabled",
            "reason": reason
        }
        
    def _apply_severe_degradation(self, reason: str) -> Dict[str, Any]:
        """Apply severe degradation - minimal analysis only"""
        return {
            "analysis_depth": "minimal",
            "pattern_matching": "disabled",
            "timeout_reduction": "50%",
            "comprehensive_analysis": "disabled",
            "systematic_fixes": "disabled",
            "reason": reason
        }
        
    def _apply_emergency_degradation(self, reason: str) -> Dict[str, Any]:
        """Apply emergency degradation - fallback mode only"""
        return {
            "analysis_depth": "none",
            "fallback_mode": "enabled",
            "all_advanced_features": "disabled",
            "basic_reporting_only": True,
            "reason": reason
        }
        
    def _simplify_operation_parameters(self, operation: Callable, attempt: int) -> Callable:
        """Simplify operation parameters based on retry attempt"""
        # This is a placeholder - actual implementation would depend on the specific operation
        # For now, return the original operation
        return operation
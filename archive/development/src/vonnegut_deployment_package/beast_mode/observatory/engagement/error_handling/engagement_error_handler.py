"""
Engagement Error Handler - Comprehensive Error Management
========================================================

Provides systematic error handling, classification, and recovery for all
engagement system operations with fallback modes and graceful degradation.
"""

import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class EngagementErrorType(Enum):
    """Types of engagement system errors."""
    IMPORT_ERROR = "import_error"
    INITIALIZATION_ERROR = "initialization_error"
    WEBSOCKET_ERROR = "websocket_error"
    DATA_PROCESSING_ERROR = "data_processing_error"
    ANIMATION_ERROR = "animation_error"
    PERSONALITY_ERROR = "personality_error"
    ATTENTION_ERROR = "attention_error"
    INTERACTION_ERROR = "interaction_error"
    LEARNING_ERROR = "learning_error"
    COORDINATION_ERROR = "coordination_error"
    MONITORING_ERROR = "monitoring_error"
    INTEGRATION_ERROR = "integration_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN_ERROR = "unknown_error"


class EngagementErrorSeverity(Enum):
    """Severity levels for engagement errors."""
    LOW = "low"           # Minor issues, system continues normally
    MEDIUM = "medium"     # Moderate issues, some features may be degraded
    HIGH = "high"         # Significant issues, major features affected
    CRITICAL = "critical" # System-threatening issues, immediate action required


class EngagementFallbackMode(Enum):
    """Fallback modes for engagement system components."""
    FULL_FUNCTIONALITY = "full_functionality"     # All features working
    REDUCED_FUNCTIONALITY = "reduced_functionality" # Some features disabled
    BASIC_FUNCTIONALITY = "basic_functionality"   # Only core features
    MINIMAL_FUNCTIONALITY = "minimal_functionality" # Bare minimum
    DISABLED = "disabled"                         # Component disabled


@dataclass
class EngagementError:
    """Structured representation of an engagement system error."""
    error_type: EngagementErrorType
    severity: EngagementErrorSeverity
    component: str
    message: str
    exception: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    fallback_mode: Optional[EngagementFallbackMode] = None
    
    def __post_init__(self):
        """Extract stack trace from exception if available."""
        if self.exception and not self.stack_trace:
            self.stack_trace = traceback.format_exception(
                type(self.exception), self.exception, self.exception.__traceback__
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/reporting."""
        return {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "component": self.component,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "fallback_mode": self.fallback_mode.value if self.fallback_mode else None,
            "exception_type": type(self.exception).__name__ if self.exception else None
        }


class EngagementErrorHandler(ReflectiveModule):
    """
    Comprehensive error handler for the engagement system.
    
    Provides systematic error handling, classification, recovery,
    and fallback mode management for all engagement components.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "engagement_error_handler"
        
        # Error tracking
        self.error_history: List[EngagementError] = []
        self.error_counts: Dict[str, int] = {}
        self.component_fallback_modes: Dict[str, EngagementFallbackMode] = {}
        
        # Recovery handlers
        self.recovery_handlers: Dict[EngagementErrorType, List[Callable]] = {}
        self.fallback_handlers: Dict[str, Dict[EngagementFallbackMode, Callable]] = {}
        
        # Configuration
        self.max_error_history = 1000
        self.error_threshold_window = timedelta(minutes=5)
        self.critical_error_threshold = 5
        self.high_error_threshold = 10
        
        # State
        self.system_degraded = False
        self.last_health_check = datetime.now()
        
        logger.info("🛡️ Engagement Error Handler initialized")
    
    async def initialize(self) -> bool:
        """Initialize the error handler."""
        try:
            # Register default recovery handlers
            self._register_default_recovery_handlers()
            
            # Register default fallback handlers
            self._register_default_fallback_handlers()
            
            logger.info("✅ Engagement Error Handler initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Error Handler: {e}")
            return False
    
    async def handle_error(self, 
                          error_type: EngagementErrorType,
                          component: str,
                          message: str,
                          exception: Optional[Exception] = None,
                          context: Dict[str, Any] = None,
                          attempt_recovery: bool = True) -> EngagementError:
        """
        Handle an engagement system error with comprehensive processing.
        
        Args:
            error_type: Type of error that occurred
            component: Component where error occurred
            message: Human-readable error message
            exception: Original exception if available
            context: Additional context information
            attempt_recovery: Whether to attempt automatic recovery
            
        Returns:
            EngagementError object with processing results
        """
        try:
            # Determine severity based on error type and history
            severity = self._determine_error_severity(error_type, component, exception)
            
            # Create error object
            engagement_error = EngagementError(
                error_type=error_type,
                severity=severity,
                component=component,
                message=message,
                exception=exception,
                context=context or {}
            )
            
            # Log the error
            self._log_error(engagement_error)
            
            # Add to error history
            self._add_to_error_history(engagement_error)
            
            # Update error counts
            self._update_error_counts(engagement_error)
            
            # Attempt recovery if requested and appropriate
            if attempt_recovery and severity in [EngagementErrorSeverity.MEDIUM, EngagementErrorSeverity.HIGH]:
                recovery_result = await self._attempt_error_recovery(engagement_error)
                engagement_error.recovery_attempted = True
                engagement_error.recovery_successful = recovery_result
            
            # Apply fallback mode if recovery failed or error is critical
            if not engagement_error.recovery_successful or severity == EngagementErrorSeverity.CRITICAL:
                fallback_mode = await self._apply_fallback_mode(engagement_error)
                engagement_error.fallback_mode = fallback_mode
            
            # Check if system-wide degradation is needed
            await self._check_system_degradation()
            
            return engagement_error
            
        except Exception as handler_error:
            # Error in error handler - log and return basic error
            logger.critical(f"Error in engagement error handler: {handler_error}")
            return EngagementError(
                error_type=EngagementErrorType.UNKNOWN_ERROR,
                severity=EngagementErrorSeverity.CRITICAL,
                component="error_handler",
                message=f"Error handler failure: {handler_error}",
                exception=handler_error
            )
    
    def _determine_error_severity(self, 
                                error_type: EngagementErrorType,
                                component: str,
                                exception: Optional[Exception]) -> EngagementErrorSeverity:
        """Determine error severity based on type, component, and history."""
        
        # Critical error types
        if error_type in [
            EngagementErrorType.INITIALIZATION_ERROR,
            EngagementErrorType.CONFIGURATION_ERROR
        ]:
            return EngagementErrorSeverity.CRITICAL
        
        # Check recent error frequency for this component
        recent_errors = self._get_recent_errors_for_component(component)
        
        if len(recent_errors) >= self.critical_error_threshold:
            return EngagementErrorSeverity.CRITICAL
        elif len(recent_errors) >= self.high_error_threshold:
            return EngagementErrorSeverity.HIGH
        
        # Exception-based severity
        if exception:
            if isinstance(exception, (ImportError, ModuleNotFoundError)):
                return EngagementErrorSeverity.HIGH
            elif isinstance(exception, (ConnectionError, TimeoutError)):
                return EngagementErrorSeverity.MEDIUM
            elif isinstance(exception, (ValueError, TypeError)):
                return EngagementErrorSeverity.LOW
        
        # Default severity based on error type
        severity_map = {
            EngagementErrorType.IMPORT_ERROR: EngagementErrorSeverity.HIGH,
            EngagementErrorType.WEBSOCKET_ERROR: EngagementErrorSeverity.MEDIUM,
            EngagementErrorType.DATA_PROCESSING_ERROR: EngagementErrorSeverity.MEDIUM,
            EngagementErrorType.ANIMATION_ERROR: EngagementErrorSeverity.LOW,
            EngagementErrorType.PERSONALITY_ERROR: EngagementErrorSeverity.LOW,
            EngagementErrorType.ATTENTION_ERROR: EngagementErrorSeverity.LOW,
            EngagementErrorType.INTERACTION_ERROR: EngagementErrorSeverity.MEDIUM,
            EngagementErrorType.LEARNING_ERROR: EngagementErrorSeverity.LOW,
            EngagementErrorType.COORDINATION_ERROR: EngagementErrorSeverity.HIGH,
            EngagementErrorType.MONITORING_ERROR: EngagementErrorSeverity.MEDIUM,
            EngagementErrorType.INTEGRATION_ERROR: EngagementErrorSeverity.HIGH,
            EngagementErrorType.NETWORK_ERROR: EngagementErrorSeverity.MEDIUM,
            EngagementErrorType.RESOURCE_ERROR: EngagementErrorSeverity.HIGH,
        }
        
        return severity_map.get(error_type, EngagementErrorSeverity.MEDIUM)
    
    def _log_error(self, error: EngagementError):
        """Log error with appropriate level based on severity."""
        # Create log message without extra data to avoid conflicts
        log_message = f"[{error.component}] {error.message} (Type: {error.error_type.value}, Severity: {error.severity.value})"
        
        if error.severity == EngagementErrorSeverity.CRITICAL:
            logger.critical(f"🚨 CRITICAL ENGAGEMENT ERROR: {log_message}")
        elif error.severity == EngagementErrorSeverity.HIGH:
            logger.error(f"❌ HIGH ENGAGEMENT ERROR: {log_message}")
        elif error.severity == EngagementErrorSeverity.MEDIUM:
            logger.warning(f"⚠️ MEDIUM ENGAGEMENT ERROR: {log_message}")
        else:
            logger.info(f"ℹ️ LOW ENGAGEMENT ERROR: {log_message}")
    
    def _add_to_error_history(self, error: EngagementError):
        """Add error to history with size management."""
        self.error_history.append(error)
        
        # Trim history if too large
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
    
    def _update_error_counts(self, error: EngagementError):
        """Update error counts for tracking."""
        key = f"{error.component}:{error.error_type.value}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def _get_recent_errors_for_component(self, component: str) -> List[EngagementError]:
        """Get recent errors for a specific component."""
        cutoff_time = datetime.now() - self.error_threshold_window
        return [
            error for error in self.error_history
            if error.component == component and error.timestamp > cutoff_time
        ]
    
    async def _attempt_error_recovery(self, error: EngagementError) -> bool:
        """Attempt to recover from an error using registered handlers."""
        try:
            handlers = self.recovery_handlers.get(error.error_type, [])
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(error)
                    else:
                        result = handler(error)
                    
                    if result:
                        logger.info(f"✅ Recovery successful for {error.component} {error.error_type.value}")
                        return True
                        
                except Exception as recovery_error:
                    logger.warning(f"Recovery handler failed for {error.error_type.value}: {recovery_error}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error during recovery attempt: {e}")
            return False
    
    async def _apply_fallback_mode(self, error: EngagementError) -> EngagementFallbackMode:
        """Apply appropriate fallback mode for the component."""
        try:
            # Determine fallback mode based on error severity
            if error.severity == EngagementErrorSeverity.CRITICAL:
                fallback_mode = EngagementFallbackMode.DISABLED
            elif error.severity == EngagementErrorSeverity.HIGH:
                fallback_mode = EngagementFallbackMode.MINIMAL_FUNCTIONALITY
            elif error.severity == EngagementErrorSeverity.MEDIUM:
                fallback_mode = EngagementFallbackMode.BASIC_FUNCTIONALITY
            else:
                fallback_mode = EngagementFallbackMode.REDUCED_FUNCTIONALITY
            
            # Apply fallback mode
            self.component_fallback_modes[error.component] = fallback_mode
            
            # Execute fallback handler if available
            component_handlers = self.fallback_handlers.get(error.component, {})
            handler = component_handlers.get(fallback_mode)
            
            if handler:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(error)
                    else:
                        handler(error)
                    
                    logger.info(f"🔄 Applied fallback mode {fallback_mode.value} to {error.component}")
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback handler failed for {error.component}: {fallback_error}")
            
            return fallback_mode
            
        except Exception as e:
            logger.error(f"Error applying fallback mode: {e}")
            return EngagementFallbackMode.DISABLED
    
    async def _check_system_degradation(self):
        """Check if system-wide degradation is needed."""
        try:
            # Count critical and high severity errors in recent window
            cutoff_time = datetime.now() - self.error_threshold_window
            recent_critical_errors = [
                error for error in self.error_history
                if error.timestamp > cutoff_time and error.severity == EngagementErrorSeverity.CRITICAL
            ]
            recent_high_errors = [
                error for error in self.error_history
                if error.timestamp > cutoff_time and error.severity == EngagementErrorSeverity.HIGH
            ]
            
            # Trigger system degradation if thresholds exceeded
            if len(recent_critical_errors) >= 3 or len(recent_high_errors) >= 10:
                if not self.system_degraded:
                    await self._trigger_system_degradation()
            else:
                if self.system_degraded:
                    await self._restore_system_functionality()
                    
        except Exception as e:
            logger.error(f"Error checking system degradation: {e}")
    
    async def _trigger_system_degradation(self):
        """Trigger system-wide degradation mode."""
        try:
            self.system_degraded = True
            logger.warning("🔻 Triggering system-wide engagement degradation due to error threshold")
            
            # Apply degradation to all components
            for component in self.component_fallback_modes:
                if self.component_fallback_modes[component] == EngagementFallbackMode.FULL_FUNCTIONALITY:
                    self.component_fallback_modes[component] = EngagementFallbackMode.BASIC_FUNCTIONALITY
                elif self.component_fallback_modes[component] == EngagementFallbackMode.REDUCED_FUNCTIONALITY:
                    self.component_fallback_modes[component] = EngagementFallbackMode.MINIMAL_FUNCTIONALITY
            
        except Exception as e:
            logger.error(f"Error triggering system degradation: {e}")
    
    async def _restore_system_functionality(self):
        """Restore system functionality when error rates decrease."""
        try:
            self.system_degraded = False
            logger.info("🔺 Restoring system functionality - error rates have decreased")
            
            # Gradually restore component functionality
            for component in self.component_fallback_modes:
                current_mode = self.component_fallback_modes[component]
                if current_mode == EngagementFallbackMode.MINIMAL_FUNCTIONALITY:
                    self.component_fallback_modes[component] = EngagementFallbackMode.BASIC_FUNCTIONALITY
                elif current_mode == EngagementFallbackMode.BASIC_FUNCTIONALITY:
                    self.component_fallback_modes[component] = EngagementFallbackMode.REDUCED_FUNCTIONALITY
            
        except Exception as e:
            logger.error(f"Error restoring system functionality: {e}")
    
    def register_recovery_handler(self, 
                                error_type: EngagementErrorType,
                                handler: Callable[[EngagementError], Union[bool, Any]]):
        """Register a recovery handler for a specific error type."""
        if error_type not in self.recovery_handlers:
            self.recovery_handlers[error_type] = []
        self.recovery_handlers[error_type].append(handler)
        logger.info(f"Registered recovery handler for {error_type.value}")
    
    def register_fallback_handler(self,
                                component: str,
                                fallback_mode: EngagementFallbackMode,
                                handler: Callable[[EngagementError], Any]):
        """Register a fallback handler for a component and mode."""
        if component not in self.fallback_handlers:
            self.fallback_handlers[component] = {}
        self.fallback_handlers[component][fallback_mode] = handler
        logger.info(f"Registered fallback handler for {component} {fallback_mode.value}")
    
    def _register_default_recovery_handlers(self):
        """Register default recovery handlers for common error types."""
        
        # Import error recovery
        def recover_import_error(error: EngagementError) -> bool:
            """Attempt to recover from import errors by using fallback implementations."""
            try:
                logger.info(f"Attempting import error recovery for {error.component}")
                # This would typically involve loading fallback implementations
                return False  # Placeholder - actual recovery would be component-specific
            except Exception:
                return False
        
        # WebSocket error recovery
        async def recover_websocket_error(error: EngagementError) -> bool:
            """Attempt to recover from WebSocket errors by reconnecting."""
            try:
                logger.info(f"Attempting WebSocket error recovery for {error.component}")
                # This would typically involve reconnection logic
                await asyncio.sleep(1)  # Brief delay before retry
                return False  # Placeholder - actual recovery would reconnect
            except Exception:
                return False
        
        # Data processing error recovery
        def recover_data_processing_error(error: EngagementError) -> bool:
            """Attempt to recover from data processing errors."""
            try:
                logger.info(f"Attempting data processing error recovery for {error.component}")
                # This would typically involve data validation and cleanup
                return False  # Placeholder - actual recovery would clean data
            except Exception:
                return False
        
        # Register handlers
        self.register_recovery_handler(EngagementErrorType.IMPORT_ERROR, recover_import_error)
        self.register_recovery_handler(EngagementErrorType.WEBSOCKET_ERROR, recover_websocket_error)
        self.register_recovery_handler(EngagementErrorType.DATA_PROCESSING_ERROR, recover_data_processing_error)
    
    def _register_default_fallback_handlers(self):
        """Register default fallback handlers for common components."""
        
        # Dashboard Engine fallback handlers
        def dashboard_basic_fallback(error: EngagementError):
            """Basic fallback for dashboard engine - disable advanced features."""
            logger.info("Dashboard Engine: Switching to basic mode - disabling advanced visualizations")
        
        def dashboard_minimal_fallback(error: EngagementError):
            """Minimal fallback for dashboard engine - static display only."""
            logger.info("Dashboard Engine: Switching to minimal mode - static display only")
        
        def dashboard_disabled_fallback(error: EngagementError):
            """Disabled fallback for dashboard engine."""
            logger.warning("Dashboard Engine: Disabled due to critical errors")
        
        # Animation Engine fallback handlers
        def animation_basic_fallback(error: EngagementError):
            """Basic fallback for animation engine - simple animations only."""
            logger.info("Animation Engine: Switching to basic mode - simple animations only")
        
        def animation_minimal_fallback(error: EngagementError):
            """Minimal fallback for animation engine - no animations."""
            logger.info("Animation Engine: Switching to minimal mode - animations disabled")
        
        # Register fallback handlers
        self.register_fallback_handler("dashboard_engine", EngagementFallbackMode.BASIC_FUNCTIONALITY, dashboard_basic_fallback)
        self.register_fallback_handler("dashboard_engine", EngagementFallbackMode.MINIMAL_FUNCTIONALITY, dashboard_minimal_fallback)
        self.register_fallback_handler("dashboard_engine", EngagementFallbackMode.DISABLED, dashboard_disabled_fallback)
        
        self.register_fallback_handler("animation_engine", EngagementFallbackMode.BASIC_FUNCTIONALITY, animation_basic_fallback)
        self.register_fallback_handler("animation_engine", EngagementFallbackMode.MINIMAL_FUNCTIONALITY, animation_minimal_fallback)
    
    def get_component_fallback_mode(self, component: str) -> EngagementFallbackMode:
        """Get current fallback mode for a component."""
        return self.component_fallback_modes.get(component, EngagementFallbackMode.FULL_FUNCTIONALITY)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        cutoff_time = datetime.now() - self.error_threshold_window
        recent_errors = [error for error in self.error_history if error.timestamp > cutoff_time]
        
        # Count by severity
        severity_counts = {}
        for severity in EngagementErrorSeverity:
            severity_counts[severity.value] = len([e for e in recent_errors if e.severity == severity])
        
        # Count by component
        component_counts = {}
        for error in recent_errors:
            component_counts[error.component] = component_counts.get(error.component, 0) + 1
        
        # Count by error type
        type_counts = {}
        for error in recent_errors:
            type_counts[error.error_type.value] = type_counts.get(error.error_type.value, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "system_degraded": self.system_degraded,
            "severity_distribution": severity_counts,
            "component_distribution": component_counts,
            "error_type_distribution": type_counts,
            "component_fallback_modes": {
                component: mode.value 
                for component, mode in self.component_fallback_modes.items()
            },
            "recovery_success_rate": self._calculate_recovery_success_rate()
        }
    
    def _calculate_recovery_success_rate(self) -> float:
        """Calculate recovery success rate."""
        recovery_attempts = [e for e in self.error_history if e.recovery_attempted]
        if not recovery_attempts:
            return 0.0
        
        successful_recoveries = [e for e in recovery_attempts if e.recovery_successful]
        return len(successful_recoveries) / len(recovery_attempts)
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Engagement Error Handler capabilities."""
        return [
            "error_classification",
            "error_recovery",
            "fallback_mode_management",
            "system_degradation_detection",
            "error_statistics",
            "recovery_handler_registration",
            "fallback_handler_registration"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Engagement Error Handler health status."""
        recent_errors = self._get_recent_errors_for_component("error_handler")
        
        return {
            "status": "degraded" if self.system_degraded else "healthy",
            "total_errors_tracked": len(self.error_history),
            "recent_errors": len(recent_errors),
            "system_degraded": self.system_degraded,
            "components_in_fallback": len(self.component_fallback_modes),
            "recovery_handlers_registered": len(self.recovery_handlers),
            "fallback_handlers_registered": sum(len(handlers) for handlers in self.fallback_handlers.values()),
            "last_health_check": self.last_health_check.isoformat()
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Engagement Error Handler module information."""
        return {
            "module_id": self.module_id,
            "name": "Engagement Error Handler",
            "version": "1.0.0",
            "description": "Comprehensive error handling and resilience for engagement system"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when the error handler itself fails."""
        try:
            logger.critical(f"Error handler entering degradation mode due to: {error}")
            
            # Disable advanced error processing
            self.system_degraded = True
            
            # Clear error history to free memory
            if len(self.error_history) > 100:
                self.error_history = self.error_history[-100:]
            
            logger.info("Error handler degradation applied: simplified error processing")
            return True
            
        except Exception as degradation_error:
            logger.critical(f"Failed to apply error handler degradation: {degradation_error}")
            return False


logger = logging.getLogger(__name__)
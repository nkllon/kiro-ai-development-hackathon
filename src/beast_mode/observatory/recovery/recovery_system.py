"""
Automated WebSocket Recovery System

This module provides the main AutomatedRecoverySystem class that orchestrates
the entire recovery process with comprehensive logging and monitoring.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from .failure_classifier import FailureClassifier, FailureType, FailureContext
from .recovery_strategies import RecoveryStrategyManager, RecoveryResult
from .recovery_validator import RecoveryValidator, ValidationResult
from .recovery_coordinator import RecoveryCoordinator, RecoverySession

logger = logging.getLogger(__name__)


@dataclass
class RecoveryMetrics:
    """Metrics for recovery system performance"""
    total_recoveries: int = 0
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    average_recovery_time: float = 0.0
    last_recovery_time: Optional[datetime] = None
    consecutive_failures: int = 0
    recovery_rate_24h: float = 0.0


class AutomatedRecoverySystem:
    """
    Main automated recovery system that coordinates all recovery components
    """
    
    def __init__(self, 
                 auto_recovery_enabled: bool = True,
                 max_consecutive_failures: int = 5,
                 recovery_cooldown: float = 60.0):
        """
        Initialize the automated recovery system
        
        Args:
            auto_recovery_enabled: Whether automatic recovery is enabled
            max_consecutive_failures: Maximum consecutive failures before escalation
            recovery_cooldown: Minimum time between recovery attempts (seconds)
        """
        self.auto_recovery_enabled = auto_recovery_enabled
        self.max_consecutive_failures = max_consecutive_failures
        self.recovery_cooldown = recovery_cooldown
        
        # Initialize components
        self.failure_classifier = FailureClassifier()
        self.strategy_manager = RecoveryStrategyManager()
        self.recovery_validator = RecoveryValidator()
        self.coordinator = RecoveryCoordinator()
        
        # State tracking
        self.last_recovery_attempt: Optional[datetime] = None
        self.metrics = RecoveryMetrics()
        self.recovery_callbacks: List[Callable] = []
        
        self._log_action("automated_recovery_system_init", "completed", {
            "auto_recovery_enabled": auto_recovery_enabled,
            "max_consecutive_failures": max_consecutive_failures,
            "recovery_cooldown": recovery_cooldown
        })

    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None) -> None:
        """Log action in JSON format"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "4.1",
            "action": action,
            "status": status
        }
        if details:
            log_entry["details"] = details
        
        print(json.dumps(log_entry))
        logger.info(f"Automated recovery system action: {action} - {status}", extra=details)

    async def detect_failure(self, symptoms: List[str]) -> FailureType:
        """
        Detect failure type from symptoms
        
        Args:
            symptoms: List of failure symptoms/indicators
            
        Returns:
            FailureType: The detected failure type
        """
        self._log_action("detect_failure", "in_progress", {
            "symptoms_count": len(symptoms)
        })
        
        try:
            failure_type = await self.failure_classifier.detect_failure_symptoms(symptoms)
            
            self._log_action("detect_failure", "completed", {
                "failure_type": failure_type.value,
                "symptoms_analyzed": len(symptoms)
            })
            
            return failure_type
            
        except Exception as e:
            self._log_action("detect_failure", "error", {
                "error": str(e),
                "fallback_type": FailureType.UNKNOWN.value
            })
            return FailureType.UNKNOWN

    async def classify_failure(self, failure_data: Dict[str, Any]) -> FailureType:
        """
        Classify failure based on detailed failure data
        
        Args:
            failure_data: Detailed failure information
            
        Returns:
            FailureType: The classified failure type
        """
        self._log_action("classify_failure", "in_progress", {
            "failure_data_keys": list(failure_data.keys())
        })
        
        try:
            # Create failure context from data
            context = FailureContext(
                error_message=failure_data.get("error_message", ""),
                error_code=failure_data.get("error_code"),
                http_status=failure_data.get("http_status"),
                response_headers=failure_data.get("response_headers"),
                timestamp=failure_data.get("timestamp"),
                retry_count=failure_data.get("retry_count", 0),
                connection_duration=failure_data.get("connection_duration"),
                last_successful_connection=failure_data.get("last_successful_connection")
            )
            
            failure_type = await self.failure_classifier.classify_failure(context)
            
            self._log_action("classify_failure", "completed", {
                "failure_type": failure_type.value,
                "classification_method": "detailed_context"
            })
            
            return failure_type
            
        except Exception as e:
            self._log_action("classify_failure", "error", {
                "error": str(e),
                "fallback_type": FailureType.UNKNOWN.value
            })
            return FailureType.UNKNOWN

    async def execute_recovery(self, failure_type: FailureType) -> RecoveryResult:
        """
        Execute recovery for the given failure type
        
        Args:
            failure_type: The type of failure to recover from
            
        Returns:
            RecoveryResult: Result of the recovery operation
        """
        self._log_action("execute_recovery", "in_progress", {
            "failure_type": failure_type.value,
            "auto_recovery_enabled": self.auto_recovery_enabled
        })
        
        # Check if recovery is enabled
        if not self.auto_recovery_enabled:
            result = RecoveryResult(
                success=False,
                strategy_used=None,
                attempts_made=0,
                total_duration=0.0,
                error_message="Automatic recovery is disabled"
            )
            
            self._log_action("execute_recovery", "skipped", {
                "reason": "auto_recovery_disabled"
            })
            
            return result
        
        # Check cooldown period
        if self.last_recovery_attempt:
            time_since_last = (datetime.utcnow() - self.last_recovery_attempt).total_seconds()
            if time_since_last < self.recovery_cooldown:
                result = RecoveryResult(
                    success=False,
                    strategy_used=None,
                    attempts_made=0,
                    total_duration=0.0,
                    error_message=f"Recovery cooldown active: {self.recovery_cooldown - time_since_last:.1f}s remaining"
                )
                
                self._log_action("execute_recovery", "skipped", {
                    "reason": "cooldown_active",
                    "remaining_seconds": self.recovery_cooldown - time_since_last
                })
                
                return result
        
        try:
            # Update last recovery attempt time
            self.last_recovery_attempt = datetime.utcnow()
            
            # Execute recovery through strategy manager
            result = await self.strategy_manager.execute_recovery(failure_type, {})
            
            # Update metrics
            self.metrics.total_recoveries += 1
            if result.success:
                self.metrics.successful_recoveries += 1
                self.metrics.consecutive_failures = 0
            else:
                self.metrics.failed_recoveries += 1
                self.metrics.consecutive_failures += 1
            
            self.metrics.last_recovery_time = datetime.utcnow()
            self.metrics.average_recovery_time = (
                (self.metrics.average_recovery_time * (self.metrics.total_recoveries - 1) + result.total_duration) /
                self.metrics.total_recoveries
            )
            
            # Trigger callbacks
            await self._trigger_recovery_callbacks(result)
            
            self._log_action("execute_recovery", "completed", {
                "success": result.success,
                "strategy_used": result.strategy_used.value if result.strategy_used else None,
                "attempts_made": result.attempts_made,
                "total_duration": result.total_duration,
                "consecutive_failures": self.metrics.consecutive_failures
            })
            
            return result
            
        except Exception as e:
            self.metrics.failed_recoveries += 1
            self.metrics.consecutive_failures += 1
            
            result = RecoveryResult(
                success=False,
                strategy_used=None,
                attempts_made=0,
                total_duration=0.0,
                error_message=str(e)
            )
            
            self._log_action("execute_recovery", "error", {
                "error": str(e),
                "consecutive_failures": self.metrics.consecutive_failures
            })
            
            return result

    async def validate_recovery(self, recovery_attempt: Any) -> bool:
        """
        Validate that a recovery attempt was successful
        
        Args:
            recovery_attempt: The recovery attempt to validate
            
        Returns:
            bool: True if recovery is validated as successful
        """
        self._log_action("validate_recovery", "in_progress", {
            "recovery_attempt_type": type(recovery_attempt).__name__
        })
        
        try:
            # Use recovery validator to validate the attempt
            validation_result = await self.recovery_validator.validate_recovery(recovery_attempt)
            
            success = validation_result.overall_success
            
            self._log_action("validate_recovery", "completed", {
                "validation_success": success,
                "checks_performed": len(validation_result.checks_performed),
                "warnings_count": validation_result.warnings_count,
                "failures_count": validation_result.failures_count,
                "total_duration": validation_result.total_duration
            })
            
            return success
            
        except Exception as e:
            self._log_action("validate_recovery", "error", {
                "error": str(e)
            })
            return False

    async def full_recovery_cycle(self, symptoms: List[str], context: Dict[str, Any] = None) -> RecoverySession:
        """
        Execute a full recovery cycle from detection to validation
        
        Args:
            symptoms: List of failure symptoms
            context: Additional context information
            
        Returns:
            RecoverySession: Complete recovery session information
        """
        self._log_action("full_recovery_cycle", "in_progress", {
            "symptoms_count": len(symptoms),
            "context_provided": context is not None
        })
        
        try:
            # Use coordinator for full recovery cycle
            session = await self.coordinator.initiate_recovery(symptoms, context)
            
            # Update metrics based on session result
            if session.success:
                self.metrics.successful_recoveries += 1
                self.metrics.consecutive_failures = 0
            else:
                self.metrics.failed_recoveries += 1
                self.metrics.consecutive_failures += 1
            
            self.metrics.total_recoveries += 1
            self.metrics.last_recovery_time = datetime.utcnow()
            
            self._log_action("full_recovery_cycle", "completed", {
                "session_id": session.session_id,
                "success": session.success,
                "failure_type": session.failure_type.value if session.failure_type else None,
                "total_duration": (session.end_time - session.start_time).total_seconds() if session.end_time else 0
            })
            
            return session
            
        except Exception as e:
            self._log_action("full_recovery_cycle", "error", {
                "error": str(e)
            })
            
            # Create failed session
            failed_session = RecoverySession(
                session_id=f"failed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                success=False,
                error_message=str(e)
            )
            
            return failed_session

    def add_recovery_callback(self, callback: Callable) -> None:
        """Add a callback to be triggered after recovery attempts"""
        self.recovery_callbacks.append(callback)
        
        self._log_action("add_recovery_callback", "completed", {
            "callback_count": len(self.recovery_callbacks)
        })

    async def _trigger_recovery_callbacks(self, result: RecoveryResult) -> None:
        """Trigger all registered recovery callbacks"""
        for callback in self.recovery_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                self._log_action("trigger_recovery_callbacks", "error", {
                    "callback_error": str(e)
                })

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        coordinator_stats = self.coordinator.get_recovery_statistics()
        
        status = {
            "system_enabled": self.auto_recovery_enabled,
            "metrics": {
                "total_recoveries": self.metrics.total_recoveries,
                "successful_recoveries": self.metrics.successful_recoveries,
                "failed_recoveries": self.metrics.failed_recoveries,
                "success_rate": (
                    self.metrics.successful_recoveries / self.metrics.total_recoveries
                    if self.metrics.total_recoveries > 0 else 0.0
                ),
                "average_recovery_time": self.metrics.average_recovery_time,
                "consecutive_failures": self.metrics.consecutive_failures,
                "last_recovery_time": self.metrics.last_recovery_time.isoformat() if self.metrics.last_recovery_time else None
            },
            "coordinator_stats": coordinator_stats,
            "active_sessions": len(self.coordinator.active_sessions),
            "recovery_callbacks": len(self.recovery_callbacks),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._log_action("get_system_status", "completed", {
            "total_recoveries": self.metrics.total_recoveries,
            "success_rate": status["metrics"]["success_rate"]
        })
        
        return status

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        self._log_action("health_check", "in_progress", {})
        
        try:
            # Get coordinator health
            coordinator_health = await self.coordinator.health_check()
            
            # Check for escalation conditions
            escalation_needed = (
                self.metrics.consecutive_failures >= self.max_consecutive_failures
            )
            
            health_status = {
                "overall_health": "healthy",
                "escalation_needed": escalation_needed,
                "consecutive_failures": self.metrics.consecutive_failures,
                "max_consecutive_failures": self.max_consecutive_failures,
                "coordinator_health": coordinator_health,
                "system_metrics": {
                    "total_recoveries": self.metrics.total_recoveries,
                    "success_rate": (
                        self.metrics.successful_recoveries / self.metrics.total_recoveries
                        if self.metrics.total_recoveries > 0 else 0.0
                    )
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if escalation_needed:
                health_status["overall_health"] = "critical"
            elif coordinator_health.get("overall_health") == "warning":
                health_status["overall_health"] = "warning"
            
            self._log_action("health_check", "completed", {
                "overall_health": health_status["overall_health"],
                "escalation_needed": escalation_needed
            })
            
            return health_status
            
        except Exception as e:
            health_status = {
                "overall_health": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self._log_action("health_check", "error", {
                "error": str(e)
            })
            
            return health_status

    def enable_auto_recovery(self) -> None:
        """Enable automatic recovery"""
        self.auto_recovery_enabled = True
        
        self._log_action("enable_auto_recovery", "completed", {})

    def disable_auto_recovery(self) -> None:
        """Disable automatic recovery"""
        self.auto_recovery_enabled = False
        
        self._log_action("disable_auto_recovery", "completed", {})

    def reset_metrics(self) -> None:
        """Reset recovery metrics"""
        self.metrics = RecoveryMetrics()
        
        self._log_action("reset_metrics", "completed", {})
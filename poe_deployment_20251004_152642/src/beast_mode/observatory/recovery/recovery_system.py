"""
Automated WebSocket Recovery System

Main system that orchestrates automated recovery for WebSocket failures.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .failure_classifier import FailureClassifier, FailureType, FailureData
from .recovery_strategies import (
    RecoveryStrategy,
    WebSocketReconnectionStrategy,
    TunnelRestartStrategy,
    ConfigurationReloadStrategy,
    BotProtectionClearStrategy,
    FallbackActivationStrategy,
    RecoveryAttempt,
    RecoveryResult
)
from .recovery_validator import RecoveryValidator
from .recovery_coordinator import RecoveryCoordinator, RecoverySession


@dataclass
class SystemMetrics:
    """System metrics for monitoring."""
    total_failures_detected: int = 0
    total_recoveries_attempted: int = 0
    total_recoveries_successful: int = 0
    average_recovery_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_recovery_time: Optional[datetime] = None
    system_uptime: float = 0.0


class AutomatedRecoverySystem:
    """Main automated recovery system for WebSocket failures."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.failure_classifier = FailureClassifier()
        self.recovery_validator = RecoveryValidator()
        self.recovery_coordinator = RecoveryCoordinator()
        
        # Initialize recovery strategies
        self.recovery_strategies = [
            WebSocketReconnectionStrategy(),
            TunnelRestartStrategy(),
            TunnelRestartStrategy(),
            ConfigurationReloadStrategy(),
            BotProtectionClearStrategy()
        ]
        
        # System state
        self.is_active = False
        self.metrics = SystemMetrics()
        self.start_time = datetime.utcnow()
        
        # Configuration
        self.failure_detection_timeout = 30  # seconds
        self.recovery_timeout = 60  # seconds
        self.validation_timeout = 30  # seconds
        
    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "4.1",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        
    async def start(self):
        """Start the automated recovery system."""
        self._log_action("start_recovery_system", "in_progress")
        
        try:
            self.is_active = True
            self.start_time = datetime.utcnow()
            
            self._log_action("start_recovery_system", "completed", {
                "system_active": True,
                "start_time": self.start_time.isoformat(),
                "strategies_loaded": len(self.recovery_strategies)
            })
            
        except Exception as e:
            self._log_action("start_recovery_system", "error", {"error": str(e)})
            raise
    
    async def stop(self):
        """Stop the automated recovery system."""
        self._log_action("stop_recovery_system", "in_progress")
        
        try:
            self.is_active = False
            
            # Update metrics
            self.metrics.system_uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            self._log_action("stop_recovery_system", "completed", {
                "system_active": False,
                "total_uptime": self.metrics.system_uptime,
                "total_failures": self.metrics.total_failures_detected,
                "total_recoveries": self.metrics.total_recoveries_attempted,
                "success_rate": self._calculate_success_rate()
            })
            
        except Exception as e:
            self._log_action("stop_recovery_system", "error", {"error": str(e)})
            raise
    
    async def detect_failure(self, symptoms: List[str]) -> FailureType:
        """
        Detect failure type from symptoms.
        
        Args:
            symptoms: List of failure symptoms
            
        Returns:
            FailureType: The detected failure type
        """
        self._log_action("detect_failure", "in_progress", {
            "symptoms": symptoms,
            "symptom_count": len(symptoms)
        })
        
        try:
            # Update metrics
            self.metrics.total_failures_detected += 1
            self.metrics.last_failure_time = datetime.utcnow()
            
            # Detect failure type
            failure_type = await self.failure_classifier.detect_failure_from_symptoms(symptoms)
            
            self._log_action("detect_failure", "completed", {
                "failure_type": failure_type.value,
                "priority": self.failure_classifier.get_recovery_priority(failure_type),
                "estimated_recovery_time": self.failure_classifier.get_estimated_recovery_time(failure_type)
            })
            
            return failure_type
            
        except Exception as e:
            self._log_action("detect_failure", "error", {"error": str(e)})
            return FailureType.UNKNOWN
    
    async def classify_failure(self, failure_data: Dict[str, Any]) -> FailureType:
        """
        Classify failure from detailed failure data.
        
        Args:
            failure_data: Detailed failure information
            
        Returns:
            FailureType: The classified failure type
        """
        self._log_action("classify_failure", "in_progress", {
            "error_code": failure_data.get("error_code"),
            "error_message": failure_data.get("error_message"),
            "http_status": failure_data.get("http_status")
        })
        
        try:
            # Convert dict to FailureData
            failure_data_obj = FailureData(
                error_code=failure_data.get("error_code"),
                error_message=failure_data.get("error_message"),
                http_status=failure_data.get("http_status"),
                response_headers=failure_data.get("response_headers"),
                connection_attempts=failure_data.get("connection_attempts", 0),
                last_successful_connection=failure_data.get("last_successful_connection"),
                symptoms=failure_data.get("symptoms", [])
            )
            
            # Classify failure
            failure_type = await self.failure_classifier.classify_failure(failure_data_obj)
            
            self._log_action("classify_failure", "completed", {
                "failure_type": failure_type.value,
                "confidence": "high" if failure_type != FailureType.UNKNOWN else "low"
            })
            
            return failure_type
            
        except Exception as e:
            self._log_action("classify_failure", "error", {"error": str(e)})
            return FailureType.UNKNOWN
    
    async def execute_recovery(self, failure_type: FailureType) -> RecoveryResult:
        """
        Execute recovery for a specific failure type.
        
        Args:
            failure_type: The type of failure to recover from
            
        Returns:
            RecoveryResult: The result of the recovery attempt
        """
        self._log_action("execute_recovery", "in_progress", {
            "failure_type": failure_type.value,
            "system_active": self.is_active
        })
        
        if not self.is_active:
            self._log_action("execute_recovery", "error", {
                "error": "Recovery system is not active"
            })
            return RecoveryResult(
                success=False,
                strategy_used="none",
                recovery_time=0.0,
                error_message="Recovery system is not active"
            )
        
        try:
            # Update metrics
            self.metrics.total_recoveries_attempted += 1
            
            # Create failure data for coordination
            failure_data = FailureData(
                symptoms=[f"Recovery requested for {failure_type.value}"]
            )
            
            # Coordinate recovery
            recovery_session = await self.recovery_coordinator.coordinate_recovery(failure_data)
            
            # Update metrics
            if recovery_session.success:
                self.metrics.total_recoveries_successful += 1
                self.metrics.last_recovery_time = datetime.utcnow()
                
                # Update average recovery time
                total_time = self.metrics.average_recovery_time * (self.metrics.total_recoveries_successful - 1)
                self.metrics.average_recovery_time = (total_time + recovery_session.total_recovery_time) / self.metrics.total_recoveries_successful
            
            # Create recovery result
            recovery_result = RecoveryResult(
                success=recovery_session.success,
                strategy_used=recovery_session.final_strategy or "none",
                recovery_time=recovery_session.total_recovery_time,
                error_message=None if recovery_session.success else "Recovery failed",
                fallback_activated=recovery_session.final_strategy == "fallback_activation"
            )
            
            self._log_action("execute_recovery", "completed", {
                "success": recovery_session.success,
                "recovery_time": recovery_session.total_recovery_time,
                "attempts_made": len(recovery_session.attempts),
                "final_strategy": recovery_session.final_strategy,
                "session_id": recovery_session.session_id
            })
            
            return recovery_result
            
        except Exception as e:
            self._log_action("execute_recovery", "error", {"error": str(e)})
            
            return RecoveryResult(
                success=False,
                strategy_used="none",
                recovery_time=0.0,
                error_message=str(e)
            )
    
    async def validate_recovery(self, recovery_attempt: RecoveryAttempt) -> bool:
        """
        Validate a recovery attempt.
        
        Args:
            recovery_attempt: The recovery attempt to validate
            
        Returns:
            bool: True if recovery is valid
        """
        self._log_action("validate_recovery", "in_progress", {
            "strategy": recovery_attempt.strategy_name,
            "failure_type": recovery_attempt.failure_type.value,
            "attempt_number": recovery_attempt.attempt_number
        })
        
        try:
            # Validate recovery
            is_valid = await self.recovery_validator.verify_recovery_success(recovery_attempt)
            
            self._log_action("validate_recovery", "completed", {
                "is_valid": is_valid,
                "strategy": recovery_attempt.strategy_name
            })
            
            return is_valid
            
        except Exception as e:
            self._log_action("validate_recovery", "error", {"error": str(e)})
            return False
    
    async def handle_failure(self, symptoms: List[str], failure_data: Optional[Dict[str, Any]] = None) -> RecoveryResult:
        """
        Handle a failure by detecting, classifying, and recovering.
        
        Args:
            symptoms: List of failure symptoms
            failure_data: Optional detailed failure data
            
        Returns:
            RecoveryResult: The result of the recovery attempt
        """
        self._log_action("handle_failure", "in_progress", {
            "symptoms": symptoms,
            "has_failure_data": failure_data is not None
        })
        
        try:
            # Detect failure type
            if failure_data:
                failure_type = await self.classify_failure(failure_data)
            else:
                failure_type = await self.detect_failure(symptoms)
            
            # Execute recovery
            recovery_result = await self.execute_recovery(failure_type)
            
            self._log_action("handle_failure", "completed", {
                "failure_type": failure_type.value,
                "recovery_success": recovery_result.success,
                "recovery_time": recovery_result.recovery_time,
                "strategy_used": recovery_result.strategy_used
            })
            
            return recovery_result
            
        except Exception as e:
            self._log_action("handle_failure", "error", {"error": str(e)})
            
            return RecoveryResult(
                success=False,
                strategy_used="none",
                recovery_time=0.0,
                error_message=str(e)
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        current_time = datetime.utcnow()
        
        status = {
            "is_active": self.is_active,
            "uptime_seconds": (current_time - self.start_time).total_seconds(),
            "metrics": {
                "total_failures_detected": self.metrics.total_failures_detected,
                "total_recoveries_attempted": self.metrics.total_recoveries_attempted,
                "total_recoveries_successful": self.metrics.total_recoveries_successful,
                "success_rate": self._calculate_success_rate(),
                "average_recovery_time": self.metrics.average_recovery_time,
                "last_failure_time": self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                "last_recovery_time": self.metrics.last_recovery_time.isoformat() if self.metrics.last_recovery_time else None
            },
            "available_strategies": len(self.recovery_strategies),
            "configuration": {
                "failure_detection_timeout": self.failure_detection_timeout,
                "recovery_timeout": self.recovery_timeout,
                "validation_timeout": self.validation_timeout
            }
        }
        
        return status
    
    def _calculate_success_rate(self) -> float:
        """Calculate recovery success rate."""
        if self.metrics.total_recoveries_attempted == 0:
            return 0.0
        
        return self.metrics.total_recoveries_successful / self.metrics.total_recoveries_attempted
    
    async def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get detailed recovery statistics."""
        self._log_action("get_recovery_statistics", "in_progress")
        
        try:
            # Get statistics from coordinator
            coordinator_stats = await self.recovery_coordinator.get_recovery_statistics()
            
            # Combine with system metrics
            statistics = {
                "system_metrics": {
                    "total_failures_detected": self.metrics.total_failures_detected,
                    "total_recoveries_attempted": self.metrics.total_recoveries_attempted,
                    "total_recoveries_successful": self.metrics.total_recoveries_successful,
                    "success_rate": self._calculate_success_rate(),
                    "average_recovery_time": self.metrics.average_recovery_time,
                    "system_uptime": (datetime.utcnow() - self.start_time).total_seconds()
                },
                "coordinator_statistics": coordinator_stats,
                "available_strategies": self.recovery_coordinator.get_available_strategies()
            }
            
            self._log_action("get_recovery_statistics", "completed", {
                "total_strategies": len(statistics["available_strategies"]),
                "success_rate": statistics["system_metrics"]["success_rate"]
            })
            
            return statistics
            
        except Exception as e:
            self._log_action("get_recovery_statistics", "error", {"error": str(e)})
            
            return {
                "system_metrics": {
                    "total_failures_detected": self.metrics.total_failures_detected,
                    "total_recoveries_attempted": self.metrics.total_recoveries_attempted,
                    "total_recoveries_successful": self.metrics.total_recoveries_successful,
                    "success_rate": self._calculate_success_rate(),
                    "average_recovery_time": self.metrics.average_recovery_time,
                    "system_uptime": (datetime.utcnow() - self.start_time).total_seconds()
                },
                "error": str(e)
            }
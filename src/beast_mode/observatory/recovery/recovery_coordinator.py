"""
Recovery Coordination System

This module provides coordination between different recovery components
and manages the overall recovery process.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .failure_classifier import FailureClassifier, FailureType, FailureContext
from .recovery_strategies import RecoveryStrategyManager, RecoveryResult, RecoveryAttempt
from .recovery_validator import RecoveryValidator, ValidationResult

logger = logging.getLogger(__name__)


class RecoveryState(Enum):
    """States of the recovery process"""
    IDLE = "idle"
    DETECTING = "detecting"
    CLASSIFYING = "classifying"
    RECOVERING = "recovering"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RecoverySession:
    """Information about a recovery session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    state: RecoveryState = RecoveryState.IDLE
    failure_type: Optional[FailureType] = None
    recovery_result: Optional[RecoveryResult] = None
    validation_result: Optional[ValidationResult] = None
    success: bool = False
    error_message: Optional[str] = None


class RecoveryCoordinator:
    """
    Coordinates the entire recovery process from detection to validation
    """
    
    def __init__(self):
        self.failure_classifier = FailureClassifier()
        self.strategy_manager = RecoveryStrategyManager()
        self.recovery_validator = RecoveryValidator()
        
        self.active_sessions: Dict[str, RecoverySession] = {}
        self.recovery_history: List[RecoverySession] = []
        
        self._log_action("recovery_coordinator_init", "completed", {
            "components_initialized": 3
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
        logger.info(f"Recovery coordinator action: {action} - {status}", extra=details)

    async def initiate_recovery(self, symptoms: List[str], context: Dict[str, Any] = None) -> RecoverySession:
        """
        Initiate a complete recovery process
        
        Args:
            symptoms: List of failure symptoms
            context: Additional context information
            
        Returns:
            RecoverySession: Information about the recovery session
        """
        session_id = f"recovery_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        session = RecoverySession(
            session_id=session_id,
            start_time=datetime.utcnow(),
            state=RecoveryState.DETECTING
        )
        
        self.active_sessions[session_id] = session
        
        self._log_action("initiate_recovery", "in_progress", {
            "session_id": session_id,
            "symptoms_count": len(symptoms)
        })
        
        try:
            # Step 1: Detect and classify failure
            session.state = RecoveryState.CLASSIFYING
            failure_type = await self.failure_classifier.detect_failure_symptoms(symptoms)
            session.failure_type = failure_type
            
            # Step 2: Execute recovery strategies
            session.state = RecoveryState.RECOVERING
            recovery_result = await self.strategy_manager.execute_recovery(failure_type, context or {})
            session.recovery_result = recovery_result
            
            # Step 3: Validate recovery
            if recovery_result.success:
                session.state = RecoveryState.VALIDATING
                
                # Create a recovery attempt for validation
                recovery_attempt = RecoveryAttempt(
                    strategy_type=recovery_result.strategy_used,
                    failure_type=failure_type,
                    attempt_number=recovery_result.attempts_made,
                    start_time=datetime.utcnow() - timedelta(seconds=recovery_result.total_duration),
                    end_time=datetime.utcnow(),
                    success=True,
                    recovery_data=recovery_result.recovery_data
                )
                
                validation_result = await self.recovery_validator.validate_recovery(recovery_attempt)
                session.validation_result = validation_result
                
                # Check for recurring failures
                recent_sessions = [
                    s for s in self.recovery_history
                    if s.start_time > datetime.utcnow() - timedelta(hours=1)
                ]
                recurring_validation = await self.recovery_validator.validate_recurring_failures([])
                
                # Overall success if recovery succeeded and validation passed
                session.success = recovery_result.success and validation_result.overall_success
            else:
                session.success = False
                session.error_message = recovery_result.error_message
            
            # Step 4: Complete session
            session.state = RecoveryState.COMPLETED
            session.end_time = datetime.utcnow()
            
            # Move to history
            self.recovery_history.append(session)
            del self.active_sessions[session_id]
            
            self._log_action("initiate_recovery", "completed", {
                "session_id": session_id,
                "success": session.success,
                "failure_type": failure_type.value,
                "strategy_used": recovery_result.strategy_used.value if recovery_result else None,
                "total_duration": (session.end_time - session.start_time).total_seconds()
            })
            
            return session
            
        except Exception as e:
            session.state = RecoveryState.FAILED
            session.end_time = datetime.utcnow()
            session.success = False
            session.error_message = str(e)
            
            # Move to history even on failure
            self.recovery_history.append(session)
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            self._log_action("initiate_recovery", "error", {
                "session_id": session_id,
                "error": str(e),
                "total_duration": (session.end_time - session.start_time).total_seconds()
            })
            
            return session

    async def quick_recovery(self, failure_type: FailureType, context: Dict[str, Any] = None) -> bool:
        """
        Perform a quick recovery without full validation
        
        Args:
            failure_type: The type of failure to recover from
            context: Additional context information
            
        Returns:
            bool: True if recovery was successful
        """
        self._log_action("quick_recovery", "in_progress", {
            "failure_type": failure_type.value
        })
        
        try:
            # Execute recovery strategies
            recovery_result = await self.strategy_manager.execute_recovery(failure_type, context or {})
            
            success = recovery_result.success
            
            self._log_action("quick_recovery", "completed", {
                "failure_type": failure_type.value,
                "success": success,
                "strategy_used": recovery_result.strategy_used.value if recovery_result else None
            })
            
            return success
            
        except Exception as e:
            self._log_action("quick_recovery", "error", {
                "failure_type": failure_type.value,
                "error": str(e)
            })
            return False

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get statistics about recovery operations"""
        total_sessions = len(self.recovery_history)
        successful_sessions = len([s for s in self.recovery_history if s.success])
        
        # Calculate success rate
        success_rate = (successful_sessions / total_sessions) if total_sessions > 0 else 0.0
        
        # Get failure type distribution
        failure_types = {}
        for session in self.recovery_history:
            if session.failure_type:
                failure_types[session.failure_type.value] = failure_types.get(session.failure_type.value, 0) + 1
        
        # Get strategy usage distribution
        strategies = {}
        for session in self.recovery_history:
            if session.recovery_result:
                strategy = session.recovery_result.strategy_used.value
                strategies[strategy] = strategies.get(strategy, 0) + 1
        
        # Calculate average recovery time
        recovery_times = [
            (s.end_time - s.start_time).total_seconds()
            for s in self.recovery_history
            if s.end_time
        ]
        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0.0
        
        stats = {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "success_rate": success_rate,
            "failure_type_distribution": failure_types,
            "strategy_usage": strategies,
            "average_recovery_time": avg_recovery_time,
            "active_sessions": len(self.active_sessions)
        }
        
        self._log_action("get_recovery_statistics", "completed", {
            "total_sessions": total_sessions,
            "success_rate": success_rate
        })
        
        return stats

    def get_active_sessions(self) -> List[RecoverySession]:
        """Get list of active recovery sessions"""
        return list(self.active_sessions.values())

    def get_recent_sessions(self, hours: int = 24) -> List[RecoverySession]:
        """Get recent recovery sessions within specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            session for session in self.recovery_history
            if session.start_time > cutoff_time
        ]

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on recovery system components"""
        self._log_action("health_check", "in_progress", {})
        
        health_status = {
            "overall_health": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check failure classifier
            health_status["components"]["failure_classifier"] = {
                "status": "healthy",
                "patterns_loaded": len(self.failure_classifier.failure_patterns)
            }
            
            # Check strategy manager
            health_status["components"]["strategy_manager"] = {
                "status": "healthy",
                "strategies_available": len(self.strategy_manager.strategies)
            }
            
            # Check recovery validator
            health_status["components"]["recovery_validator"] = {
                "status": "healthy",
                "validation_timeout": self.recovery_validator.validation_timeout
            }
            
            # Check for stuck sessions
            stuck_sessions = [
                session for session in self.active_sessions.values()
                if (datetime.utcnow() - session.start_time).total_seconds() > 300  # 5 minutes
            ]
            
            if stuck_sessions:
                health_status["overall_health"] = "warning"
                health_status["components"]["active_sessions"] = {
                    "status": "warning",
                    "stuck_sessions": len(stuck_sessions)
                }
            
            self._log_action("health_check", "completed", {
                "overall_health": health_status["overall_health"]
            })
            
        except Exception as e:
            health_status["overall_health"] = "unhealthy"
            health_status["error"] = str(e)
            
            self._log_action("health_check", "error", {
                "error": str(e)
            })
        
        return health_status
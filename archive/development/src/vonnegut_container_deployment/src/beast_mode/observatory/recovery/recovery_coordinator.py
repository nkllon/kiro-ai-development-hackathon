"""
Recovery Coordinator

Coordinates recovery strategies and manages the recovery process.
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


@dataclass
class RecoverySession:
    """Data structure for a recovery session."""
    session_id: str
    failure_type: FailureType
    start_time: datetime
    end_time: Optional[datetime] = None
    attempts: List[RecoveryAttempt] = None
    success: bool = False
    total_recovery_time: float = 0.0
    final_strategy: Optional[str] = None
    
    def __post_init__(self):
        if self.attempts is None:
            self.attempts = []


class RecoveryCoordinator:
    """Coordinates recovery strategies and manages the recovery process."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.failure_classifier = FailureClassifier()
        self.recovery_validator = RecoveryValidator()
        
        # Initialize recovery strategies
        self.strategies = [
            WebSocketReconnectionStrategy(),
            TunnelRestartStrategy(),
            ConfigurationReloadStrategy(),
            BotProtectionClearStrategy(),
            FallbackActivationStrategy()
        ]
        
        # Sort strategies by priority
        self.strategies.sort(key=lambda s: s.get_priority())
        
        # Recovery configuration
        self.max_attempts = 3
        self.max_recovery_time = 300  # 5 minutes
        self.recovery_timeout = 60  # 1 minute per attempt
        
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
        
    async def coordinate_recovery(self, failure_data: FailureData) -> RecoverySession:
        """
        Coordinate the recovery process for a failure.
        
        Args:
            failure_data: Information about the failure
            
        Returns:
            RecoverySession: The recovery session results
        """
        session_id = f"recovery_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        self._log_action("coordinate_recovery", "in_progress", {
            "session_id": session_id,
            "failure_type": failure_data.error_message or "unknown",
            "symptoms": failure_data.symptoms
        })
        
        # Create recovery session
        session = RecoverySession(
            session_id=session_id,
            failure_type=FailureType.UNKNOWN,  # Will be updated after classification
            start_time=datetime.utcnow()
        )
        
        try:
            # Step 1: Classify the failure
            failure_type = await self.failure_classifier.classify_failure(failure_data)
            session.failure_type = failure_type
            
            self._log_action("failure_classified", "completed", {
                "session_id": session_id,
                "failure_type": failure_type.value,
                "priority": self.failure_classifier.get_recovery_priority(failure_type)
            })
            
            # Step 2: Select appropriate strategies
            applicable_strategies = await self._select_strategies(failure_type)
            
            self._log_action("strategies_selected", "completed", {
                "session_id": session_id,
                "applicable_strategies": [s.name for s in applicable_strategies],
                "strategy_count": len(applicable_strategies)
            })
            
            # Step 3: Execute recovery attempts
            recovery_success = await self._execute_recovery_attempts(
                session, applicable_strategies
            )
            
            session.success = recovery_success
            session.end_time = datetime.utcnow()
            session.total_recovery_time = (session.end_time - session.start_time).total_seconds()
            
            if recovery_success:
                self._log_action("coordinate_recovery", "completed", {
                    "session_id": session_id,
                    "success": True,
                    "total_recovery_time": session.total_recovery_time,
                    "attempts_made": len(session.attempts),
                    "final_strategy": session.final_strategy
                })
            else:
                self._log_action("coordinate_recovery", "failed", {
                    "session_id": session_id,
                    "success": False,
                    "total_recovery_time": session.total_recovery_time,
                    "attempts_made": len(session.attempts),
                    "max_attempts_reached": len(session.attempts) >= self.max_attempts
                })
            
            return session
            
        except Exception as e:
            session.end_time = datetime.utcnow()
            session.total_recovery_time = (session.end_time - session.start_time).total_seconds()
            
            self._log_action("coordinate_recovery", "error", {
                "session_id": session_id,
                "error": str(e),
                "total_recovery_time": session.total_recovery_time
            })
            
            return session
    
    async def _select_strategies(self, failure_type: FailureType) -> List[RecoveryStrategy]:
        """Select applicable strategies for the failure type."""
        applicable_strategies = []
        
        for strategy in self.strategies:
            if await strategy.can_handle(failure_type):
                applicable_strategies.append(strategy)
        
        return applicable_strategies
    
    async def _execute_recovery_attempts(
        self, 
        session: RecoverySession, 
        strategies: List[RecoveryStrategy]
    ) -> bool:
        """Execute recovery attempts using the selected strategies."""
        
        for attempt_number in range(1, self.max_attempts + 1):
            self._log_action("recovery_attempt", "in_progress", {
                "session_id": session.session_id,
                "attempt_number": attempt_number,
                "max_attempts": self.max_attempts
            })
            
            # Try each strategy in order of priority
            for strategy in strategies:
                try:
                    # Create recovery attempt
                    attempt = RecoveryAttempt(
                        strategy_name=strategy.name,
                        failure_type=session.failure_type,
                        attempt_number=attempt_number,
                        start_time=datetime.utcnow()
                    )
                    
                    # Execute strategy with timeout
                    recovery_result = await asyncio.wait_for(
                        strategy.execute(session.failure_type, attempt_number),
                        timeout=self.recovery_timeout
                    )
                    
                    attempt.end_time = datetime.utcnow()
                    attempt.success = recovery_result.success
                    attempt.error_message = recovery_result.error_message
                    attempt.recovery_data = {
                        "recovery_time": recovery_result.recovery_time,
                        "fallback_activated": recovery_result.fallback_activated
                    }
                    
                    session.attempts.append(attempt)
                    
                    if recovery_result.success:
                        # Validate the recovery
                        validation_success = await self.recovery_validator.verify_recovery_success(attempt)
                        
                        if validation_success:
                            session.final_strategy = strategy.name
                            
                            self._log_action("recovery_attempt", "completed", {
                                "session_id": session.session_id,
                                "attempt_number": attempt_number,
                                "strategy": strategy.name,
                                "success": True,
                                "recovery_time": recovery_result.recovery_time,
                                "validation_success": True
                            })
                            
                            return True
                        else:
                            self._log_action("recovery_attempt", "validation_failed", {
                                "session_id": session.session_id,
                                "attempt_number": attempt_number,
                                "strategy": strategy.name,
                                "recovery_success": True,
                                "validation_success": False
                            })
                    else:
                        self._log_action("recovery_attempt", "failed", {
                            "session_id": session.session_id,
                            "attempt_number": attempt_number,
                            "strategy": strategy.name,
                            "success": False,
                            "error": recovery_result.error_message
                        })
                        
                        # If fallback was activated, don't try other strategies
                        if recovery_result.fallback_activated:
                            session.final_strategy = strategy.name
                            return True
                
                except asyncio.TimeoutError:
                    self._log_action("recovery_attempt", "timeout", {
                        "session_id": session.session_id,
                        "attempt_number": attempt_number,
                        "strategy": strategy.name,
                        "timeout": self.recovery_timeout
                    })
                    
                    # Create failed attempt record
                    attempt = RecoveryAttempt(
                        strategy_name=strategy.name,
                        failure_type=session.failure_type,
                        attempt_number=attempt_number,
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow(),
                        success=False,
                        error_message="Recovery attempt timed out"
                    )
                    session.attempts.append(attempt)
                
                except Exception as e:
                    self._log_action("recovery_attempt", "error", {
                        "session_id": session.session_id,
                        "attempt_number": attempt_number,
                        "strategy": strategy.name,
                        "error": str(e)
                    })
                    
                    # Create failed attempt record
                    attempt = RecoveryAttempt(
                        strategy_name=strategy.name,
                        failure_type=session.failure_type,
                        attempt_number=attempt_number,
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow(),
                        success=False,
                        error_message=str(e)
                    )
                    session.attempts.append(attempt)
            
            # Check if we've exceeded max recovery time
            elapsed_time = (datetime.utcnow() - session.start_time).total_seconds()
            if elapsed_time > self.max_recovery_time:
                self._log_action("recovery_timeout", "reached", {
                    "session_id": session.session_id,
                    "elapsed_time": elapsed_time,
                    "max_recovery_time": self.max_recovery_time
                })
                break
            
            # Wait before next attempt (exponential backoff)
            if attempt_number < self.max_attempts:
                wait_time = min(2 ** attempt_number, 30)  # Max 30 seconds
                self._log_action("recovery_backoff", "waiting", {
                    "session_id": session.session_id,
                    "wait_time": wait_time,
                    "next_attempt": attempt_number + 1
                })
                await asyncio.sleep(wait_time)
        
        return False
    
    async def get_recovery_status(self, session_id: str) -> Optional[RecoverySession]:
        """Get the status of a recovery session."""
        # In a real implementation, this would retrieve from a persistent store
        # For now, we'll return None as sessions are not persisted
        return None
    
    async def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        self._log_action("get_recovery_statistics", "in_progress")
        
        # In a real implementation, this would aggregate statistics from persistent storage
        # For now, return mock statistics
        statistics = {
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "average_recovery_time": 0.0,
            "strategy_success_rates": {
                strategy.name: 0.0 for strategy in self.strategies
            },
            "failure_type_distribution": {
                failure_type.value: 0 for failure_type in FailureType
            }
        }
        
        self._log_action("get_recovery_statistics", "completed", statistics)
        
        return statistics
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """Get information about available recovery strategies."""
        strategies_info = []
        
        for strategy in self.strategies:
            strategies_info.append({
                "name": strategy.name,
                "priority": strategy.get_priority(),
                "description": self._get_strategy_description(strategy.name)
            })
        
        return strategies_info
    
    def _get_strategy_description(self, strategy_name: str) -> str:
        """Get description for a strategy."""
        descriptions = {
            "websocket_reconnection": "Simple WebSocket reconnection with exponential backoff",
            "tunnel_restart": "Restart cloudflared tunnel process",
            "configuration_reload": "Reload tunnel configuration and restart",
            "bot_protection_clear": "Wait for Cloudflare bot protection to clear",
            "fallback_activation": "Activate HTTP polling fallback mode"
        }
        
        return descriptions.get(strategy_name, "Unknown strategy")
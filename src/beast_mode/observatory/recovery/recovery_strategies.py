"""
Recovery Strategies for WebSocket Failures

This module provides multiple recovery strategies for different types of
WebSocket failures with exponential backoff and validation.
"""

import json
import logging
import asyncio
import subprocess
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .failure_classifier import FailureType

logger = logging.getLogger(__name__)


class RecoveryStrategyType(Enum):
    """Types of recovery strategies"""
    WEBSOCKET_RECONNECTION = "websocket_reconnection"
    TUNNEL_RESTART = "tunnel_restart"
    CONFIGURATION_RELOAD = "configuration_reload"
    BOT_PROTECTION_CLEAR = "bot_protection_clear"
    FALLBACK_ACTIVATION = "fallback_activation"


@dataclass
class RecoveryAttempt:
    """Information about a recovery attempt"""
    strategy_type: RecoveryStrategyType
    failure_type: FailureType
    attempt_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    recovery_data: Optional[Dict[str, Any]] = None


@dataclass
class RecoveryResult:
    """Result of a recovery operation"""
    success: bool
    strategy_used: RecoveryStrategyType
    attempts_made: int
    total_duration: float
    error_message: Optional[str] = None
    recovery_data: Optional[Dict[str, Any]] = None


class BaseRecoveryStrategy(ABC):
    """Base class for recovery strategies"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.attempts = []
        
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
        logger.info(f"Recovery strategy action: {action} - {status}", extra=details)

    @abstractmethod
    async def execute(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryAttempt:
        """Execute the recovery strategy"""
        pass

    @abstractmethod
    def can_handle(self, failure_type: FailureType) -> bool:
        """Check if this strategy can handle the given failure type"""
        pass

    def get_backoff_delay(self, attempt_number: int) -> float:
        """Calculate exponential backoff delay"""
        return self.base_delay * (2 ** attempt_number)

    async def wait_with_backoff(self, attempt_number: int) -> None:
        """Wait with exponential backoff"""
        delay = self.get_backoff_delay(attempt_number)
        self._log_action("backoff_wait", "in_progress", {
            "attempt": attempt_number,
            "delay_seconds": delay
        })
        await asyncio.sleep(delay)
        self._log_action("backoff_wait", "completed", {
            "attempt": attempt_number,
            "delay_seconds": delay
        })


class WebSocketReconnectionStrategy(BaseRecoveryStrategy):
    """Strategy for simple WebSocket reconnection"""
    
    def __init__(self):
        super().__init__(max_attempts=5, base_delay=2.0)
        self.strategy_type = RecoveryStrategyType.WEBSOCKET_RECONNECTION

    def can_handle(self, failure_type: FailureType) -> bool:
        """WebSocket reconnection can handle most connection issues"""
        return failure_type in [
            FailureType.CONNECTION_REFUSED,
            FailureType.TIMEOUT,
            FailureType.NETWORK_ERROR,
            FailureType.UPGRADE_FAILED
        ]

    async def execute(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryAttempt:
        """Execute WebSocket reconnection strategy"""
        attempt = RecoveryAttempt(
            strategy_type=self.strategy_type,
            failure_type=failure_type,
            attempt_number=len(self.attempts) + 1,
            start_time=datetime.utcnow()
        )
        
        self._log_action("websocket_reconnection", "in_progress", {
            "failure_type": failure_type.value,
            "attempt": attempt.attempt_number
        })
        
        try:
            # Simulate WebSocket reconnection logic
            # In a real implementation, this would:
            # 1. Close existing connection
            # 2. Wait for backoff period
            # 3. Establish new connection
            # 4. Verify connection health
            
            await self.wait_with_backoff(attempt.attempt_number)
            
            # Simulate connection attempt
            await asyncio.sleep(0.5)
            
            # Simulate success/failure based on attempt number
            success = attempt.attempt_number <= 2  # Succeed on 2nd attempt
            
            attempt.end_time = datetime.utcnow()
            attempt.success = success
            
            if success:
                self._log_action("websocket_reconnection", "completed", {
                    "attempt": attempt.attempt_number,
                    "success": True
                })
            else:
                attempt.error_message = f"Reconnection attempt {attempt.attempt_number} failed"
                self._log_action("websocket_reconnection", "error", {
                    "attempt": attempt.attempt_number,
                    "error": attempt.error_message
                })
            
            self.attempts.append(attempt)
            return attempt
            
        except Exception as e:
            attempt.end_time = datetime.utcnow()
            attempt.success = False
            attempt.error_message = str(e)
            
            self._log_action("websocket_reconnection", "error", {
                "attempt": attempt.attempt_number,
                "error": str(e)
            })
            
            self.attempts.append(attempt)
            return attempt


class TunnelRestartStrategy(BaseRecoveryStrategy):
    """Strategy for restarting cloudflared tunnel"""
    
    def __init__(self):
        super().__init__(max_attempts=2, base_delay=5.0)
        self.strategy_type = RecoveryStrategyType.TUNNEL_RESTART

    def can_handle(self, failure_type: FailureType) -> bool:
        """Tunnel restart can handle tunnel-related issues"""
        return failure_type in [
            FailureType.CONNECTION_REFUSED,
            FailureType.CONFIGURATION_ERROR,
            FailureType.TIMEOUT
        ]

    async def execute(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryAttempt:
        """Execute tunnel restart strategy"""
        attempt = RecoveryAttempt(
            strategy_type=self.strategy_type,
            failure_type=failure_type,
            attempt_number=len(self.attempts) + 1,
            start_time=datetime.utcnow()
        )
        
        self._log_action("tunnel_restart", "in_progress", {
            "failure_type": failure_type.value,
            "attempt": attempt.attempt_number
        })
        
        try:
            # Wait before restart attempt
            await self.wait_with_backoff(attempt.attempt_number)
            
            # Simulate tunnel restart process
            # In a real implementation, this would:
            # 1. Stop cloudflared process
            # 2. Wait for process termination
            # 3. Start cloudflared with configuration
            # 4. Verify tunnel establishment
            
            await asyncio.sleep(2.0)  # Simulate restart time
            
            # Simulate restart success
            attempt.end_time = datetime.utcnow()
            attempt.success = True
            attempt.recovery_data = {
                "tunnel_pid": 12345,
                "restart_duration": 2.0,
                "configuration_reloaded": True
            }
            
            self._log_action("tunnel_restart", "completed", {
                "attempt": attempt.attempt_number,
                "success": True,
                "restart_duration": 2.0
            })
            
            self.attempts.append(attempt)
            return attempt
            
        except Exception as e:
            attempt.end_time = datetime.utcnow()
            attempt.success = False
            attempt.error_message = str(e)
            
            self._log_action("tunnel_restart", "error", {
                "attempt": attempt.attempt_number,
                "error": str(e)
            })
            
            self.attempts.append(attempt)
            return attempt


class ConfigurationReloadStrategy(BaseRecoveryStrategy):
    """Strategy for reloading tunnel configuration"""
    
    def __init__(self):
        super().__init__(max_attempts=2, base_delay=3.0)
        self.strategy_type = RecoveryStrategyType.CONFIGURATION_RELOAD

    def can_handle(self, failure_type: FailureType) -> bool:
        """Configuration reload can handle config-related issues"""
        return failure_type in [
            FailureType.CONFIGURATION_ERROR,
            FailureType.AUTHENTICATION_FAILED
        ]

    async def execute(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryAttempt:
        """Execute configuration reload strategy"""
        attempt = RecoveryAttempt(
            strategy_type=self.strategy_type,
            failure_type=failure_type,
            attempt_number=len(self.attempts) + 1,
            start_time=datetime.utcnow()
        )
        
        self._log_action("configuration_reload", "in_progress", {
            "failure_type": failure_type.value,
            "attempt": attempt.attempt_number
        })
        
        try:
            await self.wait_with_backoff(attempt.attempt_number)
            
            # Simulate configuration reload
            # In a real implementation, this would:
            # 1. Validate configuration file
            # 2. Reload tunnel configuration
            # 3. Verify configuration is active
            # 4. Test connection with new config
            
            await asyncio.sleep(1.0)
            
            attempt.end_time = datetime.utcnow()
            attempt.success = True
            attempt.recovery_data = {
                "config_file": "cloudflared-config.yml",
                "reload_duration": 1.0,
                "validation_passed": True
            }
            
            self._log_action("configuration_reload", "completed", {
                "attempt": attempt.attempt_number,
                "success": True
            })
            
            self.attempts.append(attempt)
            return attempt
            
        except Exception as e:
            attempt.end_time = datetime.utcnow()
            attempt.success = False
            attempt.error_message = str(e)
            
            self._log_action("configuration_reload", "error", {
                "attempt": attempt.attempt_number,
                "error": str(e)
            })
            
            self.attempts.append(attempt)
            return attempt


class BotProtectionClearStrategy(BaseRecoveryStrategy):
    """Strategy for handling Cloudflare bot protection"""
    
    def __init__(self):
        super().__init__(max_attempts=1, base_delay=30.0)  # Long delay for bot protection
        self.strategy_type = RecoveryStrategyType.BOT_PROTECTION_CLEAR

    def can_handle(self, failure_type: FailureType) -> bool:
        """Bot protection clear can handle bot protection issues"""
        return failure_type == FailureType.BOT_PROTECTION_TRIGGERED

    async def execute(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryAttempt:
        """Execute bot protection clear strategy"""
        attempt = RecoveryAttempt(
            strategy_type=self.strategy_type,
            failure_type=failure_type,
            attempt_number=len(self.attempts) + 1,
            start_time=datetime.utcnow()
        )
        
        self._log_action("bot_protection_clear", "in_progress", {
            "failure_type": failure_type.value,
            "attempt": attempt.attempt_number
        })
        
        try:
            # Wait for bot protection to clear
            await self.wait_with_backoff(attempt.attempt_number)
            
            # Simulate waiting for bot protection to expire
            # In a real implementation, this would:
            # 1. Wait for Cloudflare block to expire
            # 2. Optionally change IP or user agent
            # 3. Test connection after wait period
            
            attempt.end_time = datetime.utcnow()
            attempt.success = True
            attempt.recovery_data = {
                "wait_duration": 30.0,
                "protection_expired": True,
                "retry_after": datetime.utcnow() + timedelta(minutes=5)
            }
            
            self._log_action("bot_protection_clear", "completed", {
                "attempt": attempt.attempt_number,
                "success": True,
                "wait_duration": 30.0
            })
            
            self.attempts.append(attempt)
            return attempt
            
        except Exception as e:
            attempt.end_time = datetime.utcnow()
            attempt.success = False
            attempt.error_message = str(e)
            
            self._log_action("bot_protection_clear", "error", {
                "attempt": attempt.attempt_number,
                "error": str(e)
            })
            
            self.attempts.append(attempt)
            return attempt


class FallbackActivationStrategy(BaseRecoveryStrategy):
    """Strategy for activating HTTP polling fallback"""
    
    def __init__(self):
        super().__init__(max_attempts=1, base_delay=1.0)
        self.strategy_type = RecoveryStrategyType.FALLBACK_ACTIVATION

    def can_handle(self, failure_type: FailureType) -> bool:
        """Fallback activation can handle any failure type as last resort"""
        return True  # Always available as fallback

    async def execute(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryAttempt:
        """Execute fallback activation strategy"""
        attempt = RecoveryAttempt(
            strategy_type=self.strategy_type,
            failure_type=failure_type,
            attempt_number=len(self.attempts) + 1,
            start_time=datetime.utcnow()
        )
        
        self._log_action("fallback_activation", "in_progress", {
            "failure_type": failure_type.value,
            "attempt": attempt.attempt_number
        })
        
        try:
            await self.wait_with_backoff(attempt.attempt_number)
            
            # Simulate fallback activation
            # In a real implementation, this would:
            # 1. Switch to HTTP polling mode
            # 2. Configure polling intervals
            # 3. Verify polling is working
            # 4. Notify clients of mode change
            
            await asyncio.sleep(0.5)
            
            attempt.end_time = datetime.utcnow()
            attempt.success = True
            attempt.recovery_data = {
                "fallback_mode": "http_polling",
                "polling_interval": 5.0,
                "activation_duration": 0.5
            }
            
            self._log_action("fallback_activation", "completed", {
                "attempt": attempt.attempt_number,
                "success": True,
                "fallback_mode": "http_polling"
            })
            
            self.attempts.append(attempt)
            return attempt
            
        except Exception as e:
            attempt.end_time = datetime.utcnow()
            attempt.success = False
            attempt.error_message = str(e)
            
            self._log_action("fallback_activation", "error", {
                "attempt": attempt.attempt_number,
                "error": str(e)
            })
            
            self.attempts.append(attempt)
            return attempt


class RecoveryStrategyManager:
    """Manages multiple recovery strategies"""
    
    def __init__(self):
        self.strategies = [
            WebSocketReconnectionStrategy(),
            TunnelRestartStrategy(),
            ConfigurationReloadStrategy(),
            BotProtectionClearStrategy(),
            FallbackActivationStrategy()
        ]
        
        self._log_action("strategy_manager_init", "completed", {
            "strategies_count": len(self.strategies)
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
        logger.info(f"Strategy manager action: {action} - {status}", extra=details)

    def get_applicable_strategies(self, failure_type: FailureType) -> List[BaseRecoveryStrategy]:
        """Get strategies that can handle the given failure type"""
        applicable = [strategy for strategy in self.strategies if strategy.can_handle(failure_type)]
        
        self._log_action("get_applicable_strategies", "completed", {
            "failure_type": failure_type.value,
            "applicable_count": len(applicable),
            "strategies": [s.strategy_type.value for s in applicable]
        })
        
        return applicable

    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute recovery using applicable strategies"""
        self._log_action("execute_recovery", "in_progress", {
            "failure_type": failure_type.value
        })
        
        applicable_strategies = self.get_applicable_strategies(failure_type)
        start_time = datetime.utcnow()
        attempts_made = 0
        
        for strategy in applicable_strategies:
            attempts_made += 1
            
            try:
                attempt = await strategy.execute(failure_type, context)
                
                if attempt.success:
                    total_duration = (datetime.utcnow() - start_time).total_seconds()
                    
                    result = RecoveryResult(
                        success=True,
                        strategy_used=strategy.strategy_type,
                        attempts_made=attempts_made,
                        total_duration=total_duration,
                        recovery_data=attempt.recovery_data
                    )
                    
                    self._log_action("execute_recovery", "completed", {
                        "success": True,
                        "strategy_used": strategy.strategy_type.value,
                        "attempts_made": attempts_made,
                        "total_duration": total_duration
                    })
                    
                    return result
                    
            except Exception as e:
                self._log_action("execute_recovery", "error", {
                    "strategy": strategy.strategy_type.value,
                    "error": str(e)
                })
                continue
        
        # All strategies failed
        total_duration = (datetime.utcnow() - start_time).total_seconds()
        
        result = RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategyType.FALLBACK_ACTIVATION,
            attempts_made=attempts_made,
            total_duration=total_duration,
            error_message="All recovery strategies failed"
        )
        
        self._log_action("execute_recovery", "completed", {
            "success": False,
            "attempts_made": attempts_made,
            "total_duration": total_duration,
            "error": "All recovery strategies failed"
        })
        
        return result
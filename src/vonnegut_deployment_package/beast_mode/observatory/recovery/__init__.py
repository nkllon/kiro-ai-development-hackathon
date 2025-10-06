"""
Automated WebSocket Recovery System

This module provides comprehensive automated recovery capabilities for WebSocket
connections with multiple strategies, failure classification, and validation.
"""

from .recovery_system import AutomatedRecoverySystem
from .failure_classifier import FailureClassifier, FailureType
from .recovery_strategies import (
    RecoveryStrategy,
    WebSocketReconnectionStrategy,
    TunnelRestartStrategy,
    ConfigurationReloadStrategy,
    BotProtectionClearStrategy,
    FallbackActivationStrategy
)
from .recovery_validator import RecoveryValidator, RecoveryResult
from .recovery_coordinator import RecoveryCoordinator

__all__ = [
    "AutomatedRecoverySystem",
    "FailureClassifier",
    "FailureType",
    "RecoveryStrategy",
    "WebSocketReconnectionStrategy",
    "TunnelRestartStrategy",
    "ConfigurationReloadStrategy",
    "BotProtectionClearStrategy",
    "FallbackActivationStrategy",
    "RecoveryValidator",
    "RecoveryResult",
    "RecoveryCoordinator"
]
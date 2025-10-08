"""
Engagement System Error Handling
================================

Comprehensive error handling and resilience framework for the Live Dashboard
Engagement System, providing systematic error recovery, fallback modes, and
graceful degradation capabilities.
"""

from .engagement_error_handler import (
    EngagementErrorHandler,
    EngagementErrorType,
    EngagementErrorSeverity,
    EngagementError,
    EngagementFallbackMode
)
from .resilience_manager import (
    EngagementResilienceManager,
    ResilienceStrategy,
    FallbackStrategy
)
from .error_recovery import (
    EngagementErrorRecovery,
    RecoveryAction,
    RecoveryResult
)

__all__ = [
    "EngagementErrorHandler",
    "EngagementErrorType", 
    "EngagementErrorSeverity",
    "EngagementError",
    "EngagementFallbackMode",
    "EngagementResilienceManager",
    "ResilienceStrategy",
    "FallbackStrategy",
    "EngagementErrorRecovery",
    "RecoveryAction",
    "RecoveryResult"
]
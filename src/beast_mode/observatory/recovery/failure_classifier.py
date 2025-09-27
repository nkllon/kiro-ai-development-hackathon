"""
Failure Classification System for WebSocket Recovery

This module provides comprehensive failure detection and classification
capabilities for WebSocket connection issues.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Enumeration of WebSocket failure types"""
    CONNECTION_REFUSED = "connection_refused"
    UPGRADE_FAILED = "upgrade_failed"
    TIMEOUT = "timeout"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMITED = "rate_limited"
    BOT_PROTECTION_TRIGGERED = "bot_protection_triggered"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN = "unknown"


@dataclass
class FailureContext:
    """Context information for a failure"""
    error_message: str
    error_code: Optional[int] = None
    http_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    timestamp: Optional[datetime] = None
    retry_count: int = 0
    connection_duration: Optional[float] = None
    last_successful_connection: Optional[datetime] = None


class FailureClassifier:
    """
    Classifies WebSocket failures into specific types for targeted recovery
    """
    
    def __init__(self):
        self.failure_patterns = {
            FailureType.CONNECTION_REFUSED: [
                r"connection refused",
                r"connection reset",
                r"refused to connect",
                r"ECONNREFUSED",
                r"tunnel.*not.*running"
            ],
            FailureType.UPGRADE_FAILED: [
                r"upgrade.*failed",
                r"websocket.*upgrade.*error",
                r"101.*switching.*protocols",
                r"invalid.*upgrade.*header"
            ],
            FailureType.TIMEOUT: [
                r"timeout",
                r"timed out",
                r"connection.*timeout",
                r"read.*timeout",
                r"ETIMEDOUT"
            ],
            FailureType.AUTHENTICATION_FAILED: [
                r"authentication.*failed",
                r"unauthorized",
                r"401",
                r"invalid.*credentials",
                r"auth.*error"
            ],
            FailureType.RATE_LIMITED: [
                r"rate.*limit",
                r"too.*many.*requests",
                r"429",
                r"throttled",
                r"quota.*exceeded"
            ],
            FailureType.BOT_PROTECTION_TRIGGERED: [
                r"1033",
                r"bot.*protection",
                r"cloudflare.*block",
                r"access.*denied.*cloudflare",
                r"ray.*id"
            ],
            FailureType.NETWORK_ERROR: [
                r"network.*error",
                r"dns.*resolution",
                r"no.*route.*to.*host",
                r"EHOSTUNREACH",
                r"ENETUNREACH"
            ],
            FailureType.CONFIGURATION_ERROR: [
                r"configuration.*error",
                r"invalid.*config",
                r"missing.*config",
                r"config.*not.*found"
            ]
        }
        
        self._log_action("failure_classifier_init", "completed", {
            "patterns_count": sum(len(patterns) for patterns in self.failure_patterns.values())
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
        logger.info(f"Recovery action: {action} - {status}", extra=details)

    async def classify_failure(self, failure_context: FailureContext) -> FailureType:
        """
        Classify a failure based on context information
        
        Args:
            failure_context: Context information about the failure
            
        Returns:
            FailureType: The classified failure type
        """
        self._log_action("classify_failure", "in_progress", {
            "error_message": failure_context.error_message[:100],
            "error_code": failure_context.error_code,
            "http_status": failure_context.http_status
        })
        
        try:
            # Primary classification based on error codes
            failure_type = self._classify_by_error_code(failure_context)
            if failure_type != FailureType.UNKNOWN:
                self._log_action("classify_failure", "completed", {
                    "failure_type": failure_type.value,
                    "method": "error_code"
                })
                return failure_type
            
            # Secondary classification based on error message patterns
            failure_type = self._classify_by_message_pattern(failure_context.error_message)
            if failure_type != FailureType.UNKNOWN:
                self._log_action("classify_failure", "completed", {
                    "failure_type": failure_type.value,
                    "method": "message_pattern"
                })
                return failure_type
            
            # Tertiary classification based on HTTP status
            failure_type = self._classify_by_http_status(failure_context.http_status)
            if failure_type != FailureType.UNKNOWN:
                self._log_action("classify_failure", "completed", {
                    "failure_type": failure_type.value,
                    "method": "http_status"
                })
                return failure_type
            
            # Fallback classification based on context analysis
            failure_type = self._classify_by_context_analysis(failure_context)
            
            self._log_action("classify_failure", "completed", {
                "failure_type": failure_type.value,
                "method": "context_analysis"
            })
            return failure_type
            
        except Exception as e:
            self._log_action("classify_failure", "error", {
                "error": str(e),
                "fallback_type": FailureType.UNKNOWN.value
            })
            return FailureType.UNKNOWN

    def _classify_by_error_code(self, context: FailureContext) -> FailureType:
        """Classify failure based on error codes"""
        if context.error_code is None:
            return FailureType.UNKNOWN
            
        error_code_mapping = {
            1033: FailureType.BOT_PROTECTION_TRIGGERED,
            401: FailureType.AUTHENTICATION_FAILED,
            429: FailureType.RATE_LIMITED,
            101: FailureType.UPGRADE_FAILED,
        }
        
        return error_code_mapping.get(context.error_code, FailureType.UNKNOWN)

    def _classify_by_message_pattern(self, error_message: str) -> FailureType:
        """Classify failure based on error message patterns"""
        if not error_message:
            return FailureType.UNKNOWN
            
        error_message_lower = error_message.lower()
        
        for failure_type, patterns in self.failure_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message_lower, re.IGNORECASE):
                    return failure_type
        
        return FailureType.UNKNOWN

    def _classify_by_http_status(self, http_status: Optional[int]) -> FailureType:
        """Classify failure based on HTTP status codes"""
        if http_status is None:
            return FailureType.UNKNOWN
            
        status_mapping = {
            401: FailureType.AUTHENTICATION_FAILED,
            429: FailureType.RATE_LIMITED,
            101: FailureType.UPGRADE_FAILED,
            500: FailureType.CONFIGURATION_ERROR,
            502: FailureType.CONNECTION_REFUSED,
            503: FailureType.CONNECTION_REFUSED,
            504: FailureType.TIMEOUT,
        }
        
        return status_mapping.get(http_status, FailureType.UNKNOWN)

    def _classify_by_context_analysis(self, context: FailureContext) -> FailureType:
        """Classify failure based on contextual analysis"""
        # Analyze retry patterns
        if context.retry_count > 5:
            return FailureType.RATE_LIMITED
        
        # Analyze connection duration
        if context.connection_duration and context.connection_duration < 1.0:
            return FailureType.CONNECTION_REFUSED
        
        # Analyze time since last successful connection
        if context.last_successful_connection:
            time_since_success = (datetime.utcnow() - context.last_successful_connection).total_seconds()
            if time_since_success > 3600:  # 1 hour
                return FailureType.CONFIGURATION_ERROR
        
        # Default to network error for unclassified cases
        return FailureType.NETWORK_ERROR

    async def detect_failure_symptoms(self, symptoms: List[str]) -> FailureType:
        """
        Detect failure type from a list of symptoms
        
        Args:
            symptoms: List of failure symptoms/indicators
            
        Returns:
            FailureType: The detected failure type
        """
        self._log_action("detect_failure_symptoms", "in_progress", {
            "symptoms_count": len(symptoms)
        })
        
        # Combine all symptoms into a single context
        combined_message = " ".join(symptoms)
        context = FailureContext(error_message=combined_message)
        
        failure_type = await self.classify_failure(context)
        
        self._log_action("detect_failure_symptoms", "completed", {
            "failure_type": failure_type.value,
            "symptoms_analyzed": len(symptoms)
        })
        
        return failure_type

    def get_recovery_priority(self, failure_type: FailureType) -> int:
        """
        Get recovery priority for a failure type (lower number = higher priority)
        
        Args:
            failure_type: The failure type
            
        Returns:
            int: Priority level (1-10, where 1 is highest priority)
        """
        priority_mapping = {
            FailureType.CONNECTION_REFUSED: 1,
            FailureType.UPGRADE_FAILED: 2,
            FailureType.TIMEOUT: 3,
            FailureType.AUTHENTICATION_FAILED: 4,
            FailureType.CONFIGURATION_ERROR: 5,
            FailureType.NETWORK_ERROR: 6,
            FailureType.RATE_LIMITED: 7,
            FailureType.BOT_PROTECTION_TRIGGERED: 8,
            FailureType.UNKNOWN: 9
        }
        
        return priority_mapping.get(failure_type, 9)

    def is_recoverable(self, failure_type: FailureType) -> bool:
        """
        Determine if a failure type is recoverable
        
        Args:
            failure_type: The failure type
            
        Returns:
            bool: True if recoverable, False otherwise
        """
        # All failure types are considered recoverable in this implementation
        # In a production system, some might be marked as non-recoverable
        return True
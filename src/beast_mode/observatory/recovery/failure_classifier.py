"""
Failure Classification System

Classifies WebSocket failures into specific types for targeted recovery strategies.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class FailureType(Enum):
    """Types of WebSocket failures that can occur."""
    CONNECTION_REFUSED = "connection_refused"
    UPGRADE_FAILED = "upgrade_failed"
    TIMEOUT = "timeout"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMITED = "rate_limited"
    BOT_PROTECTION_TRIGGERED = "bot_protection_triggered"
    UNKNOWN = "unknown"


@dataclass
class FailureData:
    """Data structure containing failure information."""
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    http_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    connection_attempts: int = 0
    last_successful_connection: Optional[datetime] = None
    symptoms: List[str] = None
    
    def __post_init__(self):
        if self.symptoms is None:
            self.symptoms = []


class FailureClassifier:
    """Classifies WebSocket failures into specific types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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
        
    async def classify_failure(self, failure_data: FailureData) -> FailureType:
        """
        Classify a failure based on symptoms and error data.
        
        Args:
            failure_data: Information about the failure
            
        Returns:
            FailureType: The classified failure type
        """
        self._log_action("classify_failure", "in_progress", {
            "error_code": failure_data.error_code,
            "error_message": failure_data.error_message,
            "http_status": failure_data.http_status,
            "symptoms": failure_data.symptoms
        })
        
        try:
            failure_type = await self._analyze_failure(failure_data)
            
            self._log_action("classify_failure", "completed", {
                "failure_type": failure_type.value,
                "confidence": "high" if failure_type != FailureType.UNKNOWN else "low"
            })
            
            return failure_type
            
        except Exception as e:
            self._log_action("classify_failure", "error", {
                "error": str(e),
                "fallback_type": FailureType.UNKNOWN.value
            })
            return FailureType.UNKNOWN
    
    async def _analyze_failure(self, failure_data: FailureData) -> FailureType:
        """Analyze failure data to determine failure type."""
        
        # Check for specific error codes
        if failure_data.error_code == 1033:
            return FailureType.BOT_PROTECTION_TRIGGERED
            
        # Check HTTP status codes
        if failure_data.http_status:
            if failure_data.http_status == 429:
                return FailureType.RATE_LIMITED
            elif failure_data.http_status == 401:
                return FailureType.AUTHENTICATION_FAILED
            elif failure_data.http_status == 403:
                return FailureType.BOT_PROTECTION_TRIGGERED
            elif failure_data.http_status in [502, 503, 504]:
                return FailureType.CONNECTION_REFUSED
                
        # Check error messages for patterns
        if failure_data.error_message:
            error_msg = failure_data.error_message.lower()
            
            if "timeout" in error_msg or "timed out" in error_msg:
                return FailureType.TIMEOUT
            elif "connection refused" in error_msg:
                return FailureType.CONNECTION_REFUSED
            elif "upgrade" in error_msg and "failed" in error_msg:
                return FailureType.UPGRADE_FAILED
            elif "authentication" in error_msg or "unauthorized" in error_msg:
                return FailureType.AUTHENTICATION_FAILED
            elif "rate limit" in error_msg or "too many" in error_msg:
                return FailureType.RATE_LIMITED
            elif "cloudflare" in error_msg or "bot" in error_msg:
                return FailureType.BOT_PROTECTION_TRIGGERED
                
        # Check symptoms for patterns
        for symptom in failure_data.symptoms:
            symptom_lower = symptom.lower()
            
            if "connection refused" in symptom_lower:
                return FailureType.CONNECTION_REFUSED
            elif "timeout" in symptom_lower:
                return FailureType.TIMEOUT
            elif "upgrade failed" in symptom_lower:
                return FailureType.UPGRADE_FAILED
            elif "authentication" in symptom_lower:
                return FailureType.AUTHENTICATION_FAILED
            elif "rate limit" in symptom_lower:
                return FailureType.RATE_LIMITED
            elif "cloudflare" in symptom_lower or "bot protection" in symptom_lower:
                return FailureType.BOT_PROTECTION_TRIGGERED
                
        # Check connection attempt patterns
        if failure_data.connection_attempts > 10:
            return FailureType.RATE_LIMITED
            
        # Check response headers for Cloudflare indicators
        if failure_data.response_headers:
            cf_ray = failure_data.response_headers.get("cf-ray")
            cf_cache_status = failure_data.response_headers.get("cf-cache-status")
            
            if cf_ray or cf_cache_status:
                return FailureType.BOT_PROTECTION_TRIGGERED
                
        return FailureType.UNKNOWN
    
    async def detect_failure_from_symptoms(self, symptoms: List[str]) -> FailureType:
        """
        Detect failure type from a list of symptoms.
        
        Args:
            symptoms: List of failure symptoms
            
        Returns:
            FailureType: The detected failure type
        """
        self._log_action("detect_failure_from_symptoms", "in_progress", {
            "symptoms": symptoms
        })
        
        failure_data = FailureData(symptoms=symptoms)
        failure_type = await self.classify_failure(failure_data)
        
        self._log_action("detect_failure_from_symptoms", "completed", {
            "failure_type": failure_type.value,
            "symptoms_count": len(symptoms)
        })
        
        return failure_type
    
    def get_recovery_priority(self, failure_type: FailureType) -> int:
        """
        Get recovery priority for a failure type.
        Lower numbers indicate higher priority.
        
        Args:
            failure_type: The failure type
            
        Returns:
            int: Priority level (1-5, where 1 is highest priority)
        """
        priority_map = {
            FailureType.CONNECTION_REFUSED: 1,
            FailureType.UPGRADE_FAILED: 2,
            FailureType.TIMEOUT: 2,
            FailureType.AUTHENTICATION_FAILED: 3,
            FailureType.RATE_LIMITED: 4,
            FailureType.BOT_PROTECTION_TRIGGERED: 5,
            FailureType.UNKNOWN: 3
        }
        
        return priority_map.get(failure_type, 3)
    
    def get_estimated_recovery_time(self, failure_type: FailureType) -> int:
        """
        Get estimated recovery time in seconds for a failure type.
        
        Args:
            failure_type: The failure type
            
        Returns:
            int: Estimated recovery time in seconds
        """
        recovery_time_map = {
            FailureType.CONNECTION_REFUSED: 30,
            FailureType.UPGRADE_FAILED: 45,
            FailureType.TIMEOUT: 60,
            FailureType.AUTHENTICATION_FAILED: 30,
            FailureType.RATE_LIMITED: 120,
            FailureType.BOT_PROTECTION_TRIGGERED: 300,
            FailureType.UNKNOWN: 60
        }
        
        return recovery_time_map.get(failure_type, 60)
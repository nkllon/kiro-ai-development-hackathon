"""
Custom exceptions for AI Consultation System

These exceptions provide specific error handling for various failure modes
in the AI consultation system.
"""

from typing import Optional, Dict, Any


class ConsultationError(Exception):
    """Base exception for AI consultation system errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_possible: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CONSULTATION_ERROR"
        self.details = details or {}
        self.retry_possible = retry_possible
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error_code": self.error_code,
            "error_message": self.message,
            "details": self.details,
            "retry_possible": self.retry_possible
        }


class CostLimitExceededError(ConsultationError):
    """Raised when cost limits are exceeded"""
    
    def __init__(
        self, 
        message: str = "Cost limit exceeded", 
        current_cost: Optional[float] = None,
        limit: Optional[float] = None,
        budget_type: str = "daily"
    ):
        details = {
            "current_cost": current_cost,
            "limit": limit,
            "budget_type": budget_type
        }
        super().__init__(
            message=message,
            error_code="COST_LIMIT_EXCEEDED",
            details=details,
            retry_possible=False  # Don't retry until budget resets
        )


class QueueFullError(ConsultationError):
    """Raised when the query queue is at capacity"""
    
    def __init__(
        self, 
        message: str = "Query queue is at capacity", 
        queue_size: Optional[int] = None,
        capacity: Optional[int] = None
    ):
        details = {
            "queue_size": queue_size,
            "capacity": capacity
        }
        super().__init__(
            message=message,
            error_code="QUEUE_FULL",
            details=details,
            retry_possible=True  # Can retry later when queue has space
        )


class ContextUnavailableError(ConsultationError):
    """Raised when Observatory context cannot be retrieved"""
    
    def __init__(
        self, 
        message: str = "Observatory context unavailable", 
        context_type: Optional[str] = None,
        fallback_available: bool = False
    ):
        details = {
            "context_type": context_type,
            "fallback_available": fallback_available
        }
        super().__init__(
            message=message,
            error_code="CONTEXT_UNAVAILABLE",
            details=details,
            retry_possible=True  # Context might become available later
        )


class LLMServiceError(ConsultationError):
    """Raised when LLM service is unavailable or returns errors"""
    
    def __init__(
        self, 
        message: str = "LLM service error", 
        service_status: Optional[str] = None,
        api_error_code: Optional[str] = None
    ):
        details = {
            "service_status": service_status,
            "api_error_code": api_error_code
        }
        super().__init__(
            message=message,
            error_code="LLM_SERVICE_ERROR",
            details=details,
            retry_possible=True  # LLM service might recover
        )


class AuthenticationError(ConsultationError):
    """Raised when user authentication fails"""
    
    def __init__(
        self, 
        message: str = "Authentication failed", 
        user_id: Optional[str] = None
    ):
        details = {
            "user_id": user_id
        }
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            retry_possible=False  # Don't retry auth failures
        )


class PermissionError(ConsultationError):
    """Raised when user lacks required permissions"""
    
    def __init__(
        self, 
        message: str = "Insufficient permissions", 
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None
    ):
        details = {
            "user_id": user_id,
            "required_permission": required_permission
        }
        super().__init__(
            message=message,
            error_code="PERMISSION_ERROR",
            details=details,
            retry_possible=False  # Don't retry permission failures
        )


class ValidationError(ConsultationError):
    """Raised when input validation fails"""
    
    def __init__(
        self, 
        message: str = "Input validation failed", 
        field: Optional[str] = None,
        value: Optional[str] = None
    ):
        details = {
            "field": field,
            "value": value
        }
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            retry_possible=False  # Don't retry validation failures
        )


class CircuitBreakerOpenError(ConsultationError):
    """Raised when circuit breaker is open"""
    
    def __init__(
        self, 
        message: str = "Circuit breaker is open", 
        service: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        details = {
            "service": service,
            "retry_after_seconds": retry_after
        }
        super().__init__(
            message=message,
            error_code="CIRCUIT_BREAKER_OPEN",
            details=details,
            retry_possible=True  # Can retry after circuit breaker closes
        )


class FeatureFlagDisabledError(ConsultationError):
    """Raised when a feature is disabled via feature flag"""
    
    def __init__(
        self, 
        message: str = "Feature is currently disabled", 
        feature: Optional[str] = None
    ):
        details = {
            "feature": feature
        }
        super().__init__(
            message=message,
            error_code="FEATURE_DISABLED",
            details=details,
            retry_possible=True  # Feature might be enabled later
        )


class VisualRegressionError(ConsultationError):
    """Raised when visual regression testing encounters errors"""
    
    def __init__(
        self, 
        message: str = "Visual regression testing error", 
        error_code: Optional[str] = None,
        test_id: Optional[str] = None,
        severity: Optional[str] = None
    ):
        details = {
            "test_id": test_id,
            "severity": severity
        }
        super().__init__(
            message=message,
            error_code=error_code or "VISUAL_REGRESSION_ERROR",
            details=details,
            retry_possible=True  # Visual tests can usually be retried
        )


class ProcessingError(ConsultationError):
    """Raised when processing operations fail"""
    
    def __init__(
        self, 
        message: str = "Processing operation failed", 
        operation: Optional[str] = None,
        stage: Optional[str] = None
    ):
        details = {
            "operation": operation,
            "stage": stage
        }
        super().__init__(
            message=message,
            error_code="PROCESSING_ERROR",
            details=details,
            retry_possible=True  # Processing can usually be retried
        )
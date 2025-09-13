"""
DevPost Integration Exceptions

Custom exception classes for DevPost integration error handling.
"""

from typing import Optional, Dict, Any


class DevPostIntegrationError(Exception):
    """Base exception for DevPost integration errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DevPostAPIError(DevPostIntegrationError):
    """API-related errors"""
    pass


class DevPostAuthenticationError(DevPostIntegrationError):
    """Authentication-related errors"""
    pass


class DevPostConfigurationError(DevPostIntegrationError):
    """Configuration-related errors"""
    pass


class DevPostSyncError(DevPostIntegrationError):
    """Synchronization-related errors"""
    pass


class DevPostValidationError(DevPostIntegrationError):
    """Validation-related errors"""
    pass


class DevPostRateLimitError(DevPostIntegrationError):
    """Rate limiting errors"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class DevPostNetworkError(DevPostIntegrationError):
    """Network-related errors"""
    pass


class DevPostFileError(DevPostIntegrationError):
    """File operation errors"""
    pass


class DevPostProjectError(DevPostIntegrationError):
    """Project-related errors"""
    pass

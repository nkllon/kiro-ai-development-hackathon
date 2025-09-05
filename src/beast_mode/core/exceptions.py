"""
Core exception classes for Beast Mode system.

This module defines base exceptions that can be used across all Beast Mode
components for consistent error handling and reporting.
"""


class BeastModeError(Exception):
    """Base exception for all Beast Mode system errors."""
    
    def __init__(self, message: str, component: str = None, operation: str = None):
        super().__init__(message)
        self.component = component
        self.operation = operation
        self.message = message
    
    def __str__(self):
        parts = [self.message]
        if self.component:
            parts.append(f"Component: {self.component}")
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        return " | ".join(parts)


class ConfigurationError(BeastModeError):
    """Errors related to system configuration."""
    pass


class AuthenticationError(BeastModeError):
    """Errors related to authentication operations."""
    pass


class NetworkError(BeastModeError):
    """Errors related to network operations."""
    pass


class ValidationError(BeastModeError):
    """Errors related to data validation."""
    pass


class IntegrationError(BeastModeError):
    """Errors related to external service integrations."""
    pass


class FileSystemError(BeastModeError):
    """Errors related to file system operations."""
    pass
"""
Exception classes for Discord Bot Integration

Designed for easy extraction to standalone framework.
"""

from typing import Optional, Dict, Any


class DiscordBotError(Exception):
    """Base exception for Discord bot errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(DiscordBotError):
    """Raised when bot configuration is invalid"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, error_code="CONFIGURATION_ERROR")
        self.config_key = config_key


class ServiceUnavailableError(DiscordBotError):
    """Raised when required service is unavailable"""
    
    def __init__(self, service_name: str, message: Optional[str] = None):
        msg = message or f"Service '{service_name}' is unavailable"
        super().__init__(msg, error_code="SERVICE_UNAVAILABLE")
        self.service_name = service_name


class PermissionError(DiscordBotError):
    """Raised when bot lacks required permissions"""
    
    def __init__(self, permission: str, resource: Optional[str] = None):
        msg = f"Missing permission '{permission}'"
        if resource:
            msg += f" for resource '{resource}'"
        super().__init__(msg, error_code="PERMISSION_DENIED")
        self.permission = permission
        self.resource = resource


class RateLimitError(DiscordBotError):
    """Raised when Discord API rate limits are exceeded"""
    
    def __init__(self, retry_after: float, endpoint: Optional[str] = None):
        msg = f"Rate limit exceeded, retry after {retry_after} seconds"
        if endpoint:
            msg += f" for endpoint '{endpoint}'"
        super().__init__(msg, error_code="RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after
        self.endpoint = endpoint


class AuthenticationError(DiscordBotError):
    """Raised when Discord authentication fails"""
    
    def __init__(self, message: str = "Discord authentication failed"):
        super().__init__(message, error_code="AUTHENTICATION_FAILED")


class CommandError(DiscordBotError):
    """Raised when command execution fails"""
    
    def __init__(self, command: str, message: str, user_friendly: bool = True):
        super().__init__(message, error_code="COMMAND_ERROR")
        self.command = command
        self.user_friendly = user_friendly


class ValidationError(DiscordBotError):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field
        self.value = value


class SecurityError(DiscordBotError):
    """Raised when security violations are detected"""
    
    def __init__(self, message: str, severity: str = "medium"):
        super().__init__(message, error_code="SECURITY_VIOLATION")
        self.severity = severity


class PluginError(DiscordBotError):
    """Raised when plugin operations fail"""
    
    def __init__(self, plugin_name: str, message: str):
        super().__init__(f"Plugin '{plugin_name}': {message}", error_code="PLUGIN_ERROR")
        self.plugin_name = plugin_name


class CircuitBreakerError(DiscordBotError):
    """Raised when circuit breaker is open"""
    
    def __init__(self, service_name: str, failure_count: int):
        msg = f"Circuit breaker open for '{service_name}' after {failure_count} failures"
        super().__init__(msg, error_code="CIRCUIT_BREAKER_OPEN")
        self.service_name = service_name
        self.failure_count = failure_count
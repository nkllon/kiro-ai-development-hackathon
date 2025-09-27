"""Custom exceptions for WebSocket operations."""

from typing import Optional


class WebSocketError(Exception):
    """Base exception for WebSocket-related errors."""

    def __init__(self, message: str, endpoint: Optional[str] = None):
        self.message = message
        self.endpoint = endpoint
        super().__init__(message)


class ConnectionFailedError(WebSocketError):
    """Raised when WebSocket connection fails."""
    pass


class ConnectionTimeoutError(WebSocketError):
    """Raised when WebSocket connection times out."""
    pass


class AuthenticationError(WebSocketError):
    """Raised when WebSocket authentication fails."""
    pass


class RateLimitError(WebSocketError):
    """Raised when rate limit is exceeded."""
    pass


class ProtocolError(WebSocketError):
    """Raised when WebSocket protocol error occurs."""
    pass


class RetryExhaustedError(WebSocketError):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, endpoint: Optional[str] = None, attempts: int = 0):
        self.attempts = attempts
        super().__init__(message, endpoint)


class MaxConnectionsError(WebSocketError):
    """Raised when maximum number of connections is reached."""
    pass
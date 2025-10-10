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


class WebSocketConnectionError(WebSocketError):
    """Raised when WebSocket connection encounters an error."""
    pass


class WebSocketTimeoutError(WebSocketError):
    """Raised when WebSocket operation times out."""
    pass


class WebSocketAuthenticationError(WebSocketError):
    """Raised when WebSocket authentication fails."""
    pass


class WebSocketRateLimitError(WebSocketError):
    """Raised when WebSocket rate limit is exceeded."""
    pass
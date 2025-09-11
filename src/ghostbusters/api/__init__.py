"""
Ghostbusters API Layer

Service interface layer that provides clean APIs for dependent specs
to consume Ghostbusters capabilities without creating circular dependencies.
"""

from .gateway import GhostbustersAPI
from .auth import AuthenticationManager
from .circuit_breaker import CircuitBreaker
from .rate_limiter import RateLimiter

__all__ = [
    "GhostbustersAPI",
    "AuthenticationManager", 
    "CircuitBreaker",
    "RateLimiter"
]
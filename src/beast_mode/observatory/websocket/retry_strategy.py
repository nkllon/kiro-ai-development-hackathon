"""Retry strategies for WebSocket connections."""

import asyncio
import json
import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Type

from .exceptions import (
    AuthenticationError,
    ConnectionFailedError,
    ConnectionTimeoutError,
    ProtocolError,
    RateLimitError,
    RetryExhaustedError,
)


class RetryStrategy(ABC):
    """Abstract base class for retry strategies."""

    @abstractmethod
    def calculate_delay(self) -> float:
        """Calculate delay before next retry attempt."""
        pass

    @abstractmethod
    def should_retry(self, error: Exception) -> bool:
        """Determine if retry should be attempted based on error type."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset retry state."""
        pass

    @abstractmethod
    def increment_attempt(self) -> None:
        """Increment retry attempt counter."""
        pass

    @abstractmethod
    def get_attempt_count(self) -> int:
        """Get current attempt count."""
        pass


class ExponentialBackoffRetry(RetryStrategy):
    """Exponential backoff retry strategy with jitter."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        jitter: bool = True,
        max_attempts: int = 10
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
        self.max_attempts = max_attempts
        self.attempt_count = 0
        self._non_retryable_errors = {
            AuthenticationError,
        }

    def calculate_delay(self) -> float:
        """Calculate exponential backoff delay with optional jitter."""
        if self.attempt_count == 0:
            return 0.0

        # Calculate exponential delay
        delay = self.base_delay * (self.multiplier ** (self.attempt_count - 1))
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)

        self._log_action("calculating_delay", {
            "attempt": self.attempt_count,
            "calculated_delay": delay,
            "jitter_applied": self.jitter
        })

        return delay

    def should_retry(self, error: Exception) -> bool:
        """Determine if error is retryable and attempts remain."""
        # Check if error type is retryable
        error_type = type(error)
        if error_type in self._non_retryable_errors:
            self._log_action("retry_rejected", {
                "error_type": error_type.__name__,
                "reason": "non_retryable_error"
            })
            return False

        # Check if we've exceeded max attempts
        if self.attempt_count >= self.max_attempts:
            self._log_action("retry_rejected", {
                "attempt": self.attempt_count,
                "max_attempts": self.max_attempts,
                "reason": "max_attempts_exceeded"
            })
            return False

        # Special handling for rate limit errors
        if isinstance(error, RateLimitError):
            # Always retry rate limit errors with longer delay
            self._log_action("retry_approved", {
                "error_type": "RateLimitError",
                "attempt": self.attempt_count,
                "strategy": "rate_limit_backoff"
            })
            return True

        # Retry connection and timeout errors
        retryable_errors = {
            ConnectionFailedError,
            ConnectionTimeoutError,
            ProtocolError,
        }

        if error_type in retryable_errors:
            self._log_action("retry_approved", {
                "error_type": error_type.__name__,
                "attempt": self.attempt_count,
                "max_attempts": self.max_attempts
            })
            return True

        self._log_action("retry_rejected", {
            "error_type": error_type.__name__,
            "reason": "unknown_error_type"
        })
        return False

    def reset(self) -> None:
        """Reset retry attempt counter."""
        previous_count = self.attempt_count
        self.attempt_count = 0
        self._log_action("retry_reset", {
            "previous_attempts": previous_count
        })

    def increment_attempt(self) -> None:
        """Increment retry attempt counter."""
        self.attempt_count += 1
        self._log_action("retry_attempt_incremented", {
            "current_attempt": self.attempt_count,
            "max_attempts": self.max_attempts
        })

    def get_attempt_count(self) -> int:
        """Get current attempt count."""
        return self.attempt_count

    def is_exhausted(self) -> bool:
        """Check if retry attempts are exhausted."""
        return self.attempt_count >= self.max_attempts

    def _log_action(self, action: str, details: dict) -> None:
        """Log retry action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '2.1',
            'action': f'retry_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))


class LinearBackoffRetry(RetryStrategy):
    """Linear backoff retry strategy."""

    def __init__(
        self,
        delay: float = 5.0,
        max_attempts: int = 5
    ):
        self.delay = delay
        self.max_attempts = max_attempts
        self.attempt_count = 0

    def calculate_delay(self) -> float:
        """Calculate linear delay."""
        return self.delay if self.attempt_count > 0 else 0.0

    def should_retry(self, error: Exception) -> bool:
        """Determine if retry should be attempted."""
        if isinstance(error, AuthenticationError):
            return False
        return self.attempt_count < self.max_attempts

    def reset(self) -> None:
        """Reset retry state."""
        self.attempt_count = 0

    def increment_attempt(self) -> None:
        """Increment attempt counter."""
        self.attempt_count += 1

    def get_attempt_count(self) -> int:
        """Get current attempt count."""
        return self.attempt_count


class NoRetryStrategy(RetryStrategy):
    """No retry strategy - always fails after first attempt."""

    def __init__(self):
        self.attempt_count = 0

    def calculate_delay(self) -> float:
        """No delay for no-retry strategy."""
        return 0.0

    def should_retry(self, error: Exception) -> bool:
        """Never retry."""
        return False

    def reset(self) -> None:
        """Reset attempt count."""
        self.attempt_count = 0

    def increment_attempt(self) -> None:
        """Increment attempt count."""
        self.attempt_count += 1

    def get_attempt_count(self) -> int:
        """Get attempt count."""
        return self.attempt_count


async def retry_with_strategy(
    retry_strategy: RetryStrategy,
    operation,
    endpoint: Optional[str] = None,
    *args,
    **kwargs
):
    """Execute operation with retry strategy."""
    retry_strategy.reset()

    while True:
        try:
            retry_strategy.increment_attempt()
            result = await operation(*args, **kwargs)
            retry_strategy.reset()  # Reset on success
            return result

        except Exception as error:
            if not retry_strategy.should_retry(error):
                if retry_strategy.is_exhausted():
                    raise RetryExhaustedError(
                        f"Retry attempts exhausted after {retry_strategy.get_attempt_count()} attempts",
                        endpoint=endpoint,
                        attempts=retry_strategy.get_attempt_count()
                    )
                raise error

            delay = retry_strategy.calculate_delay()
            if delay > 0:
                await asyncio.sleep(delay)
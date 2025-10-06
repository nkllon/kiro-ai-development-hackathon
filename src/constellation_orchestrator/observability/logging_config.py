"""Structured logging configuration for Constellation Orchestrator."""

import uuid
import contextvars
from typing import Any, Dict
import structlog
from structlog.types import Processor


# Context variable for correlation ID tracking
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='')


def get_correlation_id() -> str:
    """Get current correlation ID from context."""
    return correlation_id_var.get() or str(uuid.uuid4())


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in context."""
    correlation_id_var.set(correlation_id)


def add_correlation_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log events."""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict['correlation_id'] = correlation_id
    return event_dict


def add_service_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add service context to log events."""
    event_dict.update({
        'service': 'constellation_orchestrator',
        'version': '0.1.0'
    })
    return event_dict


def setup_structured_logging(log_level: str = "INFO", json_output: bool = True) -> None:
    """
    Set up structured logging for Constellation Orchestrator.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_output: Whether to output logs in JSON format
    """
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_correlation_id,
        add_service_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )


class CorrelationIdManager:
    """Context manager for correlation ID tracking."""
    
    def __init__(self, correlation_id: str = None):
        """Initialize with optional correlation ID."""
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.previous_id = None
    
    def __enter__(self) -> str:
        """Enter context and set correlation ID."""
        self.previous_id = correlation_id_var.get('')
        set_correlation_id(self.correlation_id)
        return self.correlation_id
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and restore previous correlation ID."""
        if self.previous_id:
            set_correlation_id(self.previous_id)
        else:
            correlation_id_var.set('')


def with_correlation_id(correlation_id: str = None):
    """Decorator to add correlation ID to function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with CorrelationIdManager(correlation_id):
                return func(*args, **kwargs)
        return wrapper
    return decorator


async def with_correlation_id_async(correlation_id: str = None):
    """Async decorator to add correlation ID to function execution."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with CorrelationIdManager(correlation_id):
                return await func(*args, **kwargs)
        return wrapper
    return decorator
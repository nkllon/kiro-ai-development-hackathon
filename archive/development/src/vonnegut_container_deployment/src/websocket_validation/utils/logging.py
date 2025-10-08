"""
Logging utilities for WebSocket validation framework.
"""

import logging
import sys
import uuid
from typing import Optional
from datetime import datetime

from ..config import config


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> None:
    """
    Set up logging configuration for the validation framework.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom log format string
        correlation_id: Correlation ID for request tracing
    """
    log_level = level or config.log_level
    log_format = format_string or config.log_format
    
    # Add correlation ID to format if provided
    if correlation_id:
        log_format = f"[{correlation_id}] {log_format}"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                config.evidence_dir / "validation.log",
                mode='a',
                encoding='utf-8'
            )
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.INFO)


def get_logger(name: str, correlation_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with optional correlation ID.
    
    Args:
        name: Logger name (typically __name__)
        correlation_id: Optional correlation ID for request tracing
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if correlation_id:
        # Create a custom adapter that adds correlation ID to all log records
        logger = CorrelationAdapter(logger, {"correlation_id": correlation_id})
    
    return logger


class CorrelationAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds correlation ID to log records.
    """
    
    def process(self, msg, kwargs):
        """Add correlation ID to log message."""
        correlation_id = self.extra.get("correlation_id", "")
        return f"[{correlation_id}] {msg}", kwargs


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for request tracing.
    
    Returns:
        str: Unique correlation ID
    """
    return str(uuid.uuid4())[:8]


def log_test_start(logger: logging.Logger, test_name: str, test_category: str) -> None:
    """
    Log the start of a test with standardized format.
    
    Args:
        logger: Logger instance
        test_name: Name of the test
        test_category: Category of the test
    """
    logger.info(f"TEST_START | {test_category} | {test_name}")


def log_test_end(
    logger: logging.Logger, 
    test_name: str, 
    test_category: str, 
    status: str,
    duration: float,
    details: Optional[str] = None
) -> None:
    """
    Log the end of a test with standardized format.
    
    Args:
        logger: Logger instance
        test_name: Name of the test
        test_category: Category of the test
        status: Test status (PASSED, FAILED, ERROR, etc.)
        duration: Test execution duration in seconds
        details: Optional additional details
    """
    message = f"TEST_END | {test_category} | {test_name} | {status} | {duration:.2f}s"
    if details:
        message += f" | {details}"
    
    if status in ["PASSED"]:
        logger.info(message)
    elif status in ["FAILED", "ERROR"]:
        logger.error(message)
    else:
        logger.warning(message)


def log_evidence_collection(
    logger: logging.Logger,
    evidence_type: str,
    source_test: str,
    evidence_id: str,
    size_bytes: int
) -> None:
    """
    Log evidence collection with standardized format.
    
    Args:
        logger: Logger instance
        evidence_type: Type of evidence collected
        source_test: Test that generated the evidence
        evidence_id: Unique evidence identifier
        size_bytes: Size of evidence in bytes
    """
    logger.info(
        f"EVIDENCE_COLLECTED | {evidence_type} | {source_test} | "
        f"{evidence_id} | {size_bytes} bytes"
    )


def log_validation_phase(
    logger: logging.Logger,
    phase_name: str,
    phase_status: str,
    tests_passed: int,
    tests_total: int,
    duration: float
) -> None:
    """
    Log validation phase completion with standardized format.
    
    Args:
        logger: Logger instance
        phase_name: Name of the validation phase
        phase_status: Phase status (COMPLETED, FAILED, PARTIAL)
        tests_passed: Number of tests that passed
        tests_total: Total number of tests in phase
        duration: Phase execution duration in seconds
    """
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    
    logger.info(
        f"PHASE_COMPLETE | {phase_name} | {phase_status} | "
        f"{tests_passed}/{tests_total} ({success_rate:.1f}%) | {duration:.2f}s"
    )


def log_error_with_context(
    logger: logging.Logger,
    error: Exception,
    context: dict,
    test_name: Optional[str] = None
) -> None:
    """
    Log error with additional context information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
        test_name: Optional test name where error occurred
    """
    error_msg = f"ERROR | {type(error).__name__}: {str(error)}"
    
    if test_name:
        error_msg += f" | Test: {test_name}"
    
    if context:
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        error_msg += f" | Context: {context_str}"
    
    logger.error(error_msg, exc_info=True)
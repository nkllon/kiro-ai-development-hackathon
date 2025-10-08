"""
Error handling utilities for WebSocket validation framework.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from enum import Enum

from ..models import ErrorType


class ValidationError(Exception):
    """
    Custom exception for validation framework errors.
    
    Provides structured error information with context and error types.
    """
    
    def __init__(
        self, 
        error_type: str, 
        message: str, 
        context: Dict[str, Any],
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize ValidationError.
        
        Args:
            error_type: Type of error (from ErrorType enum or custom string)
            message: Human-readable error message
            context: Additional context information
            original_exception: Original exception that caused this error
        """
        self.error_type = error_type
        self.message = message
        self.context = context
        self.original_exception = original_exception
        self.timestamp = None
        
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "context": self.context,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "traceback": traceback.format_exc() if self.original_exception else None
        }


class ErrorRecoveryAction(Enum):
    """Actions that can be taken for error recovery."""
    RETRY = "retry"
    SKIP = "skip"
    FAIL_FAST = "fail_fast"
    CONTINUE = "continue"
    ESCALATE = "escalate"


class ErrorHandler:
    """
    Centralized error handling for the validation framework.
    
    Provides error categorization, recovery strategies, and logging.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize ErrorHandler.
        
        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger
        self.error_counts = {}
        self.recovery_strategies = self._init_recovery_strategies()
    
    def _init_recovery_strategies(self) -> Dict[str, ErrorRecoveryAction]:
        """Initialize default recovery strategies for different error types."""
        return {
            ErrorType.NETWORK_ERROR.value: ErrorRecoveryAction.RETRY,
            ErrorType.TIMEOUT_ERROR.value: ErrorRecoveryAction.RETRY,
            ErrorType.CONFIG_ERROR.value: ErrorRecoveryAction.FAIL_FAST,
            ErrorType.CODE_ANALYSIS_ERROR.value: ErrorRecoveryAction.CONTINUE,
            ErrorType.SYSTEM_ERROR.value: ErrorRecoveryAction.ESCALATE,
            ErrorType.EVIDENCE_ERROR.value: ErrorRecoveryAction.CONTINUE,
            ErrorType.AUTHENTICATION_ERROR.value: ErrorRecoveryAction.FAIL_FAST,
        }
    
    def handle_error(
        self, 
        error: Exception, 
        context: Dict[str, Any],
        test_name: Optional[str] = None
    ) -> ErrorRecoveryAction:
        """
        Handle an error and determine recovery action.
        
        Args:
            error: Exception that occurred
            context: Additional context information
            test_name: Optional test name where error occurred
            
        Returns:
            ErrorRecoveryAction: Recommended recovery action
        """
        # Categorize the error
        error_type = self._categorize_error(error)
        
        # Create ValidationError if not already one
        if not isinstance(error, ValidationError):
            validation_error = ValidationError(
                error_type=error_type,
                message=str(error),
                context=context,
                original_exception=error
            )
        else:
            validation_error = error
        
        # Log the error with context
        self.log_error_with_context(validation_error, test_name)
        
        # Update error counts
        self._update_error_counts(error_type)
        
        # Determine recovery action
        recovery_action = self._determine_recovery_action(error_type, context)
        
        self.logger.info(f"Error recovery action: {recovery_action.value}")
        
        return recovery_action
    
    def _categorize_error(self, error: Exception) -> str:
        """
        Categorize an error based on its type and message.
        
        Args:
            error: Exception to categorize
            
        Returns:
            str: Error category
        """
        error_message = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        # Network-related errors
        if any(keyword in error_message for keyword in [
            "connection", "timeout", "network", "dns", "socket", "ssl"
        ]) or any(keyword in error_type_name for keyword in [
            "connection", "timeout", "network", "socket"
        ]):
            if "timeout" in error_message or "timeout" in error_type_name:
                return ErrorType.TIMEOUT_ERROR.value
            return ErrorType.NETWORK_ERROR.value
        
        # Configuration errors
        if any(keyword in error_message for keyword in [
            "config", "configuration", "setting", "parameter", "invalid"
        ]):
            return ErrorType.CONFIG_ERROR.value
        
        # Authentication errors
        if any(keyword in error_message for keyword in [
            "auth", "authentication", "unauthorized", "forbidden", "credential"
        ]):
            return ErrorType.AUTHENTICATION_ERROR.value
        
        # Code analysis errors
        if any(keyword in error_message for keyword in [
            "parse", "syntax", "import", "module", "ast"
        ]):
            return ErrorType.CODE_ANALYSIS_ERROR.value
        
        # Evidence collection errors
        if any(keyword in error_message for keyword in [
            "evidence", "file", "storage", "disk", "permission"
        ]):
            return ErrorType.EVIDENCE_ERROR.value
        
        # Default to system error
        return ErrorType.SYSTEM_ERROR.value
    
    def _determine_recovery_action(
        self, 
        error_type: str, 
        context: Dict[str, Any]
    ) -> ErrorRecoveryAction:
        """
        Determine the appropriate recovery action for an error.
        
        Args:
            error_type: Type of error
            context: Error context
            
        Returns:
            ErrorRecoveryAction: Recommended recovery action
        """
        # Check if we have too many errors of this type
        if self.error_counts.get(error_type, 0) > 5:
            self.logger.warning(f"Too many {error_type} errors, escalating")
            return ErrorRecoveryAction.ESCALATE
        
        # Use default strategy for error type
        return self.recovery_strategies.get(error_type, ErrorRecoveryAction.CONTINUE)
    
    def _update_error_counts(self, error_type: str) -> None:
        """Update error count statistics."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def log_error_with_context(
        self, 
        error: ValidationError, 
        test_name: Optional[str] = None
    ) -> None:
        """
        Log error with full context information.
        
        Args:
            error: ValidationError to log
            test_name: Optional test name where error occurred
        """
        error_msg = f"VALIDATION_ERROR | {error.error_type} | {error.message}"
        
        if test_name:
            error_msg += f" | Test: {test_name}"
        
        if error.context:
            context_str = " | ".join([f"{k}={v}" for k, v in error.context.items()])
            error_msg += f" | Context: {context_str}"
        
        self.logger.error(error_msg)
        
        # Log original exception traceback if available
        if error.original_exception:
            self.logger.debug(
                f"Original exception traceback:",
                exc_info=error.original_exception
            )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors encountered.
        
        Returns:
            Dict containing error statistics
        """
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "error_counts_by_type": self.error_counts.copy(),
            "most_common_error": max(
                self.error_counts.items(), 
                key=lambda x: x[1]
            )[0] if self.error_counts else None
        }
    
    def reset_error_counts(self) -> None:
        """Reset error count statistics."""
        self.error_counts.clear()
        self.logger.info("Error counts reset")


def create_network_error(message: str, context: Dict[str, Any]) -> ValidationError:
    """Create a network-related ValidationError."""
    return ValidationError(
        error_type=ErrorType.NETWORK_ERROR.value,
        message=message,
        context=context
    )


def create_config_error(message: str, context: Dict[str, Any]) -> ValidationError:
    """Create a configuration-related ValidationError."""
    return ValidationError(
        error_type=ErrorType.CONFIG_ERROR.value,
        message=message,
        context=context
    )


def create_timeout_error(message: str, context: Dict[str, Any]) -> ValidationError:
    """Create a timeout-related ValidationError."""
    return ValidationError(
        error_type=ErrorType.TIMEOUT_ERROR.value,
        message=message,
        context=context
    )
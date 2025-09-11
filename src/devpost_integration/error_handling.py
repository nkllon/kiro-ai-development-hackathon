#!/usr/bin/env python3
"""
Devpost Integration Error Handling Framework

Comprehensive error handling with custom exceptions, retry strategies,
and user-friendly error reporting with actionable suggestions.

Requirements: 2.5, 3.5, 5.5
"""

import logging
import time
import traceback
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error category classification."""
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    VALIDATION = "validation"
    FILE_SYSTEM = "file_system"
    API = "api"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    DATA = "data"
    SYSTEM = "system"


@dataclass
class ErrorContext:
    """Context information for error reporting."""
    operation: str
    component: str
    user_action: Optional[str] = None
    project_id: Optional[str] = None
    file_path: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class ErrorSolution:
    """Suggested solution for an error."""
    description: str
    action_steps: List[str]
    documentation_link: Optional[str] = None
    is_automatic: bool = False


class DevpostIntegrationError(Exception):
    """Base exception for Devpost integration errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        solutions: Optional[List[ErrorSolution]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext("unknown", "unknown")
        self.solutions = solutions or []
        self.original_error = original_error
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        return f"[{self.category.value.upper()}] {self.message}"
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly error message with solutions."""
        message = f"❌ {self.message}\n"
        
        if self.solutions:
            message += "\n💡 Suggested solutions:\n"
            for i, solution in enumerate(self.solutions, 1):
                message += f"{i}. {solution.description}\n"
                for step in solution.action_steps:
                    message += f"   • {step}\n"
                if solution.documentation_link:
                    message += f"   📖 More info: {solution.documentation_link}\n"
        
        return message


class AuthenticationError(DevpostIntegrationError):
    """Authentication-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class NetworkError(DevpostIntegrationError):
    """Network and connectivity errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ValidationError(DevpostIntegrationError):
    """Data validation errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ConfigurationError(DevpostIntegrationError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class FileSystemError(DevpostIntegrationError):
    """File system operation errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class APIError(DevpostIntegrationError):
    """API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.status_code = status_code


class RetryStrategy:
    """Retry strategy configuration."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay


def with_retry(
    strategy: Optional[RetryStrategy] = None,
    exceptions: tuple = (Exception,),
    context: Optional[ErrorContext] = None
):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        strategy: Retry strategy configuration
        exceptions: Tuple of exceptions to retry on
        context: Error context for logging
    """
    if strategy is None:
        strategy = RetryStrategy()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, strategy.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == strategy.max_attempts:
                        # Final attempt failed, raise with context
                        error_context = context or ErrorContext(
                            operation=func.__name__,
                            component=func.__module__
                        )
                        
                        raise DevpostIntegrationError(
                            f"Operation failed after {strategy.max_attempts} attempts: {str(e)}",
                            context=error_context,
                            original_error=e,
                            solutions=[
                                ErrorSolution(
                                    description="Check your network connection and try again",
                                    action_steps=[
                                        "Verify internet connectivity",
                                        "Check if Devpost API is accessible",
                                        "Try again in a few minutes"
                                    ]
                                )
                            ]
                        )
                    
                    # Wait before retry
                    delay = strategy.get_delay(attempt)
                    logging.warning(f"Attempt {attempt} failed, retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """Central error handling and reporting system."""
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize error handler.
        
        Args:
            log_file: Path to error log file
        """
        self.log_file = log_file or Path.cwd() / '.devpost' / 'errors.log'
        self.logger = logging.getLogger(__name__)
        
        # Error solution database
        self.solution_database = self._build_solution_database()
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        user_friendly: bool = True
    ) -> str:
        """
        Handle and report an error.
        
        Args:
            error: The exception that occurred
            context: Error context information
            user_friendly: Whether to return user-friendly message
            
        Returns:
            Error message (user-friendly or technical)
        """
        # Convert to DevpostIntegrationError if needed
        if not isinstance(error, DevpostIntegrationError):
            devpost_error = self._convert_to_devpost_error(error, context)
        else:
            devpost_error = error
        
        # Log the error
        self._log_error(devpost_error)
        
        # Get appropriate message
        if user_friendly:
            return devpost_error.get_user_friendly_message()
        else:
            return str(devpost_error)
    
    def _convert_to_devpost_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> DevpostIntegrationError:
        """Convert generic exception to DevpostIntegrationError."""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Determine category and severity based on error type
        category = ErrorCategory.SYSTEM
        severity = ErrorSeverity.MEDIUM
        solutions = []
        
        if "connection" in error_message.lower() or "network" in error_message.lower():
            category = ErrorCategory.NETWORK
            solutions = self.solution_database.get("network", [])
        elif "permission" in error_message.lower() or "access" in error_message.lower():
            category = ErrorCategory.PERMISSION
            severity = ErrorSeverity.HIGH
            solutions = self.solution_database.get("permission", [])
        elif "file" in error_message.lower() or "directory" in error_message.lower():
            category = ErrorCategory.FILE_SYSTEM
            solutions = self.solution_database.get("file_system", [])
        elif "auth" in error_message.lower() or "token" in error_message.lower():
            category = ErrorCategory.AUTHENTICATION
            severity = ErrorSeverity.HIGH
            solutions = self.solution_database.get("authentication", [])
        elif "config" in error_message.lower():
            category = ErrorCategory.CONFIGURATION
            solutions = self.solution_database.get("configuration", [])
        
        return DevpostIntegrationError(
            message=f"{error_type}: {error_message}",
            category=category,
            severity=severity,
            context=context,
            solutions=solutions,
            original_error=error
        )
    
    def _log_error(self, error: DevpostIntegrationError) -> None:
        """Log error to file and console."""
        try:
            # Ensure log directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create log entry
            log_entry = {
                'timestamp': error.timestamp.isoformat(),
                'category': error.category.value,
                'severity': error.severity.value,
                'message': error.message,
                'context': {
                    'operation': error.context.operation,
                    'component': error.context.component,
                    'user_action': error.context.user_action,
                    'project_id': error.context.project_id,
                    'file_path': error.context.file_path,
                    'additional_data': error.context.additional_data
                },
                'solutions_count': len(error.solutions),
                'original_error': str(error.original_error) if error.original_error else None,
                'traceback': traceback.format_exc() if error.original_error else None
            }
            
            # Write to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                import json
                f.write(json.dumps(log_entry) + '\n')
            
            # Log to console based on severity
            if error.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(f"[{error.category.value}] {error.message}")
            elif error.severity == ErrorSeverity.HIGH:
                self.logger.error(f"[{error.category.value}] {error.message}")
            elif error.severity == ErrorSeverity.MEDIUM:
                self.logger.warning(f"[{error.category.value}] {error.message}")
            else:
                self.logger.info(f"[{error.category.value}] {error.message}")
                
        except Exception as e:
            # Fallback logging if file logging fails
            self.logger.error(f"Failed to log error: {e}")
            self.logger.error(f"Original error: {error}")
    
    def _build_solution_database(self) -> Dict[str, List[ErrorSolution]]:
        """Build database of error solutions."""
        return {
            "network": [
                ErrorSolution(
                    description="Check your internet connection",
                    action_steps=[
                        "Verify you can access other websites",
                        "Try pinging devpost.com",
                        "Check your firewall settings"
                    ]
                ),
                ErrorSolution(
                    description="Retry the operation",
                    action_steps=[
                        "Wait a few seconds and try again",
                        "Check Devpost status page for outages"
                    ]
                )
            ],
            "authentication": [
                ErrorSolution(
                    description="Re-authenticate with Devpost",
                    action_steps=[
                        "Run 'devpost config --key auth_token --value YOUR_TOKEN'",
                        "Get a new token from Devpost settings",
                        "Verify token permissions"
                    ]
                ),
                ErrorSolution(
                    description="Check token expiration",
                    action_steps=[
                        "Log into Devpost and check token status",
                        "Generate a new token if expired",
                        "Update configuration with new token"
                    ]
                )
            ],
            "permission": [
                ErrorSolution(
                    description="Check file permissions",
                    action_steps=[
                        "Verify you have write access to the project directory",
                        "Check if files are locked by another process",
                        "Run with appropriate permissions"
                    ]
                )
            ],
            "file_system": [
                ErrorSolution(
                    description="Verify file paths and permissions",
                    action_steps=[
                        "Check that all required files exist",
                        "Verify directory structure is correct",
                        "Ensure sufficient disk space"
                    ]
                )
            ],
            "configuration": [
                ErrorSolution(
                    description="Check configuration settings",
                    action_steps=[
                        "Run 'devpost config --show' to view current settings",
                        "Verify all required configuration values are set",
                        "Check configuration file format"
                    ]
                ),
                ErrorSolution(
                    description="Reset to default configuration",
                    action_steps=[
                        "Backup current configuration",
                        "Delete .devpost/config.json",
                        "Run 'devpost connect' to reconfigure"
                    ],
                    is_automatic=True
                )
            ]
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics from log file."""
        try:
            if not self.log_file.exists():
                return {"total_errors": 0, "by_category": {}, "by_severity": {}}
            
            stats = {
                "total_errors": 0,
                "by_category": {},
                "by_severity": {},
                "recent_errors": 0  # Last 24 hours
            }
            
            cutoff_time = datetime.now().timestamp() - (24 * 3600)
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        import json
                        entry = json.loads(line.strip())
                        stats["total_errors"] += 1
                        
                        # Count by category
                        category = entry.get("category", "unknown")
                        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                        
                        # Count by severity
                        severity = entry.get("severity", "unknown")
                        stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
                        
                        # Count recent errors
                        timestamp = datetime.fromisoformat(entry["timestamp"]).timestamp()
                        if timestamp > cutoff_time:
                            stats["recent_errors"] += 1
                            
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get error statistics: {e}")
            return {"total_errors": 0, "by_category": {}, "by_severity": {}}


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(context: Optional[ErrorContext] = None):
    """
    Decorator for automatic error handling.
    
    Args:
        context: Error context for the decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DevpostIntegrationError:
                # Re-raise DevpostIntegrationError as-is
                raise
            except Exception as e:
                # Convert and handle other exceptions
                error_context = context or ErrorContext(
                    operation=func.__name__,
                    component=func.__module__
                )
                
                handled_error = error_handler._convert_to_devpost_error(e, error_context)
                error_handler._log_error(handled_error)
                raise handled_error
        
        return wrapper
    return decorator
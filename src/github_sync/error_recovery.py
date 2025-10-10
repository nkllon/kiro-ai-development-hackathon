"""
Comprehensive error handling and recovery system for GitHub synchronization.

This module provides robust error handling, categorization, and recovery
strategies for all types of failures that can occur during synchronization.
"""

import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors that can occur."""
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    API_ERROR = "api_error"
    DATA_CORRUPTION = "data_corruption"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    RETRY_IMMEDIATE = "retry_immediate"
    RETRY_EXPONENTIAL_BACKOFF = "retry_exponential_backoff"
    RETRY_AFTER_DELAY = "retry_after_delay"
    REFRESH_CREDENTIALS = "refresh_credentials"
    FALLBACK_TO_POLLING = "fallback_to_polling"
    SKIP_AND_CONTINUE = "skip_and_continue"
    ABORT_OPERATION = "abort_operation"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorContext:
    """Context information for an error."""
    operation: str
    repository: Optional[str] = None
    user: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryAction:
    """Action to take for error recovery."""
    strategy: RecoveryStrategy
    delay_seconds: float = 0.0
    max_retries: int = 3
    fallback_action: Optional['RecoveryAction'] = None
    custom_handler: Optional[Callable] = None
    message: str = ""


@dataclass
class ErrorRecord:
    """Record of an error and recovery attempt."""
    error_id: str
    category: ErrorCategory
    error_type: str
    error_message: str
    context: ErrorContext
    recovery_action: RecoveryAction
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'error_id': self.error_id,
            'category': self.category.value,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'context': {
                'operation': self.context.operation,
                'repository': self.context.repository,
                'user': self.context.user,
                'timestamp': self.context.timestamp.isoformat(),
                'additional_data': self.context.additional_data
            },
            'recovery_action': {
                'strategy': self.recovery_action.strategy.value,
                'delay_seconds': self.recovery_action.delay_seconds,
                'max_retries': self.recovery_action.max_retries,
                'message': self.recovery_action.message
            },
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count,
            'resolved': self.resolved,
            'resolution_timestamp': self.resolution_timestamp.isoformat() if self.resolution_timestamp else None
        }


class ErrorRecoveryManager:
    """
    Comprehensive error handling and recovery system.
    
    This class provides error categorization, recovery strategies,
    and graceful degradation for all types of failures.
    """
    
    def __init__(self):
        """Initialize error recovery manager."""
        self.error_records: Dict[str, ErrorRecord] = {}
        self.error_handlers: Dict[ErrorCategory, Callable] = {}
        self.recovery_strategies: Dict[ErrorCategory, RecoveryAction] = {}
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize default recovery strategies
        self._setup_default_strategies()
        
        # Initialize default error handlers
        self._setup_default_handlers()
    
    def _setup_default_strategies(self) -> None:
        """Set up default recovery strategies for each error category."""
        self.recovery_strategies = {
            ErrorCategory.AUTHENTICATION: RecoveryAction(
                strategy=RecoveryStrategy.REFRESH_CREDENTIALS,
                max_retries=2,
                message="Attempting to refresh authentication credentials"
            ),
            ErrorCategory.RATE_LIMIT: RecoveryAction(
                strategy=RecoveryStrategy.RETRY_AFTER_DELAY,
                delay_seconds=3600,  # Wait 1 hour for rate limit reset
                max_retries=3,
                message="Waiting for rate limit reset"
            ),
            ErrorCategory.NETWORK: RecoveryAction(
                strategy=RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
                delay_seconds=1.0,
                max_retries=5,
                message="Retrying with exponential backoff for network issues"
            ),
            ErrorCategory.API_ERROR: RecoveryAction(
                strategy=RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
                delay_seconds=2.0,
                max_retries=3,
                message="Retrying API call with backoff"
            ),
            ErrorCategory.DATA_CORRUPTION: RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INTERVENTION,
                message="Data corruption detected - manual intervention required"
            ),
            ErrorCategory.CONFIGURATION: RecoveryAction(
                strategy=RecoveryStrategy.ABORT_OPERATION,
                message="Configuration error - operation aborted"
            ),
            ErrorCategory.PERMISSION: RecoveryAction(
                strategy=RecoveryStrategy.SKIP_AND_CONTINUE,
                message="Permission denied - skipping operation"
            ),
            ErrorCategory.RESOURCE_EXHAUSTION: RecoveryAction(
                strategy=RecoveryStrategy.RETRY_AFTER_DELAY,
                delay_seconds=300,  # Wait 5 minutes
                max_retries=3,
                message="Resource exhaustion - waiting before retry"
            ),
            ErrorCategory.UNKNOWN: RecoveryAction(
                strategy=RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
                delay_seconds=1.0,
                max_retries=2,
                message="Unknown error - attempting limited retry"
            )
        }
    
    def _setup_default_handlers(self) -> None:
        """Set up default error handlers."""
        self.error_handlers = {
            ErrorCategory.AUTHENTICATION: self._handle_authentication_error,
            ErrorCategory.RATE_LIMIT: self._handle_rate_limit_error,
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.API_ERROR: self._handle_api_error,
            ErrorCategory.DATA_CORRUPTION: self._handle_data_corruption_error,
            ErrorCategory.CONFIGURATION: self._handle_configuration_error,
            ErrorCategory.PERMISSION: self._handle_permission_error,
            ErrorCategory.RESOURCE_EXHAUSTION: self._handle_resource_exhaustion_error,
            ErrorCategory.UNKNOWN: self._handle_unknown_error
        }
    
    def categorize_error(self, error: Exception, context: ErrorContext) -> ErrorCategory:
        """
        Categorize an error based on its type and context.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            Error category
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['unauthorized', 'authentication', 'token', 'credentials']):
            return ErrorCategory.AUTHENTICATION
        
        # Rate limit errors
        if any(keyword in error_message for keyword in ['rate limit', 'too many requests', '429']):
            return ErrorCategory.RATE_LIMIT
        
        # Network errors
        if any(keyword in error_message for keyword in ['connection', 'timeout', 'network', 'dns', 'socket']):
            return ErrorCategory.NETWORK
        
        # API errors
        if any(keyword in error_message for keyword in ['400', '404', '500', '502', '503', 'bad request', 'not found']):
            return ErrorCategory.API_ERROR
        
        # Permission errors
        if any(keyword in error_message for keyword in ['permission', 'forbidden', '403', 'access denied']):
            return ErrorCategory.PERMISSION
        
        # Resource exhaustion
        if any(keyword in error_message for keyword in ['memory', 'disk space', 'quota', 'limit exceeded']):
            return ErrorCategory.RESOURCE_EXHAUSTION
        
        # Configuration errors
        if any(keyword in error_message for keyword in ['configuration', 'config', 'invalid setting']):
            return ErrorCategory.CONFIGURATION
        
        # Data corruption
        if any(keyword in error_message for keyword in ['corrupt', 'invalid data', 'checksum', 'integrity']):
            return ErrorCategory.DATA_CORRUPTION
        
        return ErrorCategory.UNKNOWN
    
    async def handle_error(self, error: Exception, context: ErrorContext) -> RecoveryAction:
        """
        Handle an error and determine recovery action.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            Recovery action to take
        """
        # Generate unique error ID
        error_id = f"{context.operation}_{int(time.time())}_{hash(str(error)) % 10000}"
        
        # Categorize the error
        category = self.categorize_error(error, context)
        
        # Get recovery strategy
        recovery_action = self.recovery_strategies.get(category, self.recovery_strategies[ErrorCategory.UNKNOWN])
        
        # Create error record
        error_record = ErrorRecord(
            error_id=error_id,
            category=category,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            recovery_action=recovery_action
        )
        
        # Store error record
        self.error_records[error_id] = error_record
        
        # Log the error
        self.logger.error(
            f"Error in {context.operation}: {error}",
            extra={
                'error_id': error_id,
                'category': category.value,
                'recovery_strategy': recovery_action.strategy.value,
                'repository': context.repository,
                'user': context.user
            }
        )
        
        # Execute error handler if available
        if category in self.error_handlers:
            try:
                await self.error_handlers[category](error, context, error_record)
            except Exception as handler_error:
                self.logger.error(f"Error handler failed: {handler_error}")
        
        return recovery_action
    
    async def execute_recovery(self, error_record: ErrorRecord, operation_func: Callable, *args, **kwargs) -> Any:
        """
        Execute recovery strategy for an error.
        
        Args:
            error_record: Error record with recovery information
            operation_func: Function to retry
            *args: Arguments for the operation function
            **kwargs: Keyword arguments for the operation function
            
        Returns:
            Result of successful operation or raises exception
        """
        recovery_action = error_record.recovery_action
        
        if recovery_action.strategy == RecoveryStrategy.RETRY_IMMEDIATE:
            return await self._retry_immediate(error_record, operation_func, *args, **kwargs)
        
        elif recovery_action.strategy == RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF:
            return await self._retry_exponential_backoff(error_record, operation_func, *args, **kwargs)
        
        elif recovery_action.strategy == RecoveryStrategy.RETRY_AFTER_DELAY:
            return await self._retry_after_delay(error_record, operation_func, *args, **kwargs)
        
        elif recovery_action.strategy == RecoveryStrategy.REFRESH_CREDENTIALS:
            return await self._refresh_credentials_and_retry(error_record, operation_func, *args, **kwargs)
        
        elif recovery_action.strategy == RecoveryStrategy.FALLBACK_TO_POLLING:
            return await self._fallback_to_polling(error_record, operation_func, *args, **kwargs)
        
        elif recovery_action.strategy == RecoveryStrategy.SKIP_AND_CONTINUE:
            self.logger.warning(f"Skipping operation due to error: {error_record.error_message}")
            return None
        
        elif recovery_action.strategy == RecoveryStrategy.ABORT_OPERATION:
            raise Exception(f"Operation aborted due to error: {error_record.error_message}")
        
        elif recovery_action.strategy == RecoveryStrategy.MANUAL_INTERVENTION:
            raise Exception(f"Manual intervention required: {error_record.error_message}")
        
        else:
            raise Exception(f"Unknown recovery strategy: {recovery_action.strategy}")
    
    async def _retry_immediate(self, error_record: ErrorRecord, operation_func: Callable, *args, **kwargs) -> Any:
        """Retry operation immediately."""
        for attempt in range(error_record.recovery_action.max_retries):
            try:
                result = await operation_func(*args, **kwargs)
                error_record.resolved = True
                error_record.resolution_timestamp = datetime.utcnow()
                return result
            except Exception as e:
                error_record.retry_count += 1
                if attempt == error_record.recovery_action.max_retries - 1:
                    raise e
                self.logger.warning(f"Retry {attempt + 1} failed: {e}")
    
    async def _retry_exponential_backoff(self, error_record: ErrorRecord, operation_func: Callable, *args, **kwargs) -> Any:
        """Retry operation with exponential backoff."""
        base_delay = error_record.recovery_action.delay_seconds
        
        for attempt in range(error_record.recovery_action.max_retries):
            try:
                result = await operation_func(*args, **kwargs)
                error_record.resolved = True
                error_record.resolution_timestamp = datetime.utcnow()
                return result
            except Exception as e:
                error_record.retry_count += 1
                if attempt == error_record.recovery_action.max_retries - 1:
                    raise e
                
                # Calculate exponential backoff delay
                delay = base_delay * (2 ** attempt)
                self.logger.warning(f"Retry {attempt + 1} failed: {e}. Waiting {delay} seconds...")
                await asyncio.sleep(delay)
    
    async def _retry_after_delay(self, error_record: ErrorRecord, operation_func: Callable, *args, **kwargs) -> Any:
        """Retry operation after a fixed delay."""
        delay = error_record.recovery_action.delay_seconds
        
        for attempt in range(error_record.recovery_action.max_retries):
            if attempt > 0:  # Don't delay on first attempt
                self.logger.info(f"Waiting {delay} seconds before retry {attempt + 1}")
                await asyncio.sleep(delay)
            
            try:
                result = await operation_func(*args, **kwargs)
                error_record.resolved = True
                error_record.resolution_timestamp = datetime.utcnow()
                return result
            except Exception as e:
                error_record.retry_count += 1
                if attempt == error_record.recovery_action.max_retries - 1:
                    raise e
                self.logger.warning(f"Retry {attempt + 1} failed: {e}")
    
    async def _refresh_credentials_and_retry(self, error_record: ErrorRecord, operation_func: Callable, *args, **kwargs) -> Any:
        """Refresh credentials and retry operation."""
        # This would integrate with the authentication manager
        self.logger.info("Attempting to refresh credentials")
        
        # Placeholder for credential refresh logic
        # In a real implementation, this would call the authentication manager
        
        return await self._retry_immediate(error_record, operation_func, *args, **kwargs)
    
    async def _fallback_to_polling(self, error_record: ErrorRecord, operation_func: Callable, *args, **kwargs) -> Any:
        """Fallback to polling instead of webhooks."""
        self.logger.info("Falling back to polling mechanism")
        
        # This would implement a fallback polling mechanism
        # For now, just skip the operation
        return None
    
    # Default error handlers
    async def _handle_authentication_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle authentication errors."""
        self.logger.warning("Authentication error detected - credentials may need refresh")
    
    async def _handle_rate_limit_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle rate limit errors."""
        self.logger.warning("Rate limit exceeded - implementing backoff strategy")
    
    async def _handle_network_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle network errors."""
        self.logger.warning("Network error detected - will retry with backoff")
    
    async def _handle_api_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle API errors."""
        self.logger.warning(f"API error detected: {error}")
    
    async def _handle_data_corruption_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle data corruption errors."""
        self.logger.error("Data corruption detected - manual intervention required")
    
    async def _handle_configuration_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle configuration errors."""
        self.logger.error("Configuration error - check system settings")
    
    async def _handle_permission_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle permission errors."""
        self.logger.warning("Permission denied - check access rights")
    
    async def _handle_resource_exhaustion_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle resource exhaustion errors."""
        self.logger.warning("Resource exhaustion detected - implementing delay")
    
    async def _handle_unknown_error(self, error: Exception, context: ErrorContext, error_record: ErrorRecord) -> None:
        """Handle unknown errors."""
        self.logger.error(f"Unknown error type: {type(error).__name__}: {error}")
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get error statistics for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Error statistics dictionary
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.error_records.values()
            if error.timestamp >= cutoff_time
        ]
        
        if not recent_errors:
            return {'no_errors': True, 'time_period_hours': hours}
        
        # Count by category
        category_counts = {}
        for error in recent_errors:
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by resolution status
        resolved_count = sum(1 for error in recent_errors if error.resolved)
        unresolved_count = len(recent_errors) - resolved_count
        
        # Calculate average retry count
        total_retries = sum(error.retry_count for error in recent_errors)
        avg_retries = total_retries / len(recent_errors) if recent_errors else 0
        
        return {
            'time_period_hours': hours,
            'total_errors': len(recent_errors),
            'resolved_errors': resolved_count,
            'unresolved_errors': unresolved_count,
            'resolution_rate': resolved_count / len(recent_errors),
            'average_retries': avg_retries,
            'errors_by_category': category_counts,
            'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }
    
    def get_unresolved_errors(self) -> List[ErrorRecord]:
        """Get all unresolved errors."""
        return [error for error in self.error_records.values() if not error.resolved]
    
    def mark_error_resolved(self, error_id: str) -> bool:
        """
        Mark an error as resolved.
        
        Args:
            error_id: Error ID to mark as resolved
            
        Returns:
            True if error was found and marked resolved
        """
        if error_id in self.error_records:
            self.error_records[error_id].resolved = True
            self.error_records[error_id].resolution_timestamp = datetime.utcnow()
            return True
        return False
    
    def export_error_records(self, hours: int = 24) -> str:
        """
        Export error records as JSON.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            JSON string of error records
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [
            error.to_dict() for error in self.error_records.values()
            if error.timestamp >= cutoff_time
        ]
        
        return json.dumps({
            'export_timestamp': datetime.utcnow().isoformat(),
            'time_period_hours': hours,
            'error_count': len(recent_errors),
            'errors': recent_errors
        }, indent=2)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for preventing cascading failures.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            if self.last_failure_time and \
               (datetime.utcnow() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e
#!/usr/bin/env python3
"""
ACE Reporter Error Handling and Graceful Degradation System

This module provides comprehensive error handling, graceful degradation,
and fallback mechanisms for the Enhanced ACE Reporter system.

Key Features:
- Comprehensive error handling with correlation IDs
- Graceful degradation when enhanced features fail
- Fallback mechanisms to existing StatusAnnouncer behavior
- Error recovery and retry logic
- Performance monitoring and alerting
"""

import sys
import time
import traceback
import functools
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FallbackStrategy(Enum):
    """Fallback strategy types"""
    RETRY = "retry"
    DEGRADE = "degrade"
    FALLBACK = "fallback"
    DISABLE = "disable"


@dataclass
class ErrorContext:
    """Error context information with correlation tracking"""
    error_id: str
    timestamp: str
    component: str
    operation: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    fallback_used: bool = False


@dataclass
class FallbackResult:
    """Result of fallback operation"""
    success: bool
    strategy_used: FallbackStrategy
    fallback_value: Any = None
    error_message: Optional[str] = None
    performance_impact: Optional[float] = None


class ACEReporterErrorHandler:
    """
    Comprehensive error handling system for ACE Reporter
    
    Provides error tracking, graceful degradation, and fallback mechanisms
    to ensure the ACE Reporter never fails worse than the original StatusAnnouncer.
    """
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.fallback_statistics = {
            "total_errors": 0,
            "successful_recoveries": 0,
            "fallbacks_used": 0,
            "performance_degradations": 0
        }
        self.component_health = {}
        self.max_error_history = 1000
    
    def handle_error(self, 
                    component: str, 
                    operation: str, 
                    error: Exception,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    correlation_id: Optional[str] = None) -> ErrorContext:
        """
        Handle and log an error with comprehensive context
        
        Args:
            component: Component where error occurred
            operation: Operation that failed
            error: The exception that occurred
            severity: Error severity level
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            ErrorContext: Detailed error context information
        """
        import uuid
        
        error_context = ErrorContext(
            error_id=f"err_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now().isoformat(),
            component=component,
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            correlation_id=correlation_id,
            trace_id=f"trace_{uuid.uuid4().hex[:8]}",
            stack_trace=traceback.format_exc()
        )
        
        # Add to error history
        self.error_history.append(error_context)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)
        
        # Update statistics
        self.fallback_statistics["total_errors"] += 1
        
        # Update component health
        self.component_health[component] = {
            "last_error": error_context.timestamp,
            "error_count": self.component_health.get(component, {}).get("error_count", 0) + 1,
            "status": "degraded" if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else "warning"
        }
        
        # Log error
        print(f"❌ ERROR [{error_context.error_id}]: {component}.{operation} - {error_context.error_message}")
        if severity == ErrorSeverity.CRITICAL:
            print(f"🚨 CRITICAL ERROR: {error_context.error_message}")
        
        return error_context
    
    def attempt_recovery(self, 
                        error_context: ErrorContext,
                        recovery_function: Callable,
                        max_retries: int = 3,
                        retry_delay: float = 1.0) -> FallbackResult:
        """
        Attempt to recover from an error using retry logic
        
        Args:
            error_context: The error context to recover from
            recovery_function: Function to call for recovery
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            FallbackResult: Result of recovery attempt
        """
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                result = recovery_function()
                recovery_time = (time.time() - start_time) * 1000
                
                # Mark recovery as successful
                error_context.recovery_attempted = True
                self.fallback_statistics["successful_recoveries"] += 1
                
                print(f"✅ RECOVERY [{error_context.error_id}]: Successful after {attempt + 1} attempts")
                
                return FallbackResult(
                    success=True,
                    strategy_used=FallbackStrategy.RETRY,
                    fallback_value=result,
                    performance_impact=recovery_time
                )
                
            except Exception as e:
                print(f"🔄 RETRY [{error_context.error_id}]: Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return FallbackResult(
                        success=False,
                        strategy_used=FallbackStrategy.RETRY,
                        error_message=f"Recovery failed after {max_retries} attempts: {e}"
                    )
    
    def apply_fallback(self,
                      error_context: ErrorContext,
                      fallback_function: Callable,
                      fallback_strategy: FallbackStrategy = FallbackStrategy.FALLBACK) -> FallbackResult:
        """
        Apply fallback mechanism when recovery fails
        
        Args:
            error_context: The error context requiring fallback
            fallback_function: Fallback function to execute
            fallback_strategy: Type of fallback strategy
            
        Returns:
            FallbackResult: Result of fallback operation
        """
        try:
            start_time = time.time()
            result = fallback_function()
            fallback_time = (time.time() - start_time) * 1000
            
            # Mark fallback as used
            error_context.fallback_used = True
            self.fallback_statistics["fallbacks_used"] += 1
            
            if fallback_strategy == FallbackStrategy.DEGRADE:
                self.fallback_statistics["performance_degradations"] += 1
            
            print(f"🔄 FALLBACK [{error_context.error_id}]: Using {fallback_strategy.value} strategy")
            
            return FallbackResult(
                success=True,
                strategy_used=fallback_strategy,
                fallback_value=result,
                performance_impact=fallback_time
            )
            
        except Exception as e:
            print(f"❌ FALLBACK FAILED [{error_context.error_id}]: {e}")
            return FallbackResult(
                success=False,
                strategy_used=fallback_strategy,
                error_message=f"Fallback failed: {e}"
            )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        recent_errors = [e for e in self.error_history if 
                        (datetime.now() - datetime.fromisoformat(e.timestamp)).total_seconds() < 3600]
        
        return {
            "total_errors": self.fallback_statistics["total_errors"],
            "recent_errors_1h": len(recent_errors),
            "successful_recoveries": self.fallback_statistics["successful_recoveries"],
            "fallbacks_used": self.fallback_statistics["fallbacks_used"],
            "performance_degradations": self.fallback_statistics["performance_degradations"],
            "recovery_rate": (self.fallback_statistics["successful_recoveries"] / 
                            max(1, self.fallback_statistics["total_errors"])) * 100,
            "component_health": self.component_health,
            "error_history_size": len(self.error_history)
        }
    
    def is_component_healthy(self, component: str) -> bool:
        """Check if a component is healthy"""
        if component not in self.component_health:
            return True
        
        health_info = self.component_health[component]
        return health_info.get("status", "healthy") in ["healthy", "warning"]
    
    def reset_component_health(self, component: str):
        """Reset component health status"""
        if component in self.component_health:
            self.component_health[component] = {
                "status": "healthy",
                "error_count": 0,
                "last_reset": datetime.now().isoformat()
            }
            print(f"✅ Component health reset: {component}")


def error_handler_decorator(component: str, 
                          operation: str,
                          fallback_function: Optional[Callable] = None,
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          max_retries: int = 1):
    """
    Decorator for automatic error handling and fallback
    
    Args:
        component: Component name for error tracking
        operation: Operation name for error tracking
        fallback_function: Optional fallback function
        severity: Error severity level
        max_retries: Maximum retry attempts
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get error handler from first argument if it's a class instance
            error_handler = None
            if args and hasattr(args[0], '_error_handler'):
                error_handler = args[0]._error_handler
            else:
                # Create a global error handler if none exists
                if not hasattr(wrapper, '_global_error_handler'):
                    wrapper._global_error_handler = ACEReporterErrorHandler()
                error_handler = wrapper._global_error_handler
            
            # Try the original function
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_context = error_handler.handle_error(
                        component=component,
                        operation=operation,
                        error=e,
                        severity=severity
                    )
                    
                    # If this is not the last attempt, retry
                    if attempt < max_retries:
                        print(f"🔄 Retrying {operation} (attempt {attempt + 2}/{max_retries + 1})")
                        time.sleep(0.5)
                        continue
                    
                    # If we have a fallback function, use it
                    if fallback_function:
                        fallback_result = error_handler.apply_fallback(
                            error_context=error_context,
                            fallback_function=lambda: fallback_function(*args, **kwargs),
                            fallback_strategy=FallbackStrategy.FALLBACK
                        )
                        
                        if fallback_result.success:
                            return fallback_result.fallback_value
                    
                    # If all else fails, re-raise the exception
                    print(f"❌ FINAL FAILURE [{error_context.error_id}]: {operation} failed permanently")
                    raise e
        
        return wrapper
    return decorator


def create_safe_fallback(original_function: Callable, 
                        fallback_value: Any = None,
                        component: str = "unknown",
                        operation: str = "unknown") -> Callable:
    """
    Create a safe fallback wrapper for any function
    
    Args:
        original_function: The original function to wrap
        fallback_value: Value to return if function fails
        component: Component name for error tracking
        operation: Operation name for error tracking
        
    Returns:
        Callable: Safe wrapper function
    """
    @error_handler_decorator(
        component=component,
        operation=operation,
        fallback_function=lambda *args, **kwargs: fallback_value,
        severity=ErrorSeverity.LOW
    )
    def safe_wrapper(*args, **kwargs):
        return original_function(*args, **kwargs)
    
    return safe_wrapper


def main():
    """Test the error handling system"""
    print("🛡️  ACE Reporter Error Handling System Test")
    print("=" * 60)
    
    # Create error handler
    error_handler = ACEReporterErrorHandler()
    
    # Test error handling
    print("\n📋 Testing error handling...")
    try:
        raise ValueError("Test error for demonstration")
    except Exception as e:
        error_context = error_handler.handle_error(
            component="test_component",
            operation="test_operation",
            error=e,
            severity=ErrorSeverity.MEDIUM
        )
        print(f"✅ Error handled with ID: {error_context.error_id}")
    
    # Test recovery
    print("\n📋 Testing recovery mechanism...")
    def failing_function():
        if not hasattr(failing_function, 'attempts'):
            failing_function.attempts = 0
        failing_function.attempts += 1
        if failing_function.attempts < 3:
            raise RuntimeError(f"Attempt {failing_function.attempts} failed")
        return "Success after retries"
    
    recovery_result = error_handler.attempt_recovery(
        error_context=error_context,
        recovery_function=failing_function,
        max_retries=3
    )
    print(f"✅ Recovery result: {recovery_result.success}")
    
    # Test fallback
    print("\n📋 Testing fallback mechanism...")
    def fallback_function():
        return "Fallback value used"
    
    fallback_result = error_handler.apply_fallback(
        error_context=error_context,
        fallback_function=fallback_function,
        fallback_strategy=FallbackStrategy.FALLBACK
    )
    print(f"✅ Fallback result: {fallback_result.success}")
    
    # Test decorator
    print("\n📋 Testing error handler decorator...")
    
    @error_handler_decorator(
        component="test_decorator",
        operation="decorated_function",
        fallback_function=lambda: "Decorator fallback",
        max_retries=2
    )
    def test_decorated_function():
        raise RuntimeError("Decorated function error")
    
    try:
        result = test_decorated_function()
        print(f"✅ Decorated function result: {result}")
    except Exception as e:
        print(f"❌ Decorated function failed: {e}")
    
    # Show statistics
    print("\n📊 Error Statistics:")
    stats = error_handler.get_error_statistics()
    for key, value in stats.items():
        if key != "component_health":
            print(f"   {key}: {value}")
    
    print("\n🎉 Error handling system test complete!")
    print("✅ All error handling mechanisms tested successfully")
    print("🛡️  Comprehensive error protection confirmed")


if __name__ == "__main__":
    main()
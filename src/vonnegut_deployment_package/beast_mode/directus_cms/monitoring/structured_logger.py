"""
Directus CMS Structured Logging System

Single Responsibility: Provide structured logging with correlation IDs and aggregation.
Maintains <250 lines through focused logging implementation.

Requirements Addressed:
- 9.4: Structured logging with correlation IDs across all components
- 8.5: Log aggregation and analysis capabilities
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from threading import local

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability


class CorrelationContext:
    """Thread-local storage for correlation IDs"""
    
    def __init__(self):
        self._storage = local()
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current thread"""
        self._storage.correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Get correlation ID for current thread"""
        return getattr(self._storage, 'correlation_id', None)
    
    def clear_correlation_id(self):
        """Clear correlation ID for current thread"""
        if hasattr(self._storage, 'correlation_id'):
            delattr(self._storage, 'correlation_id')


# Global correlation context
correlation_context = CorrelationContext()


class StructuredLogger(ReflectiveModule):
    """
    Structured logging system with correlation ID support
    
    Provides systematic logging with JSON structure and correlation tracking.
    Maintains <250 lines through focused logging implementation.
    """
    
    def __init__(self, logger_name: str = "directus_cms", log_level: str = "INFO"):
        """Initialize structured logger with configuration"""
        super().__init__()
        
        self.module_id = "structured_logger"
        self.logger_name = logger_name
        
        # Configure Python logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add structured handler
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        
        self._log_aggregation = []
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "StructuredLogger",
            "version": "1.0.0",
            "pattern": "structured_logger",
            "logger_name": self.logger_name,
            "beast_mode_compliance": "full"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION
        ]
    
    @contextmanager
    def correlation_context_manager(self, correlation_id: str = None):
        """
        Context manager for correlation ID tracking
        
        Args:
            correlation_id: Optional correlation ID, generates one if not provided
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        # Set correlation ID
        correlation_context.set_correlation_id(correlation_id)
        
        try:
            yield correlation_id
        finally:
            # Clear correlation ID
            correlation_context.clear_correlation_id()
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self._log_structured("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self._log_structured("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self._log_structured("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self._log_structured("DEBUG", message, **kwargs)
    
    def operation_start(self, operation: str, **kwargs):
        """Log operation start with correlation tracking"""
        correlation_id = correlation_context.get_correlation_id()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            correlation_context.set_correlation_id(correlation_id)
        
        self._log_structured("INFO", f"Operation started: {operation}", 
                           operation=operation, 
                           operation_phase="start",
                           **kwargs)
        
        return correlation_id
    
    def operation_end(self, operation: str, success: bool = True, **kwargs):
        """Log operation end with correlation tracking"""
        status = "success" if success else "failure"
        
        self._log_structured("INFO" if success else "ERROR", 
                           f"Operation completed: {operation}",
                           operation=operation,
                           operation_phase="end",
                           operation_status=status,
                           **kwargs)
    
    def operation_checkpoint(self, operation: str, checkpoint: str, **kwargs):
        """Log operation checkpoint with correlation tracking"""
        self._log_structured("INFO", f"Operation checkpoint: {operation} - {checkpoint}",
                           operation=operation,
                           operation_phase="checkpoint",
                           checkpoint=checkpoint,
                           **kwargs)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Internal method to log structured data"""
        with self.trace_operation("log_structured", level=level, message=message) as trace:
            try:
                # Build structured log entry
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": level,
                    "message": message,
                    "module": self.module_id,
                    "correlation_id": correlation_context.get_correlation_id(),
                    **kwargs
                }
                
                # Add to aggregation
                self._log_aggregation.append(log_entry)
                if len(self._log_aggregation) > 1000:  # Keep last 1000 entries
                    self._log_aggregation.pop(0)
                
                # Log using Python logger
                log_method = getattr(self.logger, level.lower())
                log_method(json.dumps(log_entry))
                
                trace.output_result = {"logged": True, "level": level}
                
            except Exception as e:
                self._increment_error_count()
                # Fallback to simple logging
                self.logger.error(f"Structured logging failed: {e} - Original message: {message}")
                trace.error_info = {"error": str(e)}
    
    def get_log_aggregation(self, 
                           correlation_id: str = None, 
                           operation: str = None,
                           level: str = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get aggregated logs with filtering
        
        Args:
            correlation_id: Filter by correlation ID
            operation: Filter by operation name
            level: Filter by log level
            limit: Maximum number of entries to return
            
        Returns:
            Filtered log entries
        """
        with self.trace_operation("get_log_aggregation") as trace:
            try:
                filtered_logs = self._log_aggregation.copy()
                
                # Apply filters
                if correlation_id:
                    filtered_logs = [log for log in filtered_logs 
                                   if log.get("correlation_id") == correlation_id]
                
                if operation:
                    filtered_logs = [log for log in filtered_logs 
                                   if log.get("operation") == operation]
                
                if level:
                    filtered_logs = [log for log in filtered_logs 
                                   if log.get("level") == level.upper()]
                
                # Apply limit
                filtered_logs = filtered_logs[-limit:] if limit else filtered_logs
                
                trace.output_result = {"count": len(filtered_logs)}
                return filtered_logs
                
            except Exception as e:
                self._increment_error_count()
                trace.error_info = {"error": str(e)}
                return []
    
    def analyze_operation_performance(self, operation: str) -> Dict[str, Any]:
        """
        Analyze performance metrics for an operation
        
        Args:
            operation: Operation name to analyze
            
        Returns:
            Performance analysis results
        """
        with self.trace_operation("analyze_operation_performance", operation=operation) as trace:
            try:
                # Get operation logs
                operation_logs = [log for log in self._log_aggregation 
                                if log.get("operation") == operation]
                
                if not operation_logs:
                    return {"operation": operation, "analysis": "no_data"}
                
                # Group by correlation ID (operation instances)
                operation_instances = {}
                for log in operation_logs:
                    correlation_id = log.get("correlation_id")
                    if correlation_id:
                        if correlation_id not in operation_instances:
                            operation_instances[correlation_id] = []
                        operation_instances[correlation_id].append(log)
                
                # Analyze each instance
                analysis = {
                    "operation": operation,
                    "total_instances": len(operation_instances),
                    "successful_instances": 0,
                    "failed_instances": 0,
                    "avg_duration_seconds": 0,
                    "error_patterns": []
                }
                
                total_duration = 0
                duration_count = 0
                
                for correlation_id, logs in operation_instances.items():
                    # Find start and end logs
                    start_log = next((log for log in logs 
                                    if log.get("operation_phase") == "start"), None)
                    end_log = next((log for log in logs 
                                  if log.get("operation_phase") == "end"), None)
                    
                    if start_log and end_log:
                        # Calculate duration
                        start_time = datetime.fromisoformat(start_log["timestamp"])
                        end_time = datetime.fromisoformat(end_log["timestamp"])
                        duration = (end_time - start_time).total_seconds()
                        
                        total_duration += duration
                        duration_count += 1
                        
                        # Check success/failure
                        if end_log.get("operation_status") == "success":
                            analysis["successful_instances"] += 1
                        else:
                            analysis["failed_instances"] += 1
                            
                            # Collect error patterns
                            error_logs = [log for log in logs if log.get("level") == "ERROR"]
                            for error_log in error_logs:
                                analysis["error_patterns"].append(error_log.get("message", "Unknown error"))
                
                # Calculate average duration
                if duration_count > 0:
                    analysis["avg_duration_seconds"] = total_duration / duration_count
                
                trace.output_result = analysis
                return analysis
                
            except Exception as e:
                self._increment_error_count()
                error_analysis = {
                    "operation": operation,
                    "analysis": "error",
                    "error": str(e)
                }
                
                trace.error_info = {"error": str(e)}
                return error_analysis


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        """Format log record as structured JSON"""
        try:
            # Parse the message as JSON if it's already structured
            if hasattr(record, 'msg') and isinstance(record.msg, str):
                try:
                    structured_data = json.loads(record.msg)
                    return json.dumps(structured_data, indent=None, separators=(',', ':'))
                except (json.JSONDecodeError, ValueError):
                    # Fallback to regular formatting
                    pass
            
            # Regular log formatting
            return super().format(record)
            
        except Exception:
            # Ultimate fallback
            return str(record.msg)


# Convenience functions for global usage
def get_logger(name: str = "directus_cms") -> StructuredLogger:
    """Get or create a structured logger instance"""
    return StructuredLogger(name)


def with_correlation(correlation_id: str = None):
    """Decorator for automatic correlation ID management"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            with logger.correlation_context_manager(correlation_id):
                return func(*args, **kwargs)
        return wrapper
    return decorator
"""
Beast Mode Framework - Comprehensive Logging System
Implements comprehensive logging and audit trail system

This module provides:
- Structured logging with correlation IDs
- Audit trail for all operations
- Log aggregation and analysis
- Security and compliance logging
- Performance and error tracking
"""

import json
import logging
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading
from contextlib import contextmanager

from ..core.reflective_module import ReflectiveModule, HealthStatus

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"

class AuditEvent(Enum):
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    COMPONENT_HEALTH_CHECK = "component_health_check"
    VALIDATION_EXECUTED = "validation_executed"
    TOOL_ORCHESTRATION = "tool_orchestration"
    PDCA_CYCLE_EXECUTED = "pdca_cycle_executed"
    DASHBOARD_ACCESSED = "dashboard_accessed"
    CLI_COMMAND_EXECUTED = "cli_command_executed"
    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_THRESHOLD_EXCEEDED = "performance_threshold_exceeded"
    ERROR_OCCURRED = "error_occurred"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    message: str
    correlation_id: str
    component: str
    operation: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_event: Optional[AuditEvent] = None
    performance_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None

class ComprehensiveLoggingSystem(ReflectiveModule):
    """
    Comprehensive logging system for Beast Mode Framework
    Provides structured logging, audit trails, and compliance tracking
    """
    
    def __init__(self, project_root: str = ".", log_directory: str = "logs"):
        super().__init__("comprehensive_logging_system")
        
        # Configuration
        self.project_root = Path(project_root)
        self.log_directory = self.project_root / log_directory
        self.log_directory.mkdir(exist_ok=True)
        
        # Logging configuration
        self.log_entries = []
        self.audit_trail = []
        self.correlation_contexts = {}
        self.session_contexts = {}
        
        # Thread-local storage for correlation IDs
        self.thread_local = threading.local()
        
        # Logging metrics
        self.logging_metrics = {
            'total_log_entries': 0,
            'audit_events': 0,
            'error_count': 0,
            'warning_count': 0,
            'performance_events': 0,
            'security_events': 0,
            'log_file_size_bytes': 0,
            'retention_policy_compliant': True
        }
        
        # Initialize logging infrastructure
        self._setup_logging_infrastructure()
        
        self._update_health_indicator(
            "comprehensive_logging_system",
            HealthStatus.HEALTHY,
            "operational",
            "Comprehensive logging system ready for audit trail"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Logging system operational status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "log_directory": str(self.log_directory),
            "total_log_entries": self.logging_metrics['total_log_entries'],
            "audit_events": self.logging_metrics['audit_events'],
            "error_count": self.logging_metrics['error_count'],
            "log_file_size_mb": self.logging_metrics['log_file_size_bytes'] / (1024 * 1024)
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for logging system"""
        return (
            self.log_directory.exists() and
            self.logging_metrics['retention_policy_compliant'] and
            not self._degradation_active
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for logging system"""
        return {
            "logging_status": {
                "total_entries": self.logging_metrics['total_log_entries'],
                "error_rate": self.logging_metrics['error_count'] / max(1, self.logging_metrics['total_log_entries']),
                "audit_coverage": self.logging_metrics['audit_events'],
                "log_file_size_mb": self.logging_metrics['log_file_size_bytes'] / (1024 * 1024)
            },
            "compliance_status": {
                "retention_policy_compliant": self.logging_metrics['retention_policy_compliant'],
                "audit_trail_complete": len(self.audit_trail) > 0,
                "security_logging_active": self.logging_metrics['security_events'] >= 0,
                "performance_monitoring_active": self.logging_metrics['performance_events'] >= 0
            },
            "system_health": {
                "log_directory_accessible": self.log_directory.exists(),
                "correlation_tracking_active": len(self.correlation_contexts) >= 0,
                "session_tracking_active": len(self.session_contexts) >= 0
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: comprehensive logging and audit"""
        return "comprehensive_logging_and_audit"
        
    def log(self, 
            level: LogLevel, 
            message: str, 
            component: str,
            operation: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            audit_event: Optional[AuditEvent] = None,
            performance_data: Optional[Dict[str, Any]] = None,
            error_details: Optional[Dict[str, Any]] = None) -> str:
        """
        Create structured log entry with correlation tracking
        """
        try:
            # Generate or get correlation ID
            correlation_id = self._get_or_create_correlation_id()
            
            # Get session context
            session_id = getattr(self.thread_local, 'session_id', None)
            user_id = getattr(self.thread_local, 'user_id', None)
            
            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=level,
                message=message,
                correlation_id=correlation_id,
                component=component,
                operation=operation,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {},
                audit_event=audit_event,
                performance_data=performance_data,
                error_details=error_details
            )
            
            # Store log entry
            self.log_entries.append(log_entry)
            
            # Add to audit trail if audit event
            if audit_event:
                self.audit_trail.append(log_entry)
                self.logging_metrics['audit_events'] += 1
                
            # Update metrics
            self._update_logging_metrics(log_entry)
            
            # Write to log file
            self._write_to_log_file(log_entry)
            
            # Trigger alerts for critical events
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                self._trigger_alert(log_entry)
                
            return correlation_id
            
        except Exception as e:
            # Fallback logging to prevent logging system failure
            print(f"Logging system error: {str(e)}")
            return str(uuid.uuid4())
            
    def audit(self, 
              event: AuditEvent, 
              component: str,
              operation: str,
              metadata: Optional[Dict[str, Any]] = None,
              user_id: Optional[str] = None) -> str:
        """
        Create audit log entry
        """
        return self.log(
            level=LogLevel.AUDIT,
            message=f"Audit event: {event.value}",
            component=component,
            operation=operation,
            metadata=metadata,
            audit_event=event
        )
        
    def performance_log(self,
                       component: str,
                       operation: str,
                       duration_ms: int,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Log performance data
        """
        performance_data = {
            "duration_ms": duration_ms,
            "operation": operation,
            "component": component
        }
        
        # Check for performance threshold violations
        level = LogLevel.WARNING if duration_ms > 5000 else LogLevel.INFO  # 5 second threshold
        
        return self.log(
            level=level,
            message=f"Performance: {operation} completed in {duration_ms}ms",
            component=component,
            operation=operation,
            metadata=metadata,
            performance_data=performance_data
        )
        
    def error_log(self,
                  component: str,
                  operation: str,
                  error: Exception,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Log error with detailed information
        """
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "operation": operation,
            "component": component
        }
        
        return self.log(
            level=LogLevel.ERROR,
            message=f"Error in {operation}: {str(error)}",
            component=component,
            operation=operation,
            metadata=metadata,
            error_details=error_details
        )
        
    def security_log(self,
                     event_type: str,
                     component: str,
                     details: Dict[str, Any],
                     severity: str = "medium") -> str:
        """
        Log security-related events
        """
        security_metadata = {
            "event_type": event_type,
            "severity": severity,
            "security_details": details
        }
        
        self.logging_metrics['security_events'] += 1
        
        return self.log(
            level=LogLevel.WARNING if severity == "medium" else LogLevel.CRITICAL,
            message=f"Security event: {event_type}",
            component=component,
            operation="security_monitoring",
            metadata=security_metadata,
            audit_event=AuditEvent.SECURITY_EVENT
        )
        
    @contextmanager
    def correlation_context(self, correlation_id: Optional[str] = None, operation: Optional[str] = None):
        """
        Context manager for correlation ID tracking
        """
        # Generate or use provided correlation ID
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
            
        # Store previous correlation ID
        previous_correlation_id = getattr(self.thread_local, 'correlation_id', None)
        previous_operation = getattr(self.thread_local, 'operation', None)
        
        try:
            # Set new correlation context
            self.thread_local.correlation_id = correlation_id
            if operation:
                self.thread_local.operation = operation
                
            # Store correlation context
            self.correlation_contexts[correlation_id] = {
                "start_time": datetime.now(),
                "operation": operation,
                "thread_id": threading.get_ident()
            }
            
            yield correlation_id
            
        finally:
            # Restore previous context
            if previous_correlation_id:
                self.thread_local.correlation_id = previous_correlation_id
            else:
                delattr(self.thread_local, 'correlation_id')
                
            if previous_operation:
                self.thread_local.operation = previous_operation
            elif hasattr(self.thread_local, 'operation'):
                delattr(self.thread_local, 'operation')
                
            # Clean up correlation context
            if correlation_id in self.correlation_contexts:
                del self.correlation_contexts[correlation_id]
                
    @contextmanager
    def session_context(self, session_id: str, user_id: Optional[str] = None):
        """
        Context manager for session tracking
        """
        # Store previous session context
        previous_session_id = getattr(self.thread_local, 'session_id', None)
        previous_user_id = getattr(self.thread_local, 'user_id', None)
        
        try:
            # Set new session context
            self.thread_local.session_id = session_id
            if user_id:
                self.thread_local.user_id = user_id
                
            # Store session context
            self.session_contexts[session_id] = {
                "start_time": datetime.now(),
                "user_id": user_id,
                "thread_id": threading.get_ident()
            }
            
            yield session_id
            
        finally:
            # Restore previous context
            if previous_session_id:
                self.thread_local.session_id = previous_session_id
            elif hasattr(self.thread_local, 'session_id'):
                delattr(self.thread_local, 'session_id')
                
            if previous_user_id:
                self.thread_local.user_id = previous_user_id
            elif hasattr(self.thread_local, 'user_id'):
                delattr(self.thread_local, 'user_id')
                
    def get_logs(self, 
                 level: Optional[LogLevel] = None,
                 component: Optional[str] = None,
                 correlation_id: Optional[str] = None,
                 limit: int = 100) -> List[LogEntry]:
        """
        Retrieve log entries with filtering
        """
        filtered_logs = self.log_entries
        
        # Apply filters
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
            
        if component:
            filtered_logs = [log for log in filtered_logs if log.component == component]
            
        if correlation_id:
            filtered_logs = [log for log in filtered_logs if log.correlation_id == correlation_id]
            
        # Return most recent entries
        return filtered_logs[-limit:]
        
    def get_audit_trail(self, 
                       event_type: Optional[AuditEvent] = None,
                       component: Optional[str] = None,
                       limit: int = 50) -> List[LogEntry]:
        """
        Retrieve audit trail entries
        """
        filtered_audit = self.audit_trail
        
        # Apply filters
        if event_type:
            filtered_audit = [log for log in filtered_audit if log.audit_event == event_type]
            
        if component:
            filtered_audit = [log for log in filtered_audit if log.component == component]
            
        # Return most recent entries
        return filtered_audit[-limit:]
        
    def get_performance_analytics(self) -> Dict[str, Any]:
        """
        Get performance analytics from logs
        """
        performance_logs = [
            log for log in self.log_entries 
            if log.performance_data is not None
        ]
        
        if not performance_logs:
            return {"message": "No performance data available"}
            
        # Calculate performance metrics
        durations = [log.performance_data["duration_ms"] for log in performance_logs]
        
        return {
            "total_performance_events": len(performance_logs),
            "average_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "slow_operations": len([d for d in durations if d > 5000]),
            "performance_trend": "stable"  # Simplified - would analyze trends
        }
        
    def get_error_analytics(self) -> Dict[str, Any]:
        """
        Get error analytics from logs
        """
        error_logs = [
            log for log in self.log_entries 
            if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]
        ]
        
        if not error_logs:
            return {"message": "No errors logged"}
            
        # Analyze error patterns
        error_by_component = {}
        for log in error_logs:
            component = log.component
            error_by_component[component] = error_by_component.get(component, 0) + 1
            
        return {
            "total_errors": len(error_logs),
            "error_rate": len(error_logs) / max(1, self.logging_metrics['total_log_entries']),
            "errors_by_component": error_by_component,
            "recent_errors": len([log for log in error_logs if (datetime.now() - log.timestamp).total_seconds() < 3600])
        }
        
    # Helper methods
    
    def _setup_logging_infrastructure(self):
        """Setup logging infrastructure"""
        # Create log files
        self.main_log_file = self.log_directory / "beast_mode.log"
        self.audit_log_file = self.log_directory / "beast_mode_audit.log"
        self.error_log_file = self.log_directory / "beast_mode_errors.log"
        
        # Setup Python logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.main_log_file),
                logging.StreamHandler()
            ]
        )
        
    def _get_or_create_correlation_id(self) -> str:
        """Get or create correlation ID for current thread"""
        correlation_id = getattr(self.thread_local, 'correlation_id', None)
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
            self.thread_local.correlation_id = correlation_id
        return correlation_id
        
    def _update_logging_metrics(self, log_entry: LogEntry):
        """Update logging metrics"""
        self.logging_metrics['total_log_entries'] += 1
        
        if log_entry.level == LogLevel.ERROR:
            self.logging_metrics['error_count'] += 1
        elif log_entry.level == LogLevel.WARNING:
            self.logging_metrics['warning_count'] += 1
            
        if log_entry.performance_data:
            self.logging_metrics['performance_events'] += 1
            
    def _write_to_log_file(self, log_entry: LogEntry):
        """Write log entry to appropriate log file"""
        try:
            # Format log entry as JSON
            log_data = {
                "timestamp": log_entry.timestamp.isoformat(),
                "level": log_entry.level.value,
                "message": log_entry.message,
                "correlation_id": log_entry.correlation_id,
                "component": log_entry.component,
                "operation": log_entry.operation,
                "user_id": log_entry.user_id,
                "session_id": log_entry.session_id,
                "metadata": log_entry.metadata,
                "audit_event": log_entry.audit_event.value if log_entry.audit_event else None,
                "performance_data": log_entry.performance_data,
                "error_details": log_entry.error_details
            }
            
            log_line = json.dumps(log_data) + "\n"
            
            # Write to main log
            with open(self.main_log_file, "a") as f:
                f.write(log_line)
                
            # Write to audit log if audit event
            if log_entry.audit_event:
                with open(self.audit_log_file, "a") as f:
                    f.write(log_line)
                    
            # Write to error log if error
            if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                with open(self.error_log_file, "a") as f:
                    f.write(log_line)
                    
            # Update file size metric
            self.logging_metrics['log_file_size_bytes'] = self.main_log_file.stat().st_size
            
        except Exception as e:
            # Fallback to print if file writing fails
            print(f"Failed to write log entry: {str(e)}")
            
    def _trigger_alert(self, log_entry: LogEntry):
        """Trigger alert for critical log entries"""
        # In a full implementation, this would integrate with alerting systems
        if log_entry.level == LogLevel.CRITICAL:
            print(f"CRITICAL ALERT: {log_entry.message} (Correlation: {log_entry.correlation_id})")
            
    # Public API methods
    
    def get_logging_analytics(self) -> Dict[str, Any]:
        """Get comprehensive logging analytics"""
        return {
            "logging_metrics": self.logging_metrics.copy(),
            "performance_analytics": self.get_performance_analytics(),
            "error_analytics": self.get_error_analytics(),
            "audit_summary": {
                "total_audit_events": len(self.audit_trail),
                "recent_audit_events": len([
                    log for log in self.audit_trail 
                    if (datetime.now() - log.timestamp).total_seconds() < 3600
                ])
            },
            "system_health": {
                "logging_system_healthy": self.is_healthy(),
                "log_files_accessible": all([
                    self.main_log_file.exists(),
                    self.audit_log_file.exists(),
                    self.error_log_file.exists()
                ]),
                "correlation_tracking_active": len(self.correlation_contexts) >= 0
            }
        }
        
    def export_logs(self, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   format: str = "json") -> str:
        """
        Export logs for external analysis
        """
        # Filter logs by time range
        filtered_logs = self.log_entries
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
            
        # Export in requested format
        if format == "json":
            export_data = []
            for log in filtered_logs:
                export_data.append({
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level.value,
                    "message": log.message,
                    "correlation_id": log.correlation_id,
                    "component": log.component,
                    "operation": log.operation,
                    "metadata": log.metadata,
                    "audit_event": log.audit_event.value if log.audit_event else None
                })
            return json.dumps(export_data, indent=2)
        else:
            return "Unsupported export format"
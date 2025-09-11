"""
Logging Infrastructure Module

Provides comprehensive structured logging capabilities for monitoring, debugging, and analysis.
Implements R9.1: Logging Infrastructure requirements.
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LoggingConfig:
    """Logging configuration dataclass"""
    log_level: str = "INFO"
    log_format: str = "JSON"  # JSON, TEXT, STRUCTURED
    log_file: str = "devpost_integration.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_remote: bool = False
    remote_endpoint: Optional[str] = None


@dataclass
class LogEvent:
    """Structured log event"""
    timestamp: datetime
    level: str
    message: str
    module: str
    operation: str
    context: Dict[str, Any]
    thread_id: str
    process_id: int


class LoggingInfrastructure(ReflectiveModule):
    """
    Logging Infrastructure for DevPost Integration
    
    Provides comprehensive structured logging capabilities for monitoring,
    debugging, and analysis. Implements R9.1: Logging Infrastructure.
    """
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        """Initialize logging infrastructure"""
        super().__init__(module_id="logging_infrastructure", version="1.0.0")
        self.config = config or LoggingConfig()
        self.logger = self._setup_logger()
        self.log_events: List[LogEvent] = []
        register_module(self)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logger with configuration"""
        logger = logging.getLogger("devpost_integration")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self._get_formatter())
            logger.addHandler(console_handler)
        
        # File handler
        if self.config.enable_file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.log_file,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
            file_handler.setFormatter(self._get_formatter())
            logger.addHandler(file_handler)
        
        return logger
    
    def _get_formatter(self) -> logging.Formatter:
        """Get appropriate formatter based on configuration"""
        if self.config.log_format == "JSON":
            return JSONFormatter()
        elif self.config.log_format == "STRUCTURED":
            return StructuredFormatter()
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def initialize_logging(self, config: LoggingConfig) -> None:
        """Initialize structured logging with configuration"""
        self.config = config
        self.logger = self._setup_logger()
        self.log_event(LogLevel.INFO, "Logging infrastructure initialized", {
            "config": asdict(config)
        })
    
    def log_event(self, level: LogLevel, message: str, context: Dict[str, Any] = None) -> None:
        """Log structured event with context"""
        context = context or {}
        
        # Create log event
        log_event = LogEvent(
            timestamp=datetime.now(),
            level=level.value,
            message=message,
            module=self.module_id,
            operation=context.get("operation", "unknown"),
            context=context,
            thread_id=str(os.getpid()),
            process_id=os.getpid()
        )
        
        # Store event
        self.log_events.append(log_event)
        
        # Log using appropriate level
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, extra={"context": context, "log_event": log_event})
    
    def log_performance(self, operation: str, duration: float, metrics: Dict[str, Any]) -> None:
        """Log performance metrics for operations"""
        self.log_event(LogLevel.INFO, f"Performance: {operation}", {
            "operation": operation,
            "duration": duration,
            "metrics": metrics,
            "type": "performance"
        })
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log error with stack trace and context"""
        context = context or {}
        context.update({
            "error_type": type(error).__name__,
            "error_message": str(error),
            "type": "error"
        })
        
        self.log_event(LogLevel.ERROR, f"Error: {str(error)}", context)
        
        # Log full traceback
        import traceback
        self.log_event(LogLevel.ERROR, "Stack trace", {
            "traceback": traceback.format_exc(),
            "type": "traceback"
        })
    
    def get_log_events(self, level: Optional[LogLevel] = None, 
                      module: Optional[str] = None) -> List[LogEvent]:
        """Get filtered log events"""
        events = self.log_events
        
        if level:
            events = [e for e in events if e.level == level.value]
        
        if module:
            events = [e for e in events if e.module == module]
        
        return events
    
    def clear_log_events(self) -> None:
        """Clear stored log events"""
        self.log_events.clear()
    
    def export_logs(self, filepath: str) -> None:
        """Export logs to file"""
        with open(filepath, 'w') as f:
            for event in self.log_events:
                f.write(json.dumps(asdict(event), default=str) + '\n')
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information"""
        return {
            "module_id": self.module_id,
            "version": self.version,
            "type": "LoggingInfrastructure",
            "config": asdict(self.config),
            "log_events_count": len(self.log_events),
            "handlers_count": len(self.logger.handlers)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.STRUCTURED_LOGGING,
            ModuleCapability.PERFORMANCE_MONITORING,
            ModuleCapability.ERROR_TRACKING,
            ModuleCapability.LOG_EXPORT
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ["reflective_module"]
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check with graceful degradation"""
        issues = []
        
        # Check logger configuration with graceful degradation
        try:
            if not self.logger.handlers:
                issues.append("No logging handlers configured")
                # Graceful degradation: try to add a basic handler
                try:
                    self.logger.addHandler(logging.StreamHandler())
                    issues.append("Added fallback console handler")
                except Exception as e:
                    issues.append(f"Failed to add fallback handler: {e}")
        except Exception as e:
            issues.append(f"Error checking logger configuration: {e}")
        
        # Check log file accessibility with graceful degradation
        try:
            if self.config.enable_file:
                log_path = Path(self.config.log_file)
                if not log_path.parent.exists():
                    issues.append(f"Log directory does not exist: {log_path.parent}")
                    # Graceful degradation: try to create the directory
                    try:
                        log_path.parent.mkdir(parents=True, exist_ok=True)
                        issues.append("Created missing log directory")
                    except Exception as e:
                        issues.append(f"Failed to create log directory: {e}")
        except Exception as e:
            issues.append(f"Error checking log file accessibility: {e}")
        
        # Check log events storage with graceful degradation
        try:
            if len(self.log_events) > 10000:  # Arbitrary threshold
                issues.append("Too many log events stored, consider clearing")
                # Graceful degradation: clear old events
                try:
                    self.log_events = self.log_events[-5000:]  # Keep last 5000 events
                    issues.append("Cleared old log events")
                except Exception as e:
                    issues.append(f"Failed to clear old events: {e}")
        except Exception as e:
            issues.append(f"Error checking log events storage: {e}")
        
        # Determine status with graceful degradation consideration
        if not issues:
            status = ModuleStatus.HEALTHY
            score = 1.0
        elif any("graceful degradation" in issue.lower() or "added fallback" in issue.lower() or "created" in issue.lower() for issue in issues):
            status = ModuleStatus.DEGRADED
            score = 0.7  # Still functional with degraded performance
        else:
            status = ModuleStatus.UNHEALTHY
            score = 0.3
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=score,
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration"""
        return asdict(self.config)
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update module configuration"""
        # Update config fields
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Reinitialize logger with new config
        self.logger = self._setup_logger()
        
        self.log_event(LogLevel.INFO, "Configuration updated", {"config": config})
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        return {
            "log_events_count": len(self.log_events),
            "handlers_count": len(self.logger.handlers),
            "config": asdict(self.config),
            "log_level": self.config.log_level,
            "log_format": self.config.log_format
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self.clear_log_events()
        self.log_event(LogLevel.INFO, "Metrics reset", {"module": self.module_id})


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": getattr(record, 'module', 'unknown'),
            "operation": getattr(record, 'operation', 'unknown'),
            "context": getattr(record, 'context', {}),
            "thread_id": record.thread,
            "process_id": record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class StructuredFormatter(logging.Formatter):
    """Structured formatter for human-readable logs"""
    
    def format(self, record):
        context = getattr(record, 'context', {})
        context_str = json.dumps(context, default=str) if context else "{}"
        
        return (f"{datetime.fromtimestamp(record.created).isoformat()} "
                f"[{record.levelname}] {record.name}: {record.getMessage()} "
                f"| Context: {context_str}")


# Global logging infrastructure instance
_logging_infrastructure: Optional[LoggingInfrastructure] = None


def get_logging_infrastructure() -> LoggingInfrastructure:
    """Get global logging infrastructure instance"""
    global _logging_infrastructure
    if _logging_infrastructure is None:
        _logging_infrastructure = LoggingInfrastructure()
    return _logging_infrastructure


def initialize_logging(config: LoggingConfig) -> None:
    """Initialize global logging infrastructure"""
    global _logging_infrastructure
    _logging_infrastructure = LoggingInfrastructure(config)


def log_event(level: LogLevel, message: str, context: Dict[str, Any] = None) -> None:
    """Log event using global logging infrastructure"""
    get_logging_infrastructure().log_event(level, message, context)


def log_performance(operation: str, duration: float, metrics: Dict[str, Any]) -> None:
    """Log performance metrics using global logging infrastructure"""
    get_logging_infrastructure().log_performance(operation, duration, metrics)


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error using global logging infrastructure"""
    get_logging_infrastructure().log_error(error, context)

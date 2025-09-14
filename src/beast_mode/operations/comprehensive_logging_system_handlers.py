"""
Comprehensive Logging System Handlers

This module was extracted from comprehensive_logging_system.py
as part of RM-DDD compliance refactoring.
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

class ComprehensiveLoggingHandler(logging.Handler):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Custom logging handler that forwards to ComprehensiveLoggingSystem"""

    def __init__(self, logging_system) -> Any:
        super().__init__()
        self.logging_system = logging_system

    def emit(self, record) -> Any:
        """Emit a log record to the comprehensive logging system"""
        try:
            level_mapping = {logging.DEBUG: LogLevel.DEBUG, logging.INFO: LogLevel.INFO, logging.WARNING: LogLevel.WARNING, logging.ERROR: LogLevel.ERROR, logging.CRITICAL: LogLevel.CRITICAL}
            level = level_mapping.get(record.levelno, LogLevel.INFO)
            message = self.format(record)
            component = record.name.replace('beast_mode.', '') if record.name.startswith('beast_mode.') else record.name
            self.logging_system.log(level=level, message=message, component=component, operation=getattr(record, 'operation', None), metadata={'logger_name': record.name, 'module': record.module} if hasattr(record, 'module') else {'logger_name': record.name})
        except Exception:
            pass

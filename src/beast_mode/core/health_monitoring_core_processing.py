"""
Health Monitoring Core Processing

This module was extracted from health_monitoring_core.py
as part of RM-DDD compliance refactoring.
"""

import time
import threading
import queue
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
from .reflective_module import ReflectiveModule, HealthStatus, HealthIndicator
from ..utils.enum_serialization import SerializationHandler, make_enum_json_serializable
from src.rm_ddd.core.health import ModuleHealth


def _process_alerts(self):
    """Process alert queue"""
    while not self.alerts.empty():
        try:
            alert = self.alerts.get_nowait()
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    self.logger.error(f'Alert handler failed: {e}')
        except queue.Empty:
            break
        except Exception as e:
            self.logger.error(f'Alert processing error: {e}')

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }


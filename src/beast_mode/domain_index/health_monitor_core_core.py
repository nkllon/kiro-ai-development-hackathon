import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import DomainSystemComponent
from .interfaces import HealthMonitorInterface
from .models import Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory, HealthStatusCollection
from .exceptions import HealthMonitorError, HealthCheckFailedError
from .config import get_config
from .health_reporter import HealthReportGenerator
from ..utils.path_normalizer import safe_relative_to
from .health_monitor_core_core_core import *
from .health_monitor_core_core_validation import *
from src.rm_ddd.core.health import ModuleHealth


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


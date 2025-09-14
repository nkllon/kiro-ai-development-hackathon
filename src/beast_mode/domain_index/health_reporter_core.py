import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
from .base import DomainSystemComponent
from .models import Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory, HealthStatusCollection
from .exceptions import HealthReportError, AlertingError
from .config import get_config
from ..utils.enum_serialization import SerializationHandler
from ..utils.enum_serialization import make_enum_json_serializable
from ..utils.enum_serialization import make_enum_json_serializable
from .health_reporter_core_core import *
from .health_reporter_core_processing import *
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


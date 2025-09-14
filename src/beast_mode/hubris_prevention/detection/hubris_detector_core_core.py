from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from ..interfaces import HubrisDetector
from ..models import Decision, HubrisScore, VelocityAlert, BypassAlert, EscalationAction, HubrisFactor, RecommendedAction, TrendDirection, RiskLevel
from .hubris_detector_core_core_core import *
from .hubris_detector_core_core_validation import *
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


from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from ..models import Decision, Actor, BypassAlert, EscalationAction, GovernanceIntervention, InterventionType
from ..models import TriggerEvent
from ..models import EscalationStep
from ..models import SuccessCriterion
from ..models import RollbackPlan
from ..models import TriggerEvent
from ..models import EscalationStep
from ..models import SuccessCriterion
from ..models import RollbackPlan
from ..models import TriggerEvent
from ..models import EscalationStep
from ..models import SuccessCriterion
from ..models import RollbackPlan
from .bypass_detector_core_validation import *
from .bypass_detector_core_processing import *
from .bypass_detector_core_core import *
from src.rm_ddd.core.health import ModuleHealth


class RegistermoduleClass:
    """Auto-generated class for functions."""

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


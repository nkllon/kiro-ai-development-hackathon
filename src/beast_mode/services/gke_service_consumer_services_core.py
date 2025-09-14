import time
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..orchestration.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.registry_intelligence_engine import RegistryIntelligenceEngine
from ..tools.makefile_health_manager import MakefileHealthManager
from ..testing.comprehensive_test_suite import ComprehensiveTestSuite
from .gke_service_consumer_services_core_core import *
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


from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..models import SpecToCodeModel, SystematicSuperiorityModel, MultiAgentCollaborationModel, ProductionInfrastructureModel, Task, HumanInput, GKEConfig
from ..views import HackathonDemoView, DemoPhase, DemoContent
from .hackathon_demo_controller_processing import *
from .hackathon_demo_controller_handlers import *
from .hackathon_demo_controller_core import *
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


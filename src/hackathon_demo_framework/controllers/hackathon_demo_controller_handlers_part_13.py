from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Hackathon Demo Controller Handlers

This module was extracted from hackathon_demo_controller.py
as part of RM-DDD compliance refactoring.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..models import SpecToCodeModel, SystematicSuperiorityModel, MultiAgentCollaborationModel, ProductionInfrastructureModel, Task, HumanInput, GKEConfig
from ..views import HackathonDemoView, DemoPhase, DemoContent
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


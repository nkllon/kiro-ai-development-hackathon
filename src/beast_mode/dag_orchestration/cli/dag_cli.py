import asyncio
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import click
from tabulate import tabulate
from ..core.orchestration_engine import OrchestrationEngine, ResourceConstraints, OrchestrationResult
from ..optimization.mvp_calculator import MVPCriteria
from ..optimization.risk_assessor import RiskImpact, SuccessProbabilityFactors
from .dag_cli_core import *
from .dag_cli_validation import *
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


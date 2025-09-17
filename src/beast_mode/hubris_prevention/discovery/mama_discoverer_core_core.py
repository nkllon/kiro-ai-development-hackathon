from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import dataclass
from ..interfaces import MamaDiscoverer
from ..models import AccountabilityChain, AccountabilityRelationship, ConstraintSource, IndependenceClaim, ResearchResult, ChainChange, MappingUpdate, HumanEscalation
from .mama_discoverer_core_core_validation import *
from .mama_discoverer_core_core_core import *
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


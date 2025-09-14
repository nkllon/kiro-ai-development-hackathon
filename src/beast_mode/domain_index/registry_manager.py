import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import CachedComponent
from .interfaces import DomainRegistryInterface
from .models import Domain, DomainTools, DomainMetadata, PackagePotential, DomainCollection, ValidationResult, DependencyGraph
from .exceptions import DomainRegistryError, DomainNotFoundError, DomainValidationError, RegistryCorruptionError
from .config import get_config
from .domain_cache import DomainCache, DomainSpecificCache
from .domain_index import DomainIndex
from .domain_validator import DomainValidator
from .registry_manager_validation import *
from .registry_manager_core import *
from .registry_manager_services import *
from .registry_manager_processing import *
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


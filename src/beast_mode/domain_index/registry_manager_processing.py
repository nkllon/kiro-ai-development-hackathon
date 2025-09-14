"""
Registry Manager Processing

This module was extracted from registry_manager.py
as part of RM-DDD compliance refactoring.
"""

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
from src.rm_ddd.core.health import ModuleHealth


def _parse_domains(self) -> None:
    """Parse domains from raw registry data"""
    self._domains = {}
    domain_arch = self._raw_registry_data.get('domain_architecture', {})
    for category_name, category_data in domain_arch.items():
        if category_name == 'overview':
            continue
        if isinstance(category_data, dict) and 'domains' in category_data:
            for domain_name in category_data['domains']:
                domain = self._create_domain_from_registry(domain_name, category_name, category_data)
                if domain:
                    self._domains[domain_name] = domain

"""
Registry Manager Validation

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


def validate_domain(self, domain: Domain) -> ValidationResult:
    """Validate domain structure and requirements using comprehensive validator"""
    with self._time_operation('validate_domain'):
        self.validation_count += 1
        context = {'all_domains': self._domains}
        return self._validator.validate_domain(domain, context)

def invalidate_cache_by_category(self, category: str) -> int:
    """Invalidate all cached domains in a category"""
    return self._domain_cache.invalidate_by_category(category)

def validate_all_domains(self) -> Dict[str, ValidationResult]:
    """Validate all domains in the registry"""
    with self._time_operation('validate_all_domains'):
        return self._validator.validate_domain_collection(self._domains)

def check_domain_consistency(self) -> List[Any]:
    """Check cross-domain consistency"""
    with self._time_operation('check_domain_consistency'):
        return self._validator.check_consistency(self._domains)

def validate_domain_dependencies(self) -> List[Any]:
    """Validate all domain dependencies"""
    return self._validator.validate_dependencies(self._domains)

def add_consistency_check(self, check) -> None:
    """Add custom consistency check"""
    self._validator.add_consistency_check(check)

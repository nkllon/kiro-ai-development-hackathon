"""
Interfaces Core Core Validation

This module was extracted from interfaces_core_core.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from .models import Domain, DomainCollection, HealthStatus, HealthStatusCollection, DomainMetrics, MetricsCollection, DependencyGraph, QueryResult, ValidationResult, SyncResult, DomainSuggestion, PatternChange, DomainChange, UpdateResult, ComplexityReport, EvolutionReport, ExtractionCandidate, MakeTarget, ExecutionResult

@abstractmethod
def validate_domain(self, domain: Domain) -> ValidationResult:
    """Validate domain structure and requirements"""
    pass

@abstractmethod
def check_domain_health(self, domain_name: str) -> HealthStatus:
    """Check health of a specific domain"""
    pass

@abstractmethod
def check_all_domains(self) -> HealthStatusCollection:
    """Check health of all domains"""
    pass

@abstractmethod
def validate_dependencies(self, domain_name: Optional[str]=None) -> List[str]:
    """Validate domain dependencies"""
    pass

@abstractmethod
def schedule_health_check(self, domain_name: str, interval_minutes: int) -> bool:
    """Schedule periodic health checks"""
    pass

@abstractmethod
def validate_makefile_integration(self) -> ValidationResult:
    """Validate makefile integration completeness"""
    pass

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


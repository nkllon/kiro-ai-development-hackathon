"""
Services Validation

This module was extracted from services.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import ModuleStatus, ModuleCapability, DomainBoundaries, DomainException
from ..core.health import ModuleHealth

def _validate_statelessness(self) -> ValidationResult:
    """
        Validate that the service remains stateless.
        
        Returns:
            ValidationResult: Result of statelessness validation
        """
    result = ValidationResult(is_valid=True)
    if not self._stateless_validation_enabled:
        return result
    current_variables = set(self.__dict__.keys())
    new_variables = current_variables - self._instance_variables_at_init
    problematic_variables = [var for var in new_variables if not var.startswith('_')]
    if problematic_variables:
        result.add_error(f'Domain service has gained state variables: {problematic_variables}', code='DS_001', component=self.__class__.__name__, context={'new_variables': problematic_variables})
    for var_name in self._instance_variables_at_init:
        if not var_name.startswith('_') and hasattr(self, var_name):
            pass
    return result

@abstractmethod
def validate_domain_invariants(self) -> ValidationResult:
    """
        Validate service operates within domain boundaries.
        
        Returns:
            ValidationResult: Result of domain boundary validation
            
        Note:
            This method should validate that the service operates correctly
            within its defined domain boundaries and doesn't violate domain rules.
        """
    pass

def validate_service_constraints(self) -> ValidationResult:
    """
        Validate service-specific constraints.
        
        Returns:
            ValidationResult: Result of service constraint validation
        """
    result = ValidationResult(is_valid=True)
    stateless_result = self._validate_statelessness()
    result.merge(stateless_result)
    if not self.service_name or not self.service_name.strip():
        result.add_error('Domain service must have a valid service name', code='DS_002', component=self.__class__.__name__)
    if not self.domain_context or not self.domain_context.strip():
        result.add_error('Domain service must have a valid domain context', code='DS_003', component=self.__class__.__name__)
    return result

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


"""
Validators Core Validation

This module was extracted from validators_core.py
as part of RM-DDD compliance refactoring.
"""

import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from ..core.compliance import ValidationResult
from ..models import DomainException, ValidationException
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject

def validate(self, target: Any) -> ValidationResult:
    """Execute the validation rule."""
    try:
        return self.validator_func(target)
    except Exception as e:
        result = ValidationResult(is_valid=False)
        result.add_error(f"Validation rule '{self.name}' failed: {str(e)}")
        return result

def validate_entity(self, entity: Entity) -> ValidationResult:
    """Validate a domain entity."""
    result = ValidationResult(is_valid=True)
    for rule in self._rules['entity']:
        rule_result = rule.validate(entity)
        result.merge(rule_result)
    for rule in self._rules['general']:
        rule_result = rule.validate(entity)
        result.merge(rule_result)
    return result

def validate_aggregate(self, aggregate: AggregateRoot) -> ValidationResult:
    """Validate an aggregate root."""
    result = ValidationResult(is_valid=True)
    entity_result = self.validate_entity(aggregate)
    result.merge(entity_result)
    for rule in self._rules['aggregate']:
        rule_result = rule.validate(aggregate)
        result.merge(rule_result)
    return result

def validate_service(self, service: DomainService) -> ValidationResult:
    """Validate a domain service."""
    result = ValidationResult(is_valid=True)
    for rule in self._rules['service']:
        rule_result = rule.validate(service)
        result.merge(rule_result)
    for rule in self._rules['general']:
        rule_result = rule.validate(service)
        result.merge(rule_result)
    return result

def validate_value_object(self, value_object: ValueObject) -> ValidationResult:
    """Validate a value object."""
    result = ValidationResult(is_valid=True)
    for rule in self._rules['value_object']:
        rule_result = rule.validate(value_object)
        result.merge(rule_result)
    for rule in self._rules['general']:
        rule_result = rule.validate(value_object)
        result.merge(rule_result)
    return result

def validate_domain_model(self, model: Any) -> ValidationResult:
    """Validate any domain model by detecting its type."""
    if isinstance(model, AggregateRoot):
        return self.validate_aggregate(model)
    elif isinstance(model, Entity):
        return self.validate_entity(model)
    elif isinstance(model, DomainService):
        return self.validate_service(model)
    elif isinstance(model, ValueObject):
        return self.validate_value_object(model)
    else:
        result = ValidationResult(is_valid=True)
        result.add_warning(f'Unknown domain model type: {type(model)}')
        return result

def _validate_entity_id(self, entity: Entity) -> ValidationResult:
    """Validate entity has a valid ID."""
    result = ValidationResult(is_valid=True)
    if not hasattr(entity, 'id') or entity.id is None:
        result.add_error('Entity must have a non-null ID')
    elif entity.id == '':
        result.add_error('Entity ID cannot be empty string')
    return result

def _validate_entity_context(self, entity: Entity) -> ValidationResult:
    """Validate entity has a domain context."""
    result = ValidationResult(is_valid=True)
    if not hasattr(entity, 'domain_context') or not entity.domain_context:
        result.add_error('Entity must have a domain context')
    return result

def _validate_aggregate_size(self, aggregate: AggregateRoot) -> ValidationResult:
    """Validate aggregate size limits."""
    result = ValidationResult(is_valid=True)
    max_size = getattr(aggregate.__class__, '_max_aggregate_size', 100)
    current_size = self._count_aggregate_members(aggregate)
    if current_size > max_size:
        result.add_warning(f'Aggregate size ({current_size}) exceeds recommended limit ({max_size})')
    return result

def _validate_service_statelessness(self, service: DomainService) -> ValidationResult:
    """Validate service statelessness."""
    result = ValidationResult(is_valid=True)
    instance_vars = [attr for attr in dir(service) if not attr.startswith('_') and (not callable(getattr(service, attr)))]
    if instance_vars:
        result.add_warning(f'Domain service has instance variables that may indicate state: {instance_vars}')
    return result

def _validate_value_object_immutability(self, value_object: ValueObject) -> ValidationResult:
    """Validate value object immutability."""
    result = ValidationResult(is_valid=True)
    is_immutable = getattr(value_object.__class__, '_is_immutable', None)
    if is_immutable is False:
        result.add_warning('Value object is not marked as immutable')
    setter_methods = [method for method in dir(value_object) if method.startswith('set_') and callable(getattr(value_object, method))]
    if setter_methods:
        result.add_warning(f'Value object has setter methods that may violate immutability: {setter_methods}')
    return result

def validate_rules(self, target: Any, rule_names: Optional[List[str]]=None) -> ValidationResult:
    """
        Validate business rules against a target object.
        
        Args:
            target: Object to validate
            rule_names: Specific rules to validate (None for all)
            
        Returns:
            ValidationResult: Validation results
        """
    result = ValidationResult(is_valid=True)
    rules_to_validate = rule_names or list(self._rules.keys())
    sorted_rules = self._sort_rules_by_dependencies(rules_to_validate)
    for rule_name in sorted_rules:
        try:
            rule_func = self._rules[rule_name]
            is_satisfied = rule_func(target)
            if not is_satisfied:
                description = self._rule_descriptions.get(rule_name, 'No description')
                result.add_error(f"Business rule '{rule_name}' violated: {description}")
        except Exception as e:
            result.add_error(f"Error validating rule '{rule_name}': {str(e)}")
    return result

def validate_invariants(self, target: Any, invariant_names: Optional[List[str]]=None) -> ValidationResult:
    """
        Validate domain invariants against a target object.
        
        Args:
            target: Object to validate
            invariant_names: Specific invariants to validate (None for all)
            
        Returns:
            ValidationResult: Validation results
        """
    result = ValidationResult(is_valid=True)
    invariants_to_validate = invariant_names or list(self._invariants.keys())
    for invariant_name in invariants_to_validate:
        try:
            invariant_info = self._invariants[invariant_name]
            expression = invariant_info['expression']
            description = invariant_info['description']
            is_satisfied = self._evaluate_invariant(target, expression, invariant_info['context'])
            if not is_satisfied:
                result.add_error(f"Domain invariant '{invariant_name}' violated: {description}")
        except Exception as e:
            result.add_error(f"Error validating invariant '{invariant_name}': {str(e)}")
    return result

"""
Contexts Core Core Core

This module was extracted from contexts_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, DomainBoundaries, ContextMap, ModuleStatus, ModuleCapability
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth

class ContextRelationshipType(Enum):
    """Types of relationships between bounded contexts."""
    PARTNERSHIP = 'partnership'
    CUSTOMER_SUPPLIER = 'customer_supplier'
    CONFORMIST = 'conformist'
    ANTICORRUPTION_LAYER = 'anticorruption_layer'
    SHARED_KERNEL = 'shared_kernel'
    SEPARATE_WAYS = 'separate_ways'
    OPEN_HOST_SERVICE = 'open_host_service'
    PUBLISHED_LANGUAGE = 'published_language'

class IntegrationPattern(Enum):
    """Integration patterns between bounded contexts."""
    SYNCHRONOUS_API = 'synchronous_api'
    ASYNCHRONOUS_MESSAGING = 'asynchronous_messaging'
    SHARED_DATABASE = 'shared_database'
    DATABASE_PROJECTION = 'database_projection'
    EVENT_STREAMING = 'event_streaming'
    FILE_TRANSFER = 'file_transfer'
    BATCH_PROCESSING = 'batch_processing'

@dataclass
class ContextBoundary:
    """Defines the boundary of a bounded context."""
    context_name: str
    description: str
    core_concepts: List[str] = field(default_factory=list)
    ubiquitous_language: Dict[str, str] = field(default_factory=dict)
    business_capabilities: List[str] = field(default_factory=list)
    data_ownership: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)

    def validate_boundary(self) -> ValidationResult:
        """Validate the context boundary definition."""
        result = ValidationResult(is_valid=True)
        if not self.context_name:
            result.add_error('Context name is required')
        if not self.description:
            result.add_error('Context description is required')
        if not self.core_concepts:
            result.add_warning('No core concepts defined for context')
        if not self.business_capabilities:
            result.add_warning('No business capabilities defined for context')
        return result

@dataclass
class ContextIntegration:
    """Defines integration between two bounded contexts."""
    upstream_context: str
    downstream_context: str
    relationship_type: ContextRelationshipType
    integration_pattern: IntegrationPattern
    data_flow: str = 'bidirectional'
    shared_concepts: List[str] = field(default_factory=list)
    translation_required: bool = True

    def validate_integration(self) -> ValidationResult:
        """Validate the context integration definition."""
        result = ValidationResult(is_valid=True)
        if not self.upstream_context:
            result.add_error('Upstream context is required')
        if not self.downstream_context:
            result.add_error('Downstream context is required')
        if self.upstream_context == self.downstream_context:
            result.add_error('Upstream and downstream contexts cannot be the same')
        if self.relationship_type == ContextRelationshipType.SHARED_KERNEL and self.translation_required:
            result.add_warning("Shared kernel typically doesn't require translation")
        return result

class BoundedContext(DomainReflectiveModule):
    """
    Represents a bounded context with boundary enforcement and management.
    
    A bounded context is a central pattern in DDD that defines the boundaries
    within which a particular domain model is defined and applicable. This class
    provides systematic management of context boundaries, validation, and
    integration patterns.
    """

    def __init__(self, context_name: str, description: str, owner_team: Optional[str]=None):
        super().__init__(context_name)
        self.context_name = context_name
        self.description = description
        self.owner_team = owner_team
        self._boundary = ContextBoundary(context_name, description)
        self._integrations: Dict[str, ContextIntegration] = {}
        self._registered_entities: Set[str] = set()
        self._registered_services: Set[str] = set()
        self._registered_value_objects: Set[str] = set()
        self._boundary_violations: List[str] = []

    def define_boundary(self, boundary: ContextBoundary):
        """
        Define the boundary for this context.
        
        Args:
            boundary: Context boundary definition
            
        Raises:
            DomainException: If boundary is invalid
        """
        validation_result = boundary.validate_boundary()
        if not validation_result.is_valid:
            raise DomainException(f'Invalid context boundary: {validation_result.errors}', error_code='INVALID_CONTEXT_BOUNDARY')
        self._boundary = boundary
        logger.info(f'Defined boundary for context {self.context_name}')

    def add_integration(self, integration: ContextIntegration):
        """
        Add an integration with another context.
        
        Args:
            integration: Context integration definition
            
        Raises:
            DomainException: If integration is invalid
        """
        validation_result = integration.validate_integration()
        if not validation_result.is_valid:
            raise DomainException(f'Invalid context integration: {validation_result.errors}', error_code='INVALID_CONTEXT_INTEGRATION')
        other_context = integration.downstream_context if integration.upstream_context == self.context_name else integration.upstream_context
        self._integrations[other_context] = integration
        logger.info(f'Added integration between {self.context_name} and {other_context}')

    def register_entity(self, entity_name: str):
        """Register an entity as belonging to this context."""
        self._registered_entities.add(entity_name)
        logger.debug(f'Registered entity {entity_name} in context {self.context_name}')

    def register_service(self, service_name: str):
        """Register a service as belonging to this context."""
        self._registered_services.add(service_name)
        logger.debug(f'Registered service {service_name} in context {self.context_name}')

    def register_value_object(self, value_object_name: str):
        """Register a value object as belonging to this context."""
        self._registered_value_objects.add(value_object_name)
        logger.debug(f'Registered value object {value_object_name} in context {self.context_name}')

    def validate_boundary_integrity(self) -> ValidationResult:
        """
        Validate that the context boundary is properly maintained.
        
        Returns:
            ValidationResult: Validation results
        """
        result = ValidationResult(is_valid=True)
        boundary_result = self._boundary.validate_boundary()
        result.merge(boundary_result)
        for other_context, integration in self._integrations.items():
            integration_result = integration.validate_integration()
            if not integration_result.is_valid:
                result.add_error(f'Invalid integration with {other_context}: {integration_result.errors}')
        if self._boundary_violations:
            result.add_error(f'Boundary violations detected: {self._boundary_violations}')
        return result

    def detect_boundary_violation(self, component_name: str, external_dependency: str) -> bool:
        """
        Detect if a component is violating context boundaries.
        
        Args:
            component_name: Name of the component
            external_dependency: External dependency being used
            
        Returns:
            bool: True if violation detected
        """
        for integration in self._integrations.values():
            if external_dependency.startswith(integration.upstream_context) or external_dependency.startswith(integration.downstream_context):
                return False
        if any((infra_pattern in external_dependency.lower() for infra_pattern in ['infrastructure', 'repository', 'adapter', 'client'])):
            return False
        shared_kernel_contexts = [integration.upstream_context for integration in self._integrations.values() if integration.relationship_type == ContextRelationshipType.SHARED_KERNEL]
        if any((external_dependency.startswith(context) for context in shared_kernel_contexts)):
            return False
        violation_msg = f'Component {component_name} depends on {external_dependency} without defined integration'
        self._boundary_violations.append(violation_msg)
        logger.warning(f'Boundary violation detected in {self.context_name}: {violation_msg}')
        return True

    def get_context_map(self) -> Dict[str, ContextMap]:
        """
        Get the context map for this context.
        
        Returns:
            Dict[str, ContextMap]: Context mappings
        """
        context_maps = {}
        for other_context, integration in self._integrations.items():
            context_map = ContextMap(upstream_context=integration.upstream_context, downstream_context=integration.downstream_context, relationship_type=integration.relationship_type.value, integration_pattern=integration.integration_pattern.value, data_flow=integration.data_flow)
            context_maps[other_context] = context_map
        return context_maps

    def get_boundary_info(self) -> Dict[str, Any]:
        """Get information about the context boundary."""
        return {'context_name': self.context_name, 'description': self.description, 'owner_team': self.owner_team, 'core_concepts': self._boundary.core_concepts, 'business_capabilities': self._boundary.business_capabilities, 'registered_entities': list(self._registered_entities), 'registered_services': list(self._registered_services), 'registered_value_objects': list(self._registered_value_objects), 'integrations': list(self._integrations.keys()), 'boundary_violations': len(self._boundary_violations)}

    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        validation_result = self.validate_boundary_integrity()
        status = ModuleStatus.AVAILABLE if validation_result.is_valid else ModuleStatus.DEGRADED
        return ModuleHealth(status=status, message=f'Bounded context: {self.context_name}', capabilities=await self.get_module_capabilities(), health_indicators={'boundary_violations': len(self._boundary_violations), 'integrations_count': len(self._integrations), 'registered_components': len(self._registered_entities) + len(self._registered_services) + len(self._registered_value_objects)})

    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [ModuleCapability(name=f'bounded_context_{self.context_name}', description=f'Bounded context management for {self.context_name}', available=True, version='1.0.0')]

    async def is_healthy(self) -> bool:
        """Check if context is healthy."""
        validation_result = self.validate_boundary_integrity()
        return validation_result.is_valid

    async def get_health_indicators(self):
        """Get health indicators."""
        return {'boundary_info': self.get_boundary_info(), 'context_maps': self.get_context_map(), 'domain_context': self.domain_context}

    def get_domain_boundaries(self):
        """Get domain boundaries."""
        return DomainBoundaries(context=self.context_name, invariants=['Context boundaries must be clearly defined', 'Cross-context dependencies must go through defined integrations', 'Ubiquitous language must be consistent within context'], ubiquitous_language=self._boundary.ubiquitous_language, external_dependencies=self._boundary.external_dependencies)

    def validate_domain_invariants(self):
        """Validate domain invariants."""
        return self.validate_boundary_integrity()

class ContextMapper(DomainReflectiveModule):
    """
    Manages context mapping and relationships between bounded contexts.
    
    Provides systematic tools for creating, managing, and validating
    relationships between bounded contexts, including integration patterns
    and strategic design decisions.
    """

    def __init__(self, domain_context: str='context_mapping'):
        super().__init__(domain_context)
        self._contexts: Dict[str, BoundedContext] = {}
        self._global_integrations: List[ContextIntegration] = []
        self._mapping_violations: List[str] = []

    def register_context(self, context: BoundedContext):
        """
        Register a bounded context.
        
        Args:
            context: Bounded context to register
        """
        self._contexts[context.context_name] = context
        logger.info(f'Registered bounded context: {context.context_name}')

    def create_integration(self, upstream_context: str, downstream_context: str, relationship_type: ContextRelationshipType, integration_pattern: IntegrationPattern, **kwargs) -> ContextIntegration:
        """
        Create an integration between two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            relationship_type: Type of relationship
            integration_pattern: Integration pattern to use
            **kwargs: Additional integration parameters
            
        Returns:
            ContextIntegration: Created integration
            
        Raises:
            DomainException: If contexts don't exist or integration is invalid
        """
        if upstream_context not in self._contexts:
            raise DomainException(f'Upstream context {upstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
        if downstream_context not in self._contexts:
            raise DomainException(f'Downstream context {downstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
        integration = ContextIntegration(upstream_context=upstream_context, downstream_context=downstream_context, relationship_type=relationship_type, integration_pattern=integration_pattern, **kwargs)
        validation_result = integration.validate_integration()
        if not validation_result.is_valid:
            raise DomainException(f'Invalid integration: {validation_result.errors}', error_code='INVALID_INTEGRATION')
        self._contexts[upstream_context].add_integration(integration)
        self._contexts[downstream_context].add_integration(integration)
        self._global_integrations.append(integration)
        logger.info(f'Created integration: {upstream_context} -> {downstream_context} ({relationship_type.value}, {integration_pattern.value})')
        return integration

    def validate_context_map(self) -> ValidationResult:
        """
        Validate the entire context map.
        
        Returns:
            ValidationResult: Validation results for the context map
        """
        result = ValidationResult(is_valid=True)
        for context_name, context in self._contexts.items():
            context_result = context.validate_boundary_integrity()
            if not context_result.is_valid:
                result.add_error(f'Context {context_name} validation failed: {context_result.errors}')
        for integration in self._global_integrations:
            integration_result = integration.validate_integration()
            if not integration_result.is_valid:
                result.add_error(f'Integration validation failed: {integration_result.errors}')
        circular_deps = self._detect_circular_dependencies()
        if circular_deps:
            result.add_warning(f'Circular dependencies detected: {circular_deps}')
        return result

    def _detect_circular_dependencies(self) -> List[str]:
        """Detect circular dependencies in context relationships."""
        circular_deps = []
        for integration in self._global_integrations:
            reverse_integration = next((i for i in self._global_integrations if i.upstream_context == integration.downstream_context and i.downstream_context == integration.upstream_context), None)
            if reverse_integration:
                cycle = f'{integration.upstream_context} <-> {integration.downstream_context}'
                if cycle not in circular_deps:
                    circular_deps.append(cycle)
        return circular_deps

    def get_context_relationships(self, context_name: str) -> List[ContextIntegration]:
        """
        Get all relationships for a specific context.
        
        Args:
            context_name: Name of the context
            
        Returns:
            List[ContextIntegration]: List of integrations involving the context
        """
        return [integration for integration in self._global_integrations if integration.upstream_context == context_name or integration.downstream_context == context_name]

    def generate_context_map_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive context map report.
        
        Returns:
            Dict[str, Any]: Context map report
        """
        return {'contexts': {name: context.get_boundary_info() for name, context in self._contexts.items()}, 'integrations': [{'upstream': integration.upstream_context, 'downstream': integration.downstream_context, 'relationship': integration.relationship_type.value, 'pattern': integration.integration_pattern.value, 'data_flow': integration.data_flow} for integration in self._global_integrations], 'validation_summary': self.validate_context_map().to_dict() if hasattr(ValidationResult, 'to_dict') else {}, 'circular_dependencies': self._detect_circular_dependencies(), 'total_contexts': len(self._contexts), 'total_integrations': len(self._global_integrations)}

    def suggest_integration_patterns(self, upstream_context: str, downstream_context: str) -> List[Dict[str, Any]]:
        """
        Suggest appropriate integration patterns for two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            
        Returns:
            List[Dict[str, Any]]: Suggested integration patterns with rationale
        """
        suggestions = []
        upstream = self._contexts.get(upstream_context)
        downstream = self._contexts.get(downstream_context)
        if not upstream or not downstream:
            return suggestions
        upstream_concepts = set(upstream._boundary.core_concepts)
        downstream_concepts = set(downstream._boundary.core_concepts)
        shared_concepts = upstream_concepts.intersection(downstream_concepts)
        if shared_concepts:
            suggestions.append({'relationship': ContextRelationshipType.SHARED_KERNEL, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Shared concepts detected: {list(shared_concepts)}', 'confidence': 0.8})
        suggestions.append({'relationship': ContextRelationshipType.ANTICORRUPTION_LAYER, 'pattern': IntegrationPattern.ASYNCHRONOUS_MESSAGING, 'rationale': 'Safe default for maintaining context independence', 'confidence': 0.6})
        upstream_size = len(upstream._registered_entities) + len(upstream._registered_services)
        downstream_size = len(downstream._registered_entities) + len(downstream._registered_services)
        if upstream_size > downstream_size * 2:
            suggestions.append({'relationship': ContextRelationshipType.CUSTOMER_SUPPLIER, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Upstream context is significantly larger ({upstream_size} vs {downstream_size} components)', 'confidence': 0.7})
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)

    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        validation_result = self.validate_context_map()
        status = ModuleStatus.AVAILABLE if validation_result.is_valid else ModuleStatus.DEGRADED
        return ModuleHealth(status=status, message=f'Context mapper managing {len(self._contexts)} contexts', capabilities=await self.get_module_capabilities(), health_indicators={'contexts_count': len(self._contexts), 'integrations_count': len(self._global_integrations), 'mapping_violations': len(self._mapping_violations)})

    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [ModuleCapability(name='context_mapping', description='Manages bounded context relationships and mappings', available=True, version='1.0.0')]

    async def is_healthy(self) -> bool:
        """Check if context mapper is healthy."""
        validation_result = self.validate_context_map()
        return validation_result.is_valid

    async def get_health_indicators(self):
        """Get health indicators."""
        return {'context_map_report': self.generate_context_map_report(), 'domain_context': self.domain_context}

    def get_domain_boundaries(self):
        """Get domain boundaries."""
        return DomainBoundaries(context=self.domain_context, invariants=['All contexts must be properly registered', 'Integrations must be bidirectionally consistent', 'Circular dependencies should be minimized'])

    def validate_domain_invariants(self):
        """Validate domain invariants."""
        return self.validate_context_map()

def __init__(self, context_name: str, description: str, owner_team: Optional[str]=None):
    super().__init__(context_name)
    self.context_name = context_name
    self.description = description
    self.owner_team = owner_team
    self._boundary = ContextBoundary(context_name, description)
    self._integrations: Dict[str, ContextIntegration] = {}
    self._registered_entities: Set[str] = set()
    self._registered_services: Set[str] = set()
    self._registered_value_objects: Set[str] = set()
    self._boundary_violations: List[str] = []

def define_boundary(self, boundary: ContextBoundary):
    """
        Define the boundary for this context.
        
        Args:
            boundary: Context boundary definition
            
        Raises:
            DomainException: If boundary is invalid
        """
    validation_result = boundary.validate_boundary()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid context boundary: {validation_result.errors}', error_code='INVALID_CONTEXT_BOUNDARY')
    self._boundary = boundary
    logger.info(f'Defined boundary for context {self.context_name}')

def add_integration(self, integration: ContextIntegration):
    """
        Add an integration with another context.
        
        Args:
            integration: Context integration definition
            
        Raises:
            DomainException: If integration is invalid
        """
    validation_result = integration.validate_integration()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid context integration: {validation_result.errors}', error_code='INVALID_CONTEXT_INTEGRATION')
    other_context = integration.downstream_context if integration.upstream_context == self.context_name else integration.upstream_context
    self._integrations[other_context] = integration
    logger.info(f'Added integration between {self.context_name} and {other_context}')

def register_entity(self, entity_name: str):
    """Register an entity as belonging to this context."""
    self._registered_entities.add(entity_name)
    logger.debug(f'Registered entity {entity_name} in context {self.context_name}')

def register_service(self, service_name: str):
    """Register a service as belonging to this context."""
    self._registered_services.add(service_name)
    logger.debug(f'Registered service {service_name} in context {self.context_name}')

def register_value_object(self, value_object_name: str):
    """Register a value object as belonging to this context."""
    self._registered_value_objects.add(value_object_name)
    logger.debug(f'Registered value object {value_object_name} in context {self.context_name}')

def detect_boundary_violation(self, component_name: str, external_dependency: str) -> bool:
    """
        Detect if a component is violating context boundaries.
        
        Args:
            component_name: Name of the component
            external_dependency: External dependency being used
            
        Returns:
            bool: True if violation detected
        """
    for integration in self._integrations.values():
        if external_dependency.startswith(integration.upstream_context) or external_dependency.startswith(integration.downstream_context):
            return False
    if any((infra_pattern in external_dependency.lower() for infra_pattern in ['infrastructure', 'repository', 'adapter', 'client'])):
        return False
    shared_kernel_contexts = [integration.upstream_context for integration in self._integrations.values() if integration.relationship_type == ContextRelationshipType.SHARED_KERNEL]
    if any((external_dependency.startswith(context) for context in shared_kernel_contexts)):
        return False
    violation_msg = f'Component {component_name} depends on {external_dependency} without defined integration'
    self._boundary_violations.append(violation_msg)
    logger.warning(f'Boundary violation detected in {self.context_name}: {violation_msg}')
    return True

def get_context_map(self) -> Dict[str, ContextMap]:
    """
        Get the context map for this context.
        
        Returns:
            Dict[str, ContextMap]: Context mappings
        """
    context_maps = {}
    for other_context, integration in self._integrations.items():
        context_map = ContextMap(upstream_context=integration.upstream_context, downstream_context=integration.downstream_context, relationship_type=integration.relationship_type.value, integration_pattern=integration.integration_pattern.value, data_flow=integration.data_flow)
        context_maps[other_context] = context_map
    return context_maps

def get_boundary_info(self) -> Dict[str, Any]:
    """Get information about the context boundary."""
    return {'context_name': self.context_name, 'description': self.description, 'owner_team': self.owner_team, 'core_concepts': self._boundary.core_concepts, 'business_capabilities': self._boundary.business_capabilities, 'registered_entities': list(self._registered_entities), 'registered_services': list(self._registered_services), 'registered_value_objects': list(self._registered_value_objects), 'integrations': list(self._integrations.keys()), 'boundary_violations': len(self._boundary_violations)}

def get_domain_boundaries(self):
    """Get domain boundaries."""
    return DomainBoundaries(context=self.context_name, invariants=['Context boundaries must be clearly defined', 'Cross-context dependencies must go through defined integrations', 'Ubiquitous language must be consistent within context'], ubiquitous_language=self._boundary.ubiquitous_language, external_dependencies=self._boundary.external_dependencies)

def __init__(self, domain_context: str='context_mapping'):
    super().__init__(domain_context)
    self._contexts: Dict[str, BoundedContext] = {}
    self._global_integrations: List[ContextIntegration] = []
    self._mapping_violations: List[str] = []

def register_context(self, context: BoundedContext):
    """
        Register a bounded context.
        
        Args:
            context: Bounded context to register
        """
    self._contexts[context.context_name] = context
    logger.info(f'Registered bounded context: {context.context_name}')

def create_integration(self, upstream_context: str, downstream_context: str, relationship_type: ContextRelationshipType, integration_pattern: IntegrationPattern, **kwargs) -> ContextIntegration:
    """
        Create an integration between two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            relationship_type: Type of relationship
            integration_pattern: Integration pattern to use
            **kwargs: Additional integration parameters
            
        Returns:
            ContextIntegration: Created integration
            
        Raises:
            DomainException: If contexts don't exist or integration is invalid
        """
    if upstream_context not in self._contexts:
        raise DomainException(f'Upstream context {upstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
    if downstream_context not in self._contexts:
        raise DomainException(f'Downstream context {downstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
    integration = ContextIntegration(upstream_context=upstream_context, downstream_context=downstream_context, relationship_type=relationship_type, integration_pattern=integration_pattern, **kwargs)
    validation_result = integration.validate_integration()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid integration: {validation_result.errors}', error_code='INVALID_INTEGRATION')
    self._contexts[upstream_context].add_integration(integration)
    self._contexts[downstream_context].add_integration(integration)
    self._global_integrations.append(integration)
    logger.info(f'Created integration: {upstream_context} -> {downstream_context} ({relationship_type.value}, {integration_pattern.value})')
    return integration

def _detect_circular_dependencies(self) -> List[str]:
    """Detect circular dependencies in context relationships."""
    circular_deps = []
    for integration in self._global_integrations:
        reverse_integration = next((i for i in self._global_integrations if i.upstream_context == integration.downstream_context and i.downstream_context == integration.upstream_context), None)
        if reverse_integration:
            cycle = f'{integration.upstream_context} <-> {integration.downstream_context}'
            if cycle not in circular_deps:
                circular_deps.append(cycle)
    return circular_deps

def get_context_relationships(self, context_name: str) -> List[ContextIntegration]:
    """
        Get all relationships for a specific context.
        
        Args:
            context_name: Name of the context
            
        Returns:
            List[ContextIntegration]: List of integrations involving the context
        """
    return [integration for integration in self._global_integrations if integration.upstream_context == context_name or integration.downstream_context == context_name]

def generate_context_map_report(self) -> Dict[str, Any]:
    """
        Generate a comprehensive context map report.
        
        Returns:
            Dict[str, Any]: Context map report
        """
    return {'contexts': {name: context.get_boundary_info() for name, context in self._contexts.items()}, 'integrations': [{'upstream': integration.upstream_context, 'downstream': integration.downstream_context, 'relationship': integration.relationship_type.value, 'pattern': integration.integration_pattern.value, 'data_flow': integration.data_flow} for integration in self._global_integrations], 'validation_summary': self.validate_context_map().to_dict() if hasattr(ValidationResult, 'to_dict') else {}, 'circular_dependencies': self._detect_circular_dependencies(), 'total_contexts': len(self._contexts), 'total_integrations': len(self._global_integrations)}

def suggest_integration_patterns(self, upstream_context: str, downstream_context: str) -> List[Dict[str, Any]]:
    """
        Suggest appropriate integration patterns for two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            
        Returns:
            List[Dict[str, Any]]: Suggested integration patterns with rationale
        """
    suggestions = []
    upstream = self._contexts.get(upstream_context)
    downstream = self._contexts.get(downstream_context)
    if not upstream or not downstream:
        return suggestions
    upstream_concepts = set(upstream._boundary.core_concepts)
    downstream_concepts = set(downstream._boundary.core_concepts)
    shared_concepts = upstream_concepts.intersection(downstream_concepts)
    if shared_concepts:
        suggestions.append({'relationship': ContextRelationshipType.SHARED_KERNEL, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Shared concepts detected: {list(shared_concepts)}', 'confidence': 0.8})
    suggestions.append({'relationship': ContextRelationshipType.ANTICORRUPTION_LAYER, 'pattern': IntegrationPattern.ASYNCHRONOUS_MESSAGING, 'rationale': 'Safe default for maintaining context independence', 'confidence': 0.6})
    upstream_size = len(upstream._registered_entities) + len(upstream._registered_services)
    downstream_size = len(downstream._registered_entities) + len(downstream._registered_services)
    if upstream_size > downstream_size * 2:
        suggestions.append({'relationship': ContextRelationshipType.CUSTOMER_SUPPLIER, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Upstream context is significantly larger ({upstream_size} vs {downstream_size} components)', 'confidence': 0.7})
    return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)

def get_domain_boundaries(self):
    """Get domain boundaries."""
    return DomainBoundaries(context=self.domain_context, invariants=['All contexts must be properly registered', 'Integrations must be bidirectionally consistent', 'Circular dependencies should be minimized'])

def __init__(self, context_name: str, description: str, owner_team: Optional[str]=None):
    super().__init__(context_name)
    self.context_name = context_name
    self.description = description
    self.owner_team = owner_team
    self._boundary = ContextBoundary(context_name, description)
    self._integrations: Dict[str, ContextIntegration] = {}
    self._registered_entities: Set[str] = set()
    self._registered_services: Set[str] = set()
    self._registered_value_objects: Set[str] = set()
    self._boundary_violations: List[str] = []

def define_boundary(self, boundary: ContextBoundary):
    """
        Define the boundary for this context.
        
        Args:
            boundary: Context boundary definition
            
        Raises:
            DomainException: If boundary is invalid
        """
    validation_result = boundary.validate_boundary()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid context boundary: {validation_result.errors}', error_code='INVALID_CONTEXT_BOUNDARY')
    self._boundary = boundary
    logger.info(f'Defined boundary for context {self.context_name}')

def add_integration(self, integration: ContextIntegration):
    """
        Add an integration with another context.
        
        Args:
            integration: Context integration definition
            
        Raises:
            DomainException: If integration is invalid
        """
    validation_result = integration.validate_integration()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid context integration: {validation_result.errors}', error_code='INVALID_CONTEXT_INTEGRATION')
    other_context = integration.downstream_context if integration.upstream_context == self.context_name else integration.upstream_context
    self._integrations[other_context] = integration
    logger.info(f'Added integration between {self.context_name} and {other_context}')

def register_entity(self, entity_name: str):
    """Register an entity as belonging to this context."""
    self._registered_entities.add(entity_name)
    logger.debug(f'Registered entity {entity_name} in context {self.context_name}')

def register_service(self, service_name: str):
    """Register a service as belonging to this context."""
    self._registered_services.add(service_name)
    logger.debug(f'Registered service {service_name} in context {self.context_name}')

def register_value_object(self, value_object_name: str):
    """Register a value object as belonging to this context."""
    self._registered_value_objects.add(value_object_name)
    logger.debug(f'Registered value object {value_object_name} in context {self.context_name}')

def detect_boundary_violation(self, component_name: str, external_dependency: str) -> bool:
    """
        Detect if a component is violating context boundaries.
        
        Args:
            component_name: Name of the component
            external_dependency: External dependency being used
            
        Returns:
            bool: True if violation detected
        """
    for integration in self._integrations.values():
        if external_dependency.startswith(integration.upstream_context) or external_dependency.startswith(integration.downstream_context):
            return False
    if any((infra_pattern in external_dependency.lower() for infra_pattern in ['infrastructure', 'repository', 'adapter', 'client'])):
        return False
    shared_kernel_contexts = [integration.upstream_context for integration in self._integrations.values() if integration.relationship_type == ContextRelationshipType.SHARED_KERNEL]
    if any((external_dependency.startswith(context) for context in shared_kernel_contexts)):
        return False
    violation_msg = f'Component {component_name} depends on {external_dependency} without defined integration'
    self._boundary_violations.append(violation_msg)
    logger.warning(f'Boundary violation detected in {self.context_name}: {violation_msg}')
    return True

def get_context_map(self) -> Dict[str, ContextMap]:
    """
        Get the context map for this context.
        
        Returns:
            Dict[str, ContextMap]: Context mappings
        """
    context_maps = {}
    for other_context, integration in self._integrations.items():
        context_map = ContextMap(upstream_context=integration.upstream_context, downstream_context=integration.downstream_context, relationship_type=integration.relationship_type.value, integration_pattern=integration.integration_pattern.value, data_flow=integration.data_flow)
        context_maps[other_context] = context_map
    return context_maps

def get_boundary_info(self) -> Dict[str, Any]:
    """Get information about the context boundary."""
    return {'context_name': self.context_name, 'description': self.description, 'owner_team': self.owner_team, 'core_concepts': self._boundary.core_concepts, 'business_capabilities': self._boundary.business_capabilities, 'registered_entities': list(self._registered_entities), 'registered_services': list(self._registered_services), 'registered_value_objects': list(self._registered_value_objects), 'integrations': list(self._integrations.keys()), 'boundary_violations': len(self._boundary_violations)}

def get_domain_boundaries(self):
    """Get domain boundaries."""
    return DomainBoundaries(context=self.context_name, invariants=['Context boundaries must be clearly defined', 'Cross-context dependencies must go through defined integrations', 'Ubiquitous language must be consistent within context'], ubiquitous_language=self._boundary.ubiquitous_language, external_dependencies=self._boundary.external_dependencies)

def __init__(self, domain_context: str='context_mapping'):
    super().__init__(domain_context)
    self._contexts: Dict[str, BoundedContext] = {}
    self._global_integrations: List[ContextIntegration] = []
    self._mapping_violations: List[str] = []

def register_context(self, context: BoundedContext):
    """
        Register a bounded context.
        
        Args:
            context: Bounded context to register
        """
    self._contexts[context.context_name] = context
    logger.info(f'Registered bounded context: {context.context_name}')

def create_integration(self, upstream_context: str, downstream_context: str, relationship_type: ContextRelationshipType, integration_pattern: IntegrationPattern, **kwargs) -> ContextIntegration:
    """
        Create an integration between two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            relationship_type: Type of relationship
            integration_pattern: Integration pattern to use
            **kwargs: Additional integration parameters
            
        Returns:
            ContextIntegration: Created integration
            
        Raises:
            DomainException: If contexts don't exist or integration is invalid
        """
    if upstream_context not in self._contexts:
        raise DomainException(f'Upstream context {upstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
    if downstream_context not in self._contexts:
        raise DomainException(f'Downstream context {downstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
    integration = ContextIntegration(upstream_context=upstream_context, downstream_context=downstream_context, relationship_type=relationship_type, integration_pattern=integration_pattern, **kwargs)
    validation_result = integration.validate_integration()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid integration: {validation_result.errors}', error_code='INVALID_INTEGRATION')
    self._contexts[upstream_context].add_integration(integration)
    self._contexts[downstream_context].add_integration(integration)
    self._global_integrations.append(integration)
    logger.info(f'Created integration: {upstream_context} -> {downstream_context} ({relationship_type.value}, {integration_pattern.value})')
    return integration

def _detect_circular_dependencies(self) -> List[str]:
    """Detect circular dependencies in context relationships."""
    circular_deps = []
    for integration in self._global_integrations:
        reverse_integration = next((i for i in self._global_integrations if i.upstream_context == integration.downstream_context and i.downstream_context == integration.upstream_context), None)
        if reverse_integration:
            cycle = f'{integration.upstream_context} <-> {integration.downstream_context}'
            if cycle not in circular_deps:
                circular_deps.append(cycle)
    return circular_deps

def get_context_relationships(self, context_name: str) -> List[ContextIntegration]:
    """
        Get all relationships for a specific context.
        
        Args:
            context_name: Name of the context
            
        Returns:
            List[ContextIntegration]: List of integrations involving the context
        """
    return [integration for integration in self._global_integrations if integration.upstream_context == context_name or integration.downstream_context == context_name]

def generate_context_map_report(self) -> Dict[str, Any]:
    """
        Generate a comprehensive context map report.
        
        Returns:
            Dict[str, Any]: Context map report
        """
    return {'contexts': {name: context.get_boundary_info() for name, context in self._contexts.items()}, 'integrations': [{'upstream': integration.upstream_context, 'downstream': integration.downstream_context, 'relationship': integration.relationship_type.value, 'pattern': integration.integration_pattern.value, 'data_flow': integration.data_flow} for integration in self._global_integrations], 'validation_summary': self.validate_context_map().to_dict() if hasattr(ValidationResult, 'to_dict') else {}, 'circular_dependencies': self._detect_circular_dependencies(), 'total_contexts': len(self._contexts), 'total_integrations': len(self._global_integrations)}

def suggest_integration_patterns(self, upstream_context: str, downstream_context: str) -> List[Dict[str, Any]]:
    """
        Suggest appropriate integration patterns for two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            
        Returns:
            List[Dict[str, Any]]: Suggested integration patterns with rationale
        """
    suggestions = []
    upstream = self._contexts.get(upstream_context)
    downstream = self._contexts.get(downstream_context)
    if not upstream or not downstream:
        return suggestions
    upstream_concepts = set(upstream._boundary.core_concepts)
    downstream_concepts = set(downstream._boundary.core_concepts)
    shared_concepts = upstream_concepts.intersection(downstream_concepts)
    if shared_concepts:
        suggestions.append({'relationship': ContextRelationshipType.SHARED_KERNEL, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Shared concepts detected: {list(shared_concepts)}', 'confidence': 0.8})
    suggestions.append({'relationship': ContextRelationshipType.ANTICORRUPTION_LAYER, 'pattern': IntegrationPattern.ASYNCHRONOUS_MESSAGING, 'rationale': 'Safe default for maintaining context independence', 'confidence': 0.6})
    upstream_size = len(upstream._registered_entities) + len(upstream._registered_services)
    downstream_size = len(downstream._registered_entities) + len(downstream._registered_services)
    if upstream_size > downstream_size * 2:
        suggestions.append({'relationship': ContextRelationshipType.CUSTOMER_SUPPLIER, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Upstream context is significantly larger ({upstream_size} vs {downstream_size} components)', 'confidence': 0.7})
    return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)

def get_domain_boundaries(self):
    """Get domain boundaries."""
    return DomainBoundaries(context=self.domain_context, invariants=['All contexts must be properly registered', 'Integrations must be bidirectionally consistent', 'Circular dependencies should be minimized'])

def __init__(self, context_name: str, description: str, owner_team: Optional[str]=None):
    super().__init__(context_name)
    self.context_name = context_name
    self.description = description
    self.owner_team = owner_team
    self._boundary = ContextBoundary(context_name, description)
    self._integrations: Dict[str, ContextIntegration] = {}
    self._registered_entities: Set[str] = set()
    self._registered_services: Set[str] = set()
    self._registered_value_objects: Set[str] = set()
    self._boundary_violations: List[str] = []

def define_boundary(self, boundary: ContextBoundary):
    """
        Define the boundary for this context.
        
        Args:
            boundary: Context boundary definition
            
        Raises:
            DomainException: If boundary is invalid
        """
    validation_result = boundary.validate_boundary()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid context boundary: {validation_result.errors}', error_code='INVALID_CONTEXT_BOUNDARY')
    self._boundary = boundary
    logger.info(f'Defined boundary for context {self.context_name}')

def add_integration(self, integration: ContextIntegration):
    """
        Add an integration with another context.
        
        Args:
            integration: Context integration definition
            
        Raises:
            DomainException: If integration is invalid
        """
    validation_result = integration.validate_integration()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid context integration: {validation_result.errors}', error_code='INVALID_CONTEXT_INTEGRATION')
    other_context = integration.downstream_context if integration.upstream_context == self.context_name else integration.upstream_context
    self._integrations[other_context] = integration
    logger.info(f'Added integration between {self.context_name} and {other_context}')

def register_entity(self, entity_name: str):
    """Register an entity as belonging to this context."""
    self._registered_entities.add(entity_name)
    logger.debug(f'Registered entity {entity_name} in context {self.context_name}')

def register_service(self, service_name: str):
    """Register a service as belonging to this context."""
    self._registered_services.add(service_name)
    logger.debug(f'Registered service {service_name} in context {self.context_name}')

def register_value_object(self, value_object_name: str):
    """Register a value object as belonging to this context."""
    self._registered_value_objects.add(value_object_name)
    logger.debug(f'Registered value object {value_object_name} in context {self.context_name}')

def detect_boundary_violation(self, component_name: str, external_dependency: str) -> bool:
    """
        Detect if a component is violating context boundaries.
        
        Args:
            component_name: Name of the component
            external_dependency: External dependency being used
            
        Returns:
            bool: True if violation detected
        """
    for integration in self._integrations.values():
        if external_dependency.startswith(integration.upstream_context) or external_dependency.startswith(integration.downstream_context):
            return False
    if any((infra_pattern in external_dependency.lower() for infra_pattern in ['infrastructure', 'repository', 'adapter', 'client'])):
        return False
    shared_kernel_contexts = [integration.upstream_context for integration in self._integrations.values() if integration.relationship_type == ContextRelationshipType.SHARED_KERNEL]
    if any((external_dependency.startswith(context) for context in shared_kernel_contexts)):
        return False
    violation_msg = f'Component {component_name} depends on {external_dependency} without defined integration'
    self._boundary_violations.append(violation_msg)
    logger.warning(f'Boundary violation detected in {self.context_name}: {violation_msg}')
    return True

def get_context_map(self) -> Dict[str, ContextMap]:
    """
        Get the context map for this context.
        
        Returns:
            Dict[str, ContextMap]: Context mappings
        """
    context_maps = {}
    for other_context, integration in self._integrations.items():
        context_map = ContextMap(upstream_context=integration.upstream_context, downstream_context=integration.downstream_context, relationship_type=integration.relationship_type.value, integration_pattern=integration.integration_pattern.value, data_flow=integration.data_flow)
        context_maps[other_context] = context_map
    return context_maps

def get_boundary_info(self) -> Dict[str, Any]:
    """Get information about the context boundary."""
    return {'context_name': self.context_name, 'description': self.description, 'owner_team': self.owner_team, 'core_concepts': self._boundary.core_concepts, 'business_capabilities': self._boundary.business_capabilities, 'registered_entities': list(self._registered_entities), 'registered_services': list(self._registered_services), 'registered_value_objects': list(self._registered_value_objects), 'integrations': list(self._integrations.keys()), 'boundary_violations': len(self._boundary_violations)}

def get_domain_boundaries(self):
    """Get domain boundaries."""
    return DomainBoundaries(context=self.context_name, invariants=['Context boundaries must be clearly defined', 'Cross-context dependencies must go through defined integrations', 'Ubiquitous language must be consistent within context'], ubiquitous_language=self._boundary.ubiquitous_language, external_dependencies=self._boundary.external_dependencies)

def __init__(self, domain_context: str='context_mapping'):
    super().__init__(domain_context)
    self._contexts: Dict[str, BoundedContext] = {}
    self._global_integrations: List[ContextIntegration] = []
    self._mapping_violations: List[str] = []

def register_context(self, context: BoundedContext):
    """
        Register a bounded context.
        
        Args:
            context: Bounded context to register
        """
    self._contexts[context.context_name] = context
    logger.info(f'Registered bounded context: {context.context_name}')

def create_integration(self, upstream_context: str, downstream_context: str, relationship_type: ContextRelationshipType, integration_pattern: IntegrationPattern, **kwargs) -> ContextIntegration:
    """
        Create an integration between two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            relationship_type: Type of relationship
            integration_pattern: Integration pattern to use
            **kwargs: Additional integration parameters
            
        Returns:
            ContextIntegration: Created integration
            
        Raises:
            DomainException: If contexts don't exist or integration is invalid
        """
    if upstream_context not in self._contexts:
        raise DomainException(f'Upstream context {upstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
    if downstream_context not in self._contexts:
        raise DomainException(f'Downstream context {downstream_context} not registered', error_code='CONTEXT_NOT_FOUND')
    integration = ContextIntegration(upstream_context=upstream_context, downstream_context=downstream_context, relationship_type=relationship_type, integration_pattern=integration_pattern, **kwargs)
    validation_result = integration.validate_integration()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid integration: {validation_result.errors}', error_code='INVALID_INTEGRATION')
    self._contexts[upstream_context].add_integration(integration)
    self._contexts[downstream_context].add_integration(integration)
    self._global_integrations.append(integration)
    logger.info(f'Created integration: {upstream_context} -> {downstream_context} ({relationship_type.value}, {integration_pattern.value})')
    return integration

def _detect_circular_dependencies(self) -> List[str]:
    """Detect circular dependencies in context relationships."""
    circular_deps = []
    for integration in self._global_integrations:
        reverse_integration = next((i for i in self._global_integrations if i.upstream_context == integration.downstream_context and i.downstream_context == integration.upstream_context), None)
        if reverse_integration:
            cycle = f'{integration.upstream_context} <-> {integration.downstream_context}'
            if cycle not in circular_deps:
                circular_deps.append(cycle)
    return circular_deps

def get_context_relationships(self, context_name: str) -> List[ContextIntegration]:
    """
        Get all relationships for a specific context.
        
        Args:
            context_name: Name of the context
            
        Returns:
            List[ContextIntegration]: List of integrations involving the context
        """
    return [integration for integration in self._global_integrations if integration.upstream_context == context_name or integration.downstream_context == context_name]

def generate_context_map_report(self) -> Dict[str, Any]:
    """
        Generate a comprehensive context map report.
        
        Returns:
            Dict[str, Any]: Context map report
        """
    return {'contexts': {name: context.get_boundary_info() for name, context in self._contexts.items()}, 'integrations': [{'upstream': integration.upstream_context, 'downstream': integration.downstream_context, 'relationship': integration.relationship_type.value, 'pattern': integration.integration_pattern.value, 'data_flow': integration.data_flow} for integration in self._global_integrations], 'validation_summary': self.validate_context_map().to_dict() if hasattr(ValidationResult, 'to_dict') else {}, 'circular_dependencies': self._detect_circular_dependencies(), 'total_contexts': len(self._contexts), 'total_integrations': len(self._global_integrations)}

def suggest_integration_patterns(self, upstream_context: str, downstream_context: str) -> List[Dict[str, Any]]:
    """
        Suggest appropriate integration patterns for two contexts.
        
        Args:
            upstream_context: Name of upstream context
            downstream_context: Name of downstream context
            
        Returns:
            List[Dict[str, Any]]: Suggested integration patterns with rationale
        """
    suggestions = []
    upstream = self._contexts.get(upstream_context)
    downstream = self._contexts.get(downstream_context)
    if not upstream or not downstream:
        return suggestions
    upstream_concepts = set(upstream._boundary.core_concepts)
    downstream_concepts = set(downstream._boundary.core_concepts)
    shared_concepts = upstream_concepts.intersection(downstream_concepts)
    if shared_concepts:
        suggestions.append({'relationship': ContextRelationshipType.SHARED_KERNEL, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Shared concepts detected: {list(shared_concepts)}', 'confidence': 0.8})
    suggestions.append({'relationship': ContextRelationshipType.ANTICORRUPTION_LAYER, 'pattern': IntegrationPattern.ASYNCHRONOUS_MESSAGING, 'rationale': 'Safe default for maintaining context independence', 'confidence': 0.6})
    upstream_size = len(upstream._registered_entities) + len(upstream._registered_services)
    downstream_size = len(downstream._registered_entities) + len(downstream._registered_services)
    if upstream_size > downstream_size * 2:
        suggestions.append({'relationship': ContextRelationshipType.CUSTOMER_SUPPLIER, 'pattern': IntegrationPattern.SYNCHRONOUS_API, 'rationale': f'Upstream context is significantly larger ({upstream_size} vs {downstream_size} components)', 'confidence': 0.7})
    return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)

def get_domain_boundaries(self):
    """Get domain boundaries."""
    return DomainBoundaries(context=self.domain_context, invariants=['All contexts must be properly registered', 'Integrations must be bidirectionally consistent', 'Circular dependencies should be minimized'])

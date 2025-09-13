"""
Entities Models

This module was extracted from entities.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID, uuid4
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import ModuleStatus, ModuleCapability, DomainBoundaries, AggregateBoundaries, EntityId, AggregateId, DomainException, InvariantViolationException
from ..core.health import ModuleHealth

class Entity(DomainReflectiveModule, Generic[TEntityId], ABC):
    """
    Base class for domain entities.
    
    Provides systematic implementation of DDD entity patterns with built-in
    RM compliance, identity management, equality semantics, and domain validation.
    
    Key Responsibilities:
    - Identity management and equality semantics
    - Domain boundary definition and enforcement
    - Domain invariant validation
    - Version tracking for optimistic locking
    - Integration with RM health monitoring
    
    Accountability Chain:
    - Domain Expert: Responsible for business rules and invariants
    - Entity Owner: Responsible for entity-specific logic
    - RM Framework: Responsible for systematic compliance
    """

    def __init__(self, entity_id: TEntityId, domain_context: str, module_id: Optional[str]=None):
        """
        Initialize domain entity with systematic compliance.
        
        Args:
            entity_id: Unique identifier for this entity
            domain_context: The bounded context this entity belongs to
            module_id: Optional RM module identifier
        """
        self.id = entity_id
        self._version = 1
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._domain_events: List['DomainEvent'] = []
        super().__init__(domain_context, module_id)
        logger.debug(f'Entity created: {self.__class__.__name__}({entity_id}) in context: {domain_context}')

    def __eq__(self, other: Any) -> bool:
        """
        Entity equality based on identity and type.
        
        Two entities are equal if they have the same ID and are of the same type.
        This implements the DDD principle that entities are defined by their identity.
        """
        if not isinstance(other, Entity):
            return False
        return self.id == other.id and type(self) == type(other)

    def __hash__(self) -> int:
        """
        Hash based on entity type and ID.
        
        Allows entities to be used in sets and as dictionary keys while
        maintaining identity-based equality semantics.
        """
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        """String representation of entity."""
        return f'{self.__class__.__name__}(id={self.id}, version={self._version})'

    @abstractmethod
    def get_domain_boundaries(self) -> DomainBoundaries:
        """
        Define entity domain boundaries.
        
        Returns:
            DomainBoundaries: Definition of domain boundaries, invariants,
                            and integration patterns for this entity
                            
        Note:
            This method must be implemented by all entities to define
            their domain boundaries and business rules.
        """
        pass

    @abstractmethod
    def validate_domain_invariants(self) -> ValidationResult:
        """
        Validate entity domain invariants.
        
        Returns:
            ValidationResult: Result of domain invariant validation
            
        Note:
            This method should validate all business rules and invariants
            that must be maintained for this entity.
        """
        pass

    def add_domain_event(self, event: 'DomainEvent'):
        """
        Add domain event to be published.
        
        Args:
            event: Domain event to add to the event list
            
        Note:
            Events are collected and published when the entity is saved
            or when explicitly requested.
        """
        self._domain_events.append(event)
        logger.debug(f'Domain event added to {self.__class__.__name__}({self.id}): {event.__class__.__name__}')

    def get_domain_events(self) -> List['DomainEvent']:
        """Get pending domain events."""
        return self._domain_events.copy()

    def clear_domain_events(self):
        """Clear domain events after publishing."""
        event_count = len(self._domain_events)
        self._domain_events.clear()
        if event_count > 0:
            logger.debug(f'Cleared {event_count} domain events from {self.__class__.__name__}({self.id})')

    def update_version(self):
        """
        Update entity version for optimistic locking.
        
        Should be called whenever the entity is modified to support
        optimistic concurrency control.
        """
        self._version += 1
        self._updated_at = datetime.now()
        logger.debug(f'Entity version updated: {self.__class__.__name__}({self.id}) -> v{self._version}')

    def get_entity_info(self) -> Dict[str, Any]:
        """Get comprehensive entity information."""
        return {'entity_id': str(self.id), 'entity_type': self.__class__.__name__, 'domain_context': self.domain_context, 'version': self._version, 'created_at': self._created_at.isoformat(), 'updated_at': self._updated_at.isoformat(), 'pending_events': len(self._domain_events), 'module_id': self.module_id}

    async def get_module_status(self) -> 'ModuleHealth':
        """Get entity health status."""
        from ..core.health import ModuleHealth
        validation_result = self.validate_domain_invariants()
        status = ModuleStatus.AVAILABLE if validation_result.is_valid else ModuleStatus.DEGRADED
        message = f'Entity {self.__class__.__name__}({self.id})'
        if not validation_result.is_valid:
            message += f' - {len(validation_result.errors)} validation errors'
        return ModuleHealth(status=status, message=message, capabilities=await self.get_module_capabilities(), domain_health=await self.get_domain_health())

    async def get_module_capabilities(self) -> List[ModuleCapability]:
        """Get entity capabilities."""
        return [ModuleCapability(name=f'entity_{self.__class__.__name__.lower()}', description=f'Domain entity: {self.__class__.__name__}', available=await self.is_healthy(), version=str(self._version))]

    async def is_healthy(self) -> bool:
        """Check if entity is healthy."""
        try:
            validation_result = self.validate_domain_invariants()
            return validation_result.is_valid
        except Exception as e:
            logger.error(f'Health check failed for entity {self.__class__.__name__}({self.id}): {e}')
            return False

    async def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators."""
        validation_result = self.validate_domain_invariants()
        return {'entity_id': str(self.id), 'entity_type': self.__class__.__name__, 'version': self._version, 'domain_valid': validation_result.is_valid, 'validation_errors': len(validation_result.errors), 'validation_warnings': len(validation_result.warnings), 'pending_events': len(self._domain_events), 'last_updated': self._updated_at.isoformat()}

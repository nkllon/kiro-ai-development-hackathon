"""
Entities Core

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

class AggregateRoot(Entity[TAggregateId], ABC):
    """
    Base class for aggregate roots.
    
    Extends Entity with aggregate-specific capabilities including consistency
    boundary management, domain event coordination, and aggregate size monitoring.
    
    Additional Responsibilities:
    - Consistency boundary definition and enforcement
    - Domain event collection and publishing coordination
    - Aggregate size monitoring and validation
    - Transaction boundary management
    - Child entity lifecycle management
    
    Accountability Chain:
    - Domain Expert: Responsible for aggregate design and boundaries
    - Aggregate Owner: Responsible for aggregate-specific business logic
    - Entity Framework: Responsible for entity lifecycle management
    - RM Framework: Responsible for systematic compliance
    """

    def __init__(self, aggregate_id: TAggregateId, domain_context: str, max_size: Optional[int]=None, module_id: Optional[str]=None):
        """
        Initialize aggregate root with systematic compliance.
        
        Args:
            aggregate_id: Unique identifier for this aggregate
            domain_context: The bounded context this aggregate belongs to
            max_size: Maximum allowed size for this aggregate (optional)
            module_id: Optional RM module identifier
        """
        super().__init__(aggregate_id, domain_context, module_id)
        self._max_size = max_size or 100
        self._child_entities: Dict[str, List[Entity]] = {}
        self._aggregate_version = 1
        logger.debug(f'AggregateRoot created: {self.__class__.__name__}({aggregate_id}) with max_size: {self._max_size}')

    @abstractmethod
    def get_aggregate_boundaries(self) -> AggregateBoundaries:
        """
        Define aggregate consistency boundaries.
        
        Returns:
            AggregateBoundaries: Definition of aggregate boundaries,
                               consistency rules, and size constraints
                               
        Note:
            This method must be implemented by all aggregate roots to define
            their consistency boundaries and business rules.
        """
        pass

    def add_child_entity(self, entity_type: str, entity: Entity):
        """
        Add a child entity to this aggregate.
        
        Args:
            entity_type: Type/category of the child entity
            entity: The child entity to add
            
        Raises:
            DomainException: If adding the entity would violate aggregate constraints
        """
        if entity_type not in self._child_entities:
            self._child_entities[entity_type] = []
        current_size = self.get_aggregate_size()
        if current_size >= self._max_size:
            raise DomainException(f'Aggregate size limit exceeded: {current_size} >= {self._max_size}', error_code='AGGREGATE_SIZE_LIMIT', context={'aggregate_id': str(self.id), 'aggregate_type': self.__class__.__name__, 'current_size': current_size, 'max_size': self._max_size})
        self._child_entities[entity_type].append(entity)
        self.update_version()
        logger.debug(f'Child entity added to aggregate {self.__class__.__name__}({self.id}): {entity_type}')

    def remove_child_entity(self, entity_type: str, entity: Entity):
        """
        Remove a child entity from this aggregate.
        
        Args:
            entity_type: Type/category of the child entity
            entity: The child entity to remove
        """
        if entity_type in self._child_entities:
            try:
                self._child_entities[entity_type].remove(entity)
                self.update_version()
                logger.debug(f'Child entity removed from aggregate {self.__class__.__name__}({self.id}): {entity_type}')
            except ValueError:
                logger.warning(f'Attempted to remove non-existent child entity from aggregate {self.id}')

    def get_child_entities(self, entity_type: Optional[str]=None) -> Union[List[Entity], Dict[str, List[Entity]]]:
        """
        Get child entities of this aggregate.
        
        Args:
            entity_type: Optional type filter for child entities
            
        Returns:
            List of entities if entity_type specified, otherwise dict of all entities
        """
        if entity_type:
            return self._child_entities.get(entity_type, [])
        return self._child_entities.copy()

    def get_aggregate_size(self) -> int:
        """Get total size of this aggregate (including child entities)."""
        total_size = 1
        for entities in self._child_entities.values():
            total_size += len(entities)
        return total_size

    def validate_aggregate_constraints(self) -> ValidationResult:
        """
        Validate aggregate-specific constraints.
        
        Returns:
            ValidationResult: Result of aggregate constraint validation
        """
        result = ValidationResult(is_valid=True)
        current_size = self.get_aggregate_size()
        if current_size > self._max_size:
            result.add_error(f'Aggregate size {current_size} exceeds maximum {self._max_size}', code='AGG_001', component=self.__class__.__name__, context={'current_size': current_size, 'max_size': self._max_size})
        try:
            boundaries = self.get_aggregate_boundaries()
            if not boundaries.aggregate_type:
                result.add_error('Aggregate boundaries must specify aggregate_type', code='AGG_002', component=self.__class__.__name__)
        except Exception as e:
            result.add_error(f'Failed to get aggregate boundaries: {str(e)}', code='AGG_002', component=self.__class__.__name__)
        for entity_type, entities in self._child_entities.items():
            for i, entity in enumerate(entities):
                try:
                    child_validation = entity.validate_domain_invariants()
                    if not child_validation.is_valid:
                        result.add_error(f'Child entity {entity_type}[{i}] validation failed', code='AGG_003', component=self.__class__.__name__, context={'child_errors': child_validation.errors})
                except Exception as e:
                    result.add_error(f'Child entity {entity_type}[{i}] validation error: {str(e)}', code='AGG_003', component=self.__class__.__name__)
        return result

    def collect_all_domain_events(self) -> List['DomainEvent']:
        """
        Collect domain events from this aggregate and all child entities.
        
        Returns:
            List of all domain events from the aggregate and its children
        """
        all_events = self.get_domain_events().copy()
        for entities in self._child_entities.values():
            for entity in entities:
                all_events.extend(entity.get_domain_events())
        return all_events

    def clear_all_domain_events(self):
        """Clear domain events from this aggregate and all child entities."""
        self.clear_domain_events()
        for entities in self._child_entities.values():
            for entity in entities:
                entity.clear_domain_events()

    def get_aggregate_info(self) -> Dict[str, Any]:
        """Get comprehensive aggregate information."""
        base_info = self.get_entity_info()
        base_info.update({'aggregate_type': self.__class__.__name__, 'aggregate_size': self.get_aggregate_size(), 'max_size': self._max_size, 'child_entity_types': list(self._child_entities.keys()), 'child_entity_counts': {entity_type: len(entities) for entity_type, entities in self._child_entities.items()}, 'total_pending_events': len(self.collect_all_domain_events()), 'aggregate_version': self._aggregate_version})
        return base_info

    def validate_domain_invariants(self) -> ValidationResult:
        """
        Validate domain invariants including aggregate constraints.
        
        Returns:
            ValidationResult: Combined result of entity and aggregate validation
        """
        entity_result = super().validate_domain_invariants()
        aggregate_result = self.validate_aggregate_constraints()
        entity_result.merge(aggregate_result)
        return entity_result

    def update_version(self):
        """Update both entity and aggregate versions."""
        super().update_version()
        self._aggregate_version += 1

    async def get_module_capabilities(self) -> List[ModuleCapability]:
        """Get aggregate capabilities."""
        base_capabilities = await super().get_module_capabilities()
        base_capabilities.append(ModuleCapability(name=f'aggregate_{self.__class__.__name__.lower()}', description=f'Domain aggregate: {self.__class__.__name__}', available=await self.is_healthy(), version=str(self._aggregate_version), metadata={'aggregate_size': self.get_aggregate_size(), 'max_size': self._max_size, 'child_types': list(self._child_entities.keys())}))
        return base_capabilities

    async def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators including aggregate metrics."""
        base_indicators = await super().get_health_indicators()
        base_indicators.update({'aggregate_size': self.get_aggregate_size(), 'max_size': self._max_size, 'size_utilization': self.get_aggregate_size() / self._max_size * 100, 'child_entity_types': len(self._child_entities), 'total_child_entities': sum((len(entities) for entities in self._child_entities.values())), 'aggregate_version': self._aggregate_version, 'total_pending_events': len(self.collect_all_domain_events())})
        return base_indicators

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

def __init__(self, aggregate_id: TAggregateId, domain_context: str, max_size: Optional[int]=None, module_id: Optional[str]=None):
    """
        Initialize aggregate root with systematic compliance.
        
        Args:
            aggregate_id: Unique identifier for this aggregate
            domain_context: The bounded context this aggregate belongs to
            max_size: Maximum allowed size for this aggregate (optional)
            module_id: Optional RM module identifier
        """
    super().__init__(aggregate_id, domain_context, module_id)
    self._max_size = max_size or 100
    self._child_entities: Dict[str, List[Entity]] = {}
    self._aggregate_version = 1
    logger.debug(f'AggregateRoot created: {self.__class__.__name__}({aggregate_id}) with max_size: {self._max_size}')

@abstractmethod
def get_aggregate_boundaries(self) -> AggregateBoundaries:
    """
        Define aggregate consistency boundaries.
        
        Returns:
            AggregateBoundaries: Definition of aggregate boundaries,
                               consistency rules, and size constraints
                               
        Note:
            This method must be implemented by all aggregate roots to define
            their consistency boundaries and business rules.
        """
    pass

def add_child_entity(self, entity_type: str, entity: Entity):
    """
        Add a child entity to this aggregate.
        
        Args:
            entity_type: Type/category of the child entity
            entity: The child entity to add
            
        Raises:
            DomainException: If adding the entity would violate aggregate constraints
        """
    if entity_type not in self._child_entities:
        self._child_entities[entity_type] = []
    current_size = self.get_aggregate_size()
    if current_size >= self._max_size:
        raise DomainException(f'Aggregate size limit exceeded: {current_size} >= {self._max_size}', error_code='AGGREGATE_SIZE_LIMIT', context={'aggregate_id': str(self.id), 'aggregate_type': self.__class__.__name__, 'current_size': current_size, 'max_size': self._max_size})
    self._child_entities[entity_type].append(entity)
    self.update_version()
    logger.debug(f'Child entity added to aggregate {self.__class__.__name__}({self.id}): {entity_type}')

def remove_child_entity(self, entity_type: str, entity: Entity):
    """
        Remove a child entity from this aggregate.
        
        Args:
            entity_type: Type/category of the child entity
            entity: The child entity to remove
        """
    if entity_type in self._child_entities:
        try:
            self._child_entities[entity_type].remove(entity)
            self.update_version()
            logger.debug(f'Child entity removed from aggregate {self.__class__.__name__}({self.id}): {entity_type}')
        except ValueError:
            logger.warning(f'Attempted to remove non-existent child entity from aggregate {self.id}')

def get_child_entities(self, entity_type: Optional[str]=None) -> Union[List[Entity], Dict[str, List[Entity]]]:
    """
        Get child entities of this aggregate.
        
        Args:
            entity_type: Optional type filter for child entities
            
        Returns:
            List of entities if entity_type specified, otherwise dict of all entities
        """
    if entity_type:
        return self._child_entities.get(entity_type, [])
    return self._child_entities.copy()

def get_aggregate_size(self) -> int:
    """Get total size of this aggregate (including child entities)."""
    total_size = 1
    for entities in self._child_entities.values():
        total_size += len(entities)
    return total_size

def collect_all_domain_events(self) -> List['DomainEvent']:
    """
        Collect domain events from this aggregate and all child entities.
        
        Returns:
            List of all domain events from the aggregate and its children
        """
    all_events = self.get_domain_events().copy()
    for entities in self._child_entities.values():
        for entity in entities:
            all_events.extend(entity.get_domain_events())
    return all_events

def clear_all_domain_events(self):
    """Clear domain events from this aggregate and all child entities."""
    self.clear_domain_events()
    for entities in self._child_entities.values():
        for entity in entities:
            entity.clear_domain_events()

def get_aggregate_info(self) -> Dict[str, Any]:
    """Get comprehensive aggregate information."""
    base_info = self.get_entity_info()
    base_info.update({'aggregate_type': self.__class__.__name__, 'aggregate_size': self.get_aggregate_size(), 'max_size': self._max_size, 'child_entity_types': list(self._child_entities.keys()), 'child_entity_counts': {entity_type: len(entities) for entity_type, entities in self._child_entities.items()}, 'total_pending_events': len(self.collect_all_domain_events()), 'aggregate_version': self._aggregate_version})
    return base_info

def update_version(self):
    """Update both entity and aggregate versions."""
    super().update_version()
    self._aggregate_version += 1

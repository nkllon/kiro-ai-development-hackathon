"""
DDD Pattern Layer for RM-DDD SDK.

This module provides comprehensive Domain-Driven Design pattern implementations
with built-in Reflective Module compliance and systematic validation.
"""

from .entities import Entity, AggregateRoot
from .value_objects import ValueObject, ImmutableValueObject
from .services import DomainService
from .repositories import Repository, RepositoryRM
from .events import DomainEvent, DomainEventPublisher, DomainEventHandler
from .contexts import BoundedContext, DomainBoundaries

__all__ = [
    "Entity",
    "AggregateRoot",
    "ValueObject", 
    "ImmutableValueObject",
    "DomainService",
    "Repository",
    "RepositoryRM",
    "DomainEvent",
    "DomainEventPublisher",
    "DomainEventHandler",
    "BoundedContext",
    "DomainBoundaries",
]
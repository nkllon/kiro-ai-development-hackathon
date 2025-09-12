"""
Event sourcing capabilities for RM-DDD framework.

This module provides event store abstractions, event stream management,
and aggregate reconstruction capabilities for implementing event sourcing
patterns in domain-driven design.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, DomainBoundaries, ModuleStatus, ModuleCapability
from .events import DomainEvent, EventStream


logger = logging.getLogger(__name__)

# Type variables
AggregateType = TypeVar('AggregateType')
EventType = TypeVar('EventType', bound=DomainEvent)


@dataclass
class EventStoreRecord:
    """Represents a stored event record."""
    event_id: UUID
    aggregate_id: Any
    aggregate_type: str
    event_type: str
    event_data: Dict[str, Any]
    metadata: Dict[str, Any]
    version: int
    timestamp: datetime
    
    def to_domain_event(self, event_class: Type[DomainEvent]) -> DomainEvent:
        """Convert stored record back to domain event."""
        # This would need to be implemented based on the specific event class
        # For now, we'll use a generic approach
        return event_class.from_dict({
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'aggregate_id': str(self.aggregate_id),
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'event_data': self.event_data
        })


@dataclass
class Snapshot:
    """Represents an aggregate snapshot for performance optimization."""
    aggregate_id: Any
    aggregate_type: str
    aggregate_data: Dict[str, Any]
    version: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            'aggregate_id': str(self.aggregate_id),
            'aggregate_type': self.aggregate_type,
            'aggregate_data': self.aggregate_data,
            'version': self.version,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snapshot':
        """Create snapshot from dictionary."""
        return cls(
            aggregate_id=data['aggregate_id'],
            aggregate_type=data['aggregate_type'],
            aggregate_data=data['aggregate_data'],
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class EventStore(ABC):
    """
    Abstract interface for event storage.
    
    Defines the contract for storing and retrieving events in an event sourcing
    system. Implementations can use different storage backends (SQL, NoSQL, etc.)
    while maintaining consistent behavior.
    """
    
    @abstractmethod
    async def append_events(self, 
                          aggregate_id: Any, 
                          events: List[DomainEvent], 
                          expected_version: Optional[int] = None) -> None:
        """
        Append events to the event store.
        
        Args:
            aggregate_id: ID of the aggregate
            events: List of events to append
            expected_version: Expected current version for optimistic concurrency
            
        Raises:
            ConcurrencyException: If expected version doesn't match
            EventStoreException: If storage fails
        """
        pass
    
    @abstractmethod
    async def get_events(self, 
                        aggregate_id: Any, 
                        from_version: int = 0,
                        to_version: Optional[int] = None) -> List[DomainEvent]:
        """
        Get events for an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            from_version: Starting version (inclusive)
            to_version: Ending version (inclusive), None for all
            
        Returns:
            List[DomainEvent]: Events for the aggregate
        """
        pass
    
    @abstractmethod
    async def get_events_by_type(self, 
                               event_type: str,
                               from_timestamp: Optional[datetime] = None,
                               to_timestamp: Optional[datetime] = None) -> List[DomainEvent]:
        """
        Get events by type within a time range.
        
        Args:
            event_type: Type of events to retrieve
            from_timestamp: Start time (inclusive)
            to_timestamp: End time (inclusive)
            
        Returns:
            List[DomainEvent]: Events of the specified type
        """
        pass
    
    @abstractmethod
    async def get_aggregate_version(self, aggregate_id: Any) -> int:
        """
        Get the current version of an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            
        Returns:
            int: Current version of the aggregate
        """
        pass
    
    @abstractmethod
    async def aggregate_exists(self, aggregate_id: Any) -> bool:
        """
        Check if an aggregate exists in the event store.
        
        Args:
            aggregate_id: ID of the aggregate
            
        Returns:
            bool: True if aggregate exists
        """
        pass


class SnapshotStore(ABC):
    """
    Abstract interface for snapshot storage.
    
    Snapshots are used to optimize aggregate reconstruction by storing
    the state of an aggregate at a specific version, avoiding the need
    to replay all events from the beginning.
    """
    
    @abstractmethod
    async def save_snapshot(self, snapshot: Snapshot) -> None:
        """
        Save an aggregate snapshot.
        
        Args:
            snapshot: Snapshot to save
        """
        pass
    
    @abstractmethod
    async def get_snapshot(self, 
                          aggregate_id: Any, 
                          max_version: Optional[int] = None) -> Optional[Snapshot]:
        """
        Get the latest snapshot for an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            max_version: Maximum version to consider
            
        Returns:
            Optional[Snapshot]: Latest snapshot or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_snapshots(self, 
                             aggregate_id: Any, 
                             before_version: Optional[int] = None) -> None:
        """
        Delete snapshots for an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            before_version: Delete snapshots before this version
        """
        pass


class EventSourcedAggregate(ABC):
    """
    Base class for event-sourced aggregates.
    
    Provides the infrastructure for aggregates that are reconstructed
    from events rather than stored as current state. Handles event
    application and state reconstruction.
    """
    
    def __init__(self, aggregate_id: Any):
        self.aggregate_id = aggregate_id
        self._version = 0
        self._uncommitted_events: List[DomainEvent] = []
        self._is_new = True
    
    @property
    def version(self) -> int:
        """Get the current version of the aggregate."""
        return self._version
    
    @property
    def is_new(self) -> bool:
        """Check if this is a new aggregate (not yet persisted)."""
        return self._is_new
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get events that haven't been persisted yet."""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        """Mark all uncommitted events as committed."""
        self._uncommitted_events.clear()
        self._is_new = False
    
    def load_from_history(self, events: List[DomainEvent]):
        """
        Reconstruct aggregate state from historical events.
        
        Args:
            events: Historical events to apply
        """
        for event in events:
            self._apply_event(event, is_new=False)
        self._is_new = False
    
    def apply_event(self, event: DomainEvent):
        """
        Apply a new event to the aggregate.
        
        Args:
            event: New event to apply
        """
        self._apply_event(event, is_new=True)
        self._uncommitted_events.append(event)
    
    def _apply_event(self, event: DomainEvent, is_new: bool = True):
        """
        Apply an event to the aggregate state.
        
        Args:
            event: Event to apply
            is_new: Whether this is a new event or historical
        """
        # Find the appropriate handler method
        handler_name = f"_handle_{event.event_type}"
        handler = getattr(self, handler_name, None)
        
        if handler and callable(handler):
            handler(event)
        else:
            logger.warning(f"No handler found for event type {event.event_type} in {self.__class__.__name__}")
        
        if is_new:
            self._version += 1
    
    @abstractmethod
    def create_snapshot(self) -> Snapshot:
        """
        Create a snapshot of the current aggregate state.
        
        Returns:
            Snapshot: Current state snapshot
        """
        pass
    
    @abstractmethod
    def load_from_snapshot(self, snapshot: Snapshot):
        """
        Load aggregate state from a snapshot.
        
        Args:
            snapshot: Snapshot to load from
        """
        pass


class EventSourcingRepository(DomainReflectiveModule):
    """
    Repository for event-sourced aggregates.
    
    Provides systematic loading and saving of event-sourced aggregates
    with support for snapshots, optimistic concurrency control, and
    performance optimization.
    """
    
    def __init__(self, 
                 domain_context: str,
                 aggregate_type: str,
                 event_store: EventStore,
                 snapshot_store: Optional[SnapshotStore] = None,
                 snapshot_frequency: int = 10):
        super().__init__(domain_context)
        self.aggregate_type = aggregate_type
        self.event_store = event_store
        self.snapshot_store = snapshot_store
        self.snapshot_frequency = snapshot_frequency
        self._load_count = 0
        self._save_count = 0
        self._snapshot_count = 0
    
    async def load(self, 
                  aggregate_id: Any, 
                  aggregate_class: Type[EventSourcedAggregate]) -> Optional[EventSourcedAggregate]:
        """
        Load an aggregate from the event store.
        
        Args:
            aggregate_id: ID of the aggregate to load
            aggregate_class: Class of the aggregate
            
        Returns:
            Optional[EventSourcedAggregate]: Loaded aggregate or None if not found
        """
        try:
            # Check if aggregate exists
            if not await self.event_store.aggregate_exists(aggregate_id):
                return None
            
            # Create new aggregate instance
            aggregate = aggregate_class(aggregate_id)
            
            # Try to load from snapshot first
            from_version = 0
            if self.snapshot_store:
                snapshot = await self.snapshot_store.get_snapshot(aggregate_id)
                if snapshot:
                    aggregate.load_from_snapshot(snapshot)
                    from_version = snapshot.version + 1
                    logger.debug(f"Loaded aggregate {aggregate_id} from snapshot at version {snapshot.version}")
            
            # Load events after snapshot
            events = await self.event_store.get_events(aggregate_id, from_version)
            if events:
                aggregate.load_from_history(events)
                logger.debug(f"Applied {len(events)} events to aggregate {aggregate_id}")
            
            self._load_count += 1
            return aggregate
            
        except Exception as e:
            logger.error(f"Failed to load aggregate {aggregate_id}: {e}")
            raise DomainException(
                f"Failed to load aggregate: {str(e)}",
                error_code="AGGREGATE_LOAD_FAILED"
            )
    
    async def save(self, 
                  aggregate: EventSourcedAggregate, 
                  expected_version: Optional[int] = None) -> None:
        """
        Save an aggregate to the event store.
        
        Args:
            aggregate: Aggregate to save
            expected_version: Expected version for optimistic concurrency
            
        Raises:
            ConcurrencyException: If expected version doesn't match
        """
        try:
            uncommitted_events = aggregate.get_uncommitted_events()
            if not uncommitted_events:
                return  # Nothing to save
            
            # Append events to store
            await self.event_store.append_events(
                aggregate.aggregate_id,
                uncommitted_events,
                expected_version
            )
            
            # Mark events as committed
            aggregate.mark_events_as_committed()
            
            # Create snapshot if needed
            if (self.snapshot_store and 
                aggregate.version % self.snapshot_frequency == 0):
                await self._create_snapshot(aggregate)
            
            self._save_count += 1
            logger.debug(f"Saved aggregate {aggregate.aggregate_id} with {len(uncommitted_events)} events")
            
        except Exception as e:
            logger.error(f"Failed to save aggregate {aggregate.aggregate_id}: {e}")
            raise DomainException(
                f"Failed to save aggregate: {str(e)}",
                error_code="AGGREGATE_SAVE_FAILED"
            )
    
    async def _create_snapshot(self, aggregate: EventSourcedAggregate):
        """Create and save a snapshot of the aggregate."""
        try:
            snapshot = aggregate.create_snapshot()
            await self.snapshot_store.save_snapshot(snapshot)
            self._snapshot_count += 1
            logger.debug(f"Created snapshot for aggregate {aggregate.aggregate_id} at version {aggregate.version}")
        except Exception as e:
            logger.warning(f"Failed to create snapshot for aggregate {aggregate.aggregate_id}: {e}")
    
    async def get_events_for_aggregate(self, 
                                     aggregate_id: Any,
                                     from_version: int = 0,
                                     to_version: Optional[int] = None) -> List[DomainEvent]:
        """
        Get events for an aggregate without reconstructing it.
        
        Args:
            aggregate_id: ID of the aggregate
            from_version: Starting version
            to_version: Ending version
            
        Returns:
            List[DomainEvent]: Events for the aggregate
        """
        return await self.event_store.get_events(aggregate_id, from_version, to_version)
    
    def get_repository_metrics(self) -> Dict[str, Any]:
        """Get repository performance metrics."""
        return {
            'aggregate_type': self.aggregate_type,
            'load_count': self._load_count,
            'save_count': self._save_count,
            'snapshot_count': self._snapshot_count,
            'snapshot_frequency': self.snapshot_frequency,
            'has_snapshot_store': self.snapshot_store is not None
        }
    
    # RM Interface Implementation
    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        
        return ModuleHealth(
            status=ModuleStatus.AVAILABLE,
            message=f"Event sourcing repository for {self.aggregate_type}",
            capabilities=await self.get_module_capabilities(),
            health_indicators=self.get_repository_metrics()
        )
    
    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [
            ModuleCapability(
                name=f"event_sourcing_repository_{self.aggregate_type}",
                description=f"Event sourcing repository for {self.aggregate_type}",
                available=True,
                version="1.0.0"
            )
        ]
    
    async def is_healthy(self) -> bool:
        """Check if repository is healthy."""
        # Repository is healthy if it can perform basic operations
        return True
    
    async def get_health_indicators(self):
        """Get health indicators."""
        return {
            'repository_metrics': self.get_repository_metrics(),
            'domain_context': self.domain_context
        }
    
    def get_domain_boundaries(self):
        """Get domain boundaries."""
        return DomainBoundaries(
            context=self.domain_context,
            invariants=[
                "Events must be appended in order",
                "Aggregate version must be consistent",
                "Snapshots must represent valid aggregate state"
            ]
        )
    
    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        
        # Basic validation - in a real implementation, this would check
        # event store consistency, snapshot validity, etc.
        if self.snapshot_frequency <= 0:
            result.add_error("Snapshot frequency must be positive")
        
        return result


class InMemoryEventStore(EventStore):
    """
    In-memory implementation of EventStore for testing and development.
    
    This implementation stores events in memory and is suitable for
    testing, development, and small applications. For production use,
    consider using a persistent event store implementation.
    """
    
    def __init__(self):
        self._events: Dict[Any, List[EventStoreRecord]] = {}
        self._versions: Dict[Any, int] = {}
        self._lock = asyncio.Lock()
    
    async def append_events(self, 
                          aggregate_id: Any, 
                          events: List[DomainEvent], 
                          expected_version: Optional[int] = None) -> None:
        """Append events to the in-memory store."""
        async with self._lock:
            current_version = self._versions.get(aggregate_id, 0)
            
            # Check optimistic concurrency
            if expected_version is not None and current_version != expected_version:
                raise DomainException(
                    f"Concurrency conflict: expected version {expected_version}, "
                    f"but current version is {current_version}",
                    error_code="CONCURRENCY_CONFLICT"
                )
            
            # Initialize aggregate events list if needed
            if aggregate_id not in self._events:
                self._events[aggregate_id] = []
            
            # Append events
            for event in events:
                current_version += 1
                record = EventStoreRecord(
                    event_id=event.event_id,
                    aggregate_id=aggregate_id,
                    aggregate_type=event.__class__.__module__ + "." + event.__class__.__name__,
                    event_type=event.event_type,
                    event_data=event.get_event_data(),
                    metadata=event.metadata.__dict__,
                    version=current_version,
                    timestamp=event.timestamp
                )
                self._events[aggregate_id].append(record)
            
            self._versions[aggregate_id] = current_version
    
    async def get_events(self, 
                        aggregate_id: Any, 
                        from_version: int = 0,
                        to_version: Optional[int] = None) -> List[DomainEvent]:
        """Get events from the in-memory store."""
        if aggregate_id not in self._events:
            return []
        
        records = self._events[aggregate_id]
        
        # Filter by version range
        filtered_records = [
            record for record in records
            if record.version > from_version and 
               (to_version is None or record.version <= to_version)
        ]
        
        # Convert records back to domain events
        # Note: This is a simplified implementation
        # In practice, you'd need proper event deserialization
        events = []
        for record in filtered_records:
            # This would need proper event class resolution
            # For now, we'll create a generic event
            events.append(record)  # Placeholder
        
        return events
    
    async def get_events_by_type(self, 
                               event_type: str,
                               from_timestamp: Optional[datetime] = None,
                               to_timestamp: Optional[datetime] = None) -> List[DomainEvent]:
        """Get events by type from the in-memory store."""
        all_events = []
        
        for aggregate_events in self._events.values():
            for record in aggregate_events:
                if record.event_type == event_type:
                    # Check timestamp range
                    if from_timestamp and record.timestamp < from_timestamp:
                        continue
                    if to_timestamp and record.timestamp > to_timestamp:
                        continue
                    
                    all_events.append(record)  # Placeholder
        
        return all_events
    
    async def get_aggregate_version(self, aggregate_id: Any) -> int:
        """Get the current version of an aggregate."""
        return self._versions.get(aggregate_id, 0)
    
    async def aggregate_exists(self, aggregate_id: Any) -> bool:
        """Check if an aggregate exists."""
        return aggregate_id in self._events and len(self._events[aggregate_id]) > 0


class InMemorySnapshotStore(SnapshotStore):
    """
    In-memory implementation of SnapshotStore for testing and development.
    """
    
    def __init__(self):
        self._snapshots: Dict[Any, List[Snapshot]] = {}
        self._lock = asyncio.Lock()
    
    async def save_snapshot(self, snapshot: Snapshot) -> None:
        """Save a snapshot to memory."""
        async with self._lock:
            if snapshot.aggregate_id not in self._snapshots:
                self._snapshots[snapshot.aggregate_id] = []
            
            self._snapshots[snapshot.aggregate_id].append(snapshot)
            
            # Keep only the latest snapshots (limit to 10 per aggregate)
            self._snapshots[snapshot.aggregate_id] = sorted(
                self._snapshots[snapshot.aggregate_id],
                key=lambda s: s.version,
                reverse=True
            )[:10]
    
    async def get_snapshot(self, 
                          aggregate_id: Any, 
                          max_version: Optional[int] = None) -> Optional[Snapshot]:
        """Get the latest snapshot for an aggregate."""
        if aggregate_id not in self._snapshots:
            return None
        
        snapshots = self._snapshots[aggregate_id]
        
        # Filter by max version if specified
        if max_version is not None:
            snapshots = [s for s in snapshots if s.version <= max_version]
        
        if not snapshots:
            return None
        
        # Return the latest snapshot
        return max(snapshots, key=lambda s: s.version)
    
    async def delete_snapshots(self, 
                             aggregate_id: Any, 
                             before_version: Optional[int] = None) -> None:
        """Delete snapshots for an aggregate."""
        async with self._lock:
            if aggregate_id not in self._snapshots:
                return
            
            if before_version is None:
                # Delete all snapshots
                del self._snapshots[aggregate_id]
            else:
                # Delete snapshots before the specified version
                self._snapshots[aggregate_id] = [
                    s for s in self._snapshots[aggregate_id]
                    if s.version >= before_version
                ]
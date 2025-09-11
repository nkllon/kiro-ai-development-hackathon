"""
Domain event system for RM-DDD framework.

This module provides base classes and utilities for implementing domain events,
event publishing, and event handling in a systematic way that maintains
domain boundaries and supports event sourcing patterns.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID, uuid4

from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import (
    DomainException,
    EventMetadata,
    DomainBoundaries,
    ModuleStatus,
    ModuleCapability,
)


logger = logging.getLogger(__name__)

# Type variables
EventType = TypeVar('EventType', bound='DomainEvent')
HandlerType = TypeVar('HandlerType', bound='DomainEventHandler')


class DomainEvent(ABC):
    """
    Abstract base class for domain events.
    
    Domain events represent something significant that happened in the domain.
    They are immutable and contain all the information needed to understand
    what occurred and when.
    
    Key Principles:
    - Events are immutable once created
    - Events represent past occurrences (use past tense naming)
    - Events contain all necessary data for handlers
    - Events are serializable for persistence and messaging
    """
    
    def __init__(self, 
                 aggregate_id: Any,
                 event_version: int = 1,
                 correlation_id: Optional[UUID] = None,
                 causation_id: Optional[UUID] = None,
                 user_id: Optional[str] = None):
        """
        Initialize domain event.
        
        Args:
            aggregate_id: ID of the aggregate that generated this event
            event_version: Version of the event schema
            correlation_id: ID linking related events in a business process
            causation_id: ID of the event that caused this event
            user_id: ID of the user who triggered this event
        """
        self.metadata = EventMetadata(
            correlation_id=correlation_id,
            causation_id=causation_id,
            version=event_version,
            user_id=user_id
        )
        self.aggregate_id = aggregate_id
        self.event_type = self.__class__.__name__
        self._validated = False
    
    @property
    def event_id(self) -> UUID:
        """Get the unique event ID."""
        return self.metadata.event_id
    
    @property
    def timestamp(self) -> datetime:
        """Get the event timestamp."""
        return self.metadata.timestamp
    
    @property
    def correlation_id(self) -> Optional[UUID]:
        """Get the correlation ID."""
        return self.metadata.correlation_id
    
    @property
    def causation_id(self) -> Optional[UUID]:
        """Get the causation ID."""
        return self.metadata.causation_id
    
    @abstractmethod
    def get_event_data(self) -> Dict[str, Any]:
        """
        Get event-specific data.
        
        Returns:
            Dict[str, Any]: Event data that will be serialized
            
        Note:
            This should return all domain-specific data for the event.
            Do not include metadata here as it's handled separately.
        """
        pass
    
    def validate_event(self) -> ValidationResult:
        """
        Validate event data and business significance.
        
        Returns:
            ValidationResult: Validation results
            
        Note:
            Override this method to add event-specific validation logic.
        """
        result = ValidationResult(is_valid=True)
        
        # Basic validation
        if not self.aggregate_id:
            result.add_error("Event must have an aggregate ID")
        
        if not self.event_type:
            result.add_error("Event must have an event type")
        
        # Validate event data
        try:
            event_data = self.get_event_data()
            if not isinstance(event_data, dict):
                result.add_error("Event data must be a dictionary")
        except Exception as e:
            result.add_error(f"Failed to get event data: {str(e)}")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Complete event data including metadata
        """
        if not self._validated:
            validation_result = self.validate_event()
            if not validation_result.is_valid:
                raise DomainException(
                    f"Invalid event: {validation_result.errors}",
                    error_code="INVALID_EVENT"
                )
            self._validated = True
        
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'aggregate_id': str(self.aggregate_id),
            'timestamp': self.timestamp.isoformat(),
            'metadata': asdict(self.metadata),
            'event_data': self.get_event_data()
        }
    
    def to_json(self) -> str:
        """
        Convert event to JSON string.
        
        Returns:
            str: JSON representation of the event
        """
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, event_dict: Dict[str, Any]) -> 'DomainEvent':
        """
        Create event from dictionary.
        
        Args:
            event_dict: Dictionary containing event data
            
        Returns:
            DomainEvent: Reconstructed event instance
            
        Note:
            This is a base implementation. Subclasses should override
            this method to properly reconstruct their specific data.
        """
        # This would need to be implemented by concrete event classes
        # as they know how to reconstruct their specific data
        raise NotImplementedError("Subclasses must implement from_dict")
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DomainEvent':
        """
        Create event from JSON string.
        
        Args:
            json_str: JSON string containing event data
            
        Returns:
            DomainEvent: Reconstructed event instance
        """
        event_dict = json.loads(json_str)
        return cls.from_dict(event_dict)
    
    def __eq__(self, other: Any) -> bool:
        """Check equality based on event ID."""
        if not isinstance(other, DomainEvent):
            return False
        return self.event_id == other.event_id
    
    def __hash__(self) -> int:
        """Hash based on event ID."""
        return hash(self.event_id)
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.event_type}(id={self.event_id}, aggregate_id={self.aggregate_id})"


@dataclass
class EventStream:
    """Represents a stream of events for an aggregate."""
    aggregate_id: Any
    aggregate_type: str
    events: List[DomainEvent] = field(default_factory=list)
    version: int = 0
    
    def append_event(self, event: DomainEvent):
        """Add an event to the stream."""
        if event.aggregate_id != self.aggregate_id:
            raise DomainException(
                f"Event aggregate ID {event.aggregate_id} does not match stream aggregate ID {self.aggregate_id}",
                error_code="AGGREGATE_ID_MISMATCH"
            )
        
        self.events.append(event)
        self.version += 1
    
    def get_events_after_version(self, version: int) -> List[DomainEvent]:
        """Get events after a specific version."""
        return self.events[version:]
    
    def get_events_by_type(self, event_type: str) -> List[DomainEvent]:
        """Get events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]


class DomainEventHandler(ABC):
    """
    Abstract base class for domain event handlers.
    
    Event handlers process domain events and perform side effects
    such as updating read models, sending notifications, or
    triggering other business processes.
    """
    
    def __init__(self, handler_name: str):
        self.handler_name = handler_name
        self._handled_events = 0
        self._failed_events = 0
        self._last_handled = None
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Handle a domain event.
        
        Args:
            event: Domain event to handle
            
        Raises:
            Exception: If handling fails
            
        Note:
            Implementations should be idempotent as events may be
            replayed or delivered multiple times.
        """
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """
        Check if this handler can handle the given event type.
        
        Args:
            event_type: Type of event to check
            
        Returns:
            bool: True if this handler can handle the event type
        """
        pass
    
    async def handle_with_metrics(self, event: DomainEvent) -> None:
        """
        Handle event with metrics tracking.
        
        Args:
            event: Domain event to handle
        """
        try:
            await self.handle(event)
            self._handled_events += 1
            self._last_handled = datetime.now()
            logger.debug(f"Handler {self.handler_name} successfully handled {event.event_type}")
        except Exception as e:
            self._failed_events += 1
            logger.error(f"Handler {self.handler_name} failed to handle {event.event_type}: {e}")
            raise
    
    def get_handler_metrics(self) -> Dict[str, Any]:
        """Get handler performance metrics."""
        total_events = self._handled_events + self._failed_events
        success_rate = self._handled_events / max(total_events, 1)
        
        return {
            'handler_name': self.handler_name,
            'handled_events': self._handled_events,
            'failed_events': self._failed_events,
            'success_rate': success_rate,
            'last_handled': self._last_handled.isoformat() if self._last_handled else None
        }


class DomainEventPublisher(DomainReflectiveModule):
    """
    RM-compliant domain event publisher.
    
    Manages event publishing, handler registration, and event processing
    with systematic health monitoring and error handling.
    
    Features:
    - Asynchronous event processing
    - Handler registration and discovery
    - Error handling and retry logic
    - Performance metrics and health monitoring
    - Event ordering and consistency guarantees
    """
    
    def __init__(self, domain_context: str, publisher_id: Optional[str] = None):
        super().__init__(domain_context, publisher_id)
        self._handlers: Dict[str, List[DomainEventHandler]] = {}
        self._global_handlers: List[DomainEventHandler] = []
        self._published_events = 0
        self._failed_publications = 0
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._is_processing = False
    
    def subscribe(self, event_type: str, handler: DomainEventHandler):
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Handler to subscribe
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.handler_name} to event type {event_type}")
    
    def subscribe_to_all(self, handler: DomainEventHandler):
        """
        Subscribe a handler to all event types.
        
        Args:
            handler: Handler to subscribe to all events
        """
        self._global_handlers.append(handler)
        logger.info(f"Subscribed handler {handler.handler_name} to all events")
    
    def unsubscribe(self, event_type: str, handler: DomainEventHandler):
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to unsubscribe
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
            logger.info(f"Unsubscribed handler {handler.handler_name} from event type {event_type}")
    
    async def publish(self, event: DomainEvent):
        """
        Publish a domain event.
        
        Args:
            event: Domain event to publish
            
        Raises:
            DomainException: If publishing fails
        """
        try:
            # Validate event before publishing
            validation_result = event.validate_event()
            if not validation_result.is_valid:
                raise DomainException(
                    f"Cannot publish invalid event: {validation_result.errors}",
                    error_code="INVALID_EVENT_PUBLICATION"
                )
            
            # Add to processing queue
            await self._processing_queue.put(event)
            
            # Start processing if not already running
            if not self._is_processing:
                await self._start_processing()
            
            self._published_events += 1
            logger.info(f"Published event {event.event_type} for aggregate {event.aggregate_id}")
            
        except Exception as e:
            self._failed_publications += 1
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            raise DomainException(
                f"Event publication failed: {str(e)}",
                error_code="EVENT_PUBLICATION_FAILED"
            )
    
    async def publish_batch(self, events: List[DomainEvent]):
        """
        Publish multiple events as a batch.
        
        Args:
            events: List of events to publish
        """
        for event in events:
            await self.publish(event)
    
    async def _start_processing(self):
        """Start the event processing task."""
        if self._processing_task is None or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_events())
            self._is_processing = True
    
    async def _process_events(self):
        """Process events from the queue."""
        try:
            while True:
                try:
                    # Wait for an event with timeout
                    event = await asyncio.wait_for(
                        self._processing_queue.get(), 
                        timeout=1.0
                    )
                    
                    await self._handle_event(event)
                    self._processing_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # No events to process, continue waiting
                    continue
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    continue
                    
        except asyncio.CancelledError:
            logger.info("Event processing cancelled")
        finally:
            self._is_processing = False
    
    async def _handle_event(self, event: DomainEvent):
        """
        Handle a single event by dispatching to registered handlers.
        
        Args:
            event: Event to handle
        """
        handlers_to_notify = []
        
        # Get specific handlers for this event type
        if event.event_type in self._handlers:
            handlers_to_notify.extend(self._handlers[event.event_type])
        
        # Add global handlers
        handlers_to_notify.extend(self._global_handlers)
        
        # Filter handlers that can actually handle this event
        capable_handlers = [
            handler for handler in handlers_to_notify
            if handler.can_handle(event.event_type)
        ]
        
        if not capable_handlers:
            logger.warning(f"No handlers found for event type {event.event_type}")
            return
        
        # Handle event with all capable handlers
        handler_tasks = []
        for handler in capable_handlers:
            task = asyncio.create_task(handler.handle_with_metrics(event))
            handler_tasks.append(task)
        
        # Wait for all handlers to complete
        if handler_tasks:
            results = await asyncio.gather(*handler_tasks, return_exceptions=True)
            
            # Log any handler failures
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    handler_name = capable_handlers[i].handler_name
                    logger.error(f"Handler {handler_name} failed: {result}")
    
    def get_subscription_info(self) -> Dict[str, Any]:
        """Get information about current subscriptions."""
        return {
            'event_type_handlers': {
                event_type: [h.handler_name for h in handlers]
                for event_type, handlers in self._handlers.items()
            },
            'global_handlers': [h.handler_name for h in self._global_handlers],
            'total_handlers': sum(len(handlers) for handlers in self._handlers.values()) + len(self._global_handlers)
        }
    
    def get_publishing_metrics(self) -> Dict[str, Any]:
        """Get publishing performance metrics."""
        total_publications = self._published_events + self._failed_publications
        success_rate = self._published_events / max(total_publications, 1)
        
        return {
            'published_events': self._published_events,
            'failed_publications': self._failed_publications,
            'success_rate': success_rate,
            'queue_size': self._processing_queue.qsize(),
            'is_processing': self._is_processing
        }
    
    async def shutdown(self):
        """Gracefully shutdown the event publisher."""
        logger.info("Shutting down event publisher")
        
        # Cancel processing task
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        # Wait for queue to be empty
        await self._processing_queue.join()
        
        # Call parent shutdown
        await super().shutdown()
    
    # RM Interface Implementation
    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        
        total_publications = self._published_events + self._failed_publications
        success_rate = self._published_events / max(total_publications, 1) if total_publications > 0 else 1.0
        
        status = ModuleStatus.AVAILABLE if success_rate > 0.9 else ModuleStatus.DEGRADED
        
        return ModuleHealth(
            status=status,
            message=f"Domain event publisher for {self.domain_context}",
            capabilities=await self.get_module_capabilities(),
            health_indicators={
                'success_rate': success_rate,
                'published_events': self._published_events,
                'queue_size': self._processing_queue.qsize(),
                'handler_count': sum(len(handlers) for handlers in self._handlers.values()) + len(self._global_handlers)
            }
        )
    
    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [
            ModuleCapability(
                name="domain_event_publishing",
                description="Publishes and handles domain events",
                available=True,
                version="1.0.0"
            )
        ]
    
    async def is_healthy(self) -> bool:
        """Check if publisher is healthy."""
        total_publications = self._published_events + self._failed_publications
        if total_publications == 0:
            return True  # No publications yet, assume healthy
        
        success_rate = self._published_events / total_publications
        return success_rate > 0.9
    
    async def get_health_indicators(self):
        """Get health indicators."""
        return {
            'publishing_metrics': self.get_publishing_metrics(),
            'subscription_info': self.get_subscription_info(),
            'domain_context': self.domain_context
        }
    
    def get_domain_boundaries(self):
        """Get domain boundaries."""
        return DomainBoundaries(
            context=self.domain_context,
            invariants=[
                "Events must be valid before publishing",
                "Event handlers must be idempotent",
                "Event processing must maintain ordering within aggregate"
            ]
        )
    
    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        
        # Check publishing success rate
        total_publications = self._published_events + self._failed_publications
        if total_publications > 0:
            success_rate = self._published_events / total_publications
            if success_rate < 0.9:
                result.add_warning(f"Low publishing success rate: {success_rate:.2%}")
        
        # Check if processing is stuck
        if self._processing_queue.qsize() > 100:
            result.add_warning(f"Large event queue size: {self._processing_queue.qsize()}")
        
        return result


# Convenience classes for common event patterns
class AggregateCreatedEvent(DomainEvent):
    """Base class for aggregate creation events."""
    
    def __init__(self, aggregate_id: Any, aggregate_type: str, **kwargs):
        super().__init__(aggregate_id, **kwargs)
        self.aggregate_type = aggregate_type
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            'aggregate_type': self.aggregate_type
        }


class AggregateUpdatedEvent(DomainEvent):
    """Base class for aggregate update events."""
    
    def __init__(self, aggregate_id: Any, changes: Dict[str, Any], **kwargs):
        super().__init__(aggregate_id, **kwargs)
        self.changes = changes
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            'changes': self.changes
        }


class AggregateDeletedEvent(DomainEvent):
    """Base class for aggregate deletion events."""
    
    def __init__(self, aggregate_id: Any, aggregate_type: str, **kwargs):
        super().__init__(aggregate_id, **kwargs)
        self.aggregate_type = aggregate_type
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            'aggregate_type': self.aggregate_type
        }
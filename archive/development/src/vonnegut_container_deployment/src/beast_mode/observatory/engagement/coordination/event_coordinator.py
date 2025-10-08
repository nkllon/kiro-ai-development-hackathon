"""
Engagement Event Coordinator

Manages all engagement subsystems and coordinates events between components.
Provides unified engagement state management and event prioritization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from enum import Enum
from dataclasses import dataclass, field
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

logger = logging.getLogger(__name__)


class EngagementEventType(Enum):
    """Types of engagement events."""
    USER_INTERACTION = "user_interaction"
    ATTENTION_CHANGE = "attention_change"
    PERSONALITY_TRANSITION = "personality_transition"
    ANIMATION_TRIGGER = "animation_trigger"
    LEARNING_UPDATE = "learning_update"
    HEALTH_CHANGE = "health_change"
    SYSTEM_EVENT = "system_event"
    CUSTOM_EVENT = "custom_event"


class EngagementEventPriority(Enum):
    """Priority levels for engagement events."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class EngagementEvent:
    """Represents an engagement event."""
    event_id: str
    event_type: EngagementEventType
    priority: EngagementEventPriority
    source_component: str
    target_components: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    processing_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "priority": self.priority.value,
            "source_component": self.source_component,
            "target_components": self.target_components,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed,
            "processing_results": self.processing_results
        }


class EngagementEventCoordinator(ReflectiveModule):
    """
    Coordinates engagement events between all engagement subsystems.
    
    Manages event prioritization, routing, state management, and provides
    unified coordination for the entire engagement system.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "engagement_event_coordinator"
        
        # Event management
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.event_history: List[EngagementEvent] = []
        self.event_handlers: Dict[EngagementEventType, List[Callable]] = {}
        
        # Component registry
        self.registered_components: Dict[str, Any] = {}
        self.component_states: Dict[str, Dict[str, Any]] = {}
        
        # Coordination state
        self.running = False
        self.processing_task: Optional[asyncio.Task] = None
        
        # Event statistics
        self.events_processed = 0
        self.events_failed = 0
        self.last_event_time = datetime.now()
        
        # Configuration
        self.max_history_size = 1000
        self.event_timeout = 30.0  # seconds
        self.batch_size = 10
        
        logger.info("🎯 Engagement Event Coordinator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the event coordinator."""
        try:
            # Start event processing
            self.running = True
            self.processing_task = asyncio.create_task(self._event_processing_loop())
            
            # Register default event handlers
            self._register_default_handlers()
            
            logger.info("✅ Engagement Event Coordinator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Event Coordinator: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the event coordinator."""
        logger.info("🛑 Shutting down Engagement Event Coordinator...")
        
        self.running = False
        
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Engagement Event Coordinator shutdown complete")
    
    def register_component(self, component_id: str, component: Any, 
                          initial_state: Dict[str, Any] = None) -> None:
        """Register an engagement component."""
        self.registered_components[component_id] = component
        self.component_states[component_id] = initial_state or {}
        
        logger.info(f"📝 Registered engagement component: {component_id}")
    
    def unregister_component(self, component_id: str) -> None:
        """Unregister an engagement component."""
        if component_id in self.registered_components:
            del self.registered_components[component_id]
        
        if component_id in self.component_states:
            del self.component_states[component_id]
        
        logger.info(f"📝 Unregistered engagement component: {component_id}")
    
    def register_event_handler(self, event_type: EngagementEventType, 
                             handler: Callable) -> None:
        """Register an event handler for a specific event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.debug(f"📝 Registered event handler for {event_type.value}")
    
    async def emit_event(self, event_type: EngagementEventType, 
                        source_component: str,
                        data: Dict[str, Any] = None,
                        priority: EngagementEventPriority = EngagementEventPriority.MEDIUM,
                        target_components: List[str] = None) -> str:
        """Emit an engagement event."""
        event_id = f"event_{int(datetime.now().timestamp() * 1000)}_{len(self.event_history)}"
        
        event = EngagementEvent(
            event_id=event_id,
            event_type=event_type,
            priority=priority,
            source_component=source_component,
            target_components=target_components or [],
            data=data or {}
        )
        
        # Add to queue for processing
        await self.event_queue.put(event)
        
        logger.debug(f"📤 Emitted event: {event_type.value} from {source_component}")
        return event_id
    
    async def _event_processing_loop(self):
        """Background loop for processing engagement events."""
        logger.info("🔄 Starting engagement event processing loop")
        
        while self.running:
            try:
                # Process events in batches
                events_to_process = []
                
                # Collect events up to batch size
                for _ in range(self.batch_size):
                    try:
                        event = await asyncio.wait_for(
                            self.event_queue.get(), 
                            timeout=1.0
                        )
                        events_to_process.append(event)
                    except asyncio.TimeoutError:
                        break
                
                if events_to_process:
                    await self._process_event_batch(events_to_process)
                
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_event_batch(self, events: List[EngagementEvent]):
        """Process a batch of engagement events."""
        # Sort events by priority (highest first)
        events.sort(key=lambda e: e.priority.value, reverse=True)
        
        for event in events:
            try:
                await self._process_single_event(event)
                self.events_processed += 1
                
            except Exception as e:
                logger.error(f"Failed to process event {event.event_id}: {e}")
                self.events_failed += 1
                event.processing_results["error"] = str(e)
            
            finally:
                event.processed = True
                self.event_history.append(event)
                self.last_event_time = datetime.now()
        
        # Cleanup old events
        self._cleanup_event_history()
    
    async def _process_single_event(self, event: EngagementEvent):
        """Process a single engagement event."""
        logger.debug(f"🔄 Processing event: {event.event_id} ({event.event_type.value})")
        
        # Call registered event handlers
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    result = await self._call_handler(handler, event)
                    if result:
                        event.processing_results[f"handler_{id(handler)}"] = result
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
                    event.processing_results[f"handler_{id(handler)}_error"] = str(e)
        
        # Route to target components
        if event.target_components:
            await self._route_to_components(event)
        else:
            # Broadcast to all relevant components
            await self._broadcast_event(event)
        
        # Update component states based on event
        await self._update_component_states(event)
        
        logger.debug(f"✅ Processed event: {event.event_id}")
    
    async def _call_handler(self, handler: Callable, event: EngagementEvent) -> Any:
        """Call an event handler safely."""
        if asyncio.iscoroutinefunction(handler):
            return await handler(event)
        else:
            return handler(event)
    
    async def _route_to_components(self, event: EngagementEvent):
        """Route event to specific target components."""
        for component_id in event.target_components:
            if component_id in self.registered_components:
                component = self.registered_components[component_id]
                
                try:
                    # Try to call handle_engagement_event method
                    if hasattr(component, 'handle_engagement_event'):
                        if asyncio.iscoroutinefunction(component.handle_engagement_event):
                            result = await component.handle_engagement_event(event)
                        else:
                            result = component.handle_engagement_event(event)
                        
                        event.processing_results[component_id] = result
                    
                except Exception as e:
                    logger.error(f"Failed to route event to {component_id}: {e}")
                    event.processing_results[f"{component_id}_error"] = str(e)
    
    async def _broadcast_event(self, event: EngagementEvent):
        """Broadcast event to all registered components."""
        for component_id, component in self.registered_components.items():
            try:
                # Skip source component to avoid loops
                if component_id == event.source_component:
                    continue
                
                # Try to call handle_engagement_event method
                if hasattr(component, 'handle_engagement_event'):
                    if asyncio.iscoroutinefunction(component.handle_engagement_event):
                        result = await component.handle_engagement_event(event)
                    else:
                        result = component.handle_engagement_event(event)
                    
                    event.processing_results[component_id] = result
                
            except Exception as e:
                logger.error(f"Failed to broadcast event to {component_id}: {e}")
                event.processing_results[f"{component_id}_error"] = str(e)
    
    async def _update_component_states(self, event: EngagementEvent):
        """Update component states based on event."""
        # Update states based on event type
        if event.event_type == EngagementEventType.PERSONALITY_TRANSITION:
            mood = event.data.get('to_mood')
            if mood:
                self.component_states.setdefault('personality_engine', {})['current_mood'] = mood
        
        elif event.event_type == EngagementEventType.ATTENTION_CHANGE:
            session_id = event.data.get('session_id')
            if session_id:
                self.component_states.setdefault('attention_manager', {})['active_session'] = session_id
        
        elif event.event_type == EngagementEventType.USER_INTERACTION:
            interaction_count = self.component_states.setdefault('interaction_engine', {}).get('total_interactions', 0)
            self.component_states['interaction_engine']['total_interactions'] = interaction_count + 1
    
    def _cleanup_event_history(self):
        """Clean up old events from history."""
        if len(self.event_history) > self.max_history_size:
            # Keep only the most recent events
            self.event_history = self.event_history[-self.max_history_size:]
    
    def _register_default_handlers(self):
        """Register default event handlers."""
        # User interaction handler
        self.register_event_handler(
            EngagementEventType.USER_INTERACTION,
            self._handle_user_interaction
        )
        
        # Personality transition handler
        self.register_event_handler(
            EngagementEventType.PERSONALITY_TRANSITION,
            self._handle_personality_transition
        )
        
        # System event handler
        self.register_event_handler(
            EngagementEventType.SYSTEM_EVENT,
            self._handle_system_event
        )
    
    async def _handle_user_interaction(self, event: EngagementEvent) -> Dict[str, Any]:
        """Handle user interaction events."""
        interaction_type = event.data.get('event_type', 'unknown')
        component = event.data.get('component', 'unknown')
        
        # Trigger appropriate responses based on interaction
        if interaction_type == 'click' and component in ['chart', 'button']:
            # Trigger animation feedback
            await self.emit_event(
                EngagementEventType.ANIMATION_TRIGGER,
                'event_coordinator',
                {'animation_type': 'click_feedback', 'component': component},
                EngagementEventPriority.LOW
            )
        
        return {"handled": True, "interaction_type": interaction_type}
    
    async def _handle_personality_transition(self, event: EngagementEvent) -> Dict[str, Any]:
        """Handle personality transition events."""
        from_mood = event.data.get('from_mood', 'unknown')
        to_mood = event.data.get('to_mood', 'unknown')
        
        # Trigger visual theme changes
        await self.emit_event(
            EngagementEventType.ANIMATION_TRIGGER,
            'event_coordinator',
            {
                'animation_type': 'personality_change',
                'from_mood': from_mood,
                'to_mood': to_mood
            },
            EngagementEventPriority.MEDIUM
        )
        
        return {"handled": True, "mood_transition": f"{from_mood} -> {to_mood}"}
    
    async def _handle_system_event(self, event: EngagementEvent) -> Dict[str, Any]:
        """Handle system events."""
        system_event_type = event.data.get('system_event_type', 'unknown')
        
        # Route system events to appropriate components
        if system_event_type == 'health_change':
            # Update health-related components
            target_components = ['health_monitor', 'dashboard_engine']
        elif system_event_type == 'performance_change':
            # Update performance-related components
            target_components = ['animation_engine', 'metrics_collector']
        else:
            target_components = []
        
        if target_components:
            # Re-emit with specific targets
            await self.emit_event(
                event.event_type,
                'event_coordinator',
                event.data,
                event.priority,
                target_components
            )
        
        return {"handled": True, "system_event_type": system_event_type}
    
    # State management methods
    
    def get_unified_state(self) -> Dict[str, Any]:
        """Get unified engagement system state."""
        return {
            "coordinator_status": {
                "running": self.running,
                "events_processed": self.events_processed,
                "events_failed": self.events_failed,
                "last_event_time": self.last_event_time.isoformat(),
                "queue_size": self.event_queue.qsize(),
                "registered_components": list(self.registered_components.keys())
            },
            "component_states": self.component_states,
            "recent_events": [
                event.to_dict() for event in self.event_history[-10:]
            ]
        }
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        # Calculate event type distribution
        event_type_counts = {}
        for event in self.event_history[-100:]:  # Last 100 events
            event_type = event.event_type.value
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Calculate priority distribution
        priority_counts = {}
        for event in self.event_history[-100:]:
            priority = event.priority.name
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_events_processed": self.events_processed,
            "total_events_failed": self.events_failed,
            "success_rate": (self.events_processed / max(self.events_processed + self.events_failed, 1)) * 100,
            "event_type_distribution": event_type_counts,
            "priority_distribution": priority_counts,
            "average_processing_time": self._calculate_average_processing_time(),
            "events_per_minute": self._calculate_events_per_minute()
        }
    
    def _calculate_average_processing_time(self) -> float:
        """Calculate average event processing time."""
        # This would be implemented with actual timing data
        return 0.05  # Mock value in seconds
    
    def _calculate_events_per_minute(self) -> float:
        """Calculate events processed per minute."""
        if not self.event_history:
            return 0.0
        
        # Calculate based on recent events
        recent_events = [e for e in self.event_history if 
                        datetime.now() - e.timestamp < timedelta(minutes=5)]
        
        if not recent_events:
            return 0.0
        
        time_span = (datetime.now() - recent_events[0].timestamp).total_seconds() / 60
        return len(recent_events) / max(time_span, 1)
    
    # Analytics and logging
    
    async def log_engagement_analytics(self) -> Dict[str, Any]:
        """Log comprehensive engagement analytics."""
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "coordinator_metrics": {
                "events_processed": self.events_processed,
                "events_failed": self.events_failed,
                "queue_size": self.event_queue.qsize(),
                "registered_components": len(self.registered_components)
            },
            "event_statistics": self.get_event_statistics(),
            "component_states": self.component_states,
            "system_health": await self._assess_system_health()
        }
        
        logger.info(f"📊 Engagement Analytics: {json.dumps(analytics, indent=2)}")
        return analytics
    
    async def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall engagement system health."""
        health_score = 1.0
        issues = []
        
        # Check event processing health
        if self.events_failed > self.events_processed * 0.1:
            health_score *= 0.8
            issues.append("High event failure rate")
        
        # Check queue health
        if self.event_queue.qsize() > 100:
            health_score *= 0.9
            issues.append("Event queue backlog")
        
        # Check component health
        if len(self.registered_components) == 0:
            health_score *= 0.5
            issues.append("No registered components")
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.5 else "unhealthy",
            "issues": issues
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get event coordinator capabilities."""
        return [
            "event_coordination",
            "component_registration",
            "state_management",
            "event_prioritization",
            "analytics_logging",
            "system_health_monitoring"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get event coordinator health status."""
        return {
            "status": "healthy" if self.running else "stopped",
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "queue_size": self.event_queue.qsize(),
            "registered_components": len(self.registered_components),
            "processing_running": self.processing_task is not None and not self.processing_task.done()
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get event coordinator module information."""
        return {
            "module_id": self.module_id,
            "name": "Engagement Event Coordinator",
            "version": "1.0.0",
            "description": "Coordinates engagement events between all engagement subsystems"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Engagement Event Coordinator entering degradation mode due to: {error}")
            
            # Reduce batch size to handle events more carefully
            self.batch_size = max(1, self.batch_size // 2)
            
            # Clear event queue if it's too large
            if self.event_queue.qsize() > 50:
                # Drain some events to prevent memory issues
                for _ in range(min(25, self.event_queue.qsize())):
                    try:
                        self.event_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
            
            logger.info(f"Degradation applied: reduced batch size to {self.batch_size}")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False
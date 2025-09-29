"""
Event Capture System for AI Memory Palace.

Automatic context event capture for conversation events, code changes, 
spec updates, and decisions with correlation ID tracking.
"""

import asyncio
import inspect
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from pathlib import Path
import uuid

from ..core.reflective_module import ReflectiveModule
from ..tracing.tracer import DistributedTracer
from .models import ContextEvent, ContextEventType, EventMetadata
from .context_manager import ContextManager


class EventCapture(ReflectiveModule):
    """Automatic context event capture system"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        
        self.context_manager = context_manager
        self.tracer = DistributedTracer(service_name="event-capture")
        
        # Event capture metrics
        self._events_captured = 0
        self._code_events = 0
        self._spec_events = 0
        self._decision_events = 0
        self._discovery_events = 0
        
        # Active correlation context
        self._current_correlation_id = None
        self._event_buffer = []
        
        self.logger.info("📝 EventCapture system initialized")
    
    def set_correlation_context(self, correlation_id: str):
        """Set correlation ID for subsequent events"""
        self._current_correlation_id = correlation_id
        
        self.emit_observation({
            "type": "correlation_context_set",
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def capture_conversation_start(self, session_info: Dict[str, Any]) -> str:
        """Capture conversation start event"""
        correlation_id = str(uuid.uuid4())
        self.set_correlation_context(correlation_id)
        
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.CONVERSATION_START,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            data={
                "session_info": session_info,
                "project_id": self.context_manager.current_project_id,
                "timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["conversation", "start"],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._events_captured += 1
        
        self.logger.info(f"🎬 Conversation started: {correlation_id}")
        return correlation_id
    
    async def capture_conversation_end(self, summary: Dict[str, Any]):
        """Capture conversation end event"""
        if not self._current_correlation_id:
            self.logger.warning("⚠️ No active correlation context for conversation end")
            return
        
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.CONVERSATION_END,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id,
            data={
                "summary": summary,
                "events_captured": self._events_captured,
                "duration_minutes": summary.get("duration_minutes", 0)
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["conversation", "end"],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._events_captured += 1
        
        self.logger.info(f"🎬 Conversation ended: {self._current_correlation_id}")
        self._current_correlation_id = None
    
    async def capture_code_written(self, files_created: List[str], files_modified: List[str], 
                                 description: str, tests_added: Optional[List[str]] = None):
        """Capture code writing event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.CODE_WRITTEN,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "description": description,
                "files_created": files_created,
                "files_modified": files_modified,
                "tests_added": tests_added or [],
                "total_files": len(files_created) + len(files_modified),
                "lines_of_code": self._estimate_lines_of_code(files_created + files_modified)
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["code", "development"],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._code_events += 1
        self._events_captured += 1
        
        self.logger.info(f"💻 Code written: {len(files_created)} created, {len(files_modified)} modified")
    
    async def capture_spec_created(self, spec_name: str, spec_type: str, spec_path: str):
        """Capture specification creation event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.SPEC_CREATED,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "spec_name": spec_name,
                "spec_type": spec_type,
                "spec_path": spec_path,
                "creation_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["spec", "creation", spec_type],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._spec_events += 1
        self._events_captured += 1
        
        self.logger.info(f"📋 Spec created: {spec_name} ({spec_type})")
    
    async def capture_spec_updated(self, spec_name: str, changes: Dict[str, Any], completion_percentage: float):
        """Capture specification update event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.SPEC_UPDATED,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "spec_name": spec_name,
                "changes": changes,
                "completion_percentage": completion_percentage,
                "update_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["spec", "update"],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._spec_events += 1
        self._events_captured += 1
        
        self.logger.info(f"📋 Spec updated: {spec_name} ({completion_percentage:.1f}% complete)")
    
    async def capture_task_completed(self, task_name: str, spec_name: str, completion_time_minutes: float):
        """Capture task completion event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.TASK_COMPLETED,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "task_name": task_name,
                "spec_name": spec_name,
                "completion_time_minutes": completion_time_minutes,
                "completion_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["task", "completion", spec_name],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._events_captured += 1
        
        self.logger.info(f"✅ Task completed: {task_name} in {completion_time_minutes:.1f} minutes")
    
    async def capture_decision_made(self, description: str, rationale: str, 
                                  alternatives_considered: List[str], outcome: Optional[str] = None):
        """Capture decision making event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.DECISION_MADE,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "description": description,
                "rationale": rationale,
                "alternatives_considered": alternatives_considered,
                "outcome": outcome,
                "decision_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["decision", "reasoning"],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._decision_events += 1
        self._events_captured += 1
        
        self.logger.info(f"🤔 Decision made: {description}")
    
    async def capture_discovery_made(self, discovery_type: str, description: str, 
                                   components_found: List[str], capabilities_identified: List[str]):
        """Capture system discovery event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.DISCOVERY_MADE,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "discovery_type": discovery_type,
                "description": description,
                "components_found": components_found,
                "capabilities_identified": capabilities_identified,
                "discovery_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["discovery", discovery_type],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._discovery_events += 1
        self._events_captured += 1
        
        self.logger.info(f"🔍 Discovery made: {discovery_type} - {len(components_found)} components")
    
    async def capture_error_encountered(self, error_type: str, error_message: str, 
                                      context: Dict[str, Any], resolution: Optional[str] = None):
        """Capture error encounter event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.ERROR_ENCOUNTERED,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "error_type": error_type,
                "error_message": error_message,
                "context": context,
                "resolution": resolution,
                "error_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["error", error_type],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._events_captured += 1
        
        self.logger.warning(f"💥 Error encountered: {error_type} - {error_message}")
    
    async def capture_system_state_changed(self, change_type: str, old_state: Dict[str, Any], 
                                         new_state: Dict[str, Any], impact: str):
        """Capture system state change event"""
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=ContextEventType.SYSTEM_STATE_CHANGED,
            timestamp=datetime.now(),
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "change_type": change_type,
                "old_state": old_state,
                "new_state": new_state,
                "impact": impact,
                "change_timestamp": datetime.now().isoformat()
            },
            metadata=EventMetadata(
                source="event_capture",
                session_id=self.context_manager.current_session_id,
                tags=["system", "state_change", change_type],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
        self._events_captured += 1
        
        self.logger.info(f"🔄 System state changed: {change_type} - {impact}")
    
    def capture_decorator(self, event_type: ContextEventType, description: Optional[str] = None):
        """Decorator for automatic event capture"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = datetime.now()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Capture successful execution
                    await self._capture_function_execution(
                        func, args, kwargs, result, start_time, event_type, description
                    )
                    
                    return result
                    
                except Exception as e:
                    # Capture error
                    await self.capture_error_encountered(
                        error_type="function_execution_error",
                        error_message=str(e),
                        context={
                            "function": func.__name__,
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200]
                        }
                    )
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = datetime.now()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Capture successful execution (run async in background)
                    asyncio.create_task(self._capture_function_execution(
                        func, args, kwargs, result, start_time, event_type, description
                    ))
                    
                    return result
                    
                except Exception as e:
                    # Capture error (run async in background)
                    asyncio.create_task(self.capture_error_encountered(
                        error_type="function_execution_error",
                        error_message=str(e),
                        context={
                            "function": func.__name__,
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200]
                        }
                    ))
                    raise
            
            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def _capture_function_execution(self, func: Callable, args: tuple, kwargs: dict, 
                                        result: Any, start_time: datetime, 
                                        event_type: ContextEventType, description: Optional[str]):
        """Capture function execution as context event"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        event = ContextEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=start_time,
            correlation_id=self._current_correlation_id or str(uuid.uuid4()),
            data={
                "function_name": func.__name__,
                "description": description or f"Executed {func.__name__}",
                "execution_time_seconds": execution_time,
                "result_type": type(result).__name__,
                "success": True
            },
            metadata=EventMetadata(
                source="event_capture_decorator",
                session_id=self.context_manager.current_session_id,
                tags=["function_execution", func.__name__],
                confidence=1.0
            )
        )
        
        await self._store_event(event)
    
    async def _store_event(self, event: ContextEvent):
        """Store event in context manager"""
        with self.tracer.start_span("event_capture_store") as span:
            try:
                span.set_attribute("event_type", event.event_type.value)
                span.set_attribute("correlation_id", event.correlation_id)
                
                success = await self.context_manager.save_context_event(event)
                
                if success:
                    span.set_attribute("event_stored", True)
                    
                    self.emit_observation({
                        "type": "context_event_captured",
                        "event_type": event.event_type.value,
                        "event_id": event.event_id,
                        "correlation_id": event.correlation_id,
                        "session_id": self.context_manager.current_session_id
                    })
                else:
                    span.set_status("ERROR", "Failed to store event")
                    self.logger.error(f"❌ Failed to store event: {event.event_id}")
                
            except Exception as e:
                span.record_exception(e)
                span.set_status("ERROR", str(e))
                self.logger.error(f"💥 Error storing event: {e}")
    
    def _estimate_lines_of_code(self, file_paths: List[str]) -> int:
        """Estimate lines of code in files"""
        total_lines = 0
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists() and path.suffix in ['.py', '.js', '.ts', '.html', '.css', '.md']:
                    with open(path, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
            except Exception:
                # Ignore errors in line counting
                pass
        
        return total_lines
    
    def get_capture_stats(self) -> Dict[str, Any]:
        """Get event capture statistics"""
        return {
            "total_events_captured": self._events_captured,
            "code_events": self._code_events,
            "spec_events": self._spec_events,
            "decision_events": self._decision_events,
            "discovery_events": self._discovery_events,
            "current_correlation_id": self._current_correlation_id,
            "active_session": self.context_manager.current_session_id
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for EventCapture"""
        return {
            "status": "healthy",
            "events_captured": self._events_captured,
            "active_correlation": self._current_correlation_id is not None,
            "context_manager_healthy": self.context_manager.health_check()["status"] == "healthy"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        return {
            "event_capture_events_total": self._events_captured,
            "event_capture_code_events_total": self._code_events,
            "event_capture_spec_events_total": self._spec_events,
            "event_capture_decision_events_total": self._decision_events,
            "event_capture_discovery_events_total": self._discovery_events
        }


# Global event capture instance (initialized when context manager is available)
_global_event_capture: Optional[EventCapture] = None


def initialize_event_capture(context_manager: ContextManager):
    """Initialize global event capture instance"""
    global _global_event_capture
    _global_event_capture = EventCapture(context_manager)
    return _global_event_capture


def get_event_capture() -> Optional[EventCapture]:
    """Get global event capture instance"""
    return _global_event_capture


# Convenience functions for common event capture
async def capture_code_written(files_created: List[str], files_modified: List[str], description: str):
    """Convenience function for capturing code writing"""
    if _global_event_capture:
        await _global_event_capture.capture_code_written(files_created, files_modified, description)


async def capture_decision_made(description: str, rationale: str, alternatives: List[str]):
    """Convenience function for capturing decisions"""
    if _global_event_capture:
        await _global_event_capture.capture_decision_made(description, rationale, alternatives)


async def capture_discovery_made(discovery_type: str, description: str, components: List[str], capabilities: List[str]):
    """Convenience function for capturing discoveries"""
    if _global_event_capture:
        await _global_event_capture.capture_discovery_made(discovery_type, description, components, capabilities)


# Decorators for automatic capture
def capture_code_execution(description: Optional[str] = None):
    """Decorator for capturing code execution events"""
    if _global_event_capture:
        return _global_event_capture.capture_decorator(ContextEventType.CODE_WRITTEN, description)
    else:
        # Return no-op decorator if event capture not initialized
        def no_op_decorator(func):
            return func
        return no_op_decorator


def capture_decision_execution(description: Optional[str] = None):
    """Decorator for capturing decision execution events"""
    if _global_event_capture:
        return _global_event_capture.capture_decorator(ContextEventType.DECISION_MADE, description)
    else:
        def no_op_decorator(func):
            return func
        return no_op_decorator
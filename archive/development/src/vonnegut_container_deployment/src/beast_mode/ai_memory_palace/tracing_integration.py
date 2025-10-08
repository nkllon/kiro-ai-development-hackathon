"""
Distributed Tracing Integration for AI Memory Palace.

Integrates context operations with the existing Beast Mode distributed tracing
system for complete observability and correlation ID propagation.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import uuid

from src.beast_mode.core.beastly_module import BeastlyModule
from src.rm_ddd.core.unified_reflective_module import ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
from ..tracing.tracer import BeastModeTracer
from .models import SessionContext, ContextEvent


class ContextTracingIntegration(BeastlyModule):
    """Integration between AI Memory Palace and distributed tracing"""
    
    def __init__(self, service_name: str = "ai-memory-palace"):
        super().__init__()
        
        # Initialize tracer
        self.tracer = BeastModeTracer(service_name=service_name)
        self.service_name = service_name
        
        # Tracing metrics
        self._spans_created = 0
        self._context_operations_traced = 0
        self._correlation_ids_propagated = 0
        
        # Active span context
        self._active_spans = {}
        
        self._logger.info(f"🔗 ContextTracingIntegration initialized for service: {service_name}")
    
    @contextmanager
    def trace_context_operation(self, operation_name: str, context: Optional[SessionContext] = None, 
                               correlation_id: Optional[str] = None, **attributes):
        """Trace a context operation with proper span management"""
        span_name = f"context.{operation_name}"
        
        try:
            # Start span with the tracer
            with self.tracer.start_span(span_name) as span:
                self._spans_created += 1
                self._context_operations_traced += 1
                
                # Set standard attributes
                span.set_attribute("service.name", self.service_name)
                span.set_attribute("operation.name", operation_name)
                span.set_attribute("operation.timestamp", datetime.now().isoformat())
                
                # Set context-specific attributes
                if context:
                    span.set_attribute("context.project_id", context.project_id)
                    span.set_attribute("context.session_id", context.session_id)
                    span.set_attribute("context.size_bytes", context.get_context_size())
                    span.set_attribute("context.conversation_events", len(context.conversation_history))
                    span.set_attribute("context.decisions_count", len(context.decisions_made))
                    span.set_attribute("context.work_items_count", len(context.work_completed))
                
                # Set correlation ID
                if correlation_id:
                    span.set_attribute("correlation.id", correlation_id)
                    self._correlation_ids_propagated += 1
                
                # Set custom attributes
                for key, value in attributes.items():
                    span.set_attribute(f"custom.{key}", str(value))
                
                # Store active span
                span_id = str(uuid.uuid4())
                self._active_spans[span_id] = span
                
                # Emit observation for span creation
                self.emit_observation({
                    "type": "tracing_span_created",
                    "span_name": span_name,
                    "span_id": span_id,
                    "operation": operation_name,
                    "correlation_id": correlation_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                try:
                    yield span
                    
                    # Mark span as successful
                    span.set_attribute("operation.success", True)
                    
                except Exception as e:
                    # Record exception in span
                    span.record_exception(e)
                    span.set_status("ERROR", str(e))
                    span.set_attribute("operation.success", False)
                    span.set_attribute("error.message", str(e))
                    
                    # Emit error observation
                    self.emit_observation({
                        "type": "tracing_span_error",
                        "span_name": span_name,
                        "span_id": span_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    raise
                
                finally:
                    # Clean up active span
                    if span_id in self._active_spans:
                        del self._active_spans[span_id]
                    
                    # Emit span completion observation
                    self.emit_observation({
                        "type": "tracing_span_completed",
                        "span_name": span_name,
                        "span_id": span_id,
                        "operation": operation_name,
                        "timestamp": datetime.now().isoformat()
                    })
        
        except Exception as e:
            # Fallback if tracing fails
            self._logger.error(f"💥 Tracing failed for operation {operation_name}: {e}")
            
            # Emit tracing failure observation
            self.emit_observation({
                "type": "tracing_failure",
                "operation": operation_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            # Yield a no-op context manager
            yield None
    
    def trace_context_load(self, project_id: str, session_id: Optional[str] = None):
        """Trace context loading operation"""
        return self.trace_context_operation(
            "load",
            correlation_id=str(uuid.uuid4()),
            project_id=project_id,
            session_id=session_id or "latest",
            operation_type="read"
        )
    
    def trace_context_save(self, context: SessionContext):
        """Trace context saving operation"""
        return self.trace_context_operation(
            "save",
            context=context,
            correlation_id=str(uuid.uuid4()),
            operation_type="write",
            context_version="current"
        )
    
    def trace_context_validation(self, context: SessionContext):
        """Trace context validation operation"""
        return self.trace_context_operation(
            "validation",
            context=context,
            correlation_id=str(uuid.uuid4()),
            operation_type="validation",
            validation_type="integrity"
        )
    
    def trace_context_summarization(self, context: SessionContext, target_size_kb: int):
        """Trace context summarization operation"""
        return self.trace_context_operation(
            "summarization",
            context=context,
            correlation_id=str(uuid.uuid4()),
            operation_type="processing",
            target_size_kb=target_size_kb,
            original_size_kb=context.get_context_size() / 1024
        )
    
    def trace_context_filtering(self, context: SessionContext, query: str):
        """Trace context filtering operation"""
        return self.trace_context_operation(
            "filtering",
            context=context,
            correlation_id=str(uuid.uuid4()),
            operation_type="processing",
            query_length=len(query),
            filter_type="relevance"
        )
    
    def trace_event_capture(self, event: ContextEvent):
        """Trace context event capture"""
        return self.trace_context_operation(
            "event_capture",
            correlation_id=event.correlation_id,
            event_type=event.event_type.value,
            event_id=event.event_id,
            operation_type="capture"
        )
    
    def trace_dag_validation(self, context: SessionContext):
        """Trace DAG validation operation"""
        return self.trace_context_operation(
            "dag_validation",
            context=context,
            correlation_id=str(uuid.uuid4()),
            operation_type="validation",
            validation_type="dag_compliance",
            event_count=len(context.conversation_history)
        )
    
    def trace_context_repair(self, context: SessionContext):
        """Trace context repair operation"""
        return self.trace_context_operation(
            "repair",
            context=context,
            correlation_id=str(uuid.uuid4()),
            operation_type="repair",
            repair_type="corruption_fix"
        )
    
    def create_correlation_id(self) -> str:
        """Create a new correlation ID for tracing"""
        correlation_id = str(uuid.uuid4())
        
        self.emit_observation({
            "type": "correlation_id_created",
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return correlation_id
    
    def propagate_correlation_context(self, correlation_id: str, operation: str, metadata: Dict[str, Any]):
        """Propagate correlation context across operations"""
        try:
            # Add correlation context to current span if available
            current_span = self.tracer.get_current_span()
            if current_span:
                current_span.set_attribute("correlation.id", correlation_id)
                current_span.set_attribute("correlation.operation", operation)
                
                # Add metadata as attributes
                for key, value in metadata.items():
                    current_span.set_attribute(f"correlation.{key}", str(value))
            
            self._correlation_ids_propagated += 1
            
            self.emit_observation({
                "type": "correlation_context_propagated",
                "correlation_id": correlation_id,
                "operation": operation,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self._logger.error(f"💥 Error propagating correlation context: {e}")
    
    def get_trace_context(self) -> Dict[str, Any]:
        """Get current trace context information"""
        try:
            current_span = self.tracer.get_current_span()
            if current_span:
                span_context = current_span.get_span_context()
                return {
                    "trace_id": format(span_context.trace_id, '032x'),
                    "span_id": format(span_context.span_id, '016x'),
                    "trace_flags": span_context.trace_flags,
                    "is_valid": span_context.is_valid
                }
            else:
                return {"trace_id": None, "span_id": None, "active": False}
                
        except Exception as e:
            self._logger.error(f"💥 Error getting trace context: {e}")
            return {"error": str(e)}
    
    def add_trace_event(self, name: str, attributes: Dict[str, Any]):
        """Add an event to the current trace span"""
        try:
            current_span = self.tracer.get_current_span()
            if current_span:
                current_span.add_event(name, attributes)
                
                self.emit_observation({
                    "type": "trace_event_added",
                    "event_name": name,
                    "attributes": attributes,
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            self._logger.error(f"💥 Error adding trace event: {e}")
    
    def create_child_span(self, name: str, parent_correlation_id: str) -> str:
        """Create a child span with correlation to parent"""
        child_correlation_id = str(uuid.uuid4())
        
        try:
            # The child span will be created when the context manager is used
            # This method just creates the correlation ID and logs the relationship
            
            self.emit_observation({
                "type": "child_span_correlation_created",
                "parent_correlation_id": parent_correlation_id,
                "child_correlation_id": child_correlation_id,
                "span_name": name,
                "timestamp": datetime.now().isoformat()
            })
            
            return child_correlation_id
            
        except Exception as e:
            self._logger.error(f"💥 Error creating child span correlation: {e}")
            return str(uuid.uuid4())  # Fallback
    
    def get_tracing_stats(self) -> Dict[str, Any]:
        """Get tracing integration statistics"""
        return {
            "spans_created": self._spans_created,
            "context_operations_traced": self._context_operations_traced,
            "correlation_ids_propagated": self._correlation_ids_propagated,
            "active_spans": len(self._active_spans),
            "tracer_initialized": self.tracer.initialized if hasattr(self.tracer, 'initialized') else True,
            "service_name": self.service_name
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for tracing integration"""
        try:
            # Test if we can create a span
            with self.trace_context_operation("health_check") as span:
                if span:
                    return {
                        "status": "healthy",
                        "tracer_available": True,
                        "spans_created": self._spans_created,
                        "service_name": self.service_name
                    }
                else:
                    return {
                        "status": "degraded",
                        "tracer_available": False,
                        "message": "Tracing available but span creation failed"
                    }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "tracer_available": False
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        return {
            "context_tracing_spans_created_total": self._spans_created,
            "context_tracing_operations_traced_total": self._context_operations_traced,
            "context_tracing_correlation_ids_propagated_total": self._correlation_ids_propagated,
            "context_tracing_active_spans": len(self._active_spans)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": "ai_memory_palace_context_tracing_integration",
            "module_name": "ContextTracingIntegration", 
            "version": "1.0.0",
            "description": "Integration between AI Memory Palace and distributed tracing"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        return ModuleHealth(
            module_id="ai_memory_palace_context_tracing_integration",
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=[
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
        )


# Convenience class that combines tracer functionality
class DistributedTracer:
    """Simplified interface for distributed tracing in AI Memory Palace"""
    
    def __init__(self, service_name: str = "ai-memory-palace"):
        self.integration = ContextTracingIntegration(service_name)
    
    def start_span(self, operation_name: str, **attributes):
        """Start a new tracing span"""
        return self.integration.trace_context_operation(operation_name, **attributes)
    
    def get_current_span(self):
        """Get current span from the tracer"""
        return self.integration.tracer.get_current_span() if hasattr(self.integration.tracer, 'get_current_span') else None
    
    def create_correlation_id(self) -> str:
        """Create correlation ID"""
        return self.integration.create_correlation_id()
    
    def propagate_correlation(self, correlation_id: str, operation: str, metadata: Dict[str, Any]):
        """Propagate correlation context"""
        self.integration.propagate_correlation_context(correlation_id, operation, metadata)
    
    def add_event(self, name: str, attributes: Dict[str, Any]):
        """Add event to current span"""
        self.integration.add_trace_event(name, attributes)
    
    def get_trace_context(self) -> Dict[str, Any]:
        """Get current trace context"""
        return self.integration.get_trace_context()
    
    def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return self.integration.health_check()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics"""
        return self.integration.get_metrics()
    

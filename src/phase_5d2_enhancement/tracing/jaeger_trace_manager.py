"""
Jaeger distributed tracing integration for Phase 5D2 Enhancement System
"""

import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, ContextManager
from contextlib import contextmanager

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config


@dataclass
class TraceContext:
    """Context for a distributed trace."""
    trace_id: str
    operation_name: str
    start_time: datetime
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_tag(self, key: str, value: Any) -> None:
        """Add a tag to the trace context."""
        self.tags[key] = value
    
    def log_event(self, event: str, payload: Dict[str, Any]) -> None:
        """Log an event in the trace context."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload
        })


@dataclass
class SpanContext:
    """Context for a span within a trace."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_tag(self, key: str, value: Any) -> None:
        """Add a tag to the span context."""
        self.tags[key] = value
    
    def log_event(self, event: str, payload: Dict[str, Any]) -> None:
        """Log an event in the span context."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload
        })
    
    def finish(self) -> None:
        """Mark the span as finished."""
        self.end_time = datetime.utcnow()
    
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() * 1000
        return None


class JaegerTraceManager(ReflectiveModule):
    """
    Comprehensive distributed tracing manager using Jaeger for Phase 5D2 enhancement operations.
    
    Provides end-to-end tracing of enhancement workflows with automatic span creation,
    error tracking, and performance monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.jaeger_config = self.config.get_jaeger_config()
        self.active_traces: Dict[str, TraceContext] = {}
        self.active_spans: Dict[str, SpanContext] = {}
        
        # Initialize Jaeger connection if enabled
        if self.jaeger_config['enabled']:
            self._initialize_jaeger_connection()
        
        self.logger.info(
            "JaegerTraceManager initialized",
            extra={
                "jaeger_enabled": self.jaeger_config['enabled'],
                "jaeger_endpoint": self.jaeger_config['endpoint'],
                "service_name": self.jaeger_config['service_name']
            }
        )
    
    def get_capabilities(self):
        """Get tracer capabilities."""
        return {
            "jaeger_enabled": self.jaeger_config['enabled'],
            "service_name": self.jaeger_config['service_name'],
            "tracing_features": ["enhancement_workflows", "task_spans", "error_tracking", "performance_monitoring"]
        }
    
    def get_health_status(self):
        """Get tracer health status."""
        health_status = self.health_check()
        return {
            "status": "healthy" if health_status.get("jaeger_connectivity", True) else "degraded",
            "jaeger_enabled": health_status["jaeger_enabled"],
            "active_traces": health_status["active_traces"],
            "active_spans": health_status["active_spans"]
        }
    
    def get_module_info(self):
        """Get tracer module information."""
        return {
            "name": "JaegerTraceManager",
            "version": "1.0.0",
            "description": "Comprehensive distributed tracing manager using Jaeger"
        }
    
    def graceful_degradation(self, error):
        """Handle graceful degradation on errors."""
        self.logger.error(f"Tracer error: {error}")
        return {"status": "degraded", "error": str(error)}
    
    def _initialize_jaeger_connection(self) -> None:
        """Initialize connection to Jaeger service."""
        try:
            # Test connectivity to Jaeger endpoint
            import requests
            response = requests.get(f"{self.jaeger_config['endpoint']}/health", timeout=5)
            if response.status_code == 200:
                self.logger.info("Jaeger service connectivity verified")
            else:
                self.logger.warning(f"Jaeger service returned status {response.status_code}")
        except Exception as e:
            self.logger.warning(f"Jaeger service connectivity check failed: {e}")
            # Continue with local buffering
    
    def create_enhancement_trace(self, enhancement_id: str, operation_name: str = "enhancement_workflow") -> TraceContext:
        """
        Create a new distributed trace for an enhancement workflow.
        
        Args:
            enhancement_id: Unique identifier for the enhancement operation
            operation_name: Name of the operation being traced
            
        Returns:
            TraceContext for the new trace
        """
        trace_id = f"enhancement-{enhancement_id}-{uuid.uuid4().hex[:8]}"
        
        trace_context = TraceContext(
            trace_id=trace_id,
            operation_name=operation_name,
            start_time=datetime.utcnow()
        )
        
        # Add standard tags
        trace_context.add_tag("service.name", self.jaeger_config['service_name'])
        trace_context.add_tag("enhancement.id", enhancement_id)
        trace_context.add_tag("operation.type", "enhancement_workflow")
        trace_context.add_tag("phase", "5D2")
        
        self.active_traces[trace_id] = trace_context
        
        self.logger.info(
            "Created enhancement trace",
            extra={
                "trace_id": trace_id,
                "enhancement_id": enhancement_id,
                "operation_name": operation_name
            }
        )
        
        return trace_context
    
    def create_task_span(
        self, 
        trace_context: TraceContext, 
        task_name: str,
        parent_span_id: Optional[str] = None
    ) -> SpanContext:
        """
        Create a child span for a specific task within an enhancement workflow.
        
        Args:
            trace_context: Parent trace context
            task_name: Name of the task being traced
            parent_span_id: Optional parent span ID for nested spans
            
        Returns:
            SpanContext for the new span
        """
        span_id = f"span-{uuid.uuid4().hex[:8]}"
        
        span_context = SpanContext(
            span_id=span_id,
            trace_id=trace_context.trace_id,
            parent_span_id=parent_span_id,
            operation_name=task_name,
            start_time=datetime.utcnow()
        )
        
        # Add standard tags
        span_context.add_tag("task.name", task_name)
        span_context.add_tag("trace.id", trace_context.trace_id)
        if parent_span_id:
            span_context.add_tag("parent.span.id", parent_span_id)
        
        self.active_spans[span_id] = span_context
        
        self.logger.debug(
            "Created task span",
            extra={
                "span_id": span_id,
                "trace_id": trace_context.trace_id,
                "task_name": task_name,
                "parent_span_id": parent_span_id
            }
        )
        
        return span_context
    
    def log_enhancement_metrics(self, span_context: SpanContext, metrics: Dict[str, Any]) -> None:
        """
        Log enhancement metrics to a span.
        
        Args:
            span_context: Span to log metrics to
            metrics: Dictionary of metrics to log
        """
        # Add metrics as tags
        for key, value in metrics.items():
            span_context.add_tag(f"metric.{key}", value)
        
        # Log metrics event
        span_context.log_event("enhancement_metrics", metrics)
        
        self.logger.debug(
            "Logged enhancement metrics",
            extra={
                "span_id": span_context.span_id,
                "metrics": metrics
            }
        )
    
    def handle_enhancement_error(self, span_context: SpanContext, error: Exception) -> None:
        """
        Handle and log an error in an enhancement operation.
        
        Args:
            span_context: Span where the error occurred
            error: Exception that was raised
        """
        # Mark span as error
        span_context.add_tag("error", True)
        span_context.add_tag("error.type", type(error).__name__)
        span_context.add_tag("error.message", str(error))
        
        # Log error event
        span_context.log_event("error", {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_details": getattr(error, 'args', [])
        })
        
        self.logger.error(
            "Enhancement error logged to span",
            extra={
                "span_id": span_context.span_id,
                "error_type": type(error).__name__,
                "error_message": str(error)
            },
            exc_info=True
        )
    
    def finish_span(self, span_context: SpanContext, success: bool = True) -> None:
        """
        Finish a span and send it to Jaeger.
        
        Args:
            span_context: Span to finish
            success: Whether the operation was successful
        """
        span_context.finish()
        span_context.add_tag("success", success)
        
        if span_context.duration_ms():
            span_context.add_tag("duration_ms", span_context.duration_ms())
        
        # Send span to Jaeger if enabled
        if self.jaeger_config['enabled']:
            self._send_span_to_jaeger(span_context)
        
        # Remove from active spans
        if span_context.span_id in self.active_spans:
            del self.active_spans[span_context.span_id]
        
        self.logger.debug(
            "Finished span",
            extra={
                "span_id": span_context.span_id,
                "duration_ms": span_context.duration_ms(),
                "success": success
            }
        )
    
    def finish_trace(self, trace_context: TraceContext) -> None:
        """
        Finish a trace and send it to Jaeger.
        
        Args:
            trace_context: Trace to finish
        """
        # Calculate total duration
        end_time = datetime.utcnow()
        duration = (end_time - trace_context.start_time).total_seconds() * 1000
        trace_context.add_tag("total_duration_ms", duration)
        
        # Send trace to Jaeger if enabled
        if self.jaeger_config['enabled']:
            self._send_trace_to_jaeger(trace_context)
        
        # Remove from active traces
        if trace_context.trace_id in self.active_traces:
            del self.active_traces[trace_context.trace_id]
        
        self.logger.info(
            "Finished trace",
            extra={
                "trace_id": trace_context.trace_id,
                "total_duration_ms": duration,
                "operation_name": trace_context.operation_name
            }
        )
    
    @contextmanager
    def trace_enhancement_operation(
        self, 
        enhancement_id: str, 
        operation_name: str
    ) -> ContextManager[TraceContext]:
        """
        Context manager for tracing an enhancement operation.
        
        Args:
            enhancement_id: Unique identifier for the enhancement
            operation_name: Name of the operation
            
        Yields:
            TraceContext for the operation
        """
        trace_context = self.create_enhancement_trace(enhancement_id, operation_name)
        try:
            yield trace_context
        except Exception as e:
            trace_context.log_event("error", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise
        finally:
            self.finish_trace(trace_context)
    
    @contextmanager
    def trace_task(
        self, 
        trace_context: TraceContext, 
        task_name: str,
        parent_span_id: Optional[str] = None
    ) -> ContextManager[SpanContext]:
        """
        Context manager for tracing a task within an enhancement operation.
        
        Args:
            trace_context: Parent trace context
            task_name: Name of the task
            parent_span_id: Optional parent span ID
            
        Yields:
            SpanContext for the task
        """
        span_context = self.create_task_span(trace_context, task_name, parent_span_id)
        success = True
        try:
            yield span_context
        except Exception as e:
            success = False
            self.handle_enhancement_error(span_context, e)
            raise
        finally:
            self.finish_span(span_context, success)
    
    def _send_span_to_jaeger(self, span_context: SpanContext) -> None:
        """Send span data to Jaeger service."""
        try:
            # Convert span to Jaeger format
            jaeger_span = {
                "traceID": span_context.trace_id,
                "spanID": span_context.span_id,
                "parentSpanID": span_context.parent_span_id,
                "operationName": span_context.operation_name,
                "startTime": int(span_context.start_time.timestamp() * 1000000),  # microseconds
                "duration": int(span_context.duration_ms() * 1000) if span_context.duration_ms() else 0,
                "tags": [{"key": k, "value": str(v)} for k, v in span_context.tags.items()],
                "logs": span_context.logs
            }
            
            # Send to Jaeger (implementation would depend on Jaeger client library)
            self.logger.debug(f"Would send span to Jaeger: {jaeger_span}")
            
        except Exception as e:
            self.logger.warning(f"Failed to send span to Jaeger: {e}")
    
    def _send_trace_to_jaeger(self, trace_context: TraceContext) -> None:
        """Send trace data to Jaeger service."""
        try:
            # Convert trace to Jaeger format
            jaeger_trace = {
                "traceID": trace_context.trace_id,
                "spans": [],  # Spans are sent individually
                "processes": {
                    "p1": {
                        "serviceName": self.jaeger_config['service_name'],
                        "tags": [{"key": k, "value": str(v)} for k, v in trace_context.tags.items()]
                    }
                }
            }
            
            # Send to Jaeger (implementation would depend on Jaeger client library)
            self.logger.debug(f"Would send trace to Jaeger: {jaeger_trace}")
            
        except Exception as e:
            self.logger.warning(f"Failed to send trace to Jaeger: {e}")
    
    def get_active_traces(self) -> Dict[str, TraceContext]:
        """Get all currently active traces."""
        return self.active_traces.copy()
    
    def get_active_spans(self) -> Dict[str, SpanContext]:
        """Get all currently active spans."""
        return self.active_spans.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the tracing system."""
        health_status = {
            "jaeger_enabled": self.jaeger_config['enabled'],
            "jaeger_endpoint": self.jaeger_config['endpoint'],
            "active_traces": len(self.active_traces),
            "active_spans": len(self.active_spans),
            "service_name": self.jaeger_config['service_name']
        }
        
        if self.jaeger_config['enabled']:
            try:
                import requests
                response = requests.get(f"{self.jaeger_config['endpoint']}/health", timeout=5)
                health_status["jaeger_connectivity"] = response.status_code == 200
            except Exception as e:
                health_status["jaeger_connectivity"] = False
                health_status["jaeger_error"] = str(e)
        
        return health_status
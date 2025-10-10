"""
Beast Mode Distributed Tracing with Jaeger
Provides OpenTelemetry integration for complete system visibility
"""

import os
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

logger = logging.getLogger(__name__)

class BeastModeTracer:
    """Beast Mode distributed tracing manager"""
    
    def __init__(self, service_name: str = "beast-mode", jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self.tracer = None
        self.initialized = False
        
        if TRACING_AVAILABLE:
            self._initialize_tracing()
        else:
            logger.warning("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger")
    
    def _initialize_tracing(self):
        """Initialize OpenTelemetry tracing with Jaeger"""
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": os.getenv("ENVIRONMENT", "development")
            })
            
            # Set up tracer provider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # Create Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.jaeger_endpoint,
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Auto-instrument common libraries
            RequestsInstrumentor().instrument()
            LoggingInstrumentor().instrument()
            
            self.initialized = True
            logger.info(f"🔍 Jaeger tracing initialized for service: {self.service_name}")
            logger.info(f"📊 Jaeger UI available at: http://localhost:16686")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            self.initialized = False
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application for tracing"""
        if TRACING_AVAILABLE and self.initialized:
            try:
                FastAPIInstrumentor.instrument_app(app)
                logger.info("🌐 FastAPI instrumented for distributed tracing")
            except Exception as e:
                logger.error(f"Failed to instrument FastAPI: {e}")
    
    @contextmanager
    def trace_operation(self, operation_name: str, **attributes):
        """Context manager for tracing operations"""
        if not self.initialized or not self.tracer:
            # Fallback to no-op context
            yield None
            return
        
        with self.tracer.start_as_current_span(operation_name) as span:
            try:
                # Add attributes to span
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
                
                yield span
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    
    def trace_observation_flow(self, observation: Dict[str, Any]) -> Optional[Any]:
        """Trace observation emission and delivery"""
        if not self.initialized:
            return None
        
        with self.trace_operation(
            "observation_emission",
            module=observation.get("module", "unknown"),
            event_type=observation.get("event_type", "unknown"),
            message=observation.get("message", "")[:100]  # Truncate long messages
        ) as span:
            if span:
                span.set_attribute("observation.correlation_id", observation.get("correlation_id", ""))
                span.set_attribute("observation.severity", observation.get("severity", ""))
            return span
    
    def trace_websocket_connection(self, client_id: str, action: str):
        """Trace WebSocket connection events"""
        if not self.initialized:
            return None
        
        with self.trace_operation(
            f"websocket_{action}",
            client_id=client_id,
            action=action
        ) as span:
            return span
    
    def trace_server_startup(self, component: str, port: int):
        """Trace server startup events"""
        if not self.initialized:
            return None
        
        with self.trace_operation(
            "server_startup",
            component=component,
            port=port
        ) as span:
            return span
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add an event to the current span"""
        if not self.initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})
    
    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID for correlation"""
        if not self.initialized:
            return None
        
        current_span = trace.get_current_span()
        if current_span:
            return format(current_span.get_span_context().trace_id, '032x')
        return None
    
    def is_available(self) -> bool:
        """Check if tracing is available and initialized"""
        return TRACING_AVAILABLE and self.initialized

# Global tracer instance
_global_tracer: Optional[BeastModeTracer] = None

def get_tracer(service_name: str = "beast-mode") -> BeastModeTracer:
    """Get or create global tracer instance"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = BeastModeTracer(service_name)
    return _global_tracer

def initialize_tracing(service_name: str = "beast-mode") -> BeastModeTracer:
    """Initialize global tracing"""
    global _global_tracer
    _global_tracer = BeastModeTracer(service_name)
    return _global_tracer
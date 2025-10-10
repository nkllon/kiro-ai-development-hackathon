"""
AI Memory Palace Tracing Integration

Provides robust distributed tracing with graceful OpenTelemetry fallback.
"""

import logging
from typing import Dict, Any, Optional, ContextManager, List
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.trace import Span
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    Span = None

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class NoOpSpan:
    """No-op span for when tracing is unavailable."""
    
    def set_attribute(self, key: str, value: Any) -> None:
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class NoOpTracer:
    """No-op tracer for when OpenTelemetry is unavailable."""
    
    def start_span(self, name: str, **kwargs) -> NoOpSpan:
        return NoOpSpan()


class TracingManager(ReflectiveModule):
    """Manages distributed tracing with graceful fallback."""
    
    def __init__(self):
        super().__init__()
        self.tracer = self._initialize_tracer()
        self.logger = logging.getLogger(__name__)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "TracingManager",
            "version": "1.0.0",
            "description": "AI Memory Palace Tracing Integration",
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "status": "healthy",
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
            "tracer_type": "opentelemetry" if OPENTELEMETRY_AVAILABLE else "no-op"
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return [
            "distributed_tracing",
            "graceful_fallback",
            "span_management",
            "correlation_ids",
            "error_handling"
        ]
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self.logger.warning(f"Tracing degradation: {error}")
        self.tracer = NoOpTracer()
        return {
            "degradation_applied": "no_op_tracer",
            "reason": str(error)
        }
    
    def _initialize_tracer(self):
        """Initialize OpenTelemetry tracer with no-op fallback."""
        if OPENTELEMETRY_AVAILABLE:
            try:
                return trace.get_tracer(__name__)
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenTelemetry tracer: {e}")
                return NoOpTracer()
        else:
            self.logger.info("OpenTelemetry not available, using no-op tracer")
            return NoOpTracer()
    
    @contextmanager
    def trace_context_operation(self, operation_name: str, **attributes) -> ContextManager:
        """Trace context operations with error handling."""
        try:
            span = self.tracer.start_span(operation_name)
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
            
            with span:
                yield span
                
        except Exception as e:
            # Log failure but continue without tracing (Req 11.3)
            self.logger.warning(f"Tracing operation failed: {e}")
            yield NoOpSpan()

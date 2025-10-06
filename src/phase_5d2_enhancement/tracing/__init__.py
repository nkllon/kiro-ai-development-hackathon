"""
Distributed tracing integration for Phase 5D2 Enhancement System
"""

from .jaeger_trace_manager import JaegerTraceManager, TraceContext, SpanContext

__all__ = ['JaegerTraceManager', 'TraceContext', 'SpanContext']
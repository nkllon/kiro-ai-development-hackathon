"""
🐺 Beastly Module - Enhanced ReflectiveModule with Distributed Tracing

The Beastly Module inherits from ReflectiveModule and adds:
- Jaeger distributed tracing integration
- Enhanced observation emission with trace correlation
- Advanced performance monitoring
- System topology discovery

Use this when you want the full Beast Mode observability experience.
Use ReflectiveModule when you want the basic systematic capabilities.
"""

from typing import Dict, Any, Optional
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

# Import tracing capabilities (graceful degradation)
try:
    from src.beast_mode.tracing.tracer import get_tracer
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

logger = logging.getLogger(__name__)


class BeastlyModule(ReflectiveModule):
    """🐺 Enhanced ReflectiveModule with distributed tracing superpowers"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize distributed tracing if available
        if TRACING_AVAILABLE:
            try:
                self._tracer = get_tracer(f"beast-mode-{self.__class__.__name__.lower()}")
                self._tracing_enabled = self._tracer.is_available()
                if self._tracing_enabled:
                    logger.info(f"🔍 Beastly Module tracing enabled for {self.__class__.__name__}")
                else:
                    logger.info(f"🐺 Beastly Module created (tracing unavailable) for {self.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Tracing initialization failed: {e}")
                self._tracer = None
                self._tracing_enabled = False
        else:
            self._tracer = None
            self._tracing_enabled = False
            logger.info(f"🐺 Beastly Module created (no tracing dependencies) for {self.__class__.__name__}")
    
    def emit_observation(self, message: str, event_type: str = "info", context: Optional[Dict[str, Any]] = None, emoji: Optional[str] = None):
        """
        🐺 Enhanced observation emission with distributed tracing
        
        This method emits observations with full tracing integration when available,
        gracefully degrading to standard observation emission when tracing is not available.
        """
        try:
            # Create observation event
            observation = {
                "timestamp": self._start_time.isoformat(),
                "module": getattr(self, 'module_id', self.__class__.__name__),
                "event_type": event_type,
                "message": message,
                "emoji": emoji or self._get_default_emoji(event_type),
                "severity": self._map_event_type_to_severity(event_type),
                "context": context or {},
                "correlation_id": self._correlation_id
            }
            
            # Add trace ID if tracing is available
            if self._tracing_enabled and self._tracer:
                trace_id = self._tracer.get_trace_id()
                if trace_id:
                    observation["trace_id"] = trace_id
            
            # Send with tracing if available
            if self._tracing_enabled and self._tracer:
                with self._tracer.trace_operation(
                    "beastly_observation_emission",
                    module=observation["module"],
                    event_type=event_type,
                    message=message[:100]  # Truncate for tracing
                ) as span:
                    if span:
                        span.set_attribute("observation.correlation_id", self._correlation_id)
                        span.set_attribute("observation.severity", observation["severity"])
                    
                    self._send_observation_to_observatory(observation)
            else:
                # No tracing, send normally
                self._send_observation_to_observatory(observation)
            
            # Log the observation
            log_level = self._get_log_level_for_event_type(event_type)
            self._logger.log(log_level, f"🐺 {message} {emoji or ''}")
            
        except Exception as e:
            self._logger.error(f"Failed to emit beastly observation: {e}")
    
    def trace_operation(self, operation_name: str, **attributes):
        """🐺 Enhanced operation tracing with Jaeger integration"""
        if self._tracing_enabled and self._tracer:
            return self._tracer.trace_operation(operation_name, **attributes)
        else:
            # Fall back to parent class tracing
            return super().trace_operation(operation_name, **attributes)
    
    def get_tracing_status(self) -> Dict[str, Any]:
        """Get current tracing status and capabilities"""
        return {
            "tracing_available": TRACING_AVAILABLE,
            "tracing_enabled": self._tracing_enabled,
            "tracer_initialized": self._tracer is not None,
            "trace_id": self._tracer.get_trace_id() if self._tracing_enabled and self._tracer else None,
            "service_name": f"beast-mode-{self.__class__.__name__.lower()}"
        }
    
    def emit_trace_event(self, event_name: str, attributes: Dict[str, Any] = None):
        """🐺 Emit a trace event for debugging and analysis"""
        if self._tracing_enabled and self._tracer:
            self._tracer.add_event(event_name, attributes or {})
        else:
            # Log as regular observation
            self.emit_observation(
                message=f"Trace event: {event_name}",
                event_type="info",
                context=attributes,
                emoji="🔍"
            )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Enhanced module info with tracing capabilities"""
        base_info = super().get_module_info()
        base_info.update({
            "beastly_powers": True,
            "tracing_status": self.get_tracing_status()
        })
        return base_info
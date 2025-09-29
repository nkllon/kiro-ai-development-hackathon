"""
Observatory Integration for AI Memory Palace.

Connects context operations with the existing Beast Mode Observatory system
for real-time monitoring, WebSocket broadcasts, and Prometheus metrics.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from ..core.reflective_module import ReflectiveModule
from .models import SessionContext, ContextEvent


class ContextObservatoryIntegration(ReflectiveModule):
    """Integration between AI Memory Palace and Observatory system"""
    
    def __init__(self):
        super().__init__()
        
        # Observatory integration metrics
        self._observations_emitted = 0
        self._context_broadcasts = 0
        self._websocket_messages = 0
        self._prometheus_updates = 0
        
        # Context state tracking for Observatory
        self._active_contexts = {}
        self._context_metrics = {
            "total_contexts": 0,
            "active_sessions": 0,
            "total_events": 0,
            "total_decisions": 0,
            "total_work_items": 0,
            "total_discoveries": 0
        }
        
        self.logger.info("🔭 ContextObservatoryIntegration initialized")
    
    def emit_context_observation(self, observation_type: str, data: Dict[str, Any], 
                               correlation_id: Optional[str] = None):
        """Emit context-specific observation to Observatory"""
        try:
            # Create observation with context-specific formatting
            observation = {
                "type": f"context.{observation_type}",
                "timestamp": datetime.now().isoformat(),
                "source": "ai_memory_palace",
                "correlation_id": correlation_id,
                "data": data,
                "metadata": {
                    "component": "context_system",
                    "version": "1.0.0",
                    "environment": "development"
                }
            }
            
            # Emit through ReflectiveModule's observation system
            self.emit_observation(observation)
            self._observations_emitted += 1
            
            # Log for debugging
            self.logger.debug(f"🔭 Observatory observation: {observation_type}")
            
        except Exception as e:
            self.logger.error(f"💥 Error emitting context observation: {e}")
    
    def broadcast_context_state_change(self, context: SessionContext, change_type: str, 
                                     details: Dict[str, Any]):
        """Broadcast context state changes via WebSocket"""
        try:
            # Create WebSocket broadcast message
            broadcast_data = {
                "type": "context_state_change",
                "change_type": change_type,
                "project_id": context.project_id,
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat(),
                "context_summary": context.get_summary(),
                "details": details
            }
            
            # Emit as observation (Observatory will handle WebSocket broadcast)
            self.emit_context_observation(
                "state_change_broadcast",
                broadcast_data,
                correlation_id=context.session_id
            )
            
            self._context_broadcasts += 1
            self._websocket_messages += 1
            
            self.logger.info(f"📡 Context state broadcast: {change_type} for {context.project_id}")
            
        except Exception as e:
            self.logger.error(f"💥 Error broadcasting context state: {e}")
    
    def update_context_metrics(self, context: SessionContext):
        """Update context metrics for Prometheus"""
        try:
            # Update internal metrics
            self._context_metrics.update({
                "total_contexts": len(self._active_contexts),
                "total_events": len(context.conversation_history),
                "total_decisions": len(context.decisions_made),
                "total_work_items": len(context.work_completed),
                "total_discoveries": len(context.system_discoveries)
            })
            
            # Emit metrics observation
            self.emit_context_observation(
                "metrics_update",
                {
                    "metrics": self._context_metrics,
                    "context_size_bytes": context.get_context_size(),
                    "project_id": context.project_id,
                    "session_id": context.session_id
                },
                correlation_id=context.session_id
            )
            
            self._prometheus_updates += 1
            
        except Exception as e:
            self.logger.error(f"💥 Error updating context metrics: {e}")
    
    def register_active_context(self, context: SessionContext):
        """Register context as active in Observatory"""
        try:
            self._active_contexts[context.session_id] = {
                "project_id": context.project_id,
                "session_id": context.session_id,
                "start_time": context.timestamp,
                "last_activity": datetime.now(),
                "context_size": context.get_context_size(),
                "event_count": len(context.conversation_history)
            }
            
            self._context_metrics["active_sessions"] = len(self._active_contexts)
            
            # Broadcast context registration
            self.broadcast_context_state_change(
                context,
                "context_registered",
                {
                    "registration_time": datetime.now().isoformat(),
                    "context_summary": context.get_summary()
                }
            )
            
            self.logger.info(f"📋 Context registered: {context.session_id}")
            
        except Exception as e:
            self.logger.error(f"💥 Error registering active context: {e}")
    
    def unregister_active_context(self, session_id: str):
        """Unregister context from Observatory"""
        try:
            if session_id in self._active_contexts:
                context_info = self._active_contexts.pop(session_id)
                self._context_metrics["active_sessions"] = len(self._active_contexts)
                
                # Emit unregistration observation
                self.emit_context_observation(
                    "context_unregistered",
                    {
                        "session_id": session_id,
                        "unregistration_time": datetime.now().isoformat(),
                        "session_duration_minutes": (datetime.now() - context_info["start_time"]).total_seconds() / 60
                    },
                    correlation_id=session_id
                )
                
                self.logger.info(f"📋 Context unregistered: {session_id}")
            
        except Exception as e:
            self.logger.error(f"💥 Error unregistering context: {e}")
    
    def emit_context_event_observation(self, event: ContextEvent, session_id: str):
        """Emit observation for context event"""
        try:
            # Create event observation
            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "session_id": session_id,
                "correlation_id": event.correlation_id,
                "timestamp": event.timestamp.isoformat(),
                "data_summary": self._summarize_event_data(event.data),
                "metadata": event.metadata.to_dict()
            }
            
            self.emit_context_observation(
                "event_captured",
                event_data,
                correlation_id=event.correlation_id
            )
            
            # Update activity for active context
            if session_id in self._active_contexts:
                self._active_contexts[session_id]["last_activity"] = datetime.now()
                self._active_contexts[session_id]["event_count"] += 1
            
        except Exception as e:
            self.logger.error(f"💥 Error emitting context event observation: {e}")
    
    def emit_context_operation_observation(self, operation: str, success: bool, 
                                         duration_ms: float, details: Dict[str, Any]):
        """Emit observation for context operations"""
        try:
            operation_data = {
                "operation": operation,
                "success": success,
                "duration_ms": duration_ms,
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
            
            self.emit_context_observation(
                "operation_completed",
                operation_data,
                correlation_id=details.get("correlation_id")
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error emitting operation observation: {e}")
    
    def emit_context_health_observation(self, health_data: Dict[str, Any]):
        """Emit context system health observation"""
        try:
            health_observation = {
                "health_status": health_data,
                "active_contexts": len(self._active_contexts),
                "system_metrics": self._context_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            self.emit_context_observation(
                "health_status",
                health_observation
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error emitting health observation: {e}")
    
    def create_context_dashboard_data(self) -> Dict[str, Any]:
        """Create dashboard data for Observatory UI"""
        try:
            dashboard_data = {
                "active_contexts": len(self._active_contexts),
                "total_observations": self._observations_emitted,
                "context_broadcasts": self._context_broadcasts,
                "websocket_messages": self._websocket_messages,
                "prometheus_updates": self._prometheus_updates,
                "context_metrics": self._context_metrics,
                "active_sessions": [
                    {
                        "session_id": session_id,
                        "project_id": info["project_id"],
                        "start_time": info["start_time"].isoformat(),
                        "last_activity": info["last_activity"].isoformat(),
                        "context_size_kb": info["context_size"] / 1024,
                        "event_count": info["event_count"]
                    }
                    for session_id, info in self._active_contexts.items()
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"💥 Error creating dashboard data: {e}")
            return {"error": str(e)}
    
    def emit_context_performance_metrics(self, metrics: Dict[str, Any]):
        """Emit performance metrics for context operations"""
        try:
            performance_data = {
                "performance_metrics": metrics,
                "timestamp": datetime.now().isoformat(),
                "measurement_window": "current"
            }
            
            self.emit_context_observation(
                "performance_metrics",
                performance_data
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error emitting performance metrics: {e}")
    
    def emit_context_analytics_event(self, analytics_type: str, data: Dict[str, Any]):
        """Emit analytics events for context usage patterns"""
        try:
            analytics_data = {
                "analytics_type": analytics_type,
                "analytics_data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            self.emit_context_observation(
                "analytics_event",
                analytics_data
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error emitting analytics event: {e}")
    
    def _summarize_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of event data for observations"""
        try:
            summary = {}
            
            # Summarize based on data content
            for key, value in event_data.items():
                if isinstance(value, str):
                    summary[key] = value[:100] + "..." if len(value) > 100 else value
                elif isinstance(value, list):
                    summary[f"{key}_count"] = len(value)
                    if value:
                        summary[f"{key}_sample"] = str(value[0])[:50]
                elif isinstance(value, dict):
                    summary[f"{key}_keys"] = list(value.keys())[:5]
                else:
                    summary[key] = str(value)
            
            return summary
            
        except Exception as e:
            return {"summary_error": str(e)}
    
    def get_observatory_integration_stats(self) -> Dict[str, Any]:
        """Get Observatory integration statistics"""
        return {
            "observations_emitted": self._observations_emitted,
            "context_broadcasts": self._context_broadcasts,
            "websocket_messages": self._websocket_messages,
            "prometheus_updates": self._prometheus_updates,
            "active_contexts": len(self._active_contexts),
            "context_metrics": self._context_metrics
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for Observatory integration"""
        try:
            # Test observation emission
            test_observation = {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.emit_context_observation("health_check", test_observation)
            
            return {
                "status": "healthy",
                "observations_emitted": self._observations_emitted,
                "active_contexts": len(self._active_contexts),
                "integration_functional": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "integration_functional": False
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        return {
            "context_observatory_observations_emitted_total": self._observations_emitted,
            "context_observatory_broadcasts_total": self._context_broadcasts,
            "context_observatory_websocket_messages_total": self._websocket_messages,
            "context_observatory_prometheus_updates_total": self._prometheus_updates,
            "context_observatory_active_contexts": len(self._active_contexts),
            "context_observatory_total_events": self._context_metrics["total_events"],
            "context_observatory_total_decisions": self._context_metrics["total_decisions"],
            "context_observatory_total_work_items": self._context_metrics["total_work_items"],
            "context_observatory_total_discoveries": self._context_metrics["total_discoveries"]
        }


# WebSocket message types for context events
class ContextWebSocketMessages:
    """WebSocket message types for context system"""
    
    @staticmethod
    def context_loaded(context: SessionContext) -> Dict[str, Any]:
        """WebSocket message for context loaded"""
        return {
            "type": "context_loaded",
            "project_id": context.project_id,
            "session_id": context.session_id,
            "summary": context.get_summary(),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def context_saved(context: SessionContext) -> Dict[str, Any]:
        """WebSocket message for context saved"""
        return {
            "type": "context_saved",
            "project_id": context.project_id,
            "session_id": context.session_id,
            "size_bytes": context.get_context_size(),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def event_captured(event: ContextEvent, session_id: str) -> Dict[str, Any]:
        """WebSocket message for event captured"""
        return {
            "type": "event_captured",
            "event_type": event.event_type.value,
            "event_id": event.event_id,
            "session_id": session_id,
            "correlation_id": event.correlation_id,
            "timestamp": event.timestamp.isoformat()
        }
    
    @staticmethod
    def context_validation_result(session_id: str, is_valid: bool, issues: List[str]) -> Dict[str, Any]:
        """WebSocket message for validation result"""
        return {
            "type": "context_validation_result",
            "session_id": session_id,
            "is_valid": is_valid,
            "issue_count": len(issues),
            "issues": issues[:5],  # First 5 issues
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def context_metrics_update(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """WebSocket message for metrics update"""
        return {
            "type": "context_metrics_update",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
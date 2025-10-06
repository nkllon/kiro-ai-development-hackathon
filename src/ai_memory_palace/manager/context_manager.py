"""
AI Memory Palace Context Manager

Main orchestrator for AI conversation context persistence.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..database.context_database import ContextDatabase
from ..tracing.tracing_manager import TracingManager
from ..models.context_models import SessionContext, ContextSummary, ProjectState


class ContextManager(ReflectiveModule):
    """Main orchestrator for AI conversation context persistence."""
    
    def __init__(self):
        super().__init__()
        self.database = ContextDatabase()
        self.tracing = TracingManager()
        self.logger = logging.getLogger(__name__)
        self.memory_only_mode = False
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "ContextManager",
            "version": "1.0.0",
            "description": "AI Memory Palace Context Manager",
            "memory_only_mode": self.memory_only_mode
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "status": "healthy" if not self.memory_only_mode else "degraded",
            "database_available": not self.memory_only_mode,
            "tracing_available": True
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return [
            "context_persistence",
            "session_management", 
            "context_validation",
            "performance_optimization",
            "graceful_degradation"
        ]
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self.logger.error(f"Graceful degradation triggered: {error}")
        
        if "database" in str(error).lower():
            self.memory_only_mode = True
            return {
                "degradation_applied": "memory_only_mode",
                "reason": str(error)
            }
        
        return {
            "degradation_applied": "none",
            "reason": str(error)
        }
    
    def load_session_context(self, project_path: str) -> Optional[SessionContext]:
        """Load session context with performance guarantees."""
        project_id = Path(project_path).name
        session_id = f"{project_id}_{datetime.now().strftime('%Y%m%d')}"
        
        with self.tracing.trace_context_operation(
            "context_load",
            project_id=project_id,
            session_id=session_id
        ) as span:
            try:
                # Load from database
                context_data = self.database.load_context(session_id)
                
                if context_data:
                    # Reconstruct SessionContext
                    context = SessionContext(
                        project_id=project_id,
                        session_id=session_id,
                        timestamp=datetime.fromisoformat(context_data.get('timestamp', datetime.now().isoformat())),
                        conversation_history=context_data.get('conversation_history', []),
                        project_state=self._deserialize_project_state(context_data.get('project_state')),
                        decisions_made=context_data.get('decisions_made', []),
                        work_completed=context_data.get('work_completed', []),
                        system_discoveries=context_data.get('system_discoveries', []),
                        spec_states=context_data.get('spec_states', {})
                    )
                    
                    span.set_attribute("context_loaded", True)
                    span.set_attribute("context_size", len(context.conversation_history))
                    
                    self.emit_observation({
                        "type": "context_loaded",
                        "project_id": project_id,
                        "session_id": session_id,
                        "context_size": len(context.conversation_history)
                    })
                    
                    return context
                else:
                    # Create new context
                    context = SessionContext(
                        project_id=project_id,
                        session_id=session_id,
                        timestamp=datetime.now(),
                        project_state=ProjectState(architecture_overview="New project")
                    )
                    
                    span.set_attribute("context_loaded", False)
                    span.set_attribute("new_context_created", True)
                    
                    return context
                    
            except Exception as e:
                self.logger.error(f"Failed to load context: {e}")
                span.set_attribute("error", str(e))
                
                # Graceful degradation - return empty context
                return SessionContext(
                    project_id=project_id,
                    session_id=session_id,
                    timestamp=datetime.now(),
                    project_state=ProjectState(architecture_overview="Recovery mode")
                )
    
    def save_context_event(self, context: SessionContext, event_data: Dict[str, Any]) -> bool:
        """Save context event with validation."""
        try:
            # Serialize context
            context_data = {
                'timestamp': context.timestamp.isoformat(),
                'conversation_history': context.conversation_history,
                'project_state': self._serialize_project_state(context.project_state),
                'decisions_made': context.decisions_made,
                'work_completed': context.work_completed,
                'system_discoveries': context.system_discoveries,
                'spec_states': context.spec_states
            }
            
            # Store in database
            success = self.database.store_context(
                context.session_id,
                context.project_id,
                context_data
            )
            
            if success:
                self.emit_observation({
                    "type": "context_saved",
                    "project_id": context.project_id,
                    "session_id": context.session_id
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")
            return False
    
    def _serialize_project_state(self, project_state: Optional[ProjectState]) -> Optional[Dict[str, Any]]:
        """Serialize project state for storage."""
        if not project_state:
            return None
        
        return {
            'architecture_overview': project_state.architecture_overview,
            'running_services': [
                {
                    'name': svc.name,
                    'host': svc.host,
                    'port': svc.port,
                    'health_status': svc.health_status,
                    'discovery_source': svc.discovery_source,
                    'last_seen': svc.last_seen.isoformat(),
                    'metadata': svc.metadata
                }
                for svc in project_state.running_services
            ],
            'active_specs': project_state.active_specs,
            'recent_changes': project_state.recent_changes,
            'health_status': project_state.health_status
        }
    
    def _deserialize_project_state(self, data: Optional[Dict[str, Any]]) -> Optional[ProjectState]:
        """Deserialize project state from storage."""
        if not data:
            return None
        
        from ..models.context_models import ServiceInfo
        
        return ProjectState(
            architecture_overview=data.get('architecture_overview', ''),
            running_services=[
                ServiceInfo(
                    name=svc['name'],
                    host=svc['host'],
                    port=svc['port'],
                    health_status=svc['health_status'],
                    discovery_source=svc['discovery_source'],
                    last_seen=datetime.fromisoformat(svc['last_seen']),
                    metadata=svc.get('metadata', {})
                )
                for svc in data.get('running_services', [])
            ],
            active_specs=data.get('active_specs', []),
            recent_changes=data.get('recent_changes', []),
            health_status=data.get('health_status', 'unknown')
        )
    
    def get_context_summary(self, project_id: str) -> Optional[ContextSummary]:
        """Get context summary for developer experience."""
        try:
            session_id = f"{project_id}_{datetime.now().strftime('%Y%m%d')}"
            context_data = self.database.load_context(session_id)
            
            if not context_data:
                return None
            
            return ContextSummary(
                project_id=project_id,
                last_session=datetime.fromisoformat(context_data['timestamp']),
                total_events=len(context_data.get('conversation_history', [])),
                recent_decisions=[d.get('summary', '') for d in context_data.get('decisions_made', [])[-5:]],
                active_specs=context_data.get('project_state', {}).get('active_specs', []),
                system_health=context_data.get('project_state', {}).get('health_status', 'unknown'),
                context_size_mb=len(str(context_data)) / (1024 * 1024)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get context summary: {e}")
            return None

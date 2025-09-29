"""
Context Registry for AI Memory Palace.

Manages context storage, retrieval, and versioning with integration to the
Beast Mode ReflectiveModule architecture for systematic observability.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from pathlib import Path

from src.beast_mode.core.beastly_module import BeastlyModule
from src.rm_ddd.core.unified_reflective_module import ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
from .models import SessionContext, ContextEvent
from .storage import ContextDatabase


class ContextRegistry(BeastlyModule):
    """Persistent storage and retrieval of conversation context"""
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        
        # Initialize database
        if db_path is None:
            db_path = ".kiro/context/context.db"
        
        self.db = ContextDatabase(db_path)
        self.current_project_id = self._detect_project_id()
        
        # Metrics
        self._contexts_stored = 0
        self._contexts_loaded = 0
        self._events_stored = 0
        
        self._logger.info(f"🏛️ ContextRegistry initialized with database: {db_path}")
        self._logger.info(f"📁 Current project ID: {self.current_project_id}")
    
    def store_context(self, context: SessionContext) -> bool:
        """Store session context with versioning"""
        try:
            # Emit observation for context storage
            self.emit_observation({
                "type": "context_storage_started",
                "project_id": context.project_id,
                "session_id": context.session_id,
                "context_size": context.get_context_size(),
                "timestamp": datetime.now().isoformat()
            })
            
            success = self.db.store_session_context(context)
            
            if success:
                self._contexts_stored += 1
                self._logger.info(f"✅ Stored context for session {context.session_id}")
                
                self.emit_observation({
                    "type": "context_stored",
                    "project_id": context.project_id,
                    "session_id": context.session_id,
                    "context_size": context.get_context_size(),
                    "success": True
                })
            else:
                self._logger.error(f"❌ Failed to store context for session {context.session_id}")
                
                self.emit_observation({
                    "type": "context_storage_failed",
                    "project_id": context.project_id,
                    "session_id": context.session_id,
                    "success": False
                })
            
            return success
            
        except Exception as e:
            self._logger.error(f"💥 Error storing context: {e}")
            self.emit_observation({
                "type": "context_storage_error",
                "error": str(e),
                "project_id": context.project_id if context else "unknown"
            })
            return False
    
    def load_context(self, project_id: Optional[str] = None, session_id: Optional[str] = None) -> Optional[SessionContext]:
        """Load context for project or specific session"""
        try:
            if project_id is None:
                project_id = self.current_project_id
            
            # Emit observation for context loading
            self.emit_observation({
                "type": "context_loading_started",
                "project_id": project_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
            
            context = self.db.load_session_context(project_id, session_id)
            
            if context:
                self._contexts_loaded += 1
                self._logger.info(f"✅ Loaded context for project {project_id}")
                
                self.emit_observation({
                    "type": "context_loaded",
                    "project_id": project_id,
                    "session_id": context.session_id,
                    "context_size": context.get_context_size(),
                    "conversation_events": len(context.conversation_history),
                    "decisions": len(context.decisions_made),
                    "work_items": len(context.work_completed),
                    "discoveries": len(context.system_discoveries),
                    "success": True
                })
            else:
                self._logger.info(f"📭 No context found for project {project_id}")
                
                self.emit_observation({
                    "type": "context_not_found",
                    "project_id": project_id,
                    "session_id": session_id,
                    "success": False
                })
            
            return context
            
        except Exception as e:
            self._logger.error(f"💥 Error loading context: {e}")
            self.emit_observation({
                "type": "context_loading_error",
                "error": str(e),
                "project_id": project_id or "unknown"
            })
            return None
    
    def store_event(self, event: ContextEvent, session_id: str) -> bool:
        """Store individual context event"""
        try:
            success = self.db.store_context_event(event, session_id)
            
            if success:
                self._events_stored += 1
                self._logger.debug(f"📝 Stored event {event.event_type.value} for session {session_id}")
                
                self.emit_observation({
                    "type": "context_event_stored",
                    "event_type": event.event_type.value,
                    "session_id": session_id,
                    "correlation_id": event.correlation_id,
                    "success": True
                })
            else:
                self._logger.error(f"❌ Failed to store event for session {session_id}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"💥 Error storing context event: {e}")
            return False
    
    def list_context_versions(self, session_id: str) -> List[Dict[str, Any]]:
        """List all versions of a context"""
        try:
            versions = self.db.get_context_versions(session_id)
            
            self.emit_observation({
                "type": "context_versions_listed",
                "session_id": session_id,
                "version_count": len(versions)
            })
            
            return versions
            
        except Exception as e:
            self._logger.error(f"💥 Error listing context versions: {e}")
            return []
    
    def list_project_sessions(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sessions for a project"""
        try:
            if project_id is None:
                project_id = self.current_project_id
            
            sessions = self.db.list_project_sessions(project_id)
            
            self.emit_observation({
                "type": "project_sessions_listed",
                "project_id": project_id,
                "session_count": len(sessions)
            })
            
            return sessions
            
        except Exception as e:
            self._logger.error(f"💥 Error listing project sessions: {e}")
            return []
    
    def prune_old_contexts(self, retention_days: int = 90) -> int:
        """Remove old contexts based on retention policy"""
        try:
            self.emit_observation({
                "type": "context_pruning_started",
                "retention_days": retention_days,
                "timestamp": datetime.now().isoformat()
            })
            
            deleted_count = self.db.cleanup_old_contexts(retention_days)
            
            self._logger.info(f"🧹 Pruned {deleted_count} old context records")
            
            self.emit_observation({
                "type": "context_pruning_completed",
                "deleted_count": deleted_count,
                "retention_days": retention_days
            })
            
            return deleted_count
            
        except Exception as e:
            self._logger.error(f"💥 Error pruning old contexts: {e}")
            return 0
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            db_stats = self.db.get_database_stats()
            
            stats = {
                "contexts_stored": self._contexts_stored,
                "contexts_loaded": self._contexts_loaded,
                "events_stored": self._events_stored,
                "current_project_id": self.current_project_id,
                **db_stats
            }
            
            return stats
            
        except Exception as e:
            self._logger.error(f"💥 Error getting registry stats: {e}")
            return {}
    
    def _detect_project_id(self) -> str:
        """Detect current project ID from environment"""
        # Try to get project ID from current directory
        cwd = Path.cwd()
        
        # Look for .kiro directory to identify project root
        current = cwd
        while current != current.parent:
            if (current / ".kiro").exists():
                return current.name
            current = current.parent
        
        # Fallback to current directory name
        return cwd.name
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ContextRegistry"""
        try:
            # Test database connection
            stats = self.db.get_database_stats()
            
            return {
                "status": "healthy",
                "database_accessible": True,
                "schema_version": stats.get("schema_version", 0),
                "total_contexts": stats.get("session_contexts_count", 0),
                "total_events": stats.get("context_events_count", 0),
                "database_size_mb": round(stats.get("database_size_bytes", 0) / 1024 / 1024, 2)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_accessible": False
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        stats = self.get_registry_stats()
        
        return {
            "context_registry_contexts_stored_total": self._contexts_stored,
            "context_registry_contexts_loaded_total": self._contexts_loaded,
            "context_registry_events_stored_total": self._events_stored,
            "context_registry_database_size_bytes": stats.get("database_size_bytes", 0),
            "context_registry_total_contexts": stats.get("session_contexts_count", 0),
            "context_registry_total_events": stats.get("context_events_count", 0)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": "ai_memory_palace_context_registry",
            "module_name": "ContextRegistry", 
            "version": "1.0.0",
            "description": "Persistent storage and retrieval of conversation context",
            "contexts_stored": self._contexts_stored,
            "contexts_loaded": self._contexts_loaded,
            "events_stored": self._events_stored
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        # Check database health
        try:
            stats = self.get_registry_stats()
            if stats.get("database_size_bytes", 0) > 0:
                status = ModuleStatus.HEALTHY
                health_score = 0.95
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = ["Database appears empty"]
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.3
            issues = [f"Database error: {str(e)}"]
            
        return ModuleHealth(
            module_id="ai_memory_palace_context_registry",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        try:
            # Test database connectivity
            self.get_registry_stats()
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=[
                    ModuleCapability.CORE_FUNCTIONALITY,
                    ModuleCapability.DATA_PROCESSING,
                    ModuleCapability.VALIDATION
                ]
            )
            
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[
                    ModuleCapability.DATA_PROCESSING,
                    ModuleCapability.VALIDATION
                ],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                error_message=str(e)
            )
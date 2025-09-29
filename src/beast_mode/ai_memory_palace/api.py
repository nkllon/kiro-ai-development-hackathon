"""
REST API for AI Memory Palace.

Provides HTTP endpoints for context operations, management, analytics,
and integration with external systems.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import uuid
import logging
from dataclasses import asdict

try:
    from fastapi import FastAPI, HTTPException, Depends, Query, Path as PathParam, Body
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Fallback for when FastAPI is not available
    class BaseModel:
        pass

from ..core.reflective_module import ReflectiveModule
from .context_manager import ContextManager
from .context_registry import ContextRegistry
from .multi_project_manager import MultiProjectContextManager
from .backup_recovery import ContextBackupManager, BackupType
from .analytics import ContextAnalyzer, ContextOptimizer
from .spec_integration import SpecWorkflowIntegrator
from .developer_tools import ContextInspector
from .models import SessionContext, ContextEventType


# Pydantic models for API requests/responses
class ContextEventRequest(BaseModel):
    event_type: str = Field(..., description="Type of context event")
    content: str = Field(..., description="Event content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class SessionStartRequest(BaseModel):
    project_id: str = Field(..., description="Project identifier")


class TaskUpdateRequest(BaseModel):
    spec_name: str = Field(..., description="Specification name")
    task_number: str = Field(..., description="Task number (e.g., 1.1, 2.3)")
    status: str = Field(..., description="New task status")


class BackupRequest(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    backup_type: str = Field(default="manual", description="Type of backup")


class OptimizationRequest(BaseModel):
    recommendation_id: str = Field(..., description="Optimization recommendation ID")


class ContextResponse(BaseModel):
    project_id: str
    session_id: str
    timestamp: str
    size_bytes: int
    conversation_events: int
    decisions_made: int
    work_completed: int


class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ContextAPI(ReflectiveModule):
    """REST API for AI Memory Palace context operations"""
    
    def __init__(self, context_manager: ContextManager, 
                 multi_project_manager: MultiProjectContextManager,
                 backup_manager: ContextBackupManager,
                 analyzer: ContextAnalyzer,
                 optimizer: ContextOptimizer,
                 spec_integrator: SpecWorkflowIntegrator,
                 inspector: ContextInspector):
        super().__init__()
        
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for the REST API. Install with: pip install fastapi uvicorn")
        
        self.context_manager = context_manager
        self.multi_project_manager = multi_project_manager
        self.backup_manager = backup_manager
        self.analyzer = analyzer
        self.optimizer = optimizer
        self.spec_integrator = spec_integrator
        self.inspector = inspector
        
        # API configuration
        self.app = FastAPI(
            title="AI Memory Palace API",
            description="REST API for AI Memory Palace context management",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Security (optional)
        self.security = HTTPBearer(auto_error=False)
        
        # API metrics
        self._api_requests = 0
        self._api_errors = 0
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("🌐 ContextAPI initialized")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        # Health and status endpoints
        @self.app.get("/health", response_model=Dict[str, Any])
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "components": {
                    "context_manager": "healthy",
                    "backup_manager": "healthy",
                    "analytics": "healthy"
                }
            }
        
        @self.app.get("/status", response_model=Dict[str, Any])
        async def get_status():
            """Get system status"""
            self._api_requests += 1
            
            try:
                status = {
                    "api_requests": self._api_requests,
                    "api_errors": self._api_errors,
                    "current_session": self.context_manager.current_session_id,
                    "current_project": self.context_manager.current_project_id,
                    "multi_project_stats": self.multi_project_manager.get_multi_project_statistics(),
                    "backup_stats": self.backup_manager.get_backup_statistics(),
                    "timestamp": datetime.now().isoformat()
                }
                
                return APIResponse(success=True, data=status).dict()
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Session management endpoints
        @self.app.post("/sessions/start", response_model=APIResponse)
        async def start_session(request: SessionStartRequest):
            """Start a new context session"""
            self._api_requests += 1
            
            try:
                session_id = self.context_manager.start_session(request.project_id)
                
                if session_id:
                    return APIResponse(
                        success=True,
                        message="Session started successfully",
                        data={
                            "session_id": session_id,
                            "project_id": request.project_id
                        }
                    )
                else:
                    raise HTTPException(status_code=400, detail="Failed to start session")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/sessions/end", response_model=APIResponse)
        async def end_session():
            """End the current session"""
            self._api_requests += 1
            
            try:
                success = self.context_manager.end_session()
                
                return APIResponse(
                    success=success,
                    message="Session ended successfully" if success else "Failed to end session"
                )
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/sessions/current", response_model=APIResponse)
        async def get_current_session():
            """Get current session information"""
            self._api_requests += 1
            
            try:
                context = self.context_manager.get_current_context()
                
                if context:
                    context_data = {
                        "project_id": context.project_id,
                        "session_id": context.session_id,
                        "timestamp": context.timestamp.isoformat(),
                        "size_bytes": context.get_context_size(),
                        "conversation_events": len(context.conversation_history),
                        "decisions_made": len(context.decisions_made),
                        "work_completed": len(context.work_completed)
                    }
                    
                    return APIResponse(success=True, data=context_data)
                else:
                    return APIResponse(success=False, message="No active session")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Context operations endpoints
        @self.app.post("/context/events", response_model=APIResponse)
        async def add_context_event(request: ContextEventRequest):
            """Add a context event"""
            self._api_requests += 1
            
            try:
                # Convert string event type to enum
                try:
                    event_type = ContextEventType(request.event_type.upper())
                except ValueError:
                    event_type = ContextEventType.USER_MESSAGE  # Default fallback
                
                event_id = self.context_manager.add_conversation_event(
                    event_type=event_type,
                    content=request.content,
                    metadata=request.metadata
                )
                
                if event_id:
                    return APIResponse(
                        success=True,
                        message="Event added successfully",
                        data={"event_id": event_id}
                    )
                else:
                    raise HTTPException(status_code=400, detail="Failed to add event")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/context/{project_id}", response_model=APIResponse)
        async def get_context(project_id: str = PathParam(..., description="Project ID")):
            """Get context for a project"""
            self._api_requests += 1
            
            try:
                context = self.multi_project_manager.get_project_context(project_id)
                
                if context:
                    # Convert context to serializable format
                    context_data = {
                        "project_id": context.project_id,
                        "session_id": context.session_id,
                        "timestamp": context.timestamp.isoformat(),
                        "conversation_history": [
                            {
                                "event_id": event.event_id,
                                "event_type": event.event_type.value,
                                "timestamp": event.timestamp.isoformat(),
                                "content": event.content[:200] + "..." if len(event.content) > 200 else event.content,
                                "metadata": event.metadata
                            }
                            for event in context.conversation_history[-10:]  # Last 10 events
                        ],
                        "decisions_made": len(context.decisions_made),
                        "work_completed": len(context.work_completed),
                        "size_bytes": context.get_context_size()
                    }
                    
                    return APIResponse(success=True, data=context_data)
                else:
                    return APIResponse(success=False, message="Context not found")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/context/{project_id}/summary", response_model=APIResponse)
        async def get_context_summary(project_id: str = PathParam(..., description="Project ID")):
            """Get context summary for a project"""
            self._api_requests += 1
            
            try:
                # Switch to project context
                self.multi_project_manager.switch_to_project(project_id)
                
                summary = self.context_manager.get_context_summary()
                
                if summary:
                    return APIResponse(success=True, data=summary)
                else:
                    return APIResponse(success=False, message="No context summary available")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Project management endpoints
        @self.app.get("/projects", response_model=APIResponse)
        async def list_projects():
            """List all projects"""
            self._api_requests += 1
            
            try:
                projects = self.multi_project_manager.list_projects()
                return APIResponse(success=True, data={"projects": projects})
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/projects/{project_id}/switch", response_model=APIResponse)
        async def switch_project(project_id: str = PathParam(..., description="Project ID")):
            """Switch to a different project"""
            self._api_requests += 1
            
            try:
                success = self.multi_project_manager.switch_to_project(project_id)
                
                if success:
                    return APIResponse(
                        success=True,
                        message=f"Switched to project: {project_id}",
                        data={"current_project_id": project_id}
                    )
                else:
                    raise HTTPException(status_code=404, detail="Project not found")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Backup and recovery endpoints
        @self.app.post("/backups", response_model=APIResponse)
        async def create_backup(request: BackupRequest):
            """Create a context backup"""
            self._api_requests += 1
            
            try:
                backup_type = BackupType(request.backup_type.upper())
                metadata = self.backup_manager.create_backup(request.project_id, backup_type=backup_type)
                
                if metadata:
                    return APIResponse(
                        success=True,
                        message="Backup created successfully",
                        data=metadata.to_dict()
                    )
                else:
                    raise HTTPException(status_code=400, detail="Failed to create backup")
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/backups/{project_id}", response_model=APIResponse)
        async def list_backups(project_id: str = PathParam(..., description="Project ID"),
                              limit: int = Query(10, description="Maximum number of backups to return")):
            """List backups for a project"""
            self._api_requests += 1
            
            try:
                backups = self.backup_manager.list_backups(project_id, limit)
                backup_data = [backup.to_dict() for backup in backups]
                
                return APIResponse(success=True, data={"backups": backup_data})
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/backups/{backup_id}/restore", response_model=APIResponse)
        async def restore_backup(backup_id: str = PathParam(..., description="Backup ID")):
            """Restore from a backup"""
            self._api_requests += 1
            
            try:
                success = self.backup_manager.restore_context(backup_id)
                
                return APIResponse(
                    success=success,
                    message="Backup restored successfully" if success else "Failed to restore backup"
                )
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Analytics endpoints
        @self.app.get("/analytics/usage", response_model=APIResponse)
        async def get_usage_analytics(project_id: Optional[str] = Query(None, description="Project ID")):
            """Get usage analytics"""
            self._api_requests += 1
            
            try:
                analysis = self.analyzer.analyze_context_usage(project_id)
                return APIResponse(success=True, data=analysis)
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/analytics/dashboard", response_model=APIResponse)
        async def get_analytics_dashboard(
            project_id: Optional[str] = Query(None, description="Project ID"),
            days: int = Query(7, description="Number of days to analyze")
        ):
            """Get analytics dashboard"""
            self._api_requests += 1
            
            try:
                dashboard = self.analyzer.get_analytics_dashboard(project_id, days)
                return APIResponse(success=True, data=dashboard)
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/optimization/recommendations", response_model=APIResponse)
        async def get_optimization_recommendations(project_id: Optional[str] = Query(None, description="Project ID")):
            """Get optimization recommendations"""
            self._api_requests += 1
            
            try:
                recommendations = self.optimizer.generate_optimization_recommendations(project_id)
                recommendation_data = [rec.to_dict() for rec in recommendations]
                
                return APIResponse(success=True, data={"recommendations": recommendation_data})
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/optimization/apply", response_model=APIResponse)
        async def apply_optimization(request: OptimizationRequest):
            """Apply an optimization recommendation"""
            self._api_requests += 1
            
            try:
                # This would need to look up the recommendation by ID
                # Simplified implementation for now
                return APIResponse(
                    success=False,
                    message="Optimization application not yet implemented"
                )
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Spec integration endpoints
        @self.app.post("/specs/{spec_name}/tasks/{task_number}", response_model=APIResponse)
        async def update_task_status(
            spec_name: str = PathParam(..., description="Specification name"),
            task_number: str = PathParam(..., description="Task number"),
            request: TaskUpdateRequest = Body(...)
        ):
            """Update task status in spec"""
            self._api_requests += 1
            
            try:
                from .spec_integration import TaskStatus
                
                task_status = TaskStatus(request.status.upper())
                project_id = f"spec_{spec_name}"
                
                success = self.spec_integrator.update_task_status(
                    spec_name, task_number, task_status, project_id
                )
                
                return APIResponse(
                    success=success,
                    message="Task status updated successfully" if success else "Failed to update task status"
                )
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/specs/recommendations", response_model=APIResponse)
        async def get_spec_recommendations(project_id: Optional[str] = Query(None, description="Project ID")):
            """Get spec recommendations"""
            self._api_requests += 1
            
            try:
                recommendations = self.spec_integrator.get_spec_recommendations(project_id or "current")
                return APIResponse(success=True, data={"recommendations": recommendations})
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # Developer tools endpoints
        @self.app.get("/debug/inspect/{project_id}", response_model=APIResponse)
        async def inspect_context(project_id: str = PathParam(..., description="Project ID")):
            """Inspect context for debugging"""
            self._api_requests += 1
            
            try:
                inspection = self.inspector.inspect_context(project_id)
                return APIResponse(success=True, data=inspection)
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/debug/search/{project_id}", response_model=APIResponse)
        async def search_context(
            project_id: str = PathParam(..., description="Project ID"),
            query: str = Query(..., description="Search query"),
            content_types: Optional[str] = Query(None, description="Comma-separated content types")
        ):
            """Search context content"""
            self._api_requests += 1
            
            try:
                content_type_list = content_types.split(",") if content_types else None
                results = self.inspector.search_context_content(project_id, query, content_type_list)
                
                return APIResponse(success=True, data=results)
                
            except Exception as e:
                self._api_errors += 1
                raise HTTPException(status_code=500, detail=str(e))
        
        # WebSocket endpoint for real-time updates (if needed)
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            
            try:
                while True:
                    # Send periodic status updates
                    status = {
                        "type": "status_update",
                        "timestamp": datetime.now().isoformat(),
                        "current_session": self.context_manager.current_session_id,
                        "api_requests": self._api_requests
                    }
                    
                    await websocket.send_json(status)
                    await asyncio.sleep(30)  # Send updates every 30 seconds
                    
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
            finally:
                await websocket.close()
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000, 
                   reload: bool = False, log_level: str = "info"):
        """Run the API server"""
        try:
            self.logger.info(f"🚀 Starting AI Memory Palace API server on {host}:{port}")
            
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
                access_log=True
            )
            
        except Exception as e:
            self.logger.error(f"💥 API server error: {e}")
            raise
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI specification"""
        return self.app.openapi()


class ContextCLITools(ReflectiveModule):
    """Comprehensive CLI tools for AI Memory Palace"""
    
    def __init__(self, context_manager: ContextManager,
                 multi_project_manager: MultiProjectContextManager,
                 backup_manager: ContextBackupManager,
                 analyzer: ContextAnalyzer,
                 optimizer: ContextOptimizer,
                 spec_integrator: SpecWorkflowIntegrator,
                 inspector: ContextInspector):
        super().__init__()
        
        self.context_manager = context_manager
        self.multi_project_manager = multi_project_manager
        self.backup_manager = backup_manager
        self.analyzer = analyzer
        self.optimizer = optimizer
        self.spec_integrator = spec_integrator
        self.inspector = inspector
        
        self.logger.info("🛠️ ContextCLITools initialized")
    
    # Session management
    def start_session(self, project_id: str) -> Dict[str, Any]:
        """Start a new context session"""
        session_id = self.context_manager.start_session(project_id)
        return {
            "success": session_id is not None,
            "session_id": session_id,
            "project_id": project_id
        }
    
    def end_session(self) -> Dict[str, Any]:
        """End current session"""
        success = self.context_manager.end_session()
        return {"success": success}
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        context = self.context_manager.get_current_context()
        if context:
            return {
                "active": True,
                "project_id": context.project_id,
                "session_id": context.session_id,
                "size_mb": context.get_context_size() / 1024 / 1024,
                "events": len(context.conversation_history)
            }
        else:
            return {"active": False}
    
    # Context operations
    def add_event(self, event_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add context event"""
        try:
            event_type_enum = ContextEventType(event_type.upper())
            event_id = self.context_manager.add_conversation_event(event_type_enum, content, metadata)
            return {"success": event_id is not None, "event_id": event_id}
        except ValueError:
            return {"success": False, "error": f"Invalid event type: {event_type}"}
    
    def search_context(self, project_id: str, query: str, content_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search context content"""
        return self.inspector.search_context_content(project_id, query, content_types)
    
    def inspect_context(self, project_id: str) -> Dict[str, Any]:
        """Inspect context for debugging"""
        return self.inspector.inspect_context(project_id)
    
    # Project management
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return self.multi_project_manager.list_projects()
    
    def switch_project(self, project_id: str) -> Dict[str, Any]:
        """Switch to different project"""
        success = self.multi_project_manager.switch_to_project(project_id)
        return {"success": success is not None, "project_id": project_id}
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get multi-project statistics"""
        return self.multi_project_manager.get_multi_project_statistics()
    
    # Backup operations
    def create_backup(self, project_id: str, backup_type: str = "manual") -> Dict[str, Any]:
        """Create context backup"""
        try:
            backup_type_enum = BackupType(backup_type.upper())
            metadata = self.backup_manager.create_backup(project_id, backup_type=backup_type_enum)
            
            if metadata:
                return {
                    "success": True,
                    "backup_id": metadata.backup_id,
                    "size_mb": metadata.size_bytes / 1024 / 1024
                }
            else:
                return {"success": False, "error": "Backup creation failed"}
        except ValueError:
            return {"success": False, "error": f"Invalid backup type: {backup_type}"}
    
    def list_backups(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List backups for project"""
        backups = self.backup_manager.list_backups(project_id, limit)
        return [backup.to_dict() for backup in backups]
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup"""
        success = self.backup_manager.restore_context(backup_id)
        return {"success": success}
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        return self.backup_manager.get_backup_statistics()
    
    # Analytics operations
    def analyze_usage(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze context usage"""
        return self.analyzer.analyze_context_usage(project_id)
    
    def get_dashboard(self, project_id: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get analytics dashboard"""
        return self.analyzer.get_analytics_dashboard(project_id, days)
    
    def get_optimization_recommendations(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        recommendations = self.optimizer.generate_optimization_recommendations(project_id)
        return [rec.to_dict() for rec in recommendations]
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics statistics"""
        return {
            "analyses_performed": self.analyzer._analyses_performed,
            "patterns_detected": self.analyzer._patterns_detected,
            "metrics_collected": self.analyzer._metrics_collected,
            "optimizations_performed": self.optimizer._optimizations_performed,
            "space_saved_mb": self.optimizer._space_saved_mb
        }
    
    # Spec integration operations
    def update_task_status(self, spec_name: str, task_number: str, status: str, project_id: str) -> Dict[str, Any]:
        """Update task status"""
        try:
            from .spec_integration import TaskStatus
            task_status = TaskStatus(status.upper())
            success = self.spec_integrator.update_task_status(spec_name, task_number, task_status, project_id)
            return {"success": success}
        except ValueError:
            return {"success": False, "error": f"Invalid task status: {status}"}
    
    def get_spec_recommendations(self, project_id: str) -> List[Dict[str, Any]]:
        """Get spec recommendations"""
        return self.spec_integrator.get_spec_recommendations(project_id)
    
    def get_spec_navigation(self, project_id: str) -> Dict[str, Any]:
        """Get spec navigation info"""
        return self.spec_integrator.get_spec_navigation_info(project_id)
    
    def get_spec_stats(self) -> Dict[str, Any]:
        """Get spec integration statistics"""
        return self.spec_integrator.get_integration_statistics()
    
    # System operations
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            "context_manager": self.context_manager.health_check(),
            "multi_project_manager": self.multi_project_manager.health_check(),
            "backup_manager": self.backup_manager.health_check(),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_context(self, confirmation: str) -> Dict[str, Any]:
        """Clear current context with confirmation"""
        success = self.context_manager.clear_context(confirmation)
        return {"success": success}
    
    def export_context(self, project_id: str, format: str = "json", include_sensitive: bool = False) -> Dict[str, Any]:
        """Export context data"""
        return self.inspector.export_context(project_id, format=format, include_sensitive=include_sensitive)
    
    def import_context(self, import_path: str, project_id: str, merge_strategy: str = "replace") -> Dict[str, Any]:
        """Import context data"""
        return self.inspector.import_context(import_path, project_id, merge_strategy)
    
    def validate_context(self, project_id: str) -> Dict[str, Any]:
        """Validate context integrity"""
        return self.inspector.validate_context_integrity(project_id)
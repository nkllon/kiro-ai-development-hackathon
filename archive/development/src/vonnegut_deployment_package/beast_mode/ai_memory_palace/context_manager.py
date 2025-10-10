"""
Context Manager for AI Memory Palace.

Main orchestrator for AI conversation context persistence that coordinates
all context operations and serves as the primary entry point for the system.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid

from src.beast_mode.core.beastly_module import BeastlyModule
from src.rm_ddd.core.unified_reflective_module import ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
from .tracing_integration import DistributedTracer
from .models import (
    SessionContext, ContextEvent, ProjectState, ContextEventType,
    ConversationEvent, Decision, WorkItem, Discovery, SpecState,
    ServiceInfo, HealthStatus, Change, EventMetadata
)
from .context_registry import ContextRegistry
from .context_engine import ContextEngine
from .context_validator import ContextValidator


class ContextManager(BeastlyModule):
    """Main orchestrator for AI conversation context persistence"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        
        self.config = config or {}
        self.current_session_id = str(uuid.uuid4())
        self.current_project_id = self._detect_project_id()
        
        # Initialize components
        self.registry = ContextRegistry(self.config.get('db_path'))
        self.engine = ContextEngine()
        self.validator = ContextValidator()
        self.tracer = DistributedTracer(service_name="context-manager")
        
        # Current session state
        self.current_context: Optional[SessionContext] = None
        self.session_start_time = datetime.now()
        
        # Metrics
        self._sessions_started = 0
        self._sessions_restored = 0
        self._context_events_processed = 0
        self._validation_failures = 0
        
        self._logger.info(f"🧠 ContextManager initialized for project: {self.current_project_id}")
        self._logger.info(f"🆔 Session ID: {self.current_session_id}")
        
        # Emit initialization observation
        self.emit_observation({
            "type": "context_manager_initialized",
            "project_id": self.current_project_id,
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def load_session_context(self, project_path: Optional[str] = None) -> Optional[SessionContext]:
        """Load or create session context for the current project"""
        with self.tracer.start_span("context_load") as span:
            try:
                span.set_attribute("project_id", self.current_project_id)
                span.set_attribute("session_id", self.current_session_id)
                
                # Emit loading started observation
                self.emit_observation({
                    "type": "session_context_loading_started",
                    "project_id": self.current_project_id,
                    "session_id": self.current_session_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Try to load existing context
                existing_context = self.registry.load_context(self.current_project_id)
                
                if existing_context:
                    # Validate existing context
                    validation_result = self.validator.validate_context_integrity(existing_context)
                    
                    if validation_result.is_valid:
                        self.current_context = existing_context
                        self._sessions_restored += 1
                        
                        span.set_attribute("context_restored", True)
                        span.set_attribute("context_size", existing_context.get_context_size())
                        
                        self._logger.info(f"✅ Restored context for project {self.current_project_id}")
                        self._logger.info(f"📊 Context summary: {existing_context.get_summary()}")
                        
                        # Emit successful restoration
                        self.emit_observation({
                            "type": "session_context_restored",
                            "project_id": self.current_project_id,
                            "session_id": existing_context.session_id,
                            "context_summary": existing_context.get_summary(),
                            "restoration_time_ms": (datetime.now() - self.session_start_time).total_seconds() * 1000
                        })
                        
                        return self.current_context
                    else:
                        self._validation_failures += 1
                        self._logger.warning(f"⚠️ Context validation failed: {validation_result.errors}")
                        
                        # Attempt repair
                        repair_result = self.validator.repair_context_corruption(existing_context)
                        if repair_result.success:
                            self.current_context = repair_result.repaired_context
                            self._logger.info("🔧 Context successfully repaired")
                        else:
                            self._logger.error("💥 Context repair failed, creating new context")
                            existing_context = None
                
                # Create new context if none exists or repair failed
                if not existing_context:
                    self.current_context = await self._create_new_context()
                    self._sessions_started += 1
                    
                    span.set_attribute("context_created", True)
                    
                    self._logger.info(f"🆕 Created new context for project {self.current_project_id}")
                    
                    # Emit new context creation
                    self.emit_observation({
                        "type": "session_context_created",
                        "project_id": self.current_project_id,
                        "session_id": self.current_session_id,
                        "timestamp": datetime.now().isoformat()
                    })
                
                return self.current_context
                
            except Exception as e:
                span.record_exception(e)
                span.set_status("ERROR", str(e))
                
                self._logger.error(f"💥 Error loading session context: {e}")
                
                self.emit_observation({
                    "type": "session_context_loading_error",
                    "project_id": self.current_project_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                return None
    
    async def save_context_event(self, event: ContextEvent) -> bool:
        """Save a context event and update current context"""
        with self.tracer.start_span("context_event_save") as span:
            try:
                span.set_attribute("event_type", event.event_type.value)
                span.set_attribute("correlation_id", event.correlation_id)
                
                # Validate event
                if not self.validator.validate_context_event(event):
                    self._logger.error(f"❌ Context event validation failed: {event.event_id}")
                    return False
                
                # Store event in registry
                success = self.registry.store_event(event, self.current_session_id)
                
                if success:
                    self._context_events_processed += 1
                    
                    # Update current context if it exists
                    if self.current_context:
                        await self._update_context_with_event(event)
                    
                    span.set_attribute("event_stored", True)
                    
                    self._logger.debug(f"📝 Stored context event: {event.event_type.value}")
                    
                    # Emit event stored observation
                    self.emit_observation({
                        "type": "context_event_stored",
                        "event_type": event.event_type.value,
                        "event_id": event.event_id,
                        "correlation_id": event.correlation_id,
                        "session_id": self.current_session_id
                    })
                else:
                    self._logger.error(f"💥 Failed to store context event: {event.event_id}")
                
                return success
                
            except Exception as e:
                span.record_exception(e)
                span.set_status("ERROR", str(e))
                
                self._logger.error(f"💥 Error saving context event: {e}")
                return False
    
    def validate_context_integrity(self) -> Dict[str, Any]:
        """Validate current context integrity"""
        if not self.current_context:
            return {"valid": False, "error": "No current context"}
        
        with self.tracer.start_span("context_validation") as span:
            try:
                validation_result = self.validator.validate_context_integrity(self.current_context)
                
                span.set_attribute("validation_passed", validation_result.is_valid)
                span.set_attribute("error_count", len(validation_result.errors))
                
                result = {
                    "valid": validation_result.is_valid,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                    "context_size": self.current_context.get_context_size(),
                    "validation_timestamp": datetime.now().isoformat()
                }
                
                # Emit validation result
                self.emit_observation({
                    "type": "context_validation_completed",
                    "validation_result": result,
                    "session_id": self.current_session_id
                })
                
                return result
                
            except Exception as e:
                span.record_exception(e)
                span.set_status("ERROR", str(e))
                
                self._logger.error(f"💥 Error validating context: {e}")
                return {"valid": False, "error": str(e)}
    
    def clear_context(self, confirmation: str) -> bool:
        """Clear current context (requires confirmation)"""
        if confirmation != "CONFIRM_CLEAR_CONTEXT":
            self._logger.warning("⚠️ Context clear attempted without proper confirmation")
            return False
        
        try:
            self.current_context = None
            self.current_session_id = str(uuid.uuid4())
            
            self._logger.info("🧹 Context cleared, new session started")
            
            # Emit context cleared observation
            self.emit_observation({
                "type": "context_cleared",
                "new_session_id": self.current_session_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            self._logger.error(f"💥 Error clearing context: {e}")
            return False
    
    async def _create_new_context(self) -> SessionContext:
        """Create a new session context"""
        # Discover current project state
        project_state = await self._discover_project_state()
        
        # Create new context
        context = SessionContext(
            project_id=self.current_project_id,
            session_id=self.current_session_id,
            timestamp=datetime.now(),
            conversation_history=[],
            project_state=project_state,
            decisions_made=[],
            work_completed=[],
            system_discoveries=[],
            spec_states={}
        )
        
        # Store initial context
        self.registry.store_context(context)
        
        return context
    
    async def _discover_project_state(self) -> ProjectState:
        """Discover current project state"""
        try:
            # Get running services
            running_services = await self._discover_running_services()
            
            # Get active specs
            active_specs = self._discover_active_specs()
            
            # Get recent changes (placeholder)
            recent_changes = []
            
            # Get health status
            health_status = HealthStatus(
                overall_status="healthy",
                services_healthy=len([s for s in running_services if s.status == "healthy"]),
                services_total=len(running_services),
                last_check=datetime.now(),
                issues=[]
            )
            
            return ProjectState(
                architecture_overview="Beast Mode AI-powered development framework with Observatory monitoring",
                running_services=running_services,
                active_specs=active_specs,
                recent_changes=recent_changes,
                health_status=health_status
            )
            
        except Exception as e:
            self._logger.error(f"💥 Error discovering project state: {e}")
            
            # Return minimal project state
            return ProjectState(
                architecture_overview="Project state discovery failed",
                running_services=[],
                active_specs=[],
                recent_changes=[],
                health_status=HealthStatus(
                    overall_status="unknown",
                    services_healthy=0,
                    services_total=0,
                    last_check=datetime.now(),
                    issues=[f"Discovery error: {str(e)}"]
                )
            )
    
    async def _discover_running_services(self) -> List[ServiceInfo]:
        """Discover currently running services"""
        services = []
        
        # Check common service endpoints
        service_endpoints = [
            ("Observatory", "http://localhost:8888/health"),
            ("Jaeger", "http://localhost:16686/api/services"),
            ("Prometheus", "http://localhost:9090/-/healthy"),
            ("Grafana", "http://localhost:3000/api/health")
        ]
        
        import aiohttp
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            for name, url in service_endpoints:
                try:
                    async with session.get(url) as response:
                        status = "healthy" if response.status == 200 else f"unhealthy ({response.status})"
                        services.append(ServiceInfo(
                            name=name,
                            url=url,
                            status=status,
                            health_check_url=url
                        ))
                except Exception:
                    services.append(ServiceInfo(
                        name=name,
                        url=url,
                        status="unreachable",
                        health_check_url=url
                    ))
        
        return services
    
    def _discover_active_specs(self) -> List[str]:
        """Discover active specifications"""
        specs = []
        
        specs_dir = Path(".kiro/specs")
        if specs_dir.exists():
            for spec_dir in specs_dir.iterdir():
                if spec_dir.is_dir():
                    specs.append(spec_dir.name)
        
        return specs
    
    async def _update_context_with_event(self, event: ContextEvent):
        """Update current context with new event"""
        if not self.current_context:
            return
        
        # Add to conversation history
        conv_event = ConversationEvent(
            timestamp=event.timestamp,
            event_type=event.event_type.value,
            content=str(event.data),
            metadata=event.metadata.to_dict()
        )
        self.current_context.conversation_history.append(conv_event)
        
        # Process specific event types
        if event.event_type == ContextEventType.DECISION_MADE:
            decision = Decision(
                decision_id=event.event_id,
                timestamp=event.timestamp,
                description=event.data.get("description", ""),
                rationale=event.data.get("rationale", ""),
                alternatives_considered=event.data.get("alternatives", [])
            )
            self.current_context.decisions_made.append(decision)
        
        elif event.event_type == ContextEventType.CODE_WRITTEN:
            work_item = WorkItem(
                work_id=event.event_id,
                timestamp=event.timestamp,
                work_type="code_written",
                description=event.data.get("description", ""),
                files_created=event.data.get("files_created", []),
                files_modified=event.data.get("files_modified", []),
                tests_added=event.data.get("tests_added", [])
            )
            self.current_context.work_completed.append(work_item)
        
        elif event.event_type == ContextEventType.DISCOVERY_MADE:
            discovery = Discovery(
                discovery_id=event.event_id,
                timestamp=event.timestamp,
                discovery_type=event.data.get("discovery_type", ""),
                description=event.data.get("description", ""),
                components_found=event.data.get("components_found", []),
                capabilities_identified=event.data.get("capabilities_identified", [])
            )
            self.current_context.system_discoveries.append(discovery)
        
        # Save updated context
        self.registry.store_context(self.current_context)
    
    def _detect_project_id(self) -> str:
        """Detect current project ID"""
        cwd = Path.cwd()
        
        # Look for .kiro directory
        current = cwd
        while current != current.parent:
            if (current / ".kiro").exists():
                return current.name
            current = current.parent
        
        return cwd.name
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ContextManager"""
        try:
            registry_health = self.registry.health_check()
            
            return {
                "status": "healthy" if registry_health["status"] == "healthy" else "degraded",
                "current_project_id": self.current_project_id,
                "current_session_id": self.current_session_id,
                "has_current_context": self.current_context is not None,
                "sessions_started": self._sessions_started,
                "sessions_restored": self._sessions_restored,
                "events_processed": self._context_events_processed,
                "validation_failures": self._validation_failures,
                "registry_health": registry_health,
                "uptime_seconds": (datetime.now() - self.session_start_time).total_seconds()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        registry_metrics = self.registry.get_metrics()
        
        return {
            "context_manager_sessions_started_total": self._sessions_started,
            "context_manager_sessions_restored_total": self._sessions_restored,
            "context_manager_events_processed_total": self._context_events_processed,
            "context_manager_validation_failures_total": self._validation_failures,
            "context_manager_uptime_seconds": (datetime.now() - self.session_start_time).total_seconds(),
            **registry_metrics
        }
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        if not self.current_context:
            return {"error": "No current context"}
        
        return self.current_context.get_summary()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": "ai_memory_palace_context_manager",
            "module_name": "ContextManager", 
            "version": "1.0.0",
            "description": "Main orchestrator for AI conversation context persistence",
            "project_id": self.current_project_id,
            "session_id": self.current_session_id,
            "sessions_started": self._sessions_started,
            "sessions_restored": self._sessions_restored,
            "context_events_processed": self._context_events_processed
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        
        # Determine status based on validation failures and errors
        if self._validation_failures > 10:
            status = ModuleStatus.ERROR
            health_score = 0.3
        elif self._validation_failures > 5:
            status = ModuleStatus.WARNING  
            health_score = 0.7
        else:
            status = ModuleStatus.HEALTHY
            health_score = 0.95
            
        issues = []
        if self._validation_failures > 0:
            issues.append(f"Validation failures: {self._validation_failures}")
        if self._error_count > 0:
            issues.append(f"Error count: {self._error_count}")
            
        return ModuleHealth(
            module_id="ai_memory_palace_context_manager",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self.session_start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        
        try:
            # In degraded mode, disable advanced features but keep core functionality
            degraded_capabilities = []
            remaining_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
            
            # Check if tracing is available
            if not self.get_tracing_status().get("tracing_enabled", False):
                degraded_capabilities.append(ModuleCapability.MONITORING)
            else:
                remaining_capabilities.append(ModuleCapability.MONITORING)
                
            # Check if validation is working
            try:
                if self.validator:
                    remaining_capabilities.append(ModuleCapability.VALIDATION)
                else:
                    degraded_capabilities.append(ModuleCapability.VALIDATION)
            except:
                degraded_capabilities.append(ModuleCapability.VALIDATION)
                
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
            
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                error_message=str(e)
            )
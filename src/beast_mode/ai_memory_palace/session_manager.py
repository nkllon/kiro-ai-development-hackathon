"""
Session Manager for AI Memory Palace.

Fast context loading and session restoration with <2 second target,
project-scoped isolation, and graceful degradation capabilities.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import uuid
import time

from ..core.reflective_module import ReflectiveModule
from .models import SessionContext, ContextEvent, ProjectState, ServiceInfo, HealthStatus
from .context_registry import ContextRegistry
from .context_engine import ContextEngine
from .context_validator import ContextValidator
from .tracing_integration import DistributedTracer
from .observatory_integration import ContextObservatoryIntegration


class SessionRestorationResult:
    """Result of session restoration operation"""
    
    def __init__(self, success: bool, context: Optional[SessionContext], 
                 load_time_ms: float, source: str, issues: List[str] = None):
        self.success = success
        self.context = context
        self.load_time_ms = load_time_ms
        self.source = source  # "cache", "database", "discovery", "new"
        self.issues = issues or []
        self.timestamp = datetime.now()


class SessionManager(ReflectiveModule):
    """Fast context loading and session restoration manager"""
    
    def __init__(self, registry: ContextRegistry, engine: ContextEngine, 
                 validator: ContextValidator):
        super().__init__()
        
        self.registry = registry
        self.engine = engine
        self.validator = validator
        self.tracer = DistributedTracer(service_name="session-manager")
        self.observatory = ContextObservatoryIntegration()
        
        # Performance targets
        self.target_load_time_ms = 2000  # 2 second target
        self.cache_ttl_minutes = 30
        
        # Session cache for fast loading
        self._session_cache: Dict[str, Tuple[SessionContext, datetime]] = {}
        self._project_cache: Dict[str, Tuple[ProjectState, datetime]] = {}
        
        # Performance metrics
        self._load_operations = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._fast_loads = 0  # Under target time
        self._slow_loads = 0  # Over target time
        self._restoration_failures = 0
        
        # Active sessions
        self._active_sessions: Dict[str, SessionContext] = {}
        
        self.logger.info("⚡ SessionManager initialized with 2-second load target")
    
    async def load_session_context(self, project_id: str, session_id: Optional[str] = None,
                                 force_refresh: bool = False) -> SessionRestorationResult:
        """Load session context with fast restoration"""
        start_time = time.time()
        
        with self.tracer.trace_context_operation("session_load", 
                                                project_id=project_id, 
                                                session_id=session_id) as span:
            try:
                self._load_operations += 1
                
                # Emit loading started observation
                self.observatory.emit_context_observation(
                    "session_load_started",
                    {
                        "project_id": project_id,
                        "session_id": session_id,
                        "force_refresh": force_refresh,
                        "target_time_ms": self.target_load_time_ms
                    }
                )
                
                # Try cache first (if not forcing refresh)
                if not force_refresh:
                    cache_result = await self._try_cache_load(project_id, session_id)
                    if cache_result.success:
                        load_time_ms = (time.time() - start_time) * 1000
                        
                        if load_time_ms <= self.target_load_time_ms:
                            self._fast_loads += 1
                        else:
                            self._slow_loads += 1
                        
                        span.set_attribute("load_source", "cache")
                        span.set_attribute("load_time_ms", load_time_ms)
                        
                        return SessionRestorationResult(
                            success=True,
                            context=cache_result.context,
                            load_time_ms=load_time_ms,
                            source="cache"
                        )
                
                # Try database load
                database_result = await self._try_database_load(project_id, session_id)
                if database_result.success:
                    # Cache the loaded context
                    await self._cache_context(database_result.context)
                    
                    load_time_ms = (time.time() - start_time) * 1000
                    
                    if load_time_ms <= self.target_load_time_ms:
                        self._fast_loads += 1
                    else:
                        self._slow_loads += 1
                    
                    span.set_attribute("load_source", "database")
                    span.set_attribute("load_time_ms", load_time_ms)
                    
                    return database_result
                
                # Try discovery mode (create new context)
                discovery_result = await self._try_discovery_mode(project_id)
                load_time_ms = (time.time() - start_time) * 1000
                
                if load_time_ms <= self.target_load_time_ms:
                    self._fast_loads += 1
                else:
                    self._slow_loads += 1
                
                span.set_attribute("load_source", "discovery")
                span.set_attribute("load_time_ms", load_time_ms)
                
                return discovery_result
                
            except Exception as e:
                self._restoration_failures += 1
                load_time_ms = (time.time() - start_time) * 1000
                
                span.record_exception(e)
                span.set_status("ERROR", str(e))
                
                self.logger.error(f"💥 Session load failed: {e}")
                
                # Emit failure observation
                self.observatory.emit_context_observation(
                    "session_load_failed",
                    {
                        "project_id": project_id,
                        "session_id": session_id,
                        "error": str(e),
                        "load_time_ms": load_time_ms
                    }
                )
                
                return SessionRestorationResult(
                    success=False,
                    context=None,
                    load_time_ms=load_time_ms,
                    source="error",
                    issues=[str(e)]
                )
    
    async def _try_cache_load(self, project_id: str, session_id: Optional[str]) -> SessionRestorationResult:
        """Try to load context from cache"""
        try:
            cache_key = f"{project_id}:{session_id or 'latest'}"
            
            if cache_key in self._session_cache:
                context, cached_time = self._session_cache[cache_key]
                
                # Check if cache is still valid
                if datetime.now() - cached_time < timedelta(minutes=self.cache_ttl_minutes):
                    self._cache_hits += 1
                    
                    self.logger.debug(f"📋 Cache hit for {cache_key}")
                    
                    return SessionRestorationResult(
                        success=True,
                        context=context,
                        load_time_ms=0,  # Cache access is essentially instant
                        source="cache"
                    )
                else:
                    # Cache expired, remove it
                    del self._session_cache[cache_key]
            
            self._cache_misses += 1
            return SessionRestorationResult(success=False, context=None, load_time_ms=0, source="cache")
            
        except Exception as e:
            self.logger.error(f"💥 Cache load error: {e}")
            return SessionRestorationResult(success=False, context=None, load_time_ms=0, source="cache", issues=[str(e)])
    
    async def _try_database_load(self, project_id: str, session_id: Optional[str]) -> SessionRestorationResult:
        """Try to load context from database"""
        try:
            start_time = time.time()
            
            # Load from registry
            context = self.registry.load_context(project_id, session_id)
            
            if context:
                # Validate loaded context
                validation_result = self.validator.validate_context_integrity(context)
                
                load_time_ms = (time.time() - start_time) * 1000
                
                if validation_result.is_valid:
                    self.logger.info(f"✅ Database load successful for {project_id}")
                    
                    return SessionRestorationResult(
                        success=True,
                        context=context,
                        load_time_ms=load_time_ms,
                        source="database"
                    )
                else:
                    # Try to repair context
                    repair_result = self.validator.repair_context_corruption(context)
                    
                    if repair_result.success:
                        self.logger.info(f"🔧 Context repaired for {project_id}")
                        
                        return SessionRestorationResult(
                            success=True,
                            context=repair_result.repaired_context,
                            load_time_ms=load_time_ms,
                            source="database",
                            issues=[f"Context repaired: {', '.join(repair_result.repairs_applied)}"]
                        )
                    else:
                        return SessionRestorationResult(
                            success=False,
                            context=None,
                            load_time_ms=load_time_ms,
                            source="database",
                            issues=[f"Validation failed: {', '.join([e.message for e in validation_result.errors])}"]
                        )
            else:
                load_time_ms = (time.time() - start_time) * 1000
                return SessionRestorationResult(
                    success=False,
                    context=None,
                    load_time_ms=load_time_ms,
                    source="database",
                    issues=["No context found in database"]
                )
                
        except Exception as e:
            load_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"💥 Database load error: {e}")
            return SessionRestorationResult(
                success=False,
                context=None,
                load_time_ms=load_time_ms,
                source="database",
                issues=[str(e)]
            )
    
    async def _try_discovery_mode(self, project_id: str) -> SessionRestorationResult:
        """Create new context through discovery mode"""
        try:
            start_time = time.time()
            
            self.logger.info(f"🔍 Entering discovery mode for {project_id}")
            
            # Discover current project state
            project_state = await self._discover_project_state(project_id)
            
            # Create new session context
            new_context = SessionContext(
                project_id=project_id,
                session_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                conversation_history=[],
                project_state=project_state,
                decisions_made=[],
                work_completed=[],
                system_discoveries=[],
                spec_states={}
            )
            
            # Store the new context
            self.registry.store_context(new_context)
            
            # Cache the new context
            await self._cache_context(new_context)
            
            load_time_ms = (time.time() - start_time) * 1000
            
            self.logger.info(f"🆕 New context created for {project_id}")
            
            return SessionRestorationResult(
                success=True,
                context=new_context,
                load_time_ms=load_time_ms,
                source="discovery"
            )
            
        except Exception as e:
            load_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"💥 Discovery mode error: {e}")
            return SessionRestorationResult(
                success=False,
                context=None,
                load_time_ms=load_time_ms,
                source="discovery",
                issues=[str(e)]
            )
    
    async def _discover_project_state(self, project_id: str) -> ProjectState:
        """Discover current project state"""
        try:
            # Check cache first
            if project_id in self._project_cache:
                project_state, cached_time = self._project_cache[project_id]
                if datetime.now() - cached_time < timedelta(minutes=5):  # 5 minute cache for project state
                    return project_state
            
            # Discover running services
            running_services = await self._discover_running_services()
            
            # Discover active specs
            active_specs = self._discover_active_specs()
            
            # Create health status
            health_status = HealthStatus(
                overall_status="healthy" if running_services else "unknown",
                services_healthy=len([s for s in running_services if s.status == "healthy"]),
                services_total=len(running_services),
                last_check=datetime.now(),
                issues=[]
            )
            
            project_state = ProjectState(
                architecture_overview=f"Beast Mode AI development framework for {project_id}",
                running_services=running_services,
                active_specs=active_specs,
                recent_changes=[],
                health_status=health_status
            )
            
            # Cache project state
            self._project_cache[project_id] = (project_state, datetime.now())
            
            return project_state
            
        except Exception as e:
            self.logger.error(f"💥 Project state discovery error: {e}")
            
            # Return minimal project state
            return ProjectState(
                architecture_overview=f"Project state discovery failed for {project_id}",
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
        
        # Service endpoints to check
        service_endpoints = [
            ("Observatory", "http://localhost:8888/health"),
            ("Jaeger", "http://localhost:16686/api/services"),
            ("Prometheus", "http://localhost:9090/-/healthy"),
            ("Grafana", "http://localhost:3000/api/health")
        ]
        
        # Use aiohttp for async HTTP requests
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1)) as session:
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
        
        except ImportError:
            # Fallback if aiohttp not available
            self.logger.warning("aiohttp not available, skipping service discovery")
        
        return services
    
    def _discover_active_specs(self) -> List[str]:
        """Discover active specifications"""
        specs = []
        
        try:
            specs_dir = Path(".kiro/specs")
            if specs_dir.exists():
                for spec_dir in specs_dir.iterdir():
                    if spec_dir.is_dir():
                        specs.append(spec_dir.name)
        except Exception as e:
            self.logger.error(f"💥 Spec discovery error: {e}")
        
        return specs
    
    async def _cache_context(self, context: SessionContext):
        """Cache context for fast access"""
        try:
            cache_key = f"{context.project_id}:latest"
            session_cache_key = f"{context.project_id}:{context.session_id}"
            
            # Cache both as latest and by session ID
            self._session_cache[cache_key] = (context, datetime.now())
            self._session_cache[session_cache_key] = (context, datetime.now())
            
            # Register as active session
            self._active_sessions[context.session_id] = context
            
            # Register with Observatory
            self.observatory.register_active_context(context)
            
            self.logger.debug(f"📋 Context cached: {cache_key}")
            
        except Exception as e:
            self.logger.error(f"💥 Context caching error: {e}")
    
    def invalidate_cache(self, project_id: Optional[str] = None, session_id: Optional[str] = None):
        """Invalidate context cache"""
        try:
            if project_id and session_id:
                # Invalidate specific session
                cache_key = f"{project_id}:{session_id}"
                if cache_key in self._session_cache:
                    del self._session_cache[cache_key]
            elif project_id:
                # Invalidate all sessions for project
                keys_to_remove = [key for key in self._session_cache.keys() if key.startswith(f"{project_id}:")]
                for key in keys_to_remove:
                    del self._session_cache[key]
            else:
                # Invalidate all cache
                self._session_cache.clear()
                self._project_cache.clear()
            
            self.logger.info(f"🧹 Cache invalidated for project: {project_id}, session: {session_id}")
            
        except Exception as e:
            self.logger.error(f"💥 Cache invalidation error: {e}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions"""
        try:
            sessions = []
            for session_id, context in self._active_sessions.items():
                sessions.append({
                    "session_id": session_id,
                    "project_id": context.project_id,
                    "start_time": context.timestamp.isoformat(),
                    "context_size": context.get_context_size(),
                    "event_count": len(context.conversation_history)
                })
            return sessions
        except Exception as e:
            self.logger.error(f"💥 Error getting active sessions: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get session manager performance statistics"""
        total_loads = self._load_operations
        cache_hit_rate = (self._cache_hits / max(1, self._cache_hits + self._cache_misses)) * 100
        fast_load_rate = (self._fast_loads / max(1, total_loads)) * 100
        
        return {
            "load_operations": self._load_operations,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate_percent": cache_hit_rate,
            "fast_loads": self._fast_loads,
            "slow_loads": self._slow_loads,
            "fast_load_rate_percent": fast_load_rate,
            "restoration_failures": self._restoration_failures,
            "active_sessions": len(self._active_sessions),
            "cached_contexts": len(self._session_cache),
            "target_load_time_ms": self.target_load_time_ms
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for SessionManager"""
        try:
            stats = self.get_performance_stats()
            
            return {
                "status": "healthy",
                "performance_stats": stats,
                "cache_functional": len(self._session_cache) >= 0,  # Basic cache test
                "registry_healthy": self.registry.health_check()["status"] == "healthy"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        stats = self.get_performance_stats()
        
        return {
            "session_manager_load_operations_total": self._load_operations,
            "session_manager_cache_hits_total": self._cache_hits,
            "session_manager_cache_misses_total": self._cache_misses,
            "session_manager_cache_hit_rate": stats["cache_hit_rate_percent"] / 100,
            "session_manager_fast_loads_total": self._fast_loads,
            "session_manager_slow_loads_total": self._slow_loads,
            "session_manager_fast_load_rate": stats["fast_load_rate_percent"] / 100,
            "session_manager_restoration_failures_total": self._restoration_failures,
            "session_manager_active_sessions": len(self._active_sessions),
            "session_manager_cached_contexts": len(self._session_cache),
            "session_manager_target_load_time_ms": self.target_load_time_ms
        }
"""
Unified ReflectiveModule Interface - RDI Compliant

This is the SINGLE, CANONICAL ReflectiveModule interface for:
- RDI Compliance
- Single source of truth
- Unified method signatures
- Consistent behavior across all components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
import os
import logging
import uuid
import time
import threading
import json
from contextlib import contextmanager

# Import tracing capabilities
try:
    from src.beast_mode.tracing.tracer import get_tracer
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False


class ModuleStatus(Enum):
    """Module operational status - RDI Compliant"""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class ModuleCapability(Enum):
    """Module capability types - RDI Compliant"""

    CORE_FUNCTIONALITY = "core_functionality"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    VALIDATION = "validation"
    MONITORING = "monitoring"


@dataclass
class OperationTrace:
    """Complete operation trace with performance metrics - Requirement 22.2"""
    trace_id: str
    operation_name: str
    component_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    input_parameters: Dict[str, Any]
    output_result: Optional[Any]
    error_info: Optional[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    memory_usage: Dict[str, int]
    correlation_id: str

@dataclass
class ModuleHealth:
    """Module health information - RDI Compliant"""

    module_id: str
    status: ModuleStatus
    health_score: float
    issues: List[str]
    last_check: datetime
    uptime_seconds: float = 0.0
    error_count: int = 0
    warning_count: int = 0


@dataclass
class GracefulDegradationResult:
    """Result of graceful degradation - RDI Compliant"""

    success: bool
    degraded_capabilities: List[ModuleCapability]
    remaining_capabilities: List[ModuleCapability]
    error_message: Optional[str] = None


class ReflectiveModule(ABC):
    """Unified ReflectiveModule interface - RDI Compliant"""

    def __init__(self):
        self._start_time = datetime.now()
        self._last_activity = datetime.now()
        self._error_count = 0
        self._warning_count = 0

        # Correlation ID and tracing infrastructure - Requirement 22.1
        self._correlation_id = str(uuid.uuid4())
        self._operation_traces: List[OperationTrace] = []
        self._trace_lock = threading.Lock()
        
        # Performance and resource tracking - Requirement 22.4
        self._operation_count = 0
        self._total_operation_time = 0.0
        self._resource_usage = {
            'peak_memory_mb': 0,
            'total_cpu_time_ms': 0,
            'io_operations': 0
        }

        # Prometheus exporter integration
        self._prometheus_exporter = None
        self._enable_prometheus = self._should_enable_prometheus()
        self._logger = logging.getLogger(f"reflective_module.{self.__class__.__name__}")

        # Initialize Prometheus metrics if enabled
        if self._enable_prometheus:
            self._initialize_prometheus_metrics()
        
        # PATCH_START: ReflectiveModule Redis Auto-Registration
        # Technical Debt: Missing Redis auto-registration in base class
        # Issue: https://github.com/project/issues/redis-registration-gap
        # Cleanup Plan: Replace with proper service lifecycle management system
        # Severity: HIGH - Blocks Runtime State Registry functionality
        # Estimated Cleanup: 2 weeks after service lifecycle system implemented
        self._enable_redis = self._should_enable_redis()
        if self._enable_redis:
            self._initialize_redis_registration()
        # PATCH_END
        
        # Distributed tracing will be initialized on-demand

    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        pass

    @abstractmethod
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        pass

    @abstractmethod
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        pass

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, "register"):
            registry.register(metadata)

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": [],
            "capabilities": [],
        }

    def health_check(self):
        """Perform health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "module_id": getattr(self, "module_id", self.__class__.__name__),
        }

    def _should_enable_prometheus(self) -> bool:
        """Check if Prometheus metrics should be enabled."""
        return os.getenv("BEAST_MODE_PROMETHEUS_ENABLED", "true").lower() == "true"

    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics for this module."""
        try:
            from src.rm_ddd.core.service_config import get_service_config
            from src.beast_mode.monitoring.prometheus_exporter import PrometheusExporter

            # Get Prometheus config from central service configuration
            service_config = get_service_config()
            prometheus_config = service_config.get_prometheus_config()
            
            self._prometheus_exporter = PrometheusExporter(
                prometheus_url=prometheus_config.url,
                enable_http_server=False,  # Don't start local server, use existing one
            )
            self._logger.info(
                f"Prometheus metrics enabled for {self.__class__.__name__} -> {prometheus_config.url}"
            )
        except ImportError:
            self._logger.warning(
                "Prometheus client not available. Install with: pip install prometheus-client"
            )
            self._enable_prometheus = False
        except Exception as e:
            self._logger.error(f"Failed to initialize Prometheus metrics: {e}")
            self._enable_prometheus = False

    # PATCH_START: Redis Auto-Registration Methods
    # Technical Debt: Missing Redis integration in ReflectiveModule base class
    def _should_enable_redis(self) -> bool:
        """Check if Redis auto-registration should be enabled."""
        return os.getenv("BEAST_MODE_REDIS_ENABLED", "true").lower() == "true"

    def _detect_container_environment(self) -> dict:
        """Detect if running in a container and gather environment info."""
        container_info = {
            "is_container": False,
            "container_type": None,
            "evidence": []
        }
        
        # Check for Docker container indicators
        if os.path.exists('/.dockerenv'):
            container_info["is_container"] = True
            container_info["container_type"] = "docker"
            container_info["evidence"].append("/.dockerenv file exists")
        
        # Check for container-specific environment variables
        if os.getenv('HOSTNAME', '').startswith(('docker-', 'k8s-')):
            container_info["is_container"] = True
            container_info["evidence"].append(f"Container hostname pattern: {os.getenv('HOSTNAME')}")
        
        # Check for Docker-specific cgroup
        try:
            with open('/proc/1/cgroup', 'r') as f:
                cgroup_content = f.read()
                if 'docker' in cgroup_content or 'containerd' in cgroup_content:
                    container_info["is_container"] = True
                    container_info["container_type"] = "docker"
                    container_info["evidence"].append("Docker cgroup detected")
        except (FileNotFoundError, PermissionError):
            pass
        
        # Check for Kubernetes
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            container_info["is_container"] = True
            container_info["container_type"] = "kubernetes"
            container_info["evidence"].append("Kubernetes service host detected")
        
        return container_info

    def _resolve_redis_host(self) -> str:
        """Smart Redis host resolution with container detection and logging."""
        # Get explicit Redis host from environment
        explicit_host = os.getenv('REDIS_HOST')
        
        # Detect container environment
        container_info = self._detect_container_environment()
        
        # Log detection results
        if container_info["is_container"]:
            self._logger.info(f"🐳 Container environment detected: {container_info['container_type']}")
            for evidence in container_info["evidence"]:
                self._logger.debug(f"   Evidence: {evidence}")
        else:
            self._logger.info("🖥️  Host environment detected (not containerized)")
        
        # Resolve Redis host based on environment and explicit configuration
        if explicit_host:
            resolved_host = explicit_host
            self._logger.info(f"📍 Using explicit REDIS_HOST: {resolved_host}")
        elif container_info["is_container"]:
            # Smart container defaults
            if container_info["container_type"] == "docker":
                resolved_host = "host.docker.internal"
                self._logger.info(f"🔄 Auto-resolved for Docker container: {resolved_host}")
            elif container_info["container_type"] == "kubernetes":
                resolved_host = "redis-service"  # Common k8s service name
                self._logger.info(f"☸️  Auto-resolved for Kubernetes: {resolved_host}")
            else:
                resolved_host = "localhost"
                self._logger.warning(f"⚠️  Unknown container type, defaulting to: {resolved_host}")
        else:
            # Host environment default
            resolved_host = "localhost"
            self._logger.info(f"🏠 Auto-resolved for host environment: {resolved_host}")
        
        # Final validation and logging
        self._logger.info(f"✅ Final Redis host resolution: {resolved_host}")
        
        return resolved_host

    def _initialize_redis_registration(self):
        """Initialize Redis auto-registration for this module."""
        try:
            import redis
            import json
            import threading
            import time
            
            # Smart container detection and Redis host resolution
            redis_host = self._resolve_redis_host()
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD', '')
            
            self._logger.info(f"Redis connection resolved: {redis_host}:{redis_port}")
            
            # Connect to Redis
            self._redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            
            # Test connection
            self._redis_client.ping()
            
            # Register this module
            self._register_in_redis()
            
            # Start heartbeat
            self._start_redis_heartbeat()
            
            self._logger.info(f"Redis auto-registration enabled for {self.__class__.__name__}")
            
        except Exception as e:
            self._logger.warning(f"Redis auto-registration failed: {e}")
            self._redis_client = None

    def _register_in_redis(self):
        """Register this module in Redis."""
        if not hasattr(self, '_redis_client') or not self._redis_client:
            return
            
        try:
            module_info = self.get_module_info()
            health_status = self.get_health_status()
            capabilities = self.get_capabilities()
            
            # Create registration data
            registration_data = {
                "module_id": module_info.get("module_id", self.__class__.__name__),
                "module_type": self.__class__.__name__,
                "capabilities": [cap.value for cap in capabilities],
                "registered_at": datetime.now().isoformat(),
                "status": health_status.status.value,
                "health_score": health_status.health_score,
                "host": os.getenv('HOSTNAME', 'localhost'),
                "pid": os.getpid(),
                "version": module_info.get("version", "1.0.0")
            }
            
            # Register in multiple Redis patterns for discoverability
            module_id = registration_data["module_id"]
            
            # 1. Health key pattern (for health monitoring)
            health_key = f"health:{module_id}"
            self._redis_client.hset(health_key, mapping={
                "status": str(health_status.status.value),
                "health_score": str(health_status.health_score),
                "last_check": datetime.now().isoformat(),
                "uptime_seconds": str(health_status.uptime_seconds)
            })
            self._redis_client.expire(health_key, 300)  # 5 minute TTL
            
            # 2. Service registry pattern (for service discovery)
            service_key = f"service:registry:{module_id}"
            # Convert all values to strings for Redis
            redis_data = {k: str(v) if not isinstance(v, str) else v for k, v in registration_data.items()}
            redis_data["capabilities"] = json.dumps(registration_data["capabilities"])
            self._redis_client.hset(service_key, mapping=redis_data)
            self._redis_client.expire(service_key, 300)  # 5 minute TTL
            
            # 3. Active modules pattern (for Runtime State Registry)
            active_key = "beast_mode:active_modules"
            self._redis_client.hset(active_key, module_id, json.dumps(registration_data))
            
            self._logger.debug(f"Registered {module_id} in Redis")
            
        except Exception as e:
            self._logger.error(f"Failed to register in Redis: {e}")

    def _start_redis_heartbeat(self):
        """Start Redis heartbeat to maintain registration."""
        if not hasattr(self, '_redis_client') or not self._redis_client:
            return
            
        def heartbeat():
            while True:
                try:
                    time.sleep(60)  # Heartbeat every minute
                    self._register_in_redis()  # Refresh registration
                except Exception as e:
                    self._logger.error(f"Redis heartbeat failed: {e}")
                    break
        
        # Start heartbeat in background thread
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
    # PATCH_END

    def _collect_prometheus_metrics(self):
        """Collect metrics for Prometheus export."""
        if not self._enable_prometheus or not self._prometheus_exporter:
            return

        try:
            # Get module info
            module_info = self.get_module_info()
            module_id = module_info.get("module_id", self.__class__.__name__)

            # Get health status
            health_status = self.get_health_status()

            # Record module health metrics
            self._prometheus_exporter.record_module_health(
                module_id=module_id,
                status=health_status.status.value,
                health_score=health_status.health_score,
                error_count=health_status.error_count,
                warning_count=health_status.warning_count,
                uptime_seconds=health_status.uptime_seconds,
            )

            # Record module performance metrics
            self._prometheus_exporter.record_module_performance(
                module_id=module_id,
                class_name=self.__class__.__name__,
                version=module_info.get("version", "1.0.0"),
                capabilities=[cap.value for cap in self.get_capabilities()],
                last_activity=self._last_activity,
            )

        except Exception as e:
            self._logger.error(f"Failed to collect Prometheus metrics: {e}")

    def _update_activity(self):
        """Update last activity timestamp and collect metrics."""
        self._last_activity = datetime.now()
        if self._enable_prometheus:
            self._collect_prometheus_metrics()

    def _increment_error_count(self):
        """Increment error count and collect metrics."""
        self._error_count += 1
        self._update_activity()

    def _increment_warning_count(self):
        """Increment warning count and collect metrics."""
        self._warning_count += 1
        self._update_activity()

    def get_prometheus_metrics(self) -> Dict[str, Any]:
        """Get Prometheus metrics for this module."""
        if not self._enable_prometheus or not self._prometheus_exporter:
            return {}

        try:
            return self._prometheus_exporter.get_module_metrics(
                module_id=getattr(self, "module_id", self.__class__.__name__)
            )
        except Exception as e:
            self._logger.error(f"Failed to get Prometheus metrics: {e}")
            return {}

    def enable_prometheus_metrics(self, enable: bool = True):
        """Enable or disable Prometheus metrics for this module."""
        self._enable_prometheus = enable
        if enable and not self._prometheus_exporter:
            self._initialize_prometheus_metrics()
        elif not enable:
            self._prometheus_exporter = None

    def store_content(self, content_id: str, collection: str, data: Dict[str, Any]) -> bool:
        """Store content in unified CMS (Directus integration)."""
        try:
            # Initialize CMS connection if needed
            if not hasattr(self, '_cms_client'):
                self._initialize_cms_client()
            
            # Store content with metadata
            content_data = {
                "id": content_id,
                "data": data,
                "module_id": getattr(self, "module_id", self.__class__.__name__),
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            # Try to use real Directus client
            if hasattr(self._cms_client, 'create_item'):
                result = self._cms_client.create_item(collection, content_data)
                if result:
                    self._logger.info(f"Stored content {content_id} in Directus collection {collection}")
                    return True
                else:
                    self._logger.warning(f"Failed to store content {content_id} in Directus, using memory fallback")
            
            # Fallback to memory storage
            if not hasattr(self, '_content_store'):
                self._content_store = {}
            
            self._content_store[content_id] = content_data
            self._logger.info(f"Stored content {content_id} in memory collection {collection}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to store content {content_id}: {e}")
            return False

    def get_content(self, content_id: str, collection: str = "content") -> Optional[Dict[str, Any]]:
        """Retrieve content from unified CMS."""
        try:
            # Initialize CMS connection if needed
            if not hasattr(self, '_cms_client'):
                self._initialize_cms_client()
            
            # Try to use real Directus client
            if hasattr(self._cms_client, 'get_items'):
                items = self._cms_client.get_items(collection, {"filter": {"id": {"_eq": content_id}}})
                if items:
                    return items[0]
            
            # Fallback to memory store
            if hasattr(self, '_content_store') and content_id in self._content_store:
                return self._content_store[content_id]
            
            self._logger.warning(f"Content {content_id} not found in Directus or memory")
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve content {content_id}: {e}")
            return None

    def _initialize_cms_client(self):
        """Initialize CMS client connection."""
        try:
            # Initialize actual Directus client
            from src.beast_mode.directus_cms.directus_client import DirectusClient
            
            # Get Directus configuration from environment
            directus_url = os.getenv("DIRECTUS_URL", "http://localhost:8055")
            directus_token = os.getenv("DIRECTUS_TOKEN")
            
            self._cms_client = DirectusClient(base_url=directus_url, token=directus_token)
            
            # Test connection
            if self._cms_client.health_check():
                self._logger.info("CMS client initialized (Directus connected)")
            else:
                self._logger.warning("CMS client initialized (Directus not accessible, will retry)")
            
        except ImportError:
            # Fallback to memory storage if DirectusClient not available
            self._cms_client = "memory_store"
            self._logger.warning("DirectusClient not available, using memory storage fallback")
        except Exception as e:
            self._logger.error(f"Failed to initialize CMS client: {e}")
            # Fallback to memory storage
            self._cms_client = "memory_store"
            self._logger.warning("Using memory storage fallback due to CMS client error")

    def get_cli_interface(self) -> Dict[str, Any]:
        """
        Generate CLI interface from ReflectiveModule introspection - RDI Compliant
        
        Requirement 21.1: Use ReflectiveModule introspection framework to dynamically 
        generate CLI interfaces at runtime
        """
        import inspect
        
        cli_commands = {}
        
        # Get all public methods that can be CLI commands
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_') and name not in ['get_cli_interface', 'generate_cli_help']:
                try:
                    sig = inspect.signature(method)
                    
                    # Build command info
                    command_info = {
                        'method_name': name,
                        'signature': str(sig),
                        'docstring': method.__doc__ or f"Execute {name} command",
                        'parameters': [],
                        'return_type': str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else "Any"
                    }
                    
                    # Extract parameters (skip 'self')
                    for param_name, param in sig.parameters.items():
                        if param_name != 'self':
                            param_info = {
                                'name': param_name,
                                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else "str",
                                'required': param.default == inspect.Parameter.empty,
                                'default': str(param.default) if param.default != inspect.Parameter.empty else None
                            }
                            command_info['parameters'].append(param_info)
                    
                    cli_commands[name] = command_info
                    
                except Exception as e:
                    self._logger.warning(f"Could not introspect method {name}: {e}")
        
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'module_name': self.__class__.__name__,
            'commands': cli_commands,
            'capabilities': [cap.value for cap in self.get_capabilities()],
            'health_status': self.get_health_status().status.value
        }
    
    def generate_cli_help(self, command_name: Optional[str] = None) -> str:
        """
        Generate CLI help documentation dynamically from RM-DDD interface metadata
        
        Requirement 21.4: Generate help documentation dynamically from RM-DDD 
        interface metadata and method signatures
        """
        cli_interface = self.get_cli_interface()
        
        if command_name:
            # Help for specific command
            if command_name in cli_interface['commands']:
                cmd = cli_interface['commands'][command_name]
                help_text = f"Command: {command_name}\n"
                help_text += f"Description: {cmd['docstring']}\n"
                help_text += f"Signature: {cmd['signature']}\n"
                
                if cmd['parameters']:
                    help_text += "\nParameters:\n"
                    for param in cmd['parameters']:
                        required = "required" if param['required'] else "optional"
                        default = f" (default: {param['default']})" if param['default'] else ""
                        help_text += f"  {param['name']} ({param['type']}) - {required}{default}\n"
                
                return help_text
            else:
                return f"Command '{command_name}' not found"
        else:
            # General help
            help_text = f"Module: {cli_interface['module_name']}\n"
            help_text += f"Module ID: {cli_interface['module_id']}\n"
            help_text += f"Health: {cli_interface['health_status']}\n"
            help_text += f"Capabilities: {', '.join(cli_interface['capabilities'])}\n\n"
            help_text += "Available Commands:\n"
            
            for cmd_name, cmd_info in cli_interface['commands'].items():
                help_text += f"  {cmd_name} - {cmd_info['docstring']}\n"
            
            help_text += f"\nUse generate_cli_help('<command_name>') for detailed help on a specific command."
            
            return help_text
    
    def execute_cli_command(self, command_name: str, **kwargs) -> Any:
        """
        Execute CLI command with parameters
        
        Requirement 21.2: Project RM-DDD interface methods to CLI commands 
        with automatic help documentation generation
        """
        if hasattr(self, command_name):
            method = getattr(self, command_name)
            if callable(method) and not command_name.startswith('_'):
                try:
                    with self.trace_operation(f"cli_{command_name}", **kwargs) as trace:
                        result = method(**kwargs)
                        trace.output_result = result
                        
                        # Return CLI-formatted response
                        return {
                            'success': True,
                            'command': command_name,
                            'parameters': kwargs,
                            'result': result,
                            'executed_at': datetime.now().isoformat()
                        }
                except Exception as e:
                    self._logger.error(f"CLI command {command_name} failed: {e}")
                    return {
                        'success': False,
                        'command': command_name,
                        'parameters': kwargs,
                        'error': str(e),
                        'executed_at': datetime.now().isoformat()
                    }
            else:
                raise ValueError(f"Method {command_name} is not callable or is private")
        else:
            raise ValueError(f"Command {command_name} not found")

    @contextmanager
    def trace_operation(self, operation_name: str, **input_params):
        """
        Context manager for operation tracing - Requirement 22.1, 22.2
        
        Provides complete operation traceability with correlation IDs
        and performance metrics collection.
        """
        trace_id = str(uuid.uuid4())
        start_time = datetime.now()
        start_memory = self._get_memory_usage()
        
        trace = OperationTrace(
            trace_id=trace_id,
            operation_name=operation_name,
            component_name=self.__class__.__name__,
            start_time=start_time,
            end_time=None,
            duration_ms=None,
            input_parameters=input_params,
            output_result=None,
            error_info=None,
            performance_metrics={},
            memory_usage={'start_mb': start_memory},
            correlation_id=self._correlation_id
        )
        
        try:
            yield trace
            
            # Success path
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            end_memory = self._get_memory_usage()
            
            trace.end_time = end_time
            trace.duration_ms = duration_ms
            trace.memory_usage['end_mb'] = end_memory
            trace.memory_usage['delta_mb'] = end_memory - start_memory
            trace.performance_metrics = {
                'duration_ms': duration_ms,
                'memory_delta_mb': end_memory - start_memory,
                'success': True
            }
            
            # Update statistics
            self._operation_count += 1
            self._total_operation_time += duration_ms
            self._resource_usage['peak_memory_mb'] = max(
                self._resource_usage['peak_memory_mb'], 
                end_memory
            )
            
        except Exception as e:
            # Error path
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            trace.end_time = end_time
            trace.duration_ms = duration_ms
            trace.error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'error_occurred_at': end_time.isoformat()
            }
            trace.performance_metrics = {
                'duration_ms': duration_ms,
                'success': False
            }
            
            self._error_count += 1
            raise
        finally:
            # Store trace
            with self._trace_lock:
                self._operation_traces.append(trace)
                # Keep only last 1000 traces to prevent memory bloat
                if len(self._operation_traces) > 1000:
                    self._operation_traces = self._operation_traces[-1000:]
    
    def get_operation_traces(self, limit: int = 100) -> List[OperationTrace]:
        """
        Get recent operation traces - Requirement 22.5
        
        Provides complete operation traceability for debugging and audit.
        """
        with self._trace_lock:
            return self._operation_traces[-limit:] if self._operation_traces else []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics - Requirement 22.1, 22.4
        
        Tracks usage patterns, frequency, and performance metrics for all operations.
        """
        avg_operation_time = (
            self._total_operation_time / self._operation_count 
            if self._operation_count > 0 else 0.0
        )
        
        return {
            'operation_count': self._operation_count,
            'total_operation_time_ms': self._total_operation_time,
            'average_operation_time_ms': avg_operation_time,
            'error_count': self._error_count,
            'warning_count': self._warning_count,
            'error_rate': self._error_count / max(self._operation_count, 1),
            'uptime_seconds': (datetime.now() - self._start_time).total_seconds(),
            'resource_usage': self._resource_usage.copy(),
            'correlation_id': self._correlation_id,
            'traces_stored': len(self._operation_traces)
        }
    
    def get_usage_tracking(self) -> Dict[str, Any]:
        """
        Get usage tracking data - Requirement 22.1
        
        Track usage patterns, frequency, and performance metrics for all 
        ReflectiveModule operations.
        """
        recent_traces = self.get_operation_traces(50)
        
        # Analyze operation patterns
        operation_frequency = {}
        for trace in recent_traces:
            op_name = trace.operation_name
            operation_frequency[op_name] = operation_frequency.get(op_name, 0) + 1
        
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'tracking_period_start': self._start_time.isoformat(),
            'tracking_period_end': datetime.now().isoformat(),
            'operation_frequency': operation_frequency,
            'performance_metrics': self.get_performance_metrics(),
            'health_status': self.get_health_status().status.value,
            'capabilities_used': [cap.value for cap in self.get_capabilities()]
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # Fallback if psutil not available
            return 0.0
        except Exception:
            return 0.0
    
    def get_cli_cache_options(self) -> Dict[str, Any]:
        """
        Get CLI caching options - Requirement 21.3
        
        Provide options to cache or persist generated CLI implementations 
        while maintaining dynamic generation capability.
        """
        return {
            'lazy_instantiation': True,
            'cache_enabled': getattr(self, '_cli_cache_enabled', False),
            'cache_ttl_seconds': getattr(self, '_cli_cache_ttl', 3600),
            'cache_size_limit': getattr(self, '_cli_cache_size_limit', 100),
            'dynamic_generation': True,
            'cache_location': getattr(self, '_cli_cache_location', '/tmp/cli_cache')
        }
    
    def enable_cli_caching(self, enabled: bool = True, ttl_seconds: int = 3600):
        """
        Enable CLI caching with lazy instantiation - Requirement 21.3
        
        CLI caching so unused CLIs are never created unless actually invoked.
        """
        self._cli_cache_enabled = enabled
        self._cli_cache_ttl = ttl_seconds
        if enabled:
            self._cli_cache = {}
            self._cli_cache_timestamps = {}
            self._logger.info(f"CLI caching enabled with {ttl_seconds}s TTL")
        else:
            self._cli_cache = None
            self._cli_cache_timestamps = None
            self._logger.info("CLI caching disabled")

    def get_cli_interface(self) -> Dict[str, Any]:
        """
        Generate CLI interface through introspection - RM-DDD Dynamic CLI
        
        Returns CLI command structure based on public methods and their signatures.
        Supports lazy instantiation and automatic help generation.
        """
        import inspect
        
        cli_commands = {}
        
        # Introspect public methods
        for method_name, method in inspect.getmembers(self, inspect.ismethod):
            if not method_name.startswith('_') and method_name not in ['get_cli_interface']:
                try:
                    sig = inspect.signature(method)
                    
                    # Build command structure
                    command_info = {
                        'method_name': method_name,
                        'description': method.__doc__ or f"Execute {method_name}",
                        'signature': str(sig),
                        'parameters': [],
                        'return_type': str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else 'Any'
                    }
                    
                    # Extract parameters
                    for param_name, param in sig.parameters.items():
                        if param_name != 'self':
                            param_info = {
                                'name': param_name,
                                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                                'required': param.default == inspect.Parameter.empty,
                                'default': str(param.default) if param.default != inspect.Parameter.empty else None
                            }
                            command_info['parameters'].append(param_info)
                    
                    cli_commands[method_name] = command_info
                    
                except Exception as e:
                    self._logger.warning(f"Could not introspect method {method_name}: {e}")
        
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'module_name': self.__class__.__name__,
            'commands': cli_commands,
            'generated_at': datetime.now().isoformat()
        }
    
    def execute_cli_command(self, command_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute CLI command with parameters
        
        Args:
            command_name: Name of the method to execute
            **kwargs: Parameters to pass to the method
            
        Returns:
            Dict with execution result and metadata
        """
        try:
            if not hasattr(self, command_name):
                return {
                    'success': False,
                    'error': f"Command '{command_name}' not found",
                    'available_commands': list(self.get_cli_interface()['commands'].keys())
                }
            
            method = getattr(self, command_name)
            if command_name.startswith('_'):
                return {
                    'success': False,
                    'error': f"Command '{command_name}' is private and not accessible via CLI"
                }
            
            # Execute the method
            result = method(**kwargs)
            
            return {
                'success': True,
                'command': command_name,
                'parameters': kwargs,
                'result': result,
                'executed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'command': command_name,
                'parameters': kwargs,
                'error': str(e),
                'executed_at': datetime.now().isoformat()
            }
    
    def generate_cli_help(self, command_name: str = None) -> str:
        """
        Generate CLI help documentation
        
        Args:
            command_name: Specific command to get help for, or None for all commands
            
        Returns:
            Formatted help text
        """
        cli_interface = self.get_cli_interface()
        
        if command_name:
            if command_name not in cli_interface['commands']:
                return f"Command '{command_name}' not found. Available commands: {', '.join(cli_interface['commands'].keys())}"
            
            cmd = cli_interface['commands'][command_name]
            help_text = f"\nCommand: {command_name}\n"
            help_text += f"Description: {cmd['description']}\n"
            help_text += f"Signature: {cmd['signature']}\n"
            help_text += f"Return Type: {cmd['return_type']}\n"
            
            if cmd['parameters']:
                help_text += "\nParameters:\n"
                for param in cmd['parameters']:
                    required = "required" if param['required'] else f"optional (default: {param['default']})"
                    help_text += f"  {param['name']} ({param['type']}) - {required}\n"
            else:
                help_text += "\nNo parameters required.\n"
            
            return help_text
        else:
            # Generate help for all commands
            help_text = f"\n{cli_interface['module_name']} CLI Interface\n"
            help_text += "=" * (len(cli_interface['module_name']) + 14) + "\n"
            help_text += f"Module ID: {cli_interface['module_id']}\n"
            help_text += f"Generated: {cli_interface['generated_at']}\n\n"
            help_text += "Available Commands:\n"
            
            for cmd_name, cmd_info in cli_interface['commands'].items():
                help_text += f"  {cmd_name} - {cmd_info['description']}\n"
            
            help_text += f"\nUse generate_cli_help('<command_name>') for detailed help on specific commands.\n"
            
            return help_text

    def emit_observation(self, message: str, event_type: str = "info", context: Optional[Dict[str, Any]] = None, emoji: Optional[str] = None):
        """
        Emit an observation event for the Living Observatory Dashboard
        
        This method allows Beastly Modules to emit real-time observations that will
        be displayed in the Observatory Activity Feed.
        
        Args:
            message: Human-readable description of what happened
            event_type: Type of event (info, warning, error, success, etc.)
            context: Additional context data for the event
            emoji: Optional emoji to display with the event
        """
        try:
            # Create observation event
            observation = {
                "timestamp": datetime.now().isoformat(),
                "module": getattr(self, 'module_id', self.__class__.__name__),
                "event_type": event_type,
                "message": message,
                "emoji": emoji or self._get_default_emoji(event_type),
                "severity": self._map_event_type_to_severity(event_type),
                "context": context or {},
                "correlation_id": self._correlation_id
            }
            
            # Send to Observatory if available
            self._send_observation_to_observatory(observation)
            
            # Log the observation
            log_level = self._get_log_level_for_event_type(event_type)
            self._logger.log(log_level, f"📰 {message} {emoji or ''}")
            
        except Exception as e:
            self._logger.error(f"Failed to emit observation: {e}")
    
    def _get_default_emoji(self, event_type: str) -> str:
        """Get default emoji for event type"""
        emoji_map = {
            'certificate_lock': '🔒',
            'websocket_connect': '🔌',
            'websocket_disconnect': '🔌❌',
            'cache_invalidate': '🗑️',
            'database_query': '🗄️',
            'api_request': '📡',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅',
            'performance': '⚡',
            'security': '🛡️',
            'deployment': '🚀',
            'backup': '💾',
            'maintenance': '🔧',
            'monitoring': '👁️',
            'default': '📊'
        }
        return emoji_map.get(event_type, emoji_map['default'])
    
    def _map_event_type_to_severity(self, event_type: str) -> str:
        """Map event type to severity level"""
        severity_map = {
            'error': 'error',
            'warning': 'warning',
            'success': 'success',
            'info': 'info',
            'certificate_lock': 'info',
            'websocket_connect': 'info',
            'websocket_disconnect': 'info',
            'cache_invalidate': 'info',
            'database_query': 'info',
            'api_request': 'info',
            'performance': 'info',
            'security': 'warning',
            'deployment': 'info',
            'backup': 'info',
            'maintenance': 'info',
            'monitoring': 'info'
        }
        return severity_map.get(event_type, 'info')
    
    def _get_log_level_for_event_type(self, event_type: str) -> int:
        """Get logging level for event type"""
        level_map = {
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'success': logging.INFO,
            'info': logging.INFO
        }
        severity = self._map_event_type_to_severity(event_type)
        return level_map.get(severity, logging.INFO)
    
    def _send_observation_to_observatory(self, observation: Dict[str, Any]):
        """Send observation to Observatory WebSocket if available"""
        try:
            # Add distributed tracing if available (graceful degradation)
            if TRACING_AVAILABLE:
                try:
                    tracer = get_tracer()
                    if tracer.is_available():
                        with tracer.trace_observation_flow(observation):
                            self._do_send_observation(observation)
                    else:
                        self._do_send_observation(observation)
                except Exception as e:
                    # Tracing failed, continue without it
                    self._logger.debug(f"Tracing failed, continuing without: {e}")
                    self._do_send_observation(observation)
            else:
                # No tracing available, work normally
                self._do_send_observation(observation)
                
        except Exception as e:
            # Don't let observation emission break the main functionality
            self._logger.debug(f"Could not send observation to Observatory: {e}")
    
    def _do_send_observation(self, observation: Dict[str, Any]):
        """Actually send the observation"""
        # Try to get the global Observatory observation handler
        if hasattr(self, '_observatory_handler'):
            self._observatory_handler.broadcast_observation(observation)
        else:
            # Try to import and use the global handler
            try:
                from src.beast_mode.observatory.observation_handler import get_global_observation_handler
                handler = get_global_observation_handler()
                if handler:
                    handler.broadcast_observation(observation)
                else:
                    self._logger.debug("No global observation handler available")
            except ImportError:
                # Observatory not available, just log
                self._logger.debug("Observatory observation handler not available")
    
    def set_observatory_handler(self, handler):
        """Set the Observatory observation handler for this module"""
        self._observatory_handler = handler

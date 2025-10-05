#!/usr/bin/env python3
"""
ServiceRegistry - Centralized Service Management and Dependency Resolution

Provides centralized management of all services requiring auto-start configuration
with dependency resolution and startup ordering using topological sorting.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.service_auto_starter import ServiceDefinition


@dataclass
class ServiceRegistration:
    """Complete service registration with metadata."""
    definition: ServiceDefinition
    platform: str
    status: str = "registered"
    auto_start_enabled: bool = False
    last_health_check: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyError(Exception):
    """Raised when dependency resolution fails."""
    pass


class ServiceRegistry(ReflectiveModule):
    """
    Centralized registry for service auto-start management.
    
    Maintains service definitions, resolves dependencies, and calculates
    startup ordering using topological sorting to ensure correct sequence.
    """
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get ServiceRegistry capabilities."""
        return {
            "service_registration": True,
            "dependency_resolution": True,
            "topological_sorting": True,
            "multi_platform_support": True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "ServiceRegistry",
            "version": "1.0.0",
            "description": "Centralized service registry with dependency resolution",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"ServiceRegistry degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_registration"
        }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ServiceRegistry."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Service storage
        self._services: Dict[str, ServiceRegistration] = {}
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("ServiceRegistry initialized")
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge, Histogram
            
            self._services_registered = Counter(
                'service_registry_registered_total',
                'Total services registered',
                ['platform', 'status']
            )
            
            self._active_services = Gauge(
                'service_registry_active_count',
                'Number of active services',
                ['platform']
            )
            
            self._dependency_resolution_time = Histogram(
                'service_registry_dependency_resolution_seconds',
                'Time spent resolving dependencies'
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def register_service(self, service: ServiceDefinition, platform: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a service in the registry.
        
        Args:
            service: Service definition to register
            platform: Target platform for the service
            metadata: Additional service metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if service.name in self._services:
                self._logger.warning(f"Service {service.name} already registered, updating")
            
            registration = ServiceRegistration(
                definition=service,
                platform=platform,
                metadata=metadata or {}
            )
            
            self._services[service.name] = registration
            
            # Update dependency graph
            self._dependency_graph[service.name] = set(service.dependencies)
            
            # Update metrics
            if hasattr(self, '_services_registered'):
                self._services_registered.labels(
                    platform=platform,
                    status="registered"
                ).inc()
            
            self._logger.info(f"Registered service: {service.name} on platform: {platform}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to register service {service.name}: {e}")
            return False
    
    def get_service(self, name: str) -> Optional[ServiceRegistration]:
        """Get service registration by name."""
        return self._services.get(name)
    
    def list_services(self, platform: Optional[str] = None, status: Optional[str] = None) -> List[ServiceRegistration]:
        """
        List services with optional filtering.
        
        Args:
            platform: Filter by platform
            status: Filter by status
            
        Returns:
            List of matching service registrations
        """
        services = list(self._services.values())
        
        if platform:
            services = [s for s in services if s.platform == platform]
        
        if status:
            services = [s for s in services if s.status == status]
        
        return services
    
    def get_startup_order(self, platform: Optional[str] = None) -> List[str]:
        """
        Calculate service startup order using topological sorting.
        
        Args:
            platform: Filter services by platform
            
        Returns:
            List of service names in dependency-resolved startup order
            
        Raises:
            DependencyError: If circular dependencies are detected
        """
        start_time = self._get_current_time()
        
        try:
            # Filter services by platform if specified
            if platform:
                services = {name: reg for name, reg in self._services.items() 
                           if reg.platform == platform}
            else:
                services = self._services
            
            if not services:
                return []
            
            # Build dependency graph for selected services
            graph = {}
            in_degree = {}
            
            for service_name in services:
                graph[service_name] = set()
                in_degree[service_name] = 0
            
            # Add edges and calculate in-degrees
            for service_name, registration in services.items():
                for dependency in registration.definition.dependencies:
                    if dependency in services:  # Only include dependencies that are registered
                        graph[dependency].add(service_name)
                        in_degree[service_name] += 1
                    else:
                        self._logger.warning(f"Service {service_name} depends on unregistered service: {dependency}")
            
            # Topological sort using Kahn's algorithm
            queue = deque([name for name, degree in in_degree.items() if degree == 0])
            result = []
            
            while queue:
                current = queue.popleft()
                result.append(current)
                
                # Remove edges from current node
                for neighbor in graph[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            # Check for circular dependencies
            if len(result) != len(services):
                remaining = set(services.keys()) - set(result)
                cycle = self._detect_cycle(remaining, services)
                raise DependencyError(f"Circular dependency detected: {' -> '.join(cycle)}")
            
            # Update metrics
            if hasattr(self, '_dependency_resolution_time'):
                duration = self._get_current_time() - start_time
                self._dependency_resolution_time.observe(duration)
            
            self._logger.info(f"Calculated startup order for {len(result)} services: {result}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to calculate startup order: {e}")
            raise
    
    def _detect_cycle(self, remaining_services: Set[str], services: Dict[str, ServiceRegistration]) -> List[str]:
        """Detect and return a cycle in the dependency graph."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            if node in rec_stack:
                # Found cycle, return the cycle path
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            
            if node in visited:
                return None
            
            visited.add(node)
            rec_stack.add(node)
            
            for dependency in services[node].definition.dependencies:
                if dependency in remaining_services:
                    cycle = dfs(dependency, path + [node])
                    if cycle:
                        return cycle
            
            rec_stack.remove(node)
            return None
        
        for service in remaining_services:
            if service not in visited:
                cycle = dfs(service, [])
                if cycle:
                    return cycle
        
        return ["unknown cycle"]
    
    def update_service_status(self, name: str, status: str, auto_start_enabled: Optional[bool] = None) -> bool:
        """
        Update service status and auto-start configuration.
        
        Args:
            name: Service name
            status: New status
            auto_start_enabled: Whether auto-start is enabled
            
        Returns:
            True if update successful, False otherwise
        """
        if name not in self._services:
            self._logger.error(f"Service {name} not found")
            return False
        
        try:
            registration = self._services[name]
            registration.status = status
            
            if auto_start_enabled is not None:
                registration.auto_start_enabled = auto_start_enabled
            
            self._logger.info(f"Updated service {name}: status={status}, auto_start={registration.auto_start_enabled}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to update service {name}: {e}")
            return False
    
    def remove_service(self, name: str) -> bool:
        """
        Remove a service from the registry.
        
        Args:
            name: Service name to remove
            
        Returns:
            True if removal successful, False otherwise
        """
        if name not in self._services:
            self._logger.warning(f"Service {name} not found for removal")
            return False
        
        try:
            # Check if other services depend on this one
            dependents = []
            for service_name, registration in self._services.items():
                if name in registration.definition.dependencies:
                    dependents.append(service_name)
            
            if dependents:
                self._logger.warning(f"Service {name} has dependents: {dependents}")
            
            # Remove from registry
            del self._services[name]
            if name in self._dependency_graph:
                del self._dependency_graph[name]
            
            self._logger.info(f"Removed service: {name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to remove service {name}: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for observability."""
        platform_counts = defaultdict(int)
        status_counts = defaultdict(int)
        
        for registration in self._services.values():
            platform_counts[registration.platform] += 1
            status_counts[registration.status] += 1
        
        return {
            "status": "healthy",
            "total_services": len(self._services),
            "platforms": dict(platform_counts),
            "statuses": dict(status_counts),
            "auto_start_enabled": sum(1 for r in self._services.values() if r.auto_start_enabled)
        }
    
    def _get_current_time(self) -> float:
        """Get current time for metrics."""
        import time
        return time.time()
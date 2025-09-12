"""
Registry Core Core

This module was extracted from registry_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING
from uuid import uuid4
from dataclasses import dataclass, field
from threading import Lock
from ..models import ModuleStatus, ModuleCapability
from .base import ReflectiveModuleBase
from .health import ModuleHealth

@dataclass
class RegisteredModule:
    """Information about a registered RM module."""
    module_id: str
    module: 'ReflectiveModuleBase'
    registration_time: datetime
    last_health_check: Optional[datetime] = None
    last_health_status: Optional['ModuleHealth'] = None
    capabilities: List[ModuleCapability] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)

    @property
    def is_healthy(self) -> bool:
        """Check if module is currently healthy."""
        if not self.last_health_status:
            return False
        return self.last_health_status.is_healthy

    @property
    def uptime(self) -> timedelta:
        """Calculate module uptime since registration."""
        return datetime.now() - self.registration_time

class GlobalRegistry:
    """
    Global registry for RM-DDD components.
    
    Provides centralized component discovery, health monitoring, and
    dependency management for all RM components in the system.
    
    Responsibilities:
    - Component registration and discovery
    - Health status aggregation and monitoring
    - Dependency tracking and resolution
    - Service discovery and load balancing
    - System-wide health reporting
    
    Accountability Chain:
    - Registry Manager: Responsible for registry operations
    - Component Owners: Responsible for component health
    - System Administrator: Responsible for overall system health
    """

    def __init__(self):
        """Initialize the global registry."""
        self._modules: Dict[str, RegisteredModule] = {}
        self._capabilities: Dict[str, List[str]] = {}
        self._lock = Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._health_check_interval = timedelta(seconds=60)
        self._registry_id = str(uuid4())
        self._created_at = datetime.now()
        logger.info(f'GlobalRegistry initialized: {self._registry_id}')

    def register_module(self, module: 'ReflectiveModuleBase', module_id: str):
        """
        Register an RM module with the global registry.
        
        Args:
            module: The RM module to register
            module_id: Unique identifier for the module
        """
        with self._lock:
            if module_id in self._modules:
                logger.warning(f'Module {module_id} already registered, updating registration')
            registered_module = RegisteredModule(module_id=module_id, module=module, registration_time=datetime.now())
            self._modules[module_id] = registered_module
            if len(self._modules) == 1 and (not self._health_check_task):
                self._start_health_monitoring()
            logger.info(f'Module registered: {module_id}')

    def unregister_module(self, module_id: str):
        """
        Unregister an RM module from the global registry.
        
        Args:
            module_id: Unique identifier of the module to unregister
        """
        with self._lock:
            if module_id not in self._modules:
                logger.warning(f'Attempted to unregister unknown module: {module_id}')
                return
            registered_module = self._modules[module_id]
            for capability_name in list(self._capabilities.keys()):
                if module_id in self._capabilities[capability_name]:
                    self._capabilities[capability_name].remove(module_id)
                    if not self._capabilities[capability_name]:
                        del self._capabilities[capability_name]
            for dependent_id in registered_module.dependents:
                if dependent_id in self._modules:
                    self._modules[dependent_id].dependencies.discard(module_id)
            for dependency_id in registered_module.dependencies:
                if dependency_id in self._modules:
                    self._modules[dependency_id].dependents.discard(module_id)
            del self._modules[module_id]
            logger.info(f'Module unregistered: {module_id}')
            if not self._modules and self._health_check_task:
                self._stop_health_monitoring()

    async def update_module_capabilities(self, module_id: str, capabilities: List[ModuleCapability]):
        """
        Update capabilities for a registered module.
        
        Args:
            module_id: Unique identifier of the module
            capabilities: List of capabilities provided by the module
        """
        with self._lock:
            if module_id not in self._modules:
                logger.warning(f'Attempted to update capabilities for unknown module: {module_id}')
                return
            registered_module = self._modules[module_id]
            for old_capability in registered_module.capabilities:
                if old_capability.name in self._capabilities:
                    if module_id in self._capabilities[old_capability.name]:
                        self._capabilities[old_capability.name].remove(module_id)
                        if not self._capabilities[old_capability.name]:
                            del self._capabilities[old_capability.name]
            registered_module.capabilities = capabilities
            for capability in capabilities:
                if capability.name not in self._capabilities:
                    self._capabilities[capability.name] = []
                if module_id not in self._capabilities[capability.name]:
                    self._capabilities[capability.name].append(module_id)
            logger.debug(f'Updated capabilities for module {module_id}: {[c.name for c in capabilities]}')

    async def update_module_health(self, module_id: str, health_status: 'ModuleHealth'):
        """
        Update health status for a registered module.
        
        Args:
            module_id: Unique identifier of the module
            health_status: Current health status of the module
        """
        with self._lock:
            if module_id not in self._modules:
                logger.warning(f'Attempted to update health for unknown module: {module_id}')
                return
            registered_module = self._modules[module_id]
            registered_module.last_health_check = datetime.now()
            registered_module.last_health_status = health_status
            if health_status.capabilities != registered_module.capabilities:
                await self.update_module_capabilities(module_id, health_status.capabilities)

    def get_module(self, module_id: str) -> Optional[RegisteredModule]:
        """
        Get information about a registered module.
        
        Args:
            module_id: Unique identifier of the module
            
        Returns:
            RegisteredModule information or None if not found
        """
        with self._lock:
            return self._modules.get(module_id)

    def get_all_modules(self) -> List[RegisteredModule]:
        """Get information about all registered modules."""
        with self._lock:
            return list(self._modules.values())

    def get_healthy_modules(self) -> List[RegisteredModule]:
        """Get all modules that are currently healthy."""
        with self._lock:
            return [module for module in self._modules.values() if module.is_healthy]

    def get_modules_by_capability(self, capability_name: str) -> List[RegisteredModule]:
        """
        Get all modules that provide a specific capability.
        
        Args:
            capability_name: Name of the capability to search for
            
        Returns:
            List of modules that provide the capability
        """
        with self._lock:
            if capability_name not in self._capabilities:
                return []
            module_ids = self._capabilities[capability_name]
            return [self._modules[module_id] for module_id in module_ids if module_id in self._modules]

    def get_available_capabilities(self) -> List[str]:
        """Get list of all available capabilities in the system."""
        with self._lock:
            return list(self._capabilities.keys())

    async def discover_service(self, capability_name: str, prefer_healthy: bool=True) -> Optional[RegisteredModule]:
        """
        Discover a service that provides a specific capability.
        
        Args:
            capability_name: Name of the capability needed
            prefer_healthy: Whether to prefer healthy modules
            
        Returns:
            A module that provides the capability, or None if not found
        """
        modules = self.get_modules_by_capability(capability_name)
        if not modules:
            return None
        if prefer_healthy:
            healthy_modules = [m for m in modules if m.is_healthy]
            if healthy_modules:
                return healthy_modules[0]
        return modules[0] if modules else None

    def add_dependency(self, dependent_id: str, dependency_id: str):
        """
        Add a dependency relationship between modules.
        
        Args:
            dependent_id: Module that depends on another
            dependency_id: Module that is depended upon
        """
        with self._lock:
            if dependent_id not in self._modules or dependency_id not in self._modules:
                logger.warning(f'Cannot add dependency: one or both modules not registered')
                return
            self._modules[dependent_id].dependencies.add(dependency_id)
            self._modules[dependency_id].dependents.add(dependent_id)
            logger.debug(f'Added dependency: {dependent_id} -> {dependency_id}')

    def remove_dependency(self, dependent_id: str, dependency_id: str):
        """
        Remove a dependency relationship between modules.
        
        Args:
            dependent_id: Module that depends on another
            dependency_id: Module that is depended upon
        """
        with self._lock:
            if dependent_id in self._modules:
                self._modules[dependent_id].dependencies.discard(dependency_id)
            if dependency_id in self._modules:
                self._modules[dependency_id].dependents.discard(dependent_id)
            logger.debug(f'Removed dependency: {dependent_id} -> {dependency_id}')

    def get_dependency_graph(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the complete dependency graph for all modules.
        
        Returns:
            Dictionary representing the dependency graph
        """
        with self._lock:
            graph = {}
            for module_id, registered_module in self._modules.items():
                graph[module_id] = {'dependencies': list(registered_module.dependencies), 'dependents': list(registered_module.dependents), 'is_healthy': registered_module.is_healthy, 'capabilities': [c.name for c in registered_module.capabilities]}
            return graph

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            Dictionary containing system-wide health information
        """
        with self._lock:
            total_modules = len(self._modules)
            healthy_modules = len([m for m in self._modules.values() if m.is_healthy])
            if total_modules == 0:
                health_percentage = 100.0
                overall_status = 'healthy'
            else:
                health_percentage = healthy_modules / total_modules * 100
                if health_percentage >= 90:
                    overall_status = 'healthy'
                elif health_percentage >= 70:
                    overall_status = 'degraded'
                else:
                    overall_status = 'unhealthy'
            return {'registry_id': self._registry_id, 'overall_status': overall_status, 'health_percentage': health_percentage, 'total_modules': total_modules, 'healthy_modules': healthy_modules, 'degraded_modules': total_modules - healthy_modules, 'total_capabilities': len(self._capabilities), 'uptime': (datetime.now() - self._created_at).total_seconds(), 'last_health_check': datetime.now().isoformat()}

    def _start_health_monitoring(self):
        """Start periodic health monitoring for all registered modules."""
        if self._health_check_task and (not self._health_check_task.done()):
            return
        self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
        logger.info('Started registry health monitoring')

    def _stop_health_monitoring(self):
        """Stop periodic health monitoring."""
        if self._health_check_task:
            self._health_check_task.cancel()
            logger.info('Stopped registry health monitoring')

    async def _health_monitoring_loop(self):
        """Main health monitoring loop for the registry."""
        try:
            while True:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self._health_check_interval.total_seconds())
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f'Error in registry health monitoring: {e}')
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info('Registry health monitoring cancelled')

    async def _perform_health_checks(self):
        """Perform health checks on all registered modules."""
        with self._lock:
            modules_to_check = list(self._modules.values())
        for registered_module in modules_to_check:
            try:
                health_status = await registered_module.module.perform_health_check()
                await self.update_module_health(registered_module.module_id, health_status)
            except Exception as e:
                logger.error(f'Health check failed for module {registered_module.module_id}: {e}')

    async def shutdown(self):
        """Gracefully shutdown the registry."""
        logger.info('Shutting down GlobalRegistry')
        self._stop_health_monitoring()
        if self._health_check_task:
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        with self._lock:
            self._modules.clear()
            self._capabilities.clear()
        logger.info('GlobalRegistry shutdown complete')

def get_global_registry() -> GlobalRegistry:
    """
    Get the global registry instance.
    
    Returns:
        The singleton GlobalRegistry instance
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = GlobalRegistry()
        return _global_registry

def reset_global_registry():
    """Reset the global registry (primarily for testing)."""
    global _global_registry
    with _registry_lock:
        if _global_registry:
            pass
        _global_registry = GlobalRegistry()

@property
def is_healthy(self) -> bool:
    """Check if module is currently healthy."""
    if not self.last_health_status:
        return False
    return self.last_health_status.is_healthy

@property
def uptime(self) -> timedelta:
    """Calculate module uptime since registration."""
    return datetime.now() - self.registration_time

def __init__(self):
    """Initialize the global registry."""
    self._modules: Dict[str, RegisteredModule] = {}
    self._capabilities: Dict[str, List[str]] = {}
    self._lock = Lock()
    self._health_check_task: Optional[asyncio.Task] = None
    self._health_check_interval = timedelta(seconds=60)
    self._registry_id = str(uuid4())
    self._created_at = datetime.now()
    logger.info(f'GlobalRegistry initialized: {self._registry_id}')

def register_module(self, module: 'ReflectiveModuleBase', module_id: str):
    """
        Register an RM module with the global registry.
        
        Args:
            module: The RM module to register
            module_id: Unique identifier for the module
        """
    with self._lock:
        if module_id in self._modules:
            logger.warning(f'Module {module_id} already registered, updating registration')
        registered_module = RegisteredModule(module_id=module_id, module=module, registration_time=datetime.now())
        self._modules[module_id] = registered_module
        if len(self._modules) == 1 and (not self._health_check_task):
            self._start_health_monitoring()
        logger.info(f'Module registered: {module_id}')

def unregister_module(self, module_id: str):
    """
        Unregister an RM module from the global registry.
        
        Args:
            module_id: Unique identifier of the module to unregister
        """
    with self._lock:
        if module_id not in self._modules:
            logger.warning(f'Attempted to unregister unknown module: {module_id}')
            return
        registered_module = self._modules[module_id]
        for capability_name in list(self._capabilities.keys()):
            if module_id in self._capabilities[capability_name]:
                self._capabilities[capability_name].remove(module_id)
                if not self._capabilities[capability_name]:
                    del self._capabilities[capability_name]
        for dependent_id in registered_module.dependents:
            if dependent_id in self._modules:
                self._modules[dependent_id].dependencies.discard(module_id)
        for dependency_id in registered_module.dependencies:
            if dependency_id in self._modules:
                self._modules[dependency_id].dependents.discard(module_id)
        del self._modules[module_id]
        logger.info(f'Module unregistered: {module_id}')
        if not self._modules and self._health_check_task:
            self._stop_health_monitoring()

def get_module(self, module_id: str) -> Optional[RegisteredModule]:
    """
        Get information about a registered module.
        
        Args:
            module_id: Unique identifier of the module
            
        Returns:
            RegisteredModule information or None if not found
        """
    with self._lock:
        return self._modules.get(module_id)

def get_all_modules(self) -> List[RegisteredModule]:
    """Get information about all registered modules."""
    with self._lock:
        return list(self._modules.values())

def get_healthy_modules(self) -> List[RegisteredModule]:
    """Get all modules that are currently healthy."""
    with self._lock:
        return [module for module in self._modules.values() if module.is_healthy]

def get_modules_by_capability(self, capability_name: str) -> List[RegisteredModule]:
    """
        Get all modules that provide a specific capability.
        
        Args:
            capability_name: Name of the capability to search for
            
        Returns:
            List of modules that provide the capability
        """
    with self._lock:
        if capability_name not in self._capabilities:
            return []
        module_ids = self._capabilities[capability_name]
        return [self._modules[module_id] for module_id in module_ids if module_id in self._modules]

def get_available_capabilities(self) -> List[str]:
    """Get list of all available capabilities in the system."""
    with self._lock:
        return list(self._capabilities.keys())

def add_dependency(self, dependent_id: str, dependency_id: str):
    """
        Add a dependency relationship between modules.
        
        Args:
            dependent_id: Module that depends on another
            dependency_id: Module that is depended upon
        """
    with self._lock:
        if dependent_id not in self._modules or dependency_id not in self._modules:
            logger.warning(f'Cannot add dependency: one or both modules not registered')
            return
        self._modules[dependent_id].dependencies.add(dependency_id)
        self._modules[dependency_id].dependents.add(dependent_id)
        logger.debug(f'Added dependency: {dependent_id} -> {dependency_id}')

def remove_dependency(self, dependent_id: str, dependency_id: str):
    """
        Remove a dependency relationship between modules.
        
        Args:
            dependent_id: Module that depends on another
            dependency_id: Module that is depended upon
        """
    with self._lock:
        if dependent_id in self._modules:
            self._modules[dependent_id].dependencies.discard(dependency_id)
        if dependency_id in self._modules:
            self._modules[dependency_id].dependents.discard(dependent_id)
        logger.debug(f'Removed dependency: {dependent_id} -> {dependency_id}')

def get_dependency_graph(self) -> Dict[str, Dict[str, Any]]:
    """
        Get the complete dependency graph for all modules.
        
        Returns:
            Dictionary representing the dependency graph
        """
    with self._lock:
        graph = {}
        for module_id, registered_module in self._modules.items():
            graph[module_id] = {'dependencies': list(registered_module.dependencies), 'dependents': list(registered_module.dependents), 'is_healthy': registered_module.is_healthy, 'capabilities': [c.name for c in registered_module.capabilities]}
        return graph

def _start_health_monitoring(self):
    """Start periodic health monitoring for all registered modules."""
    if self._health_check_task and (not self._health_check_task.done()):
        return
    self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
    logger.info('Started registry health monitoring')

def _stop_health_monitoring(self):
    """Stop periodic health monitoring."""
    if self._health_check_task:
        self._health_check_task.cancel()
        logger.info('Stopped registry health monitoring')

@property
def is_healthy(self) -> bool:
    """Check if module is currently healthy."""
    if not self.last_health_status:
        return False
    return self.last_health_status.is_healthy

@property
def uptime(self) -> timedelta:
    """Calculate module uptime since registration."""
    return datetime.now() - self.registration_time

def __init__(self):
    """Initialize the global registry."""
    self._modules: Dict[str, RegisteredModule] = {}
    self._capabilities: Dict[str, List[str]] = {}
    self._lock = Lock()
    self._health_check_task: Optional[asyncio.Task] = None
    self._health_check_interval = timedelta(seconds=60)
    self._registry_id = str(uuid4())
    self._created_at = datetime.now()
    logger.info(f'GlobalRegistry initialized: {self._registry_id}')

def register_module(self, module: 'ReflectiveModuleBase', module_id: str):
    """
        Register an RM module with the global registry.
        
        Args:
            module: The RM module to register
            module_id: Unique identifier for the module
        """
    with self._lock:
        if module_id in self._modules:
            logger.warning(f'Module {module_id} already registered, updating registration')
        registered_module = RegisteredModule(module_id=module_id, module=module, registration_time=datetime.now())
        self._modules[module_id] = registered_module
        if len(self._modules) == 1 and (not self._health_check_task):
            self._start_health_monitoring()
        logger.info(f'Module registered: {module_id}')

def unregister_module(self, module_id: str):
    """
        Unregister an RM module from the global registry.
        
        Args:
            module_id: Unique identifier of the module to unregister
        """
    with self._lock:
        if module_id not in self._modules:
            logger.warning(f'Attempted to unregister unknown module: {module_id}')
            return
        registered_module = self._modules[module_id]
        for capability_name in list(self._capabilities.keys()):
            if module_id in self._capabilities[capability_name]:
                self._capabilities[capability_name].remove(module_id)
                if not self._capabilities[capability_name]:
                    del self._capabilities[capability_name]
        for dependent_id in registered_module.dependents:
            if dependent_id in self._modules:
                self._modules[dependent_id].dependencies.discard(module_id)
        for dependency_id in registered_module.dependencies:
            if dependency_id in self._modules:
                self._modules[dependency_id].dependents.discard(module_id)
        del self._modules[module_id]
        logger.info(f'Module unregistered: {module_id}')
        if not self._modules and self._health_check_task:
            self._stop_health_monitoring()

def get_module(self, module_id: str) -> Optional[RegisteredModule]:
    """
        Get information about a registered module.
        
        Args:
            module_id: Unique identifier of the module
            
        Returns:
            RegisteredModule information or None if not found
        """
    with self._lock:
        return self._modules.get(module_id)

def get_all_modules(self) -> List[RegisteredModule]:
    """Get information about all registered modules."""
    with self._lock:
        return list(self._modules.values())

def get_healthy_modules(self) -> List[RegisteredModule]:
    """Get all modules that are currently healthy."""
    with self._lock:
        return [module for module in self._modules.values() if module.is_healthy]

def get_modules_by_capability(self, capability_name: str) -> List[RegisteredModule]:
    """
        Get all modules that provide a specific capability.
        
        Args:
            capability_name: Name of the capability to search for
            
        Returns:
            List of modules that provide the capability
        """
    with self._lock:
        if capability_name not in self._capabilities:
            return []
        module_ids = self._capabilities[capability_name]
        return [self._modules[module_id] for module_id in module_ids if module_id in self._modules]

def get_available_capabilities(self) -> List[str]:
    """Get list of all available capabilities in the system."""
    with self._lock:
        return list(self._capabilities.keys())

def add_dependency(self, dependent_id: str, dependency_id: str):
    """
        Add a dependency relationship between modules.
        
        Args:
            dependent_id: Module that depends on another
            dependency_id: Module that is depended upon
        """
    with self._lock:
        if dependent_id not in self._modules or dependency_id not in self._modules:
            logger.warning(f'Cannot add dependency: one or both modules not registered')
            return
        self._modules[dependent_id].dependencies.add(dependency_id)
        self._modules[dependency_id].dependents.add(dependent_id)
        logger.debug(f'Added dependency: {dependent_id} -> {dependency_id}')

def remove_dependency(self, dependent_id: str, dependency_id: str):
    """
        Remove a dependency relationship between modules.
        
        Args:
            dependent_id: Module that depends on another
            dependency_id: Module that is depended upon
        """
    with self._lock:
        if dependent_id in self._modules:
            self._modules[dependent_id].dependencies.discard(dependency_id)
        if dependency_id in self._modules:
            self._modules[dependency_id].dependents.discard(dependent_id)
        logger.debug(f'Removed dependency: {dependent_id} -> {dependency_id}')

def get_dependency_graph(self) -> Dict[str, Dict[str, Any]]:
    """
        Get the complete dependency graph for all modules.
        
        Returns:
            Dictionary representing the dependency graph
        """
    with self._lock:
        graph = {}
        for module_id, registered_module in self._modules.items():
            graph[module_id] = {'dependencies': list(registered_module.dependencies), 'dependents': list(registered_module.dependents), 'is_healthy': registered_module.is_healthy, 'capabilities': [c.name for c in registered_module.capabilities]}
        return graph

def _start_health_monitoring(self):
    """Start periodic health monitoring for all registered modules."""
    if self._health_check_task and (not self._health_check_task.done()):
        return
    self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
    logger.info('Started registry health monitoring')

def _stop_health_monitoring(self):
    """Stop periodic health monitoring."""
    if self._health_check_task:
        self._health_check_task.cancel()
        logger.info('Stopped registry health monitoring')

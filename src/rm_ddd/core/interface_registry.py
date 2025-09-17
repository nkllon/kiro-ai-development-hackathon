#!/usr/bin/env python3
"""
Interface Registry - RDI Compliant
==================================

Comprehensive interface registry system for discovering and managing
interfaces, classes, functions, and enums within the codebase.

Author: Beast Mode Framework
Date: 2025-09-16
Version: 2.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set
import inspect
from pathlib import Path

from .base_reflective_module import ReflectiveModule, ModuleCapability, ModuleStatus


class InterfaceType(Enum):
    """Types of interfaces that can be registered"""
    CLASS = "class"
    FUNCTION = "function"
    ENUM = "enum"
    MODULE = "module"
    INTERFACE = "interface"
    DATACLASS = "dataclass"
    EXCEPTION = "exception"


class InterfaceStatus(Enum):
    """Status of registered interfaces"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    STABLE = "stable"
    UNKNOWN = "unknown"


@dataclass
class InterfaceMetadata:
    """Metadata for a registered interface"""
    interface_id: str
    interface_type: InterfaceType
    name: str
    module_path: str
    version: str = "1.0.0"
    status: InterfaceStatus = InterfaceStatus.UNKNOWN
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[ModuleCapability] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class InterfaceSearchResult:
    """Result of interface search"""
    interfaces: List[InterfaceMetadata]
    total_count: int
    search_query: str
    search_filters: Dict[str, Any]
    search_time: float


class InterfaceRegistry(ReflectiveModule):
    """
    Comprehensive interface registry system - RDI Compliant
    
    Discovers, registers, and manages all interfaces, classes, functions,
    and enums within the codebase.
    """
    
    def __init__(self, project_root: str = "."):
        super().__init__("interface_registry", "2.0.0")
        self.project_root = Path(project_root)
        self._interfaces: Dict[str, InterfaceMetadata] = {}
        self._type_index: Dict[InterfaceType, Set[str]] = {
            interface_type: set() for interface_type in InterfaceType
        }
        self._status_index: Dict[InterfaceStatus, Set[str]] = {
            status: set() for status in InterfaceStatus
        }
        self._capability_index: Dict[ModuleCapability, Set[str]] = {
            capability: set() for capability in ModuleCapability
        }
        self._search_cache: Dict[str, InterfaceSearchResult] = {}
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            'name': self.module_name,
            'version': self.version,
            'module_id': self.module_id,
            'total_interfaces': len(self._interfaces),
            'interface_types': {t.value: len(self._type_index[t]) for t in InterfaceType},
            'status_counts': {s.value: len(self._status_index[s]) for s in InterfaceStatus}
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies - RDI Compliant"""
        return [
            'src.rm_ddd.core.base_reflective_module',
            'inspect',
            'pathlib'
        ]
    
    def check_health(self) -> 'ModuleHealth':
        """Check module health - RDI Compliant"""
        from .base_reflective_module import ModuleHealth
        
        issues = []
        health_score = 1.0
        
        # Check if registry is empty
        if len(self._interfaces) == 0:
            issues.append("No interfaces registered")
            health_score -= 0.3
        
        # Check for duplicate interface IDs
        interface_ids = list(self._interfaces.keys())
        if len(interface_ids) != len(set(interface_ids)):
            issues.append("Duplicate interface IDs detected")
            health_score -= 0.2
        
        # Check index consistency
        total_indexed = sum(len(interfaces) for interfaces in self._type_index.values())
        if total_indexed != len(self._interfaces):
            issues.append("Index inconsistency detected")
            health_score -= 0.2
        
        status = ModuleStatus.HEALTHY if health_score >= 0.8 else ModuleStatus.WARNING
        if health_score < 0.5:
            status = ModuleStatus.ERROR
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=max(0.0, health_score),
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics={
                'total_interfaces': len(self._interfaces),
                'index_consistency': total_indexed == len(self._interfaces),
                'cache_size': len(self._search_cache)
            },
            last_check=datetime.now()
        )
    
    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Register an interface with the registry"""
        try:
            # Check for duplicate ID
            if interface.interface_id in self._interfaces:
                self.unregister_interface(interface.interface_id)
            
            # Register the interface
            self._interfaces[interface.interface_id] = interface
            
            # Update indexes
            self._type_index[interface.interface_type].add(interface.interface_id)
            self._status_index[interface.status].add(interface.interface_id)
            for capability in interface.capabilities:
                self._capability_index[capability].add(interface.interface_id)
            
            # Clear search cache
            self._search_cache.clear()
            
            return True
            
        except Exception as e:
            return False
    
    def unregister_interface(self, interface_id: str) -> bool:
        """Unregister an interface from the registry"""
        try:
            if interface_id not in self._interfaces:
                return False
            
            interface = self._interfaces[interface_id]
            
            # Remove from indexes
            self._type_index[interface.interface_type].discard(interface_id)
            self._status_index[interface.status].discard(interface_id)
            for capability in interface.capabilities:
                self._capability_index[capability].discard(interface_id)
            
            # Remove from registry
            del self._interfaces[interface_id]
            
            # Clear search cache
            self._search_cache.clear()
            
            return True
            
        except Exception as e:
            return False
    
    def get_interface(self, interface_id: str) -> Optional[InterfaceMetadata]:
        """Get interface metadata by ID"""
        return self._interfaces.get(interface_id)
    
    def search_interfaces(self, 
                         query: str = "",
                         interface_type: Optional[InterfaceType] = None,
                         status: Optional[InterfaceStatus] = None,
                         capabilities: Optional[List[ModuleCapability]] = None,
                         tags: Optional[List[str]] = None) -> InterfaceSearchResult:
        """Search for interfaces with various filters"""
        import time
        start_time = time.time()
        
        # Start with all interfaces
        candidate_ids = set(self._interfaces.keys())
        
        # Apply filters
        if interface_type:
            candidate_ids &= self._type_index[interface_type]
        
        if status:
            candidate_ids &= self._status_index[status]
        
        if capabilities:
            for capability in capabilities:
                candidate_ids &= self._capability_index[capability]
        
        # Apply text search
        if query:
            query_lower = query.lower()
            filtered_ids = set()
            for interface_id in candidate_ids:
                interface = self._interfaces[interface_id]
                if (query_lower in interface.name.lower() or 
                    query_lower in interface.description.lower() or
                    query_lower in interface.module_path.lower()):
                    filtered_ids.add(interface_id)
            candidate_ids = filtered_ids
        
        # Apply tag filter
        if tags:
            filtered_ids = set()
            for interface_id in candidate_ids:
                interface = self._interfaces[interface_id]
                if any(tag in interface.tags for tag in tags):
                    filtered_ids.add(interface_id)
            candidate_ids = filtered_ids
        
        # Get results
        results = [self._interfaces[interface_id] for interface_id in candidate_ids]
        
        # Create search result
        search_result = InterfaceSearchResult(
            interfaces=results,
            total_count=len(results),
            search_query=query,
            search_filters={
                'interface_type': interface_type.value if interface_type else None,
                'status': status.value if status else None,
                'capabilities': [cap.value for cap in capabilities] if capabilities else None,
                'tags': tags
            },
            search_time=time.time() - start_time
        )
        
        return search_result
    
    def discover_interfaces(self, module_path: str) -> List[InterfaceMetadata]:
        """Discover interfaces in a module"""
        interfaces = []
        
        try:
            # Import the module
            module = __import__(module_path, fromlist=[''])
            
            # Discover classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if not name.startswith('_'):
                    interface = InterfaceMetadata(
                        interface_id=f"{module_path}.{name}",
                        interface_type=InterfaceType.CLASS,
                        name=name,
                        module_path=module_path,
                        description=obj.__doc__ or "",
                        capabilities=[ModuleCapability.CORE_FUNCTIONALITY]
                    )
                    interfaces.append(interface)
            
            # Discover functions
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith('_'):
                    interface = InterfaceMetadata(
                        interface_id=f"{module_path}.{name}",
                        interface_type=InterfaceType.FUNCTION,
                        name=name,
                        module_path=module_path,
                        description=obj.__doc__ or "",
                        capabilities=[ModuleCapability.CORE_FUNCTIONALITY]
                    )
                    interfaces.append(interface)
            
            # Discover enums
            for name, obj in inspect.getmembers(module, lambda x: inspect.isclass(x) and issubclass(x, Enum)):
                if not name.startswith('_'):
                    interface = InterfaceMetadata(
                        interface_id=f"{module_path}.{name}",
                        interface_type=InterfaceType.ENUM,
                        name=name,
                        module_path=module_path,
                        description=obj.__doc__ or "",
                        capabilities=[ModuleCapability.CORE_FUNCTIONALITY]
                    )
                    interfaces.append(interface)
                    
        except Exception as e:
            pass
        
        return interfaces
    
    def auto_discover_all(self) -> int:
        """Automatically discover and register all interfaces in the project"""
        discovered_count = 0
        
        # Find all Python modules in the project
        for py_file in self.project_root.rglob("src/**/*.py"):
            if py_file.name == "__init__.py":
                continue
            
            # Convert file path to module path
            relative_path = py_file.relative_to(self.project_root)
            module_path = str(relative_path.with_suffix('')).replace('/', '.')
            
            # Discover interfaces in this module
            interfaces = self.discover_interfaces(module_path)
            
            # Register discovered interfaces
            for interface in interfaces:
                if self.register_interface(interface):
                    discovered_count += 1
        
        return discovered_count
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        return {
            'total_interfaces': len(self._interfaces),
            'by_type': {t.value: len(self._type_index[t]) for t in InterfaceType},
            'by_status': {s.value: len(self._status_index[s]) for s in InterfaceStatus},
            'by_capability': {c.value: len(self._capability_index[c]) for c in ModuleCapability},
            'cache_size': len(self._search_cache),
            'last_updated': datetime.now().isoformat()
        }


# Global registry instance
_global_registry: Optional[InterfaceRegistry] = None

def get_global_registry() -> InterfaceRegistry:
    """Get the global interface registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = InterfaceRegistry()
    return _global_registry

def register_interface(interface: InterfaceMetadata) -> bool:
    """Register an interface with the global registry"""
    return get_global_registry().register_interface(interface)

def search_interfaces(**kwargs) -> InterfaceSearchResult:
    """Search interfaces in the global registry"""
    return get_global_registry().search_interfaces(**kwargs)

def auto_discover_all() -> int:
    """Auto-discover all interfaces in the project"""
    return get_global_registry().auto_discover_all()

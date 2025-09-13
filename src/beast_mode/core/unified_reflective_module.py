"""
Unified ReflectiveModule Base Class with Integrated Registry

This is the SINGLE, CANONICAL ReflectiveModule implementation for the entire Beast Mode framework.
All other ReflectiveModule definitions are deprecated and should be replaced with this one.

Features:
- Automatic registry integration with introspection
- Configurable defaults with sensible fallbacks
- Built-in compliance validation
- Zero-configuration registration
- Domain vocabulary auto-extraction
"""

import inspect
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Callable
import functools

# Import the registry system
try:
    from ..interface_governance.interface_registry import (
        BeastModeInterfaceRegistry, InterfaceMetadata, InterfaceType, InterfaceStatus
    )
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    # Fallback classes if registry not available
    class InterfaceType(Enum):
        REFLECTIVE_MODULE = "reflective_module"
        DOMAIN_SERVICE = "domain_service"
        API_INTERFACE = "api_interface"
        DATA_MODEL = "data_model"
        VALIDATION_RULE = "validation_rule"
        CONFIGURATION = "configuration"
    
    class InterfaceStatus(Enum):
        ACTIVE = "active"
        DEPRECATED = "deprecated"
        CONFLICT = "conflict"
        DUPLICATE = "duplicate"


class ModuleStatus(Enum):
    """Module operational status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class ModuleCapability(Enum):
    """Module capability types"""
    HEALTH_MONITORING = "health_monitoring"
    METRICS_COLLECTION = "metrics_collection"
    CONFIGURATION_MANAGEMENT = "configuration_management"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    ERROR_HANDLING = "error_handling"
    LOGGING = "logging"
    PERFORMANCE_MONITORING = "performance_monitoring"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    VALIDATION = "validation"


@dataclass
class ModuleHealth:
    """Module health information"""
    module_id: str
    status: ModuleStatus
    health_score: float
    issues: List[str] = field(default_factory=list)
    capabilities: List[ModuleCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.now)


def registered(auto_register: bool = True, interface_type: InterfaceType = InterfaceType.REFLECTIVE_MODULE):
    """
    Decorator for automatic ReflectiveModule registration.
    
    Args:
        auto_register: Whether to automatically register the class
        interface_type: Type of interface for registration
    """
    def decorator(cls):
        if not issubclass(cls, ReflectiveModule):
            raise ValueError(f"@registered can only be used on ReflectiveModule subclasses, got {cls}")
        
        # Add registration metadata to the class
        cls._registry_config = {
            'auto_register': auto_register,
            'interface_type': interface_type,
            'registered_at': datetime.now()
        }
        
        # Override __init__ to handle automatic registration
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def new_init(self, *args, **kwargs):
            # Call original __init__
            original_init(self, *args, **kwargs)
            
            # Auto-register if enabled
            if auto_register and hasattr(self, '_register_self'):
                self._register_self()
        
        cls.__init__ = new_init
        return cls
    
    return decorator


class ReflectiveModule(ABC):
    """
    Unified ReflectiveModule Base Class with Integrated Registry
    
    This is the SINGLE, CANONICAL ReflectiveModule implementation for the entire
    Beast Mode framework. All modules that inherit from this class automatically
    gain registry integration, compliance validation, and systematic capabilities.
    
    Key Features:
    - Automatic registry registration with introspection
    - Configurable defaults with sensible fallbacks
    - Built-in compliance validation
    - Zero-configuration registration
    - Domain vocabulary auto-extraction
    """
    
    # Class-level registry configuration
    _registry_config = {
        'auto_register': True,
        'interface_type': InterfaceType.REFLECTIVE_MODULE,
        'registered_at': None
    }
    
    def __init__(self, module_name: Optional[str] = None, version: str = "1.0.0"):
        """
        Initialize the reflective module with automatic registry integration.
        
        Args:
            module_name: Optional module name. If not provided, uses class name.
            version: Module version string.
        """
        self.module_name = module_name or self.__class__.__name__
        self.version = version
        self._start_time = datetime.now()
        self._last_activity = datetime.now()
        self._error_count = 0
        self._warning_count = 0
        self._registry_id = None
        
        # Initialize registry integration
        self._initialize_registry_integration()
        
        # Auto-register if configured
        if self._registry_config.get('auto_register', True):
            self._register_self()
    
    def _initialize_registry_integration(self):
        """Initialize registry integration with introspection."""
        if not REGISTRY_AVAILABLE:
            return
        
        # Get source file information
        frame = inspect.currentframe().f_back
        self._source_file = frame.f_code.co_filename
        self._source_line = frame.f_lineno
        
        # Extract domain terms from class name and docstring
        self._domain_terms = self._extract_domain_terms()
        
        # Determine interface type based on class name patterns
        self._interface_type = self._determine_interface_type()
    
    def _extract_domain_terms(self) -> Set[str]:
        """Extract domain terms from class name and docstring."""
        terms = set()
        
        # Extract from class name (camelCase to snake_case)
        class_name = self.__class__.__name__
        import re
        words = re.findall(r'[A-Z][a-z]*', class_name)
        terms.update(word.lower() for word in words)
        
        # Extract from docstring
        if self.__doc__:
            docstring = self.__doc__.lower()
            # Simple term extraction (can be enhanced)
            doc_terms = re.findall(r'\b[a-z_]+\b', docstring)
            terms.update(term for term in doc_terms if len(term) > 3)
        
        return terms
    
    def _determine_interface_type(self) -> InterfaceType:
        """Determine interface type based on class name patterns."""
        class_name = self.__class__.__name__.lower()
        
        if any(term in class_name for term in ['service', 'manager', 'handler']):
            return InterfaceType.DOMAIN_SERVICE
        elif any(term in class_name for term in ['api', 'client', 'server']):
            return InterfaceType.API_INTERFACE
        elif any(term in class_name for term in ['model', 'entity', 'data']):
            return InterfaceType.DATA_MODEL
        elif any(term in class_name for term in ['rule', 'validator', 'validation']):
            return InterfaceType.VALIDATION_RULE
        elif any(term in class_name for term in ['config', 'settings', 'configuration']):
            return InterfaceType.CONFIGURATION
        else:
            return InterfaceType.REFLECTIVE_MODULE
    
    def _register_self(self):
        """Register this module instance with the registry."""
        if not REGISTRY_AVAILABLE:
            return
        
        try:
            registry = BeastModeInterfaceRegistry()
            
            # Create interface metadata with introspection
            metadata = InterfaceMetadata(
                interface_name=self.__class__.__name__,
                interface_type=self._interface_type,
                file_path=self._source_file,
                line_number=self._source_line,
                methods=self._get_method_signatures(),
                domain_terms=list(self._domain_terms),
                status=InterfaceStatus.ACTIVE
            )
            
            # Register the interface
            success = registry.register_interface(metadata)
            if success:
                self._registry_id = f"{self.__class__.__name__}_{self._interface_type.value}"
                self._last_activity = datetime.now()
        
        except Exception as e:
            # Log error but don't fail initialization
            print(f"Warning: Failed to register {self.__class__.__name__}: {e}")
    
    def _get_method_signatures(self) -> List[str]:
        """Get method signatures for registry."""
        methods = []
        
        for name, method in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods.append(name)
        
        return methods
    
    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get module information with registry integration.
        
        Returns:
            Dict containing module metadata including registry information.
        """
        base_info = {
            "name": self.module_name,
            "version": self.version,
            "type": "reflective_module",
            "created_at": self._start_time.isoformat(),
            "last_activity": self._last_activity.isoformat(),
            "error_count": self._error_count,
            "warning_count": self._warning_count
        }
        
        # Add registry information if available
        if self._registry_id:
            base_info.update({
                "registry_id": self._registry_id,
                "interface_type": self._interface_type.value if hasattr(self._interface_type, 'value') else str(self._interface_type),
                "domain_terms": list(self._domain_terms),
                "source_file": self._source_file,
                "source_line": self._source_line
            })
        
        return base_info
    
    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """
        Get module capabilities.
        
        Returns:
            List of ModuleCapability enums this module supports.
        """
        # Default capabilities based on implemented methods
        capabilities = []
        
        if hasattr(self, 'get_health_status') or hasattr(self, 'check_health'):
            capabilities.append(ModuleCapability.HEALTH_MONITORING)
        
        if hasattr(self, 'get_metrics'):
            capabilities.append(ModuleCapability.METRICS_COLLECTION)
        
        if hasattr(self, 'get_configuration'):
            capabilities.append(ModuleCapability.CONFIGURATION_MANAGEMENT)
        
        return capabilities
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Get module dependencies.
        
        Returns:
            List of module IDs this module depends on.
        """
        # Default: no dependencies
        return []
    
    @abstractmethod
    def check_health(self) -> ModuleHealth:
        """
        Check module health with registry integration.
        
        Returns:
            ModuleHealth object with current health status.
        """
        # Default health check implementation
        status = ModuleStatus.HEALTHY
        health_score = 100.0
        issues = []
        
        # Check registry registration status
        if REGISTRY_AVAILABLE and not self._registry_id:
            status = ModuleStatus.WARNING
            health_score -= 10.0
            issues.append("Not registered in interface registry")
        
        # Check error count
        if self._error_count > 0:
            status = ModuleStatus.ERROR if self._error_count > 5 else ModuleStatus.WARNING
            health_score -= min(self._error_count * 5, 50)
            issues.append(f"Error count: {self._error_count}")
        
        return ModuleHealth(
            module_id=self._registry_id or self.module_name,
            status=status,
            health_score=max(health_score, 0.0),
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get module configuration.
        
        Returns:
            Dict containing current configuration.
        """
        return {
            "module_name": self.module_name,
            "version": self.version,
            "auto_register": self._registry_config.get('auto_register', True),
            "interface_type": self._interface_type.value if hasattr(self._interface_type, 'value') else str(self._interface_type)
        }
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get module metrics with registry integration.
        
        Returns:
            Dict containing performance and operational metrics.
        """
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        metrics = {
            "uptime_seconds": uptime,
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "last_activity": self._last_activity.isoformat(),
            "registry_registered": bool(self._registry_id),
            "domain_terms_count": len(self._domain_terms),
            "methods_count": len(self._get_method_signatures())
        }
        
        # Add registry-specific metrics if available
        if self._registry_id and REGISTRY_AVAILABLE:
            try:
                registry = BeastModeInterfaceRegistry()
                registry_status = registry.get_registry_status()
                metrics.update({
                    "registry_total_interfaces": registry_status.get('total_interfaces', 0),
                    "registry_duplicates": registry_status.get('duplicates', 0),
                    "registry_conflicts": registry_status.get('conflicts', 0)
                })
            except Exception:
                pass  # Don't fail metrics collection
        
        return metrics
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status (compatibility method).
        
        Returns:
            Dict containing health status information.
        """
        health = self.check_health()
        return {
            "status": health.status.value,
            "health_score": health.health_score,
            "issues": health.issues,
            "last_check": health.last_check.isoformat()
        }
    
    def is_healthy(self) -> bool:
        """
        Check if module is healthy.
        
        Returns:
            True if module is healthy, False otherwise.
        """
        health = self.check_health()
        return health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING]
    
    def get_health_indicators(self) -> List[str]:
        """
        Get health indicators for monitoring.
        
        Returns:
            List of health indicator strings.
        """
        indicators = []
        
        if self.is_healthy():
            indicators.append("✅ Module operational")
        else:
            indicators.append("❌ Module unhealthy")
        
        if self._registry_id:
            indicators.append("✅ Registry registered")
        else:
            indicators.append("⚠️ Not registry registered")
        
        if self._error_count == 0:
            indicators.append("✅ No errors")
        else:
            indicators.append(f"⚠️ {self._error_count} errors")
        
        return indicators
    
    def get_module_status(self) -> str:
        """
        Get module status string.
        
        Returns:
            Current module status.
        """
        health = self.check_health()
        return health.status.value
    
    def _get_primary_responsibility(self) -> str:
        """
        Get primary responsibility description.
        
        Returns:
            Description of primary responsibility.
        """
        # Extract from class name and docstring
        class_name = self.__class__.__name__
        docstring = self.__doc__ or ""
        
        if docstring:
            # Use first line of docstring
            first_line = docstring.split('\n')[0].strip()
            if first_line:
                return first_line
        
        # Fallback to class name
        return f"Manages {class_name.lower().replace('module', '').replace('manager', '').replace('service', '')}"
    
    def update_activity(self):
        """Update last activity timestamp."""
        self._last_activity = datetime.now()
    
    def increment_error_count(self):
        """Increment error count."""
        self._error_count += 1
        self.update_activity()
    
    def increment_warning_count(self):
        """Increment warning count."""
        self._warning_count += 1
        self.update_activity()


# Convenience function for manual registration
def register_reflective_module(module: ReflectiveModule, 
                             interface_type: Optional[InterfaceType] = None) -> bool:
    """
    Manually register a ReflectiveModule instance.
    
    Args:
        module: ReflectiveModule instance to register
        interface_type: Optional interface type override
        
    Returns:
        True if registration successful, False otherwise
    """
    if not REGISTRY_AVAILABLE:
        return False
    
    try:
        registry = BeastModeInterfaceRegistry()
        
        # Create metadata
        metadata = InterfaceMetadata(
            interface_name=module.__class__.__name__,
            interface_type=interface_type or module._interface_type,
            file_path=module._source_file,
            line_number=module._source_line,
            methods=module._get_method_signatures(),
            domain_terms=list(module._domain_terms),
            status=InterfaceStatus.ACTIVE
        )
        
        return registry.register_interface(metadata)
    
    except Exception:
        return False


# Global registry for tracking instances
_module_instances: Dict[str, ReflectiveModule] = {}


def get_registered_modules() -> Dict[str, ReflectiveModule]:
    """
    Get all registered ReflectiveModule instances.
    
    Returns:
        Dict mapping registry IDs to module instances.
    """
    return _module_instances.copy()


def get_module_by_id(module_id: str) -> Optional[ReflectiveModule]:
    """
    Get module instance by registry ID.
    
    Args:
        module_id: Registry ID of the module
        
    Returns:
        ReflectiveModule instance or None if not found.
    """
    return _module_instances.get(module_id)


# Export the main classes
__all__ = [
    'ReflectiveModule',
    'ModuleStatus',
    'ModuleCapability', 
    'ModuleHealth',
    'registered',
    'register_reflective_module',
    'get_registered_modules',
    'get_module_by_id',
    'InterfaceType',
    'InterfaceStatus'
]

"""
Unified ReflectiveModule Base Class with Proper Class-Level Registry Integration

This is the CORRECTED ReflectiveModule implementation that properly separates
class-level interface definition from instance-level registration.

Key Design Principles:
- Class-level introspection happens once per class (static methods)
- Interface definition is a class property, not instance property
- Instance registration references the class-level interface definition
- Multiple instances of the same class share the same interface metadata
"""

import inspect
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Callable, ClassVar
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


@dataclass
class ClassInterfaceMetadata:
    """Class-level interface metadata (shared by all instances)"""
    interface_name: str
    interface_type: InterfaceType
    source_file: str
    source_line: int
    methods: List[str]
    domain_terms: Set[str]
    class_docstring: Optional[str] = None
    registered_at: Optional[datetime] = None


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
        
        return cls
    
    return decorator


class ReflectiveModule(ABC):
    """
    Unified ReflectiveModule Base Class with Proper Class-Level Registry Integration
    
    This implementation correctly separates class-level interface definition
    from instance-level registration, ensuring efficient and proper registry management.
    
    Key Design Features:
    - Class-level introspection happens once per class (static methods)
    - Interface definition is a class property, not instance property
    - Instance registration references the class-level interface definition
    - Multiple instances of the same class share the same interface metadata
    """
    
    # Class-level registry configuration (shared by all instances)
    _registry_config: ClassVar[Dict[str, Any]] = {
        'auto_register': True,
        'interface_type': InterfaceType.REFLECTIVE_MODULE,
        'registered_at': None
    }
    
    # Class-level interface metadata (shared by all instances)
    _class_interface_metadata: ClassVar[Optional[ClassInterfaceMetadata]] = None
    
    # Class-level registry ID (shared by all instances)
    _class_registry_id: ClassVar[Optional[str]] = None
    
    @classmethod
    def _initialize_class_registry_integration(cls) -> ClassInterfaceMetadata:
        """
        Initialize class-level registry integration with introspection.
        This happens ONCE per class, not per instance.
        
        Returns:
            ClassInterfaceMetadata object with class-level interface information
        """
        if not REGISTRY_AVAILABLE:
            return None
        
        # Get source file information for the class
        source_file = inspect.getfile(cls)
        source_line = inspect.getsourcelines(cls)[1]
        
        # Extract domain terms from class name and docstring
        domain_terms = cls._extract_class_domain_terms()
        
        # Determine interface type based on class name patterns
        interface_type = cls._determine_class_interface_type()
        
        # Get method signatures for the class
        methods = cls._get_class_method_signatures()
        
        # Get class docstring
        class_docstring = cls.__doc__
        
        # Create class-level interface metadata
        metadata = ClassInterfaceMetadata(
            interface_name=cls.__name__,
            interface_type=interface_type,
            source_file=source_file,
            source_line=source_line,
            methods=methods,
            domain_terms=domain_terms,
            class_docstring=class_docstring
        )
        
        # Store class-level metadata
        cls._class_interface_metadata = metadata
        
        return metadata
    
    @classmethod
    def _extract_class_domain_terms(cls) -> Set[str]:
        """Extract domain terms from class name and docstring."""
        terms = set()
        
        # Extract from class name (camelCase to snake_case)
        class_name = cls.__name__
        import re
        words = re.findall(r'[A-Z][a-z]*', class_name)
        terms.update(word.lower() for word in words)
        
        # Extract from docstring
        if cls.__doc__:
            docstring = cls.__doc__.lower()
            # Simple term extraction (can be enhanced)
            doc_terms = re.findall(r'\b[a-z_]+\b', docstring)
            terms.update(term for term in doc_terms if len(term) > 3)
        
        return terms
    
    @classmethod
    def _determine_class_interface_type(cls) -> InterfaceType:
        """Determine interface type based on class name patterns."""
        class_name = cls.__name__.lower()
        
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
    
    @classmethod
    def _get_class_method_signatures(cls) -> List[str]:
        """Get method signatures for the class."""
        methods = []
        
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods.append(name)
        
        return methods
    
    @classmethod
    def _register_class_interface(cls) -> bool:
        """
        Register the class interface with the registry.
        This happens ONCE per class, not per instance.
        
        Returns:
            True if registration successful, False otherwise
        """
        if not REGISTRY_AVAILABLE:
            return False
        
        # Ensure class-level metadata is initialized
        if cls._class_interface_metadata is None:
            cls._initialize_class_registry_integration()
        
        if cls._class_interface_metadata is None:
            return False
        
        try:
            registry = BeastModeInterfaceRegistry()
            
            # Create interface metadata for registry
            metadata = InterfaceMetadata(
                interface_name=cls._class_interface_metadata.interface_name,
                interface_type=cls._class_interface_metadata.interface_type,
                file_path=cls._class_interface_metadata.source_file,
                line_number=cls._class_interface_metadata.source_line,
                methods=cls._class_interface_metadata.methods,
                domain_terms=list(cls._class_interface_metadata.domain_terms),
                status=InterfaceStatus.ACTIVE
            )
            
            # Register the interface
            success = registry.register_interface(metadata)
            if success:
                cls._class_registry_id = f"{cls.__name__}_{cls._class_interface_metadata.interface_type.value}"
                cls._class_interface_metadata.registered_at = datetime.now()
            
            return success
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Failed to register class {cls.__name__}: {e}")
            return False
    
    @classmethod
    def get_class_interface_metadata(cls) -> Optional[ClassInterfaceMetadata]:
        """
        Get class-level interface metadata.
        
        Returns:
            ClassInterfaceMetadata object or None if not initialized
        """
        if cls._class_interface_metadata is None:
            cls._initialize_class_registry_integration()
        
        return cls._class_interface_metadata
    
    @classmethod
    def get_class_registry_id(cls) -> Optional[str]:
        """
        Get class-level registry ID.
        
        Returns:
            Registry ID string or None if not registered
        """
        return cls._class_registry_id
    
    def __init__(self, module_name: Optional[str] = None, version: str = "1.0.0"):
        """
        Initialize the reflective module with proper class-level registry integration.
        
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
        self._instance_id = f"{self.__class__.__name__}_{id(self)}"
        
        # Initialize class-level registry integration if needed
        if self.__class__._class_interface_metadata is None:
            self.__class__._initialize_class_registry_integration()
        
        # Register class interface if configured and not already registered
        if (self.__class__._registry_config.get('auto_register', True) and 
            self.__class__._class_registry_id is None):
            self.__class__._register_class_interface()
    
    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get module information with class-level registry integration.
        
        Returns:
            Dict containing module metadata including class-level registry information.
        """
        base_info = {
            "name": self.module_name,
            "version": self.version,
            "type": "reflective_module",
            "created_at": self._start_time.isoformat(),
            "last_activity": self._last_activity.isoformat(),
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "instance_id": self._instance_id
        }
        
        # Add class-level registry information if available
        class_metadata = self.__class__.get_class_interface_metadata()
        if class_metadata:
            base_info.update({
                "class_registry_id": self.__class__.get_class_registry_id(),
                "interface_type": class_metadata.interface_type.value if hasattr(class_metadata.interface_type, 'value') else str(class_metadata.interface_type),
                "domain_terms": list(class_metadata.domain_terms),
                "source_file": class_metadata.source_file,
                "source_line": class_metadata.source_line,
                "methods": class_metadata.methods,
                "class_docstring": class_metadata.class_docstring
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
        Check module health with class-level registry integration.
        
        Returns:
            ModuleHealth object with current health status.
        """
        # Default health check implementation
        status = ModuleStatus.HEALTHY
        health_score = 100.0
        issues = []
        
        # Check class-level registry registration status
        if REGISTRY_AVAILABLE and not self.__class__.get_class_registry_id():
            status = ModuleStatus.WARNING
            health_score -= 10.0
            issues.append("Class not registered in interface registry")
        
        # Check error count
        if self._error_count > 0:
            status = ModuleStatus.ERROR if self._error_count > 5 else ModuleStatus.WARNING
            health_score -= min(self._error_count * 5, 50)
            issues.append(f"Error count: {self._error_count}")
        
        return ModuleHealth(
            module_id=self._instance_id,
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
            "auto_register": self.__class__._registry_config.get('auto_register', True),
            "interface_type": self.__class__.get_class_interface_metadata().interface_type.value if self.__class__.get_class_interface_metadata() else "unknown"
        }
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get module metrics with class-level registry integration.
        
        Returns:
            Dict containing performance and operational metrics.
        """
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        metrics = {
            "uptime_seconds": uptime,
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "last_activity": self._last_activity.isoformat(),
            "instance_id": self._instance_id,
            "class_registry_registered": bool(self.__class__.get_class_registry_id())
        }
        
        # Add class-level registry metrics if available
        class_metadata = self.__class__.get_class_interface_metadata()
        if class_metadata:
            metrics.update({
                "domain_terms_count": len(class_metadata.domain_terms),
                "methods_count": len(class_metadata.methods),
                "interface_type": class_metadata.interface_type.value if hasattr(class_metadata.interface_type, 'value') else str(class_metadata.interface_type)
            })
        
        # Add registry-specific metrics if available
        if self.__class__.get_class_registry_id() and REGISTRY_AVAILABLE:
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
        
        if self.__class__.get_class_registry_id():
            indicators.append("✅ Class registry registered")
        else:
            indicators.append("⚠️ Class not registry registered")
        
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


# Convenience function for manual class registration
def register_reflective_module_class(cls: type, 
                                   interface_type: Optional[InterfaceType] = None) -> bool:
    """
    Manually register a ReflectiveModule class.
    
    Args:
        cls: ReflectiveModule class to register
        interface_type: Optional interface type override
        
    Returns:
        True if registration successful, False otherwise
    """
    if not REGISTRY_AVAILABLE:
        return False
    
    try:
        # Initialize class-level metadata if needed
        if cls._class_interface_metadata is None:
            cls._initialize_class_registry_integration()
        
        # Override interface type if specified
        if interface_type and cls._class_interface_metadata:
            cls._class_interface_metadata.interface_type = interface_type
        
        # Register the class
        return cls._register_class_interface()
    
    except Exception:
        return False


# Global registry for tracking class registrations
_registered_classes: Dict[str, type] = {}


def get_registered_classes() -> Dict[str, type]:
    """
    Get all registered ReflectiveModule classes.
    
    Returns:
        Dict mapping registry IDs to class objects.
    """
    return _registered_classes.copy()


def get_class_by_registry_id(registry_id: str) -> Optional[type]:
    """
    Get class by registry ID.
    
    Args:
        registry_id: Registry ID of the class
        
    Returns:
        ReflectiveModule class or None if not found.
    """
    return _registered_classes.get(registry_id)


# Export the main classes
__all__ = [
    'ReflectiveModule',
    'ModuleStatus',
    'ModuleCapability', 
    'ModuleHealth',
    'ClassInterfaceMetadata',
    'registered',
    'register_reflective_module_class',
    'get_registered_classes',
    'get_class_by_registry_id',
    'InterfaceType',
    'InterfaceStatus'
]

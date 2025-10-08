# ReflectiveModule Integration Guide

## Overview

The Beast Mode framework now includes **integrated registry functionality** directly in the `ReflectiveModule` base class. This eliminates the need for manual registry management and provides automatic introspection with sensible defaults.

## Key Benefits

- **✅ Zero Configuration**: Automatic registry integration with sensible defaults
- **✅ Introspection-Based**: Automatic method signature and domain term extraction
- **✅ Type Detection**: Automatic interface type detection based on class name patterns
- **✅ Decorator Support**: Optional `@registered` decorator for custom configuration
- **✅ Backward Compatible**: Existing ReflectiveModule implementations continue to work

## Migration Guide

### 1. Replace Existing ReflectiveModule Definitions

**Before (Multiple Definitions):**
```python
# ❌ OLD: Multiple ReflectiveModule definitions scattered across codebase
class ReflectiveModule(ABC):
    def __init__(self):
        self.module_name = self.__class__.__name__
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        pass
```

**After (Unified Definition):**
```python
# ✅ NEW: Single unified ReflectiveModule with integrated registry
from beast_mode.core.unified_reflective_module import ReflectiveModule

class MyModule(ReflectiveModule):
    def __init__(self):
        super().__init__()  # Automatic registry integration!
    
    def get_module_info(self) -> Dict[str, Any]:
        info = super().get_module_info()
        info.update({"custom": "data"})
        return info
    
    # ... other required methods
```

### 2. Automatic Registry Integration

**No Configuration Required:**
```python
class HealthMonitor(ReflectiveModule):
    """Health monitoring module - automatically registered!"""
    
    def __init__(self):
        super().__init__()
        # Registry integration happens automatically
        # - Interface type auto-detected
        # - Domain terms extracted from class name/docstring
        # - Method signatures captured
        # - File location tracked
```

**With Custom Configuration:**
```python
from beast_mode.core.unified_reflective_module import registered, InterfaceType

@registered(interface_type=InterfaceType.DOMAIN_SERVICE)
class ServiceManager(ReflectiveModule):
    """Service management with custom interface type"""
    
    def __init__(self, service_name: str):
        super().__init__(module_name=f"ServiceManager-{service_name}")
        # Custom module name with automatic registry integration
```

### 3. Enhanced Method Signatures

**Automatic Method Extraction:**
```python
class DataProcessor(ReflectiveModule):
    def process_data(self, data: List[str]) -> Dict[str, Any]:
        """Process data with automatic signature capture"""
        pass
    
    def validate_input(self, input_data: str) -> bool:
        """Validate input with automatic signature capture"""
        pass
    
    # These methods are automatically captured for registry!
```

### 4. Automatic Interface Type Detection

The system automatically detects interface types based on class name patterns:

- **`*Service*`, `*Manager*`, `*Handler*`** → `DOMAIN_SERVICE`
- **`*API*`, `*Client*`, `*Server*`** → `API_INTERFACE`
- **`*Model*`, `*Entity*`, `*Data*`** → `DATA_MODEL`
- **`*Rule*`, `*Validator*`, `*Validation*`** → `VALIDATION_RULE`
- **`*Config*`, `*Settings*`, `*Configuration*`** → `CONFIGURATION`
- **Default** → `REFLECTIVE_MODULE`

### 5. Automatic Domain Term Extraction

Domain terms are automatically extracted from:
- **Class name**: `HealthMonitor` → `['health', 'monitor']`
- **Docstring**: Extracted meaningful terms
- **Method names**: Used for semantic analysis

## Implementation Examples

### Basic Module (Zero Configuration)
```python
from beast_mode.core.unified_reflective_module import ReflectiveModule

class SystemMonitor(ReflectiveModule):
    """System monitoring module with automatic registry integration"""
    
    def __init__(self):
        super().__init__()
        self.metrics = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        info = super().get_module_info()
        info.update({
            "description": "Monitors system health and performance",
            "metrics_count": len(self.metrics)
        })
        return info
    
    def get_capabilities(self) -> List[ModuleCapability]:
        return [ModuleCapability.HEALTH_MONITORING, ModuleCapability.METRICS_COLLECTION]
    
    def get_dependencies(self) -> List[str]:
        return ["SystemRegistry"]
    
    def check_health(self) -> ModuleHealth:
        return super().check_health()  # Use default implementation
    
    def get_configuration(self) -> Dict[str, Any]:
        config = super().get_configuration()
        config.update({"monitoring_interval": 30})
        return config
    
    def get_metrics(self) -> Dict[str, Any]:
        metrics = super().get_metrics()
        metrics.update({"metrics_count": len(self.metrics)})
        return metrics
```

### Advanced Module (With Decorator)
```python
from beast_mode.core.unified_reflective_module import (
    ReflectiveModule, registered, InterfaceType, ModuleCapability
)

@registered(interface_type=InterfaceType.DOMAIN_SERVICE)
class UserServiceManager(ReflectiveModule):
    """User service management with custom configuration"""
    
    def __init__(self, service_name: str):
        super().__init__(module_name=f"UserService-{service_name}")
        self.services = {}
        self.active_connections = 0
    
    def get_module_info(self) -> Dict[str, Any]:
        info = super().get_module_info()
        info.update({
            "service_name": service_name,
            "managed_services": len(self.services),
            "active_connections": self.active_connections
        })
        return info
    
    def get_capabilities(self) -> List[ModuleCapability]:
        return [
            ModuleCapability.DEPENDENCY_MANAGEMENT,
            ModuleCapability.INTEGRATION,
            ModuleCapability.HEALTH_MONITORING
        ]
    
    def get_dependencies(self) -> List[str]:
        return ["UserRegistry", "AuthenticationService", "DatabaseConnection"]
    
    def check_health(self) -> ModuleHealth:
        # Custom health check logic
        status = ModuleStatus.HEALTHY
        health_score = 100.0
        issues = []
        
        if self.active_connections > 1000:
            status = ModuleStatus.WARNING
            health_score -= 20.0
            issues.append("High connection count")
        
        if len(self.services) == 0:
            status = ModuleStatus.ERROR
            health_score -= 50.0
            issues.append("No services managed")
        
        return ModuleHealth(
            module_id=self._registry_id or self.module_name,
            status=status,
            health_score=health_score,
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    
    def get_configuration(self) -> Dict[str, Any]:
        config = super().get_configuration()
        config.update({
            "max_connections": 1000,
            "health_check_interval": 60,
            "service_timeout": 30
        })
        return config
    
    def get_metrics(self) -> Dict[str, Any]:
        metrics = super().get_metrics()
        metrics.update({
            "services_managed": len(self.services),
            "active_connections": self.active_connections,
            "connection_utilization": self.active_connections / 1000.0
        })
        return metrics
```

## Registry Integration Features

### Automatic Registration
- **Zero configuration** required for basic registration
- **Automatic interface type detection** based on naming patterns
- **Domain term extraction** from class names and docstrings
- **Method signature capture** for comprehensive metadata

### Enhanced Metadata
- **File location tracking** with precise line numbers
- **Source file information** for traceability
- **Domain vocabulary indexing** for searchability
- **Compliance scoring** for quality assessment

### Health Monitoring
- **Registry registration status** in health checks
- **Domain term coverage** in metrics
- **Method count tracking** for complexity assessment
- **Registry-wide statistics** in module metrics

## Migration Checklist

- [ ] **Replace imports**: Update all `ReflectiveModule` imports to use unified version
- [ ] **Update constructors**: Call `super().__init__()` in all subclasses
- [ ] **Implement required methods**: Ensure all abstract methods are implemented
- [ ] **Test registration**: Verify modules are automatically registered
- [ ] **Check health indicators**: Confirm registry integration appears in health checks
- [ ] **Review metrics**: Ensure registry metadata appears in module metrics
- [ ] **Remove manual registration**: Remove any manual registry calls (now automatic)

## Benefits of Integration

1. **Reduced Boilerplate**: No manual registry management required
2. **Automatic Introspection**: Method signatures and domain terms captured automatically
3. **Consistent Metadata**: All modules have standardized registry information
4. **Better Traceability**: File locations and source information automatically tracked
5. **Enhanced Searchability**: Domain vocabulary indexing for better discovery
6. **Quality Assessment**: Compliance scoring and health monitoring built-in
7. **Zero Configuration**: Sensible defaults with optional customization

## Troubleshooting

### Registry Not Available
If the registry system is not available, the ReflectiveModule will still function normally with fallback classes.

### Duplicate Registration
The system automatically prevents duplicate registrations and provides clear error messages.

### Interface Type Detection
If automatic type detection doesn't work as expected, use the `@registered` decorator to specify the type explicitly.

### Health Check Issues
Check that all required abstract methods are implemented and that `super()` is called in constructors.

## Conclusion

The integrated registry functionality provides a **zero-configuration, automatic solution** for ReflectiveModule registration with comprehensive metadata capture and health monitoring. This eliminates the need for manual registry management while providing enhanced capabilities for interface governance and systematic compliance.

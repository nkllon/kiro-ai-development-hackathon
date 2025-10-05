# Registry Integration Implementation & Lifecycle Events

## Overview

The integrated registry system in the `ReflectiveModule` base class uses a sophisticated lifecycle management approach with automatic introspection, configurable defaults, and seamless integration. Here's exactly how it works:

## 🔄 Class Lifecycle Events & Registry Triggers

### 1. **Class Definition Phase** (Decorator Application)

```python
@registered(interface_type=InterfaceType.DOMAIN_SERVICE)
class ServiceManager(ReflectiveModule):
    pass
```

**What Happens:**
- Decorator modifies the class's `_registry_config`
- Sets `auto_register=True` and custom `interface_type`
- Stores `registered_at` timestamp
- **No registry interaction yet** - just metadata preparation

**Code Implementation:**
```python
def registered(auto_register: bool = True, interface_type: InterfaceType = InterfaceType.REFLECTIVE_MODULE):
    def decorator(cls):
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
```

### 2. **Instance Creation Phase** (`__init__`)

```python
service = ServiceManager("UserService")  # Instance creation
```

**Lifecycle Sequence:**

#### **Step 2a: Basic Initialization**
```python
def __init__(self, module_name: Optional[str] = None, version: str = "1.0.0"):
    self.module_name = module_name or self.__class__.__name__
    self.version = version
    self._start_time = datetime.now()
    self._last_activity = datetime.now()
    self._error_count = 0
    self._warning_count = 0
    self._registry_id = None
```

#### **Step 2b: Registry Integration Setup**
```python
# Initialize registry integration
self._initialize_registry_integration()
```

**What `_initialize_registry_integration()` Does:**
```python
def _initialize_registry_integration(self):
    """Initialize registry integration with introspection."""
    if not REGISTRY_AVAILABLE:
        return
    
    # 1. Get source file information using inspect
    frame = inspect.currentframe().f_back
    self._source_file = frame.f_code.co_filename
    self._source_line = frame.f_lineno
    
    # 2. Extract domain terms from class name and docstring
    self._domain_terms = self._extract_domain_terms()
    
    # 3. Determine interface type based on class name patterns
    self._interface_type = self._determine_interface_type()
```

**Domain Term Extraction:**
```python
def _extract_domain_terms(self) -> Set[str]:
    terms = set()
    
    # Extract from class name (camelCase to snake_case)
    class_name = self.__class__.__name__
    import re
    words = re.findall(r'[A-Z][a-z]*', class_name)
    terms.update(word.lower() for word in words)
    
    # Extract from docstring
    if self.__doc__:
        docstring = self.__doc__.lower()
        doc_terms = re.findall(r'\b[a-z_]+\b', docstring)
        terms.update(term for term in doc_terms if len(term) > 3)
    
    return terms
```

**Interface Type Detection:**
```python
def _determine_interface_type(self) -> InterfaceType:
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
```

#### **Step 2c: Automatic Registry Registration**
```python
# Auto-register if configured
if self._registry_config.get('auto_register', True):
    self._register_self()
```

**What `_register_self()` Does:**
```python
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
            methods=self._get_method_signatures(),  # Introspection happens here
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
```

**Method Signature Introspection:**
```python
def _get_method_signatures(self) -> List[str]:
    """Get method signatures for registry."""
    methods = []
    
    for name, method in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
        if not name.startswith('_'):
            methods.append(name)
    
    return methods
```

### 3. **Runtime Phase** (Ongoing Registry Integration)

#### **Health Check Integration**
```python
def check_health(self) -> ModuleHealth:
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
```

#### **Metrics Integration**
```python
def get_metrics(self) -> Dict[str, Any]:
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
```

### 4. **Activity Tracking Phase**

#### **Automatic Activity Updates**
```python
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
```

## 🔍 Registry Interrogation Points

### **1. Instance Creation Time**
- **Trigger**: `__init__()` method call
- **Purpose**: Initial registration and metadata capture
- **Data Captured**: 
  - Class name and interface type
  - Source file location and line number
  - Method signatures via introspection
  - Domain terms from class name and docstring

### **2. Health Check Time**
- **Trigger**: `check_health()` method call
- **Purpose**: Registry status validation
- **Data Retrieved**:
  - Registry registration status
  - Registry-wide statistics
  - Compliance metrics

### **3. Metrics Collection Time**
- **Trigger**: `get_metrics()` method call
- **Purpose**: Registry integration metrics
- **Data Retrieved**:
  - Registry registration status
  - Total interfaces in registry
  - Duplicate and conflict counts
  - Domain term coverage

### **4. Module Info Time**
- **Trigger**: `get_module_info()` method call
- **Purpose**: Comprehensive module metadata
- **Data Retrieved**:
  - Registry ID and interface type
  - Domain terms and source location
  - Method count and capabilities

## 🎯 Key Implementation Features

### **1. Zero-Configuration Registration**
- **Default**: `auto_register=True`
- **Behavior**: Automatic registration on instance creation
- **Override**: Use `@registered(auto_register=False)` to disable

### **2. Automatic Introspection**
- **Source Location**: Uses `inspect.currentframe()` to capture file/line
- **Method Signatures**: Uses `inspect.getmembers()` to find public methods
- **Domain Terms**: Regex extraction from class names and docstrings
- **Interface Types**: Pattern matching on class names

### **3. Graceful Degradation**
- **Registry Unavailable**: Falls back to local operation
- **Registration Failure**: Logs warning but doesn't fail initialization
- **Missing Dependencies**: Provides fallback classes and methods

### **4. Lifecycle Integration**
- **Creation**: Registry integration during `__init__`
- **Operation**: Registry status in health checks and metrics
- **Activity**: Automatic timestamp updates on state changes
- **Monitoring**: Registry statistics included in module metrics

## 🔧 Configuration Options

### **Class-Level Configuration**
```python
class MyModule(ReflectiveModule):
    _registry_config = {
        'auto_register': True,  # Enable/disable automatic registration
        'interface_type': InterfaceType.DOMAIN_SERVICE,  # Override type detection
        'registered_at': None  # Set by decorator or system
    }
```

### **Decorator Configuration**
```python
@registered(
    auto_register=True,  # Enable automatic registration
    interface_type=InterfaceType.API_INTERFACE  # Specify interface type
)
class ApiClient(ReflectiveModule):
    pass
```

### **Instance-Level Configuration**
```python
# Custom module name and version
module = MyModule(module_name="CustomName", version="2.0.0")

# Registry integration happens automatically with these parameters
```

## 🚀 Benefits of This Implementation

1. **Zero Configuration**: Works out of the box with sensible defaults
2. **Automatic Introspection**: Captures metadata without manual intervention
3. **Lifecycle Integration**: Registry status integrated into health and metrics
4. **Graceful Degradation**: Continues to work even if registry is unavailable
5. **Flexible Configuration**: Multiple ways to customize behavior
6. **Comprehensive Metadata**: Captures file locations, method signatures, domain terms
7. **Real-time Updates**: Registry status reflected in ongoing operations

## 🔄 Lifecycle Flow Diagram

```
Class Definition → @registered decorator → _registry_config setup
       ↓
Instance Creation → __init__() → _initialize_registry_integration()
       ↓
Introspection → _extract_domain_terms() + _determine_interface_type()
       ↓
Registry Registration → _register_self() → BeastModeInterfaceRegistry.register_interface()
       ↓
Runtime Operation → check_health() + get_metrics() → Registry status integration
       ↓
Activity Tracking → update_activity() → Timestamp updates on state changes
```

This implementation provides a **seamless, automatic, and comprehensive** registry integration that requires zero configuration while providing extensive customization options for advanced use cases.

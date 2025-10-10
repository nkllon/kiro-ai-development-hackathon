# ReflectiveModule API

## Overview

The `ReflectiveModule` is the foundational base class for all components in the Beast Mode AI Development Framework. It provides systematic health monitoring, error handling, and observability capabilities.

## Location

```python
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
```

## Class Definition

```python
class ReflectiveModule(ABC):
    """
    Base class for all framework components providing systematic
    health monitoring, error handling, and observability.
    """
```

## Core Methods

### Abstract Methods (Must Implement)

#### `get_module_info() -> Dict[str, Any]`

Returns basic module information.

```python
def get_module_info(self) -> Dict[str, Any]:
    return {
        'module_name': 'MyComponent',
        'version': '1.0.0',
        'description': 'Component description',
        'dependencies': ['redis', 'asyncio']
    }
```

**Returns:**
- `module_name` (str): Human-readable module name
- `version` (str): Semantic version string
- `description` (str): Brief component description
- `dependencies` (List[str]): Required dependencies

#### `get_capabilities() -> List[ModuleCapability]`

Returns list of component capabilities.

```python
def get_capabilities(self) -> List[ModuleCapability]:
    return [
        ModuleCapability.CORE_FUNCTIONALITY,
        ModuleCapability.DATA_PROCESSING,
        ModuleCapability.MONITORING
    ]
```

**Available Capabilities:**
- `CORE_FUNCTIONALITY`: Basic component operations
- `DATA_PROCESSING`: Data transformation and analysis
- `API_INTEGRATION`: External API interactions
- `MONITORING`: Health and metrics reporting
- `STORAGE`: Data persistence capabilities
- `NETWORKING`: Network communication features

#### `async get_health_status() -> ModuleHealth`

Returns detailed health status information.

```python
async def get_health_status(self) -> ModuleHealth:
    return ModuleHealth(
        module_id=self.module_id,
        status=ModuleStatus.HEALTHY,
        health_score=1.0,
        issues=[],
        last_check=datetime.utcnow(),
        uptime_seconds=self.get_uptime(),
        error_count=self.error_count,
        warning_count=self.warning_count
    )
```

**Returns ModuleHealth with:**
- `module_id` (str): Unique module identifier
- `status` (ModuleStatus): Current health status
- `health_score` (float): Health score 0.0-1.0
- `issues` (List[str]): Current health issues
- `last_check` (datetime): Last health check timestamp
- `uptime_seconds` (float): Module uptime in seconds
- `error_count` (int): Total error count
- `warning_count` (int): Total warning count

#### `async graceful_degradation(error: Exception) -> GracefulDegradationResult`

Handles graceful degradation when errors occur.

```python
async def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
    # Save critical state
    await self.save_state()
    
    # Determine remaining capabilities
    remaining = [ModuleCapability.MONITORING]
    degraded = [ModuleCapability.CORE_FUNCTIONALITY]
    
    return GracefulDegradationResult(
        success=True,
        degraded_capabilities=degraded,
        remaining_capabilities=remaining,
        error_message=str(error)
    )
```

**Parameters:**
- `error` (Exception): The error that triggered degradation

**Returns GracefulDegradationResult with:**
- `success` (bool): Whether degradation was successful
- `degraded_capabilities` (List[ModuleCapability]): Lost capabilities
- `remaining_capabilities` (List[ModuleCapability]): Still available capabilities
- `error_message` (str): Error description

### Provided Methods

#### `health_check() -> Dict[str, Any]`

Synchronous health check returning basic status information.

```python
health = component.health_check()
print(f"Status: {health['status']}")
print(f"Uptime: {health['uptime_seconds']}s")
```

**Returns:**
- `status` (str): Basic health status
- `uptime_seconds` (float): Component uptime
- `module_name` (str): Component name
- `last_error` (str, optional): Last error message

## Data Models

### ModuleStatus

```python
class ModuleStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    DEGRADED = "degraded"
    OFFLINE = "offline"
```

### ModuleHealth

```python
@dataclass
class ModuleHealth:
    module_id: str
    status: ModuleStatus
    health_score: float  # 0.0 to 1.0
    issues: List[str]
    last_check: datetime
    uptime_seconds: float
    error_count: int
    warning_count: int
```

### GracefulDegradationResult

```python
@dataclass
class GracefulDegradationResult:
    success: bool
    degraded_capabilities: List[ModuleCapability]
    remaining_capabilities: List[ModuleCapability]
    error_message: Optional[str] = None
```

## Implementation Example

```python
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from datetime import datetime
from typing import Dict, Any, List

class MyComponent(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.utcnow()
        self.error_count = 0
        self.warning_count = 0
        self.is_healthy = True
    
    def get_module_info(self) -> Dict[str, Any]:
        return {
            'module_name': 'MyComponent',
            'version': '1.0.0',
            'description': 'Example component implementation',
            'dependencies': ['asyncio']
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING
        ]
    
    async def get_health_status(self) -> ModuleHealth:
        # Determine current status
        if not self.is_healthy:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["Component is unhealthy"]
        elif self.warning_count > 0:
            status = ModuleStatus.WARNING
            health_score = 0.7
            issues = [f"{self.warning_count} warnings detected"]
        else:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
            issues = []
        
        return ModuleHealth(
            module_id=f"my_component_{id(self)}",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.utcnow(),
            uptime_seconds=(datetime.utcnow() - self.start_time).total_seconds(),
            error_count=self.error_count,
            warning_count=self.warning_count
        )
    
    async def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
        try:
            # Attempt to save state
            await self.save_critical_state()
            
            # Disable non-essential features
            self.is_healthy = False
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[ModuleCapability.MONITORING],
                error_message=str(error)
            )
        except Exception as degradation_error:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.MONITORING],
                remaining_capabilities=[],
                error_message=f"Degradation failed: {degradation_error}"
            )
    
    async def save_critical_state(self):
        """Save critical component state during degradation."""
        # Implementation specific to component
        pass
    
    async def perform_operation(self):
        """Example operation with error handling."""
        try:
            # Perform operation
            result = await self.do_work()
            return result
        except Exception as e:
            self.error_count += 1
            # Trigger graceful degradation
            degradation_result = await self.graceful_degradation(e)
            if not degradation_result.success:
                raise
            # Continue with reduced functionality
            return await self.fallback_operation()
```

## Usage Patterns

### Health Monitoring

```python
# Check component health
health = await component.get_health_status()

if health.status == ModuleStatus.HEALTHY:
    print("Component is healthy")
elif health.status == ModuleStatus.WARNING:
    print(f"Component has warnings: {health.issues}")
elif health.status == ModuleStatus.ERROR:
    print(f"Component has errors: {health.issues}")
    # Consider graceful degradation
```

### Error Handling with Graceful Degradation

```python
try:
    result = await component.critical_operation()
except Exception as e:
    # Let component handle graceful degradation
    degradation = await component.graceful_degradation(e)
    
    if degradation.success:
        print(f"Degraded capabilities: {degradation.degraded_capabilities}")
        print(f"Remaining capabilities: {degradation.remaining_capabilities}")
        
        # Continue with reduced functionality
        if ModuleCapability.MONITORING in degradation.remaining_capabilities:
            health = await component.get_health_status()
            print(f"Component health after degradation: {health.status}")
    else:
        print(f"Graceful degradation failed: {degradation.error_message}")
        raise
```

### Capability-Based Operations

```python
capabilities = component.get_capabilities()

if ModuleCapability.DATA_PROCESSING in capabilities:
    result = await component.process_data(data)
else:
    print("Data processing not available")

if ModuleCapability.MONITORING in capabilities:
    health = await component.get_health_status()
    print(f"Health score: {health.health_score}")
```

## Best Practices

### 1. Health Check Implementation

```python
async def get_health_status(self) -> ModuleHealth:
    issues = []
    
    # Check dependencies
    if not await self.check_database_connection():
        issues.append("Database connection failed")
    
    if not await self.check_external_api():
        issues.append("External API unreachable")
    
    # Determine status based on issues
    if len(issues) == 0:
        status = ModuleStatus.HEALTHY
        health_score = 1.0
    elif len(issues) <= 2:
        status = ModuleStatus.WARNING
        health_score = 0.7
    else:
        status = ModuleStatus.ERROR
        health_score = 0.3
    
    return ModuleHealth(
        module_id=self.module_id,
        status=status,
        health_score=health_score,
        issues=issues,
        last_check=datetime.utcnow(),
        uptime_seconds=self.get_uptime(),
        error_count=self.error_count,
        warning_count=self.warning_count
    )
```

### 2. Graceful Degradation Strategy

```python
async def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
    degradation_actions = []
    
    try:
        # Save critical state
        await self.save_state()
        degradation_actions.append("state_saved")
        
        # Disable non-essential features
        self.disable_non_essential_features()
        degradation_actions.append("features_disabled")
        
        # Switch to fallback mode
        self.enable_fallback_mode()
        degradation_actions.append("fallback_enabled")
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
            remaining_capabilities=[ModuleCapability.MONITORING],
            error_message=f"Degradation successful: {', '.join(degradation_actions)}"
        )
    
    except Exception as degradation_error:
        return GracefulDegradationResult(
            success=False,
            degraded_capabilities=self.get_capabilities(),
            remaining_capabilities=[],
            error_message=f"Degradation failed: {degradation_error}"
        )
```

### 3. Module Information

```python
def get_module_info(self) -> Dict[str, Any]:
    return {
        'module_name': self.__class__.__name__,
        'version': self.VERSION,
        'description': self.__doc__ or "No description available",
        'dependencies': self.get_dependencies(),
        'configuration': self.get_configuration_info(),
        'endpoints': self.get_api_endpoints() if hasattr(self, 'get_api_endpoints') else []
    }
```

## Error Handling

The ReflectiveModule provides systematic error handling:

```python
# Automatic error counting
try:
    await component.operation()
except Exception as e:
    # Error count is automatically incremented
    # Graceful degradation is triggered
    degradation = await component.graceful_degradation(e)
    # Handle based on degradation result
```

## Integration with Framework

All framework components extend ReflectiveModule:

- `ConstellationOrchestrator`
- `ContextEngine`
- `RedisExecutionTracker`
- `DAGManager`
- `ExecutionManager`

This ensures consistent health monitoring and error handling across the entire framework.

---

**Next**: [Configuration Management](./configuration.md) | **Up**: [Core APIs](../core/)
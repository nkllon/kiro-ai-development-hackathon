---
inclusion: always
---

# Beast Mode Framework Patterns - Systematic AI Development

## Core Principle

**"Use Beast Mode's systematic patterns instead of ad-hoc solutions. Every component should inherit from ReflectiveModule for instant production readiness."**

## The ReflectiveModule Pattern 🐺

### **ALWAYS Inherit from ReflectiveModule**

```python
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

class YourAIAgent(ReflectiveModule):
    """🐺 Inherit from ReflectiveModule = Instant production readiness"""
    
    def __init__(self):
        super().__init__()
        # You now automatically have:
        # ✅ Prometheus metrics integration
        # ✅ Health endpoints (/health, /ready, /metrics)  
        # ✅ Performance tracing with correlation IDs
        # ✅ Graceful degradation on failures
        # ✅ Structured logging with audit trails
        # ✅ Systematic error handling
        # ✅ Memory persistence across sessions
```

### **Automatic Capabilities You Get**

When you inherit from ReflectiveModule:

- **Health Monitoring**: Automatic `/health`, `/ready`, `/metrics` endpoints
- **Performance Tracing**: Built-in correlation IDs and timing
- **Error Handling**: Graceful degradation and systematic error recovery
- **Logging**: Structured logging with audit trails
- **Metrics**: Prometheus metrics integration
- **Memory**: Persistent state across sessions

## DAG Orchestration Patterns

### **ALWAYS Use DAG for Task Dependencies**

```python
from src.dag_orchestration import DAGOrchestrator

# ✅ CORRECT: Use DAG orchestration
orchestrator = DAGOrchestrator()
orchestrator.add_task("setup_db", dependencies=[])
orchestrator.add_task("create_models", dependencies=["setup_db"])
orchestrator.add_task("setup_api", dependencies=["create_models"])

# Execute with automatic parallelization and cycle detection
results = orchestrator.execute()
```

### **NEVER Use Manual Task Sequencing**

```python
# ❌ WRONG: Manual sequencing without dependency management
def setup_system():
    setup_db()
    create_models()  # What if setup_db fails?
    setup_api()      # No parallelization opportunity
    run_tests()      # No cycle detection
```

## AI Memory Palace Integration

### **ALWAYS Use Memory Palace for AI Context**

```python
from src.ai_memory_palace import MemoryPalace

class YourAISystem(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.memory = MemoryPalace()
    
    def remember_context(self, key: str, context: dict):
        """Store context for future AI sessions"""
        self.memory.remember(key, context)
    
    def recall_context(self, key: str) -> dict:
        """Retrieve context from previous sessions"""
        return self.memory.recall(key)
```

### **Context Persistence Patterns**

```python
# ✅ CORRECT: Systematic context management
def process_user_request(self, request):
    # Load previous context
    context = self.memory.recall("user_session")
    
    # Process with context
    response = self.process_with_context(request, context)
    
    # Update context for next session
    updated_context = {
        **context,
        "last_request": request,
        "last_response": response,
        "timestamp": datetime.now().isoformat()
    }
    self.memory.remember("user_session", updated_context)
    
    return response
```

## CMS Platform Integration

### **ALWAYS Use CMS Platform for Content Management**

```python
from src.cms_platform import CMSPlatform

class YourContentSystem(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.cms = CMSPlatform()
        self.cms.setup_collections()
        self.cms.configure_relationships()
    
    def deploy_with_monitoring(self):
        """Deploy CMS with automatic health monitoring"""
        self.cms.deploy_with_monitoring()
        return self.cms.health_check()
```

## Error Handling Patterns

### **ALWAYS Use Systematic Error Handling**

```python
class YourSystem(ReflectiveModule):
    def process_request(self, request):
        try:
            # Use correlation ID for tracing
            correlation_id = self.generate_correlation_id()
            self.log_info(f"Processing request", correlation_id=correlation_id)
            
            result = self.do_processing(request)
            
            # Record success metrics
            self.record_metric("requests_processed", 1, {"status": "success"})
            return result
            
        except Exception as e:
            # Systematic error handling
            self.log_error(f"Request processing failed: {str(e)}", 
                          correlation_id=correlation_id)
            self.record_metric("requests_processed", 1, {"status": "error"})
            
            # Graceful degradation
            return self.fallback_response(request, e)
```

## Configuration Patterns

### **ALWAYS Use Environment Variables**

```python
import os
from dataclasses import dataclass

@dataclass
class BeastModeConfig:
    """Secure configuration using environment variables"""
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    redis_password: str = os.getenv('REDIS_PASSWORD', '')
    
    def __post_init__(self):
        if not self.redis_password:
            raise ValueError("REDIS_PASSWORD environment variable is required")
```

## Testing Patterns

### **ALWAYS Test ReflectiveModule Components**

```python
import pytest
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

class TestYourSystem:
    def test_health_endpoint(self):
        """Test automatic health endpoint"""
        system = YourSystem()
        health = system.health_check()
        assert health["status"] == "healthy"
    
    def test_metrics_collection(self):
        """Test automatic metrics collection"""
        system = YourSystem()
        system.process_request({"test": "data"})
        metrics = system.get_metrics()
        assert "requests_processed" in metrics
```

## Anti-Patterns - NEVER Do These

### ❌ **Manual Health Checks**
```python
# WRONG: Manual health check implementation
def health_check():
    return {"status": "ok"}  # No systematic monitoring
```

### ❌ **Ad-hoc Error Handling**
```python
# WRONG: Inconsistent error handling
try:
    do_something()
except:
    print("Something went wrong")  # No correlation ID, no metrics
```

### ❌ **Hardcoded Configuration**
```python
# WRONG: Hardcoded values
REDIS_PASSWORD = "hardcoded_password"  # Security violation
```

### ❌ **Manual Task Sequencing**
```python
# WRONG: No dependency management
def deploy():
    step1()
    step2()  # What if step1 fails?
    step3()  # No parallelization
```

## Success Patterns

### ✅ **Complete Beast Mode Integration**

```python
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration import DAGOrchestrator
from src.ai_memory_palace import MemoryPalace
from src.cms_platform import CMSPlatform

class ProductionAISystem(ReflectiveModule):
    """Complete Beast Mode integration example"""
    
    def __init__(self):
        super().__init__()
        self.memory = MemoryPalace()
        self.orchestrator = DAGOrchestrator()
        self.cms = CMSPlatform()
        
        # Setup systematic task orchestration
        self.setup_task_dependencies()
    
    def setup_task_dependencies(self):
        """Define systematic task execution order"""
        self.orchestrator.add_task("initialize_memory", dependencies=[])
        self.orchestrator.add_task("setup_cms", dependencies=["initialize_memory"])
        self.orchestrator.add_task("load_context", dependencies=["setup_cms"])
        self.orchestrator.add_task("process_requests", dependencies=["load_context"])
    
    def deploy(self):
        """Deploy with systematic orchestration"""
        results = self.orchestrator.execute()
        health = self.health_check()
        
        self.log_info("System deployed successfully", 
                     results=results, health=health)
        return results
```

## The Meta-Principle

**"Every Beast Mode component should be systematic, observable, and production-ready by default. If you're writing custom infrastructure code, you're probably doing it wrong."**

Use Beast Mode's proven patterns instead of reinventing the wheel. The framework provides systematic solutions for:

- **Health monitoring** (ReflectiveModule)
- **Task orchestration** (DAG Orchestration)  
- **AI memory** (Memory Palace)
- **Content management** (CMS Platform)
- **Error handling** (Built-in patterns)
- **Configuration** (Environment variables)
- **Testing** (Systematic test patterns)

---

**This steering rule ensures developers use Beast Mode systematically and get maximum value from the framework's production-ready patterns.**
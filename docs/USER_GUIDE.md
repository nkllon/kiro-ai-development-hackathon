# 🐺 Beast Mode User Guide

Welcome to the Beast Mode AI Development Framework! This comprehensive guide will help you master systematic AI development with mathematical governance.

## 🎯 What You'll Learn

By the end of this guide, you'll understand:
- How to build AI agents with automatic observability
- The ReflectiveModule pattern and its benefits
- AI Memory Palace for persistent context
- DAG orchestration for complex workflows
- Mathematical governance principles
- Production deployment strategies

## 📚 Table of Contents

1. [Core Concepts](#core-concepts)
2. [The ReflectiveModule Pattern](#the-reflectivemodule-pattern)
3. [AI Memory Palace System](#ai-memory-palace-system)
4. [DAG Orchestration](#dag-orchestration)
5. [Mathematical Governance](#mathematical-governance)
6. [Building Your First Agent](#building-your-first-agent)
7. [Advanced Features](#advanced-features)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🧠 Core Concepts

### The Beast Mode Philosophy

Beast Mode is built on three fundamental principles:

1. **Systematic over Ad-Hoc**: Use proven patterns instead of custom solutions
2. **Mathematical Governance**: Let math prevent common development failures  
3. **Physics-Informed Design**: Build for real-world constraints and failure modes

### Key Components

- **ReflectiveModule**: Base class providing automatic observability
- **AI Memory Palace**: Persistent context across AI sessions
- **DAG Orchestrator**: Mathematical task dependency management
- **CMS Platform**: Systematic content and configuration management

---

## 🐺 The ReflectiveModule Pattern

The ReflectiveModule is the heart of Beast Mode. Every component inherits from it to get automatic superpowers.

### Basic Usage

```python
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

class MyAIAgent(ReflectiveModule):
    def __init__(self):
        super().__init__()
        # You now have automatic:
        # - Health monitoring
        # - Metrics collection  
        # - Error handling
        # - Audit trails
```

### What You Get Automatically

When you inherit from ReflectiveModule, you automatically get:

#### 🏥 Health Monitoring
```python
agent = MyAIAgent()
health = agent.get_health_status()
print(f"Status: {health.status}")  # healthy, warning, error
print(f"Health Score: {health.health_score}")  # 0.0 to 1.0
```

#### 📊 Metrics Collection
```python
metrics = agent.get_prometheus_metrics()
# Automatic Prometheus integration for monitoring
```

#### 🔄 Graceful Degradation
```python
degradation = agent.graceful_degradation()
if degradation.success:
    print(f"Running with capabilities: {degradation.remaining_capabilities}")
```

### Advanced ReflectiveModule Features

#### Operation Tracing
```python
class MyAgent(ReflectiveModule):
    def process_data(self, data):
        with self.trace_operation("process_data", data_size=len(data)) as trace:
            result = self._do_processing(data)
            trace.output_result = result
            return result
```

#### CLI Generation
```python
# Automatic CLI interface generation
cli_interface = agent.get_cli_interface()
help_text = agent.generate_cli_help()
```

---

## 🧠 AI Memory Palace System

The AI Memory Palace eliminates the "50 First Dates" problem where AI assistants forget everything between sessions.

### Basic Usage

```python
from src.ai_memory_palace import MemoryPalace

# Initialize memory palace
palace = MemoryPalace()

# Store context
palace.remember("project_state", {
    "current_task": "implementing user authentication",
    "decisions_made": ["using JWT tokens", "PostgreSQL for users"],
    "code_patterns": ["FastAPI for REST API", "Pydantic for validation"],
    "next_steps": ["implement login endpoint", "add password hashing"]
})

# Later, in a different session...
context = palace.recall("project_state")
# AI picks up exactly where you left off!
```

### Advanced Memory Palace Features

#### Contextual Memory
```python
# Store different types of context
palace.remember("user_preferences", {
    "coding_style": "functional",
    "testing_approach": "TDD",
    "documentation_level": "comprehensive"
})

palace.remember("project_architecture", {
    "framework": "FastAPI",
    "database": "PostgreSQL", 
    "cache": "Redis",
    "deployment": "Docker"
})
```

#### Memory Optimization
```python
# Automatic memory optimization
palace.optimize_storage()  # 10-70% storage reduction
palace.cleanup_old_memories(days=30)  # Remove old context
```

#### Performance Characteristics
- **Retrieval Speed**: Sub-2 second context loading
- **Storage Efficiency**: 10-70% optimization vs naive storage
- **Scalability**: Handles 1000+ context items efficiently
- **Isolation**: Multi-project boundaries enforced

---

## 🔄 DAG Orchestration

DAG (Directed Acyclic Graph) orchestration provides mathematical governance for complex workflows.

### Basic DAG Usage

```python
from src.dag_orchestration import DAGOrchestrator

# Create orchestrator
orchestrator = DAGOrchestrator()

# Define tasks with dependencies
orchestrator.add_task("setup_database", dependencies=[])
orchestrator.add_task("create_models", dependencies=["setup_database"])
orchestrator.add_task("setup_api", dependencies=["create_models"])
orchestrator.add_task("run_tests", dependencies=["setup_api"])

# Execute with automatic parallelization
results = orchestrator.execute()
```

### Mathematical Governance

#### Cycle Detection
```python
# This will fail with mathematical proof:
orchestrator.add_task("task_a", dependencies=["task_b"])
orchestrator.add_task("task_b", dependencies=["task_a"])  # Creates cycle!

# DAG orchestrator detects and prevents this:
# DAGCycleError: Circular dependency detected between task_a and task_b
```

#### Topological Sorting
```python
# Automatic optimal execution order
execution_plan = orchestrator.get_execution_plan()
# Returns mathematically optimal parallel execution strategy
```

### Advanced DAG Features

#### Conditional Execution
```python
orchestrator.add_conditional_task(
    "deploy_to_production",
    condition=lambda: os.getenv("ENVIRONMENT") == "production",
    dependencies=["run_tests"]
)
```

#### Resource-Aware Scheduling
```python
orchestrator.configure_resources(
    max_parallel_tasks=4,
    memory_limit_mb=2048,
    cpu_limit_percent=80
)
```

---

## 📐 Mathematical Governance

Beast Mode uses mathematical principles to prevent common development failures.

### Graph Theory Application

#### DAG Compliance
```python
# Mathematical guarantee: If dependencies form a DAG,
# then topological ordering exists and is unique
if orchestrator.is_dag_compliant():
    execution_order = orchestrator.topological_sort()
    # Guaranteed to be valid execution order
```

#### Cycle Detection Algorithm
```python
# O(V+E) cycle detection prevents impossible requirements
cycles = orchestrator.detect_cycles()
if cycles:
    raise ValueError(f"Circular dependencies found: {cycles}")
```

### Physics-Informed Constraints

#### Resource Limits
```python
# Mathematical constraints based on physical reality
orchestrator.set_constraints(
    max_memory_mb=lambda: psutil.virtual_memory().available // (1024**2),
    max_cpu_percent=lambda: 100 - psutil.cpu_percent(),
    max_disk_io=lambda: get_available_disk_bandwidth()
)
```

#### Performance Bounds
```python
# Mathematical performance guarantees
@performance_bound(max_duration_ms=5000, max_memory_mb=512)
def process_large_dataset(data):
    # Function guaranteed to complete within bounds
    # or fail fast with clear error message
    pass
```

---

## 🏗️ Building Your First Agent

Let's build a complete AI agent step by step.

### Step 1: Create the Agent Class

```python
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.ai_memory_palace import MemoryPalace

class DocumentAnalyzer(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.memory_palace = MemoryPalace()
        self.processed_documents = 0
    
    def get_module_info(self):
        return {
            "module_id": "document_analyzer",
            "version": "1.0.0",
            "description": "AI-powered document analysis agent"
        }
    
    def get_capabilities(self):
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self):
        return ModuleHealth(
            module_id="document_analyzer",
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=time.time() - self.start_time
        )
    
    def graceful_degradation(self):
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
```

### Step 2: Add Core Functionality

```python
def analyze_document(self, document_path: str) -> Dict[str, Any]:
    """Analyze a document and return insights."""
    with self.trace_operation("analyze_document", path=document_path) as trace:
        # Load previous analysis context
        context = self.memory_palace.recall("analysis_context")
        
        # Perform analysis (simplified for demo)
        analysis = {
            "document": document_path,
            "word_count": len(open(document_path).read().split()),
            "analysis_time": datetime.now().isoformat(),
            "previous_context": context
        }
        
        # Store results for future reference
        self.memory_palace.remember("last_analysis", analysis)
        
        # Update metrics
        self.processed_documents += 1
        self.metrics["documents_processed"] = self.processed_documents
        
        trace.output_result = analysis
        return analysis
```

### Step 3: Add DAG Orchestration

```python
def analyze_multiple_documents(self, document_paths: List[str]) -> Dict[str, Any]:
    """Analyze multiple documents using DAG orchestration."""
    from src.dag_orchestration import DAGOrchestrator
    
    orchestrator = DAGOrchestrator()
    
    # Create tasks for each document
    for i, doc_path in enumerate(document_paths):
        task_id = f"analyze_doc_{i}"
        orchestrator.add_task(
            task_id,
            func=self.analyze_document,
            args=[doc_path],
            dependencies=[]  # Can run in parallel
        )
    
    # Add summary task that depends on all analyses
    orchestrator.add_task(
        "create_summary",
        func=self._create_analysis_summary,
        dependencies=[f"analyze_doc_{i}" for i in range(len(document_paths))]
    )
    
    # Execute with automatic parallelization
    results = orchestrator.execute()
    return results
```

### Step 4: Test Your Agent

```python
# Create and test the agent
analyzer = DocumentAnalyzer()

# Check health
health = analyzer.get_health_status()
print(f"Agent health: {health.status}")

# Analyze a document
result = analyzer.analyze_document("README.md")
print(f"Analysis complete: {result}")

# The agent automatically:
# - Traces the operation with correlation IDs
# - Stores context in Memory Palace
# - Updates health metrics
# - Provides Prometheus metrics
# - Handles errors gracefully
```

---

## 🚀 Advanced Features

### Custom Health Checks

```python
class MyAgent(ReflectiveModule):
    def get_health_status(self):
        # Custom health logic
        issues = []
        health_score = 1.0
        
        # Check external dependencies
        if not self._check_database_connection():
            issues.append("Database connection failed")
            health_score -= 0.3
        
        if not self._check_api_endpoints():
            issues.append("API endpoints not responding")
            health_score -= 0.2
        
        status = ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.WARNING
        
        return ModuleHealth(
            module_id=self.get_module_info()["module_id"],
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now()
        )
```

### Custom Metrics

```python
def process_request(self, request):
    # Custom metrics collection
    start_time = time.time()
    
    try:
        result = self._handle_request(request)
        
        # Record success metrics
        self.metrics["requests_processed"] = self.metrics.get("requests_processed", 0) + 1
        self.metrics["avg_response_time"] = (time.time() - start_time) * 1000
        
        return result
        
    except Exception as e:
        # Record error metrics
        self.metrics["request_errors"] = self.metrics.get("request_errors", 0) + 1
        raise
```

---

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build production image
docker build -t beast-mode-app .

# Run with production configuration
docker run -d \
  --name beast-mode \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e REDIS_HOST=redis.example.com \
  -e REDIS_PASSWORD=${REDIS_PASSWORD} \
  beast-mode-app
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beast-mode-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: beast-mode
  template:
    metadata:
      labels:
        app: beast-mode
    spec:
      containers:
      - name: app
        image: beast-mode-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
```

### Monitoring Setup

```bash
# Start monitoring stack
docker-compose -f deployment/monitoring.yml up -d

# Access dashboards
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

---

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Redis Connection Issues  
```bash
# Error: Redis connection failed
# Solution: Check Redis configuration
redis-cli ping  # Should return PONG
```

#### Health Check Failures
```python
# Debug health issues
agent = MyAgent()
health = agent.get_health_status()
for issue in health.issues:
    print(f"Issue: {issue}")
```

### Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: Working code in `examples/`
- **Issues**: GitHub Issues for bug reports
- **Community**: GitHub Discussions for questions

---

*This is a condensed version. The full user guide continues with detailed examples, API reference, and advanced patterns.*
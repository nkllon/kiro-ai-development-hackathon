# Beast Mode API Reference

## Visual Diagram Validation API

### Core Interfaces

#### ValidationPipeline

The main entry point for visual diagram quality validation.

```python
from src.visual_diagram_validation import ValidationPipeline

pipeline = ValidationPipeline()
result = pipeline.validate(
    input_data=diagram_bytes,
    filename="diagram.svg",
    audience_mode="general"  # "general", "technical", "accessibility"
)
```

**Parameters:**
- `input_data` (bytes): Raw diagram data
- `filename` (str, optional): Filename for format detection
- `audience_mode` (str): Target audience for feedback generation

**Returns:**
- `Dict[str, Any]`: Comprehensive validation results including violations, recommendations, and quality scores

#### ProcessorInterface

Base interface for format-specific processors.

```python
from src.visual_diagram_validation.core.interfaces import ProcessorInterface

class CustomProcessor(ProcessorInterface):
    def can_process(self, input_data: bytes, filename: str = None) -> bool:
        """Check if this processor can handle the input format."""
        
    def render_to_png(self, input_data: bytes, width: int = 2048, 
                     height: int = 2048, dpi: int = 300) -> PNGImage:
        """Convert input to standardized PNG format."""
        
    def extract_metadata(self, input_data: bytes) -> Dict[str, Any]:
        """Extract format-specific metadata."""
        
    @property
    def supported_formats(self) -> List[str]:
        """List of supported file extensions."""
```

#### QualityAnalyzer

Base interface for quality analysis modules.

```python
from src.visual_diagram_validation.core.interfaces import QualityAnalyzer

class CustomAnalyzer(QualityAnalyzer):
    def analyze(self, image: PNGImage, metadata: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze image for quality violations."""
        
    @property
    def analyzer_name(self) -> str:
        """Name of this analyzer."""
        
    @property
    def supported_rules(self) -> List[str]:
        """List of quality rules this analyzer enforces."""
```

### Data Models

#### PNGImage

Represents a processed PNG image with metadata.

```python
from src.visual_diagram_validation.core.models import PNGImage

image = PNGImage(
    data=png_bytes,
    width=1920,
    height=1080,
    dpi=300,
    color_mode="RGB",
    metadata={"source_format": "svg"}
)
```

#### AnalysisResult

Contains quality analysis results and recommendations.

```python
from src.visual_diagram_validation.core.models import AnalysisResult

result = AnalysisResult(
    analyzer_name="contrast_analyzer",
    violations=[...],
    recommendations=[...],
    quality_score=0.85,
    metadata={}
)
```

#### QualityViolation

Represents a specific quality issue found during analysis.

```python
from src.visual_diagram_validation.core.models import QualityViolation, Severity

violation = QualityViolation(
    rule_id="contrast_ratio",
    severity=Severity.WARNING,
    message="Low contrast ratio detected",
    location=BoundingBox(x=100, y=200, width=50, height=30),
    suggested_fix="Increase color contrast to meet WCAG guidelines"
)
```

## DAG Orchestration API

### Core Interfaces

#### OrchestrationEngine

Main interface for DAG analysis and optimization.

```python
from src.beast_mode.dag_orchestration import OrchestrationEngine

engine = OrchestrationEngine()
result = engine.optimize_execution(constraint_graph)
```

**Methods:**
- `optimize_execution(constraint_graph: ConstraintGraph) -> OptimizedExecution`
- `analyze_dependencies(specs: List[str]) -> DependencyAnalysisResult`
- `calculate_mvp_route(criteria: MVPCriteria) -> MVPRoute`

#### ParallelOptimizer

Optimization engine for parallel execution planning.

```python
from src.beast_mode.dag_orchestration.optimization import ParallelOptimizer

optimizer = ParallelOptimizer(OptimizationStrategy.BALANCED)
execution_plan = optimizer.optimize_execution(constraint_graph)
```

**Parameters:**
- `optimization_strategy`: SPEED_OPTIMIZED, RESOURCE_OPTIMIZED, or BALANCED

**Returns:**
- `OptimizedExecution`: Complete execution plan with parallel groups and phases

### Data Models

#### TaskNode

Represents a task in the dependency graph.

```python
from src.beast_mode.dag_orchestration.models import TaskNode, TaskStatus

task = TaskNode(
    task_id="implement_feature_x",
    spec_name="feature_x_spec",
    task_name="Implement Feature X",
    description="Core implementation of feature X functionality",
    estimated_effort=40,  # hours
    completion_status=TaskStatus.NOT_STARTED,
    dependencies=["setup_environment"],
    priority=2,  # 1=highest, 5=lowest
    complexity=3.0  # 1.0=simple, 5.0=very complex
)
```

#### ParallelGroup

Group of tasks that can execute in parallel.

```python
from src.beast_mode.dag_orchestration.models import ParallelGroup

group = ParallelGroup(
    group_id="frontend_tasks",
    tasks=[task1, task2, task3],
    estimated_duration=5,  # days
    coordination_overhead=0.15,  # 15% overhead
    resource_requirements={"developers": 2, "skills": ["react", "typescript"]}
)
```

#### OptimizedExecution

Complete optimized execution plan.

```python
from src.beast_mode.dag_orchestration.models import OptimizedExecution

execution = OptimizedExecution(
    execution_id="project_alpha_v1",
    execution_phases=[phase1, phase2, phase3],
    resource_allocation=resource_plan,
    parallel_groups=[group1, group2],
    estimated_timeline=8,  # weeks
    maximum_parallelism=4,  # concurrent tasks
    bottlenecks=["senior_developer_availability", "testing_environment"]
)
```

#### ResourceRequirements

Defines resource needs for execution.

```python
from src.beast_mode.dag_orchestration.models import ResourceRequirements

requirements = ResourceRequirements(
    developers_needed=3,
    skill_requirements=["python", "react", "docker"],
    estimated_hours=120,
    tools_required=["pytest", "jest", "docker-compose"]
)
```

### Enums

#### TaskStatus

```python
from src.beast_mode.dag_orchestration.models.enums import TaskStatus

# Available values:
TaskStatus.NOT_STARTED
TaskStatus.IN_PROGRESS  
TaskStatus.COMPLETED
TaskStatus.BLOCKED
TaskStatus.ON_HOLD
```

#### OptimizationStrategy

```python
from src.beast_mode.dag_orchestration.models.enums import OptimizationStrategy

# Available values:
OptimizationStrategy.SPEED_OPTIMIZED    # Minimize timeline
OptimizationStrategy.RESOURCE_OPTIMIZED # Minimize resource usage
OptimizationStrategy.BALANCED          # Balance speed and resources
```

## Beast Mode Core API

### Reflective Module Pattern

Base class for all Beast Mode components.

```python
from src.beast_mode.core.reflective_module import ReflectiveModule

class MyModule(ReflectiveModule):
    def _get_module_name(self) -> str:
        """Return unique module identifier."""
        return "my_module"
    
    def _get_primary_responsibility(self) -> str:
        """Return single primary responsibility."""
        return "specific_functionality_implementation"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return current health status."""
        return {
            "status": "healthy",
            "last_check": datetime.now().isoformat(),
            "metrics": self._collect_metrics()
        }
```

### PDCA Orchestrator

Systematic Plan-Do-Check-Act cycle management.

```python
from src.beast_mode.core.pdca_orchestrator import PDCAOrchestrator

orchestrator = PDCAOrchestrator()

# Execute PDCA cycle
result = orchestrator.execute_cycle(
    plan_config={"objective": "implement_feature", "resources": resources},
    execution_strategy="systematic",
    validation_criteria=["tests_pass", "coverage_90_percent"],
    improvement_actions=["optimize_performance", "enhance_documentation"]
)
```

### Model Registry

Central registry for model-driven decisions.

```python
from src.beast_mode.core.model_registry import ModelRegistry

registry = ModelRegistry()

# Register a model
registry.register_model(
    model_id="feature_complexity_predictor",
    model_type="classification",
    version="1.0.0",
    metadata={"accuracy": 0.92, "training_date": "2025-01-01"}
)

# Query for decisions
decision = registry.get_decision_recommendation(
    context={"feature_type": "api_endpoint", "complexity": "medium"},
    decision_type="resource_allocation"
)
```

## Error Handling

### Standard Exception Hierarchy

```python
from src.beast_mode.core.exceptions import (
    BeastModeException,
    ValidationError,
    ConfigurationError,
    ResourceError
)

try:
    result = pipeline.validate(diagram_data)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Suggestions: {e.suggestions}")
except ResourceError as e:
    print(f"Resource issue: {e.resource_type} - {e.message}")
```

### Systematic Error Recovery

```python
from src.beast_mode.resilience import GracefulDegradationManager

degradation_manager = GracefulDegradationManager()

# Register service with fallback
degradation_manager.register_service(
    service_name="diagram_processor",
    health_check=lambda: processor.is_healthy(),
    fallback_handler=lambda data: basic_processing(data)
)

# Execute with automatic fallback
result = degradation_manager.execute_with_fallback(
    service_name="diagram_processor",
    primary_function=advanced_processing,
    data=input_data
)
```

## Configuration

### Environment Configuration

```python
from src.visual_diagram_validation.core.config import ValidationConfig

config = ValidationConfig(
    max_image_size=10_000_000,  # 10MB
    default_dpi=300,
    supported_formats=["svg", "png", "pdf"],
    quality_thresholds={
        "contrast_ratio": 4.5,
        "text_size_minimum": 12,
        "color_difference": 3.0
    }
)
```

### Optimization Configuration

```python
from src.beast_mode.dag_orchestration.optimization import OptimizationConfig

config = OptimizationConfig(
    max_parallel_tasks=8,
    coordination_overhead_factor=0.1,
    resource_utilization_target=0.85,
    risk_tolerance="medium"
)
```

## Integration Examples

### Complete Workflow Example

```python
from src.visual_diagram_validation import ValidationPipeline
from src.beast_mode.dag_orchestration import OrchestrationEngine
from src.beast_mode.core.pdca_orchestrator import PDCAOrchestrator

# Initialize components
validator = ValidationPipeline()
orchestrator = OrchestrationEngine()
pdca = PDCAOrchestrator()

# Validate diagrams in specification
diagram_results = []
for diagram_file in spec_diagrams:
    with open(diagram_file, 'rb') as f:
        result = validator.validate(f.read(), diagram_file)
        diagram_results.append(result)

# Optimize implementation execution
constraint_graph = orchestrator.analyze_dependencies(spec_files)
execution_plan = orchestrator.optimize_execution(constraint_graph)

# Execute with PDCA cycle
pdca_result = pdca.execute_cycle(
    plan_config={
        "execution_plan": execution_plan,
        "quality_gates": ["diagram_validation", "test_coverage"]
    },
    execution_strategy="systematic_parallel",
    validation_criteria=["all_tests_pass", "coverage_90_percent"],
    improvement_actions=["optimize_bottlenecks", "enhance_monitoring"]
)

print(f"Execution timeline: {execution_plan.estimated_timeline} weeks")
print(f"Maximum parallelism: {execution_plan.maximum_parallelism} tasks")
print(f"Quality score: {sum(r['quality_score'] for r in diagram_results) / len(diagram_results)}")
```

This API reference provides comprehensive coverage of the Beast Mode framework's public interfaces, enabling systematic integration and extension of the development environment.
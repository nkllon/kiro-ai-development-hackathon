# DAG Orchestration Examples

This directory contains practical examples demonstrating common DAG orchestration patterns and use cases.

## Example Categories

### Basic Patterns
- [Simple Sequential Pipeline](basic-sequential-pipeline.py) - Tasks that run in order
- [Parallel Execution](parallel-execution.py) - Independent tasks running concurrently
- [Fan-Out Fan-In](fan-out-fan-in.py) - One task triggers multiple, then converges
- [Diamond Dependencies](diamond-dependencies.py) - Complex dependency relationships

### LLM Integration
- [Code Review Workflow](llm-code-review.py) - Automated code review using LLMs
- [Documentation Generation](llm-documentation.py) - Generate docs from code
- [Multi-LLM Pipeline](multi-llm-pipeline.py) - Using different LLMs for different tasks
- [Cost-Aware Execution](cost-aware-llm.py) - Budget-constrained LLM usage

### Real-World Workflows
- [CI/CD Pipeline](cicd-pipeline.py) - Complete CI/CD workflow
- [Data Processing Pipeline](data-processing.py) - ETL workflow with validation
- [Machine Learning Pipeline](ml-pipeline.py) - Model training and deployment
- [Website Deployment](website-deployment.py) - Full website deployment workflow

### Advanced Patterns
- [Conditional Execution](conditional-execution.py) - Tasks that run based on conditions
- [Dynamic Task Generation](dynamic-tasks.py) - Generate tasks at runtime
- [Error Recovery](error-recovery.py) - Handling and recovering from failures
- [Resource Optimization](resource-optimization.py) - Optimizing resource usage

### Beast Mode Integration
- [ReflectiveModule Integration](beast-mode-integration.py) - Using Beast Mode patterns
- [Health Monitoring](health-monitoring.py) - Comprehensive health checks
- [Metrics Collection](metrics-collection.py) - Custom metrics and monitoring
- [Observatory Integration](observatory-integration.py) - Integration with Observatory

## Running Examples

Each example is self-contained and can be run independently:

```bash
# Run a basic example
python examples/basic-sequential-pipeline.py

# Run with verbose output
python examples/parallel-execution.py --verbose

# Run with custom configuration
python examples/cicd-pipeline.py --config examples/configs/cicd-config.yaml
```

## Example Structure

Each example follows this structure:

```python
#!/usr/bin/env python3
"""
Example: [Name]
Description: [What this example demonstrates]
"""

# Imports
from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
# ... other imports

def create_tasks():
    """Create the task definitions for this example."""
    # Task creation logic
    pass

def main():
    """Main execution function."""
    # Setup and execution logic
    pass

if __name__ == "__main__":
    main()
```

## Configuration Files

Some examples use configuration files in the `configs/` directory:

- `basic-config.yaml` - Basic orchestration settings
- `llm-config.yaml` - LLM provider configurations
- `resource-config.yaml` - Resource limit configurations
- `monitoring-config.yaml` - Monitoring and observability settings

## Prerequisites

Before running examples, ensure you have:

1. **DAG Orchestration System** installed and configured
2. **Redis server** running (for distributed examples)
3. **LLM CLI tools** installed (for LLM examples)
4. **Required dependencies** for specific examples

Check prerequisites:

```bash
bash scripts/check_dag_orchestrated_parallel_execution_prereqs.sh
```

## Example Output

Most examples produce structured output showing:

- DAG validation results
- Execution progress
- Task completion status
- Performance metrics
- Resource usage
- Cost information (for LLM tasks)

Example output format:

```
🚀 Example: Basic Sequential Pipeline
=====================================
📋 Created 4 tasks
🔍 Validating DAG structure...
✅ DAG validation passed
📊 Execution order: setup → process → validate → cleanup
🎯 Executing DAG...
  ✅ setup (2.1s)
  ✅ process (5.3s)
  ✅ validate (1.8s)
  ✅ cleanup (0.9s)
📊 Results: 4/4 completed, 0 failed, 10.1s total
```

## Contributing Examples

To contribute a new example:

1. **Follow the standard structure** shown above
2. **Include comprehensive comments** explaining the pattern
3. **Add error handling** for common failure scenarios
4. **Include configuration options** where appropriate
5. **Test thoroughly** with different scenarios
6. **Update this README** with your example

### Example Template

```python
#!/usr/bin/env python3
"""
Example: [Your Example Name]
Description: [What this example demonstrates]

This example shows how to [specific use case].
Key concepts demonstrated:
- [Concept 1]
- [Concept 2]
- [Concept 3]
"""

import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.core.task_definition import TaskDefinition
# ... other imports

def create_tasks() -> List[TaskDefinition]:
    """
    Create task definitions for this example.
    
    Returns:
        List[TaskDefinition]: Tasks to execute
    """
    tasks = [
        # Your task definitions here
    ]
    return tasks

def main():
    """Main execution function."""
    print("🚀 Example: [Your Example Name]")
    print("=" * 40)
    
    try:
        # Setup orchestrator
        orchestrator = DAGOrchestrator()
        
        # Create and validate tasks
        tasks = create_tasks()
        validation = orchestrator.validate_dag(tasks)
        
        if not validation.is_valid:
            print("❌ DAG validation failed")
            return False
        
        # Execute DAG
        result = orchestrator.execute_dag(tasks)
        
        # Report results
        print(f"📊 Results: {len(result.completed_tasks)}/{result.total_tasks} completed")
        return result.status == "COMPLETED"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Troubleshooting Examples

If examples fail to run:

1. **Check prerequisites**: Run the prerequisite checker
2. **Verify paths**: Ensure Python can find the DAG orchestration modules
3. **Check dependencies**: Install any missing dependencies
4. **Review logs**: Check execution logs for detailed error information
5. **Test components**: Run individual components to isolate issues

Common issues:

- **Import errors**: Add `src/` to Python path
- **Redis connection**: Ensure Redis server is running
- **Resource limits**: Adjust resource limits for your system
- **LLM availability**: Install and configure LLM CLI tools
- **Permission errors**: Ensure proper file permissions

## Performance Notes

Examples are designed for demonstration and may not be optimized for production use. For production deployments:

- **Adjust resource limits** based on your system capacity
- **Configure appropriate timeouts** for your use case
- **Implement proper error handling** and retry logic
- **Add comprehensive monitoring** and alerting
- **Test with realistic workloads** before deployment

## Next Steps

After exploring examples:

1. **Adapt patterns** to your specific use cases
2. **Combine patterns** to create complex workflows
3. **Add custom executors** for specialized tasks
4. **Integrate with your systems** using Beast Mode patterns
5. **Contribute back** examples that others might find useful

For more advanced usage, see:
- [API Reference](../api-reference.md)
- [Performance Tuning Guide](../performance-tuning.md)
- [Integration Guide](../integration-guide.md)
- [Troubleshooting Guide](../troubleshooting.md)
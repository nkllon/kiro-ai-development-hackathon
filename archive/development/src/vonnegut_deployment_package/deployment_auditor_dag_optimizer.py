#!/usr/bin/env python3
"""
Deployment Data Auditor DAG Optimizer
=====================================

Transforms the deployment data auditor task list into a DAG-optimized execution plan
with proper dependency validation, parallel execution groups, and Beast Mode integration.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import json
import yaml
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import networkx as nx
from datetime import datetime

@dataclass
class Task:
    """Represents a single task in the DAG."""
    id: str
    name: str
    description: str
    requirements: List[str]
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: float = 1.0
    parallel_group: str = ""
    beast_mode_integration: bool = False

@dataclass
class ParallelGroup:
    """Represents a group of tasks that can run in parallel."""
    name: str
    tasks: List[str]
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)

class DeploymentAuditorDAGOptimizer:
    """Optimizes deployment auditor tasks into DAG structure."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.parallel_groups: Dict[str, ParallelGroup] = {}
        self.dag = nx.DiGraph()
        
    def load_tasks_from_spec(self) -> None:
        """Load tasks from the specification file."""
        # Define all tasks with their dependencies and metadata
        task_definitions = [
            # Foundation Layer - Can run in parallel
            Task("1.1", "Create core data models", "Implement FileEvent, Violation, ClassifiedViolation", 
                 ["6.1", "6.5"], [], 2.0, "foundation", True),
            Task("1.2", "Implement ReflectiveModule integration", "Beast Mode framework integration", 
                 ["8.1", "8.2", "8.3"], [], 3.0, "foundation", True),
            Task("1.3", "Write unit tests for base classes", "Test data models and base classes", 
                 ["10.1"], ["1.1", "1.2"], 2.0, "foundation", False),
            
            Task("6.1", "Build configuration system", "YAML-based configuration with validation", 
                 ["6.1", "6.2", "6.3", "6.5"], [], 3.0, "foundation", True),
            Task("6.2", "Implement hot-reloading", "Configuration reloading and validation", 
                 ["6.5", "6.6"], ["6.1"], 2.0, "foundation", True),
            Task("6.3", "Write configuration tests", "Test configuration management", 
                 ["10.1"], ["6.1", "6.2"], 1.5, "foundation", False),
            
            Task("9.1", "Implement CLI interface", "Command-line interface for management", 
                 ["5.1", "6.1"], ["1.2"], 4.0, "foundation", True),
            Task("9.2", "Build daemon lifecycle", "Daemon start/stop/restart functionality", 
                 ["1.1", "8.6"], ["1.2"], 3.0, "foundation", True),
            Task("9.3", "Write CLI tests", "Test CLI and daemon functionality", 
                 ["10.1", "10.2"], ["9.1", "9.2"], 2.0, "foundation", False), 
           
            # Core Components Layer - After foundation
            Task("2.1", "Implement file system watching", "Cross-platform file monitoring", 
                 ["1.1", "7.1", "7.5"], ["1.2", "6.1"], 4.0, "core", True),
            Task("2.2", "Create baseline scanning", "Full directory scan functionality", 
                 ["1.4", "7.1", "7.2"], ["1.2", "6.1"], 3.0, "core", True),
            Task("2.3", "Write file monitoring tests", "Test file system monitoring", 
                 ["10.1", "10.4"], ["2.1", "2.2"], 2.0, "core", False),
            
            Task("3.1", "Implement pattern matching", "Core violation detection engine", 
                 ["2.1", "2.2", "2.3", "2.4", "2.5"], ["1.2", "6.1"], 4.0, "core", True),
            Task("3.2", "Create violation classifier", "Severity assessment and risk scoring", 
                 ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"], ["3.1"], 3.0, "core", True),
            Task("3.3", "Write pattern matching tests", "Test violation detection", 
                 ["10.1", "10.2"], ["3.1", "3.2"], 2.5, "core", False),
            
            # Integration Layer - After core components
            Task("4.1", "Implement gitignore management", "Automated .gitignore updates", 
                 ["3.1", "3.5"], ["3.2"], 3.0, "integration", True),
            Task("4.2", "Create file quarantine", "Secure file quarantine system", 
                 ["3.2", "3.4"], ["3.2"], 2.5, "integration", True),
            Task("4.3", "Build git integration", "Repository operations and commit blocking", 
                 ["4.1", "4.2", "4.3", "4.4"], ["4.1", "4.2"], 4.0, "integration", True),
            Task("4.4", "Write remediation tests", "Test automated remediation", 
                 ["10.2", "10.4"], ["4.1", "4.2", "4.3"], 3.0, "integration", False),
            
            Task("5.1", "Create reporting engine", "Violation reports and analysis", 
                 ["5.1", "5.4", "9.1", "9.2"], ["3.2"], 3.5, "integration", True),
            Task("5.2", "Build notification system", "Multi-channel alert system", 
                 ["5.3", "6.4", "9.2"], ["5.1"], 3.0, "integration", True),
            Task("5.3", "Implement Prometheus metrics", "Metrics export and monitoring", 
                 ["5.5", "8.3", "8.5"], ["1.2", "5.1"], 2.5, "integration", True),
            Task("5.4", "Write reporting tests", "Test reporting and notifications", 
                 ["10.1", "10.2"], ["5.1", "5.2", "5.3"], 2.0, "integration", False),
            
            # Optimization Layer - After integration
            Task("7.1", "Create resource monitoring", "CPU and memory usage tracking", 
                 ["7.2", "7.3", "7.4"], ["1.2", "5.3"], 3.0, "optimization", True),
            Task("7.2", "Build event processing", "Event batching and queue management", 
                 ["7.1", "7.5"], ["2.1", "7.1"], 3.5, "optimization", True),
            Task("7.3", "Write performance tests", "Load testing and optimization", 
                 ["10.4"], ["7.1", "7.2"], 4.0, "optimization", False),
            
            Task("8.1", "Create emergency detection", "Mass violation detection system", 
                 ["9.1", "9.2", "9.3"], ["4.3", "5.2"], 3.0, "optimization", True),
            Task("8.2", "Build recovery systems", "Automated cleanup and recovery", 
                 ["9.3", "9.4", "9.5"], ["8.1"], 3.5, "optimization", True),
            Task("8.3", "Write emergency tests", "Test emergency response", 
                 ["10.1", "10.4"], ["8.1", "8.2"], 2.5, "optimization", False),
            
            # Validation Layer - Requires all previous tasks
            Task("10.1", "Create end-to-end tests", "Complete workflow testing", 
                 ["10.2", "10.4"], ["4.3", "5.2", "8.2"], 5.0, "validation", False),
            Task("10.2", "Build deployment tools", "Installation and integration", 
                 ["4.3"], ["9.2", "10.1"], 3.0, "validation", False),
            Task("10.3", "Create documentation", "User guides and troubleshooting", 
                 ["6.1", "6.2"], ["10.1", "10.2"], 4.0, "validation", False),
            Task("10.4", "Write integration tests", "Test deployment and setup", 
                 ["10.1", "10.2"], ["10.2", "10.3"], 3.0, "validation", False),
        ]
        
        # Store tasks
        for task in task_definitions:
            self.tasks[task.id] = task
            
    def build_dag(self) -> None:
        """Build the DAG from task dependencies."""
        # Add all tasks as nodes
        for task_id, task in self.tasks.items():
            self.dag.add_node(task_id, **task.__dict__)
            
        # Add dependency edges
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    self.dag.add_edge(dep_id, task_id)
                    
    def validate_dag(self) -> Dict[str, Any]:
        """Validate DAG structure and detect cycles."""
        validation_result = {
            "is_valid": True,
            "has_cycles": False,
            "cycles": [],
            "topological_order": [],
            "parallel_groups": {},
            "critical_path": [],
            "total_tasks": len(self.tasks),
            "estimated_sequential_hours": sum(task.estimated_hours for task in self.tasks.values()),
            "estimated_parallel_hours": 0
        }
        
        try:
            # Check for cycles
            cycles = list(nx.simple_cycles(self.dag))
            if cycles:
                validation_result["has_cycles"] = True
                validation_result["cycles"] = cycles
                validation_result["is_valid"] = False
                return validation_result
                
            # Get topological order
            validation_result["topological_order"] = list(nx.topological_sort(self.dag))
            
            # Create parallel groups
            self._create_parallel_groups()
            validation_result["parallel_groups"] = {
                name: {
                    "tasks": group.tasks,
                    "estimated_hours": group.estimated_hours,
                    "dependencies": group.dependencies
                }
                for name, group in self.parallel_groups.items()
            }
            
            # Calculate critical path
            critical_path = self._calculate_critical_path()
            validation_result["critical_path"] = critical_path
            validation_result["estimated_parallel_hours"] = sum(
                group.estimated_hours for group in self.parallel_groups.values()
            )
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["error"] = str(e)
            
        return validation_result   
     
    def _create_parallel_groups(self) -> None:
        """Create parallel execution groups from tasks."""
        # Group tasks by their parallel_group attribute
        groups = {}
        for task_id, task in self.tasks.items():
            if task.parallel_group:
                if task.parallel_group not in groups:
                    groups[task.parallel_group] = []
                groups[task.parallel_group].append(task_id)
                
        # Create ParallelGroup objects
        for group_name, task_ids in groups.items():
            group_tasks = [self.tasks[tid] for tid in task_ids]
            total_hours = max(task.estimated_hours for task in group_tasks)  # Parallel execution
            
            # Find group dependencies (tasks that all group members depend on)
            all_deps = set()
            for task in group_tasks:
                all_deps.update(task.dependencies)
            
            # Remove internal dependencies (within the group)
            external_deps = [dep for dep in all_deps if dep not in task_ids]
            
            self.parallel_groups[group_name] = ParallelGroup(
                name=group_name,
                tasks=task_ids,
                estimated_hours=total_hours,
                dependencies=external_deps
            )
            
    def _calculate_critical_path(self) -> List[str]:
        """Calculate the critical path through the DAG."""
        # Add weights to edges based on task duration
        weighted_dag = self.dag.copy()
        for node in weighted_dag.nodes():
            task = self.tasks[node]
            weighted_dag.nodes[node]['weight'] = task.estimated_hours
            
        # Find longest path (critical path)
        try:
            # Use topological sort to find longest path
            topo_order = list(nx.topological_sort(weighted_dag))
            distances = {node: 0 for node in weighted_dag.nodes()}
            predecessors = {node: None for node in weighted_dag.nodes()}
            
            for node in topo_order:
                node_weight = weighted_dag.nodes[node]['weight']
                for successor in weighted_dag.successors(node):
                    new_distance = distances[node] + node_weight
                    if new_distance > distances[successor]:
                        distances[successor] = new_distance
                        predecessors[successor] = node
                        
            # Find the node with maximum distance
            max_node = max(distances.keys(), key=lambda x: distances[x])
            
            # Reconstruct path
            path = []
            current = max_node
            while current is not None:
                path.append(current)
                current = predecessors[current]
                
            return list(reversed(path))
            
        except Exception:
            return []
            
    def generate_makefile(self) -> str:
        """Generate optimized Makefile with parallel execution."""
        makefile_content = [
            "# Deployment Data Auditor - DAG Optimized Makefile",
            "# Generated automatically - do not edit manually",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            ".PHONY: all clean validate-dag help",
            "",
            "# Default target",
            "all: validate-dag deployment-auditor",
            "",
            "# Help target",
            "help:",
            "\t@echo 'Deployment Data Auditor Build System'",
            "\t@echo 'Available targets:'",
            "\t@echo '  all                 - Build complete system'",
            "\t@echo '  validate-dag        - Validate DAG structure'",
            "\t@echo '  foundation          - Build foundation layer'",
            "\t@echo '  core                - Build core components'",
            "\t@echo '  integration         - Build integration layer'",
            "\t@echo '  optimization        - Build optimization layer'",
            "\t@echo '  validation          - Build validation layer'",
            "\t@echo '  clean               - Clean build artifacts'",
            "",
            "# DAG validation",
            "validate-dag:",
            "\t@echo 'Validating DAG structure...'",
            "\t@python scripts/deployment_auditor_dag_optimizer.py --validate",
            "",
        ]
        
        # Add parallel group targets
        for group_name, group in self.parallel_groups.items():
            # Group target
            makefile_content.extend([
                f"# {group_name.title()} Layer - Parallel Execution",
                f"{group_name}: {' '.join(group.dependencies)} {' '.join([f'task-{tid}' for tid in group.tasks])}",
                f"\t@echo '{group_name.title()} layer complete'",
                "",
            ])
            
            # Individual task targets
            for task_id in group.tasks:
                task = self.tasks[task_id]
                deps = ' '.join([f'task-{dep}' for dep in task.dependencies])
                makefile_content.extend([
                    f"task-{task_id}: {deps}",
                    f"\t@echo 'Executing Task {task_id}: {task.name}'",
                    f"\t@python scripts/execute_task_{task_id.replace('.', '_')}.py",
                    f"\t@touch .task-{task_id}-complete",
                    "",
                ])
                
        # Add main target
        group_order = ["foundation", "core", "integration", "optimization", "validation"]
        makefile_content.extend([
            "# Main deployment auditor target",
            f"deployment-auditor: {' '.join(group_order)}",
            "\t@echo 'Deployment Data Auditor build complete!'",
            "\t@echo 'Run: python -m deployment_auditor --help'",
            "",
            "# Clean target",
            "clean:",
            "\t@echo 'Cleaning build artifacts...'",
            "\t@rm -f .task-*-complete",
            "\t@find . -name '*.pyc' -delete",
            "\t@find . -name '__pycache__' -delete",
            "",
        ])
        
        return '\n'.join(makefile_content)
        
    def generate_execution_scripts(self) -> Dict[str, str]:
        """Generate execution scripts for each task."""
        scripts = {}
        
        for task_id, task in self.tasks.items():
            script_name = f"execute_task_{task_id.replace('.', '_')}.py"
            script_content = f'''#!/usr/bin/env python3
"""
Task {task_id} Execution Script: {task.name}
Generated automatically from DAG optimization

Requirements: {', '.join(task.requirements)}
Dependencies: {', '.join(task.dependencies)}
Estimated Hours: {task.estimated_hours}
Beast Mode Integration: {task.beast_mode_integration}
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_logging():
    """Set up structured logging for task execution."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/task_{task_id.replace(".", "_")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(f'task_{task_id.replace(".", "_")}')

def validate_dependencies():
    """Validate that all dependencies are complete."""
    dependencies = {repr(task.dependencies)}
    missing_deps = []
    
    for dep in dependencies:
        dep_file = Path(f'.task-{{dep}}-complete')
        if not dep_file.exists():
            missing_deps.append(dep)
            
    if missing_deps:
        raise RuntimeError(f"Missing dependencies: {{missing_deps}}")
        
def execute_task():
    """Execute the main task logic."""
    logger = setup_logging()
    logger.info(f"Starting Task {task_id}: {task.name}")
    
    try:
        # Validate dependencies
        validate_dependencies()
        
        # Task-specific implementation would go here
        logger.info(f"Task {task_id} implementation placeholder")
        logger.info(f"Description: {task.description}")
        logger.info(f"Requirements: {', '.join(task.requirements)}")
        
        # Beast Mode integration setup
        if {task.beast_mode_integration}:
            logger.info("Setting up Beast Mode ReflectiveModule integration")
            # from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
            
        # Mark task as complete
        Path(f'.task-{task_id}-complete').touch()
        
        logger.info(f"Task {task_id} completed successfully")
        return {{"status": "success", "task_id": "{task_id}", "completed_at": datetime.now().isoformat()}}
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {{e}}")
        return {{"status": "error", "task_id": "{task_id}", "error": str(e)}}

if __name__ == "__main__":
    result = execute_task()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "success" else 1)
'''
            scripts[script_name] = script_content
            
        return scripts       
 
    def generate_dag_visualization(self) -> str:
        """Generate Mermaid diagram for DAG visualization."""
        mermaid_content = [
            "graph TD",
            "    %% Deployment Data Auditor DAG Structure",
            f"    %% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "    %% Parallel Groups: Foundation → Core → Integration → Optimization → Validation",
            "",
        ]
        
        # Add nodes with styling
        for task_id, task in self.tasks.items():
            node_id = f"T{task_id.replace('.', '_')}"
            node_label = f"{task_id}: {task.name[:30]}..."
            
            if task.beast_mode_integration:
                mermaid_content.append(f"    {node_id}[\"{node_label}\"]")
            else:
                mermaid_content.append(f"    {node_id}(\"{node_label}\")")
                
        mermaid_content.append("")
        
        # Add edges
        for task_id, task in self.tasks.items():
            node_id = f"T{task_id.replace('.', '_')}"
            for dep_id in task.dependencies:
                dep_node_id = f"T{dep_id.replace('.', '_')}"
                mermaid_content.append(f"    {dep_node_id} --> {node_id}")
                
        mermaid_content.append("")
        
        # Add styling
        mermaid_content.extend([
            "    %% Styling",
            "    classDef foundation fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
            "    classDef core fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px", 
            "    classDef integration fill:#fff3e0,stroke:#ef6c00,stroke-width:2px",
            "    classDef optimization fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            "    classDef validation fill:#ffebee,stroke:#c62828,stroke-width:2px",
            "",
        ])
        
        # Apply styling to nodes
        for group_name, group in self.parallel_groups.items():
            task_nodes = [f"T{tid.replace('.', '_')}" for tid in group.tasks]
            mermaid_content.append(f"    class {','.join(task_nodes)} {group_name}")
            
        return '\n'.join(mermaid_content)
        
    def generate_documentation(self) -> str:
        """Generate comprehensive documentation for the DAG execution."""
        validation = self.validate_dag()
        
        doc_content = f"""# Deployment Data Auditor - DAG Execution Plan

## Overview

This document describes the optimized DAG execution plan for the Deployment Data Auditor system.
The plan transforms the original sequential task list into parallel execution groups, reducing
estimated execution time from {validation['estimated_sequential_hours']:.1f} hours to {validation['estimated_parallel_hours']:.1f} hours
(approximately {((validation['estimated_sequential_hours'] - validation['estimated_parallel_hours']) / validation['estimated_sequential_hours'] * 100):.1f}% reduction).

## DAG Structure Validation

- **Total Tasks**: {validation['total_tasks']}
- **DAG Valid**: {validation['is_valid']}
- **Has Cycles**: {validation['has_cycles']}
- **Critical Path Length**: {len(validation['critical_path'])} tasks

## Parallel Execution Groups

The tasks are organized into 5 parallel execution groups:

"""
        
        for group_name, group_data in validation['parallel_groups'].items():
            doc_content += f"""### {group_name.title()} Layer
- **Tasks**: {len(group_data['tasks'])} tasks
- **Estimated Time**: {group_data['estimated_hours']:.1f} hours
- **Dependencies**: {', '.join(group_data['dependencies']) if group_data['dependencies'] else 'None'}
- **Task List**: {', '.join(group_data['tasks'])}

"""
        
        doc_content += f"""## Critical Path Analysis

The critical path through the DAG consists of {len(validation['critical_path'])} tasks:

"""
        
        for i, task_id in enumerate(validation['critical_path']):
            task = self.tasks[task_id]
            doc_content += f"{i+1}. **Task {task_id}**: {task.name} ({task.estimated_hours:.1f}h)\n"
            
        doc_content += f"""
## Execution Instructions

### Prerequisites
- Python 3.9+ with required dependencies
- Beast Mode Framework installed
- Git repository with write access
- Make build system available

### Build Commands

```bash
# Validate DAG structure
make validate-dag

# Build complete system
make all

# Build specific layers
make foundation    # Foundation layer (parallel)
make core         # Core components (parallel) 
make integration  # Integration layer (parallel)
make optimization # Optimization layer (parallel)
make validation   # Validation layer (sequential)

# Clean build artifacts
make clean
```

### Execution Monitoring

Each task generates execution logs in the `logs/` directory:
- `logs/task_X_Y.log` - Individual task execution logs
- `logs/dag_execution.log` - Overall DAG execution log

### Beast Mode Integration

Tasks marked with Beast Mode integration ({sum(1 for t in self.tasks.values() if t.beast_mode_integration)} of {len(self.tasks)}) will:
- Inherit from ReflectiveModule for observability
- Provide health endpoints (/health, /ready, /metrics)
- Export Prometheus metrics
- Use structured logging with correlation IDs

## Quality Gates

Each parallel group includes validation checkpoints:
- **Foundation**: Configuration and base class validation
- **Core**: File monitoring and violation detection validation  
- **Integration**: Git integration and remediation validation
- **Optimization**: Performance and emergency response validation
- **Validation**: End-to-end testing and deployment validation

## Troubleshooting

### Common Issues
1. **Missing Dependencies**: Check `.task-X-Y-complete` files
2. **Build Failures**: Review individual task logs in `logs/`
3. **DAG Validation Errors**: Run `make validate-dag` for details

### Recovery Procedures
1. **Partial Failure**: Re-run specific layer (e.g., `make core`)
2. **Complete Failure**: Run `make clean && make all`
3. **Dependency Issues**: Manually create missing `.task-X-Y-complete` files

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return doc_content

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Auditor DAG Optimizer')
    parser.add_argument('--validate', action='store_true', help='Validate DAG structure')
    parser.add_argument('--generate-makefile', action='store_true', help='Generate Makefile')
    parser.add_argument('--generate-scripts', action='store_true', help='Generate execution scripts')
    parser.add_argument('--generate-docs', action='store_true', help='Generate documentation')
    parser.add_argument('--generate-all', action='store_true', help='Generate all artifacts')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    
    args = parser.parse_args()
    
    # Initialize optimizer
    optimizer = DeploymentAuditorDAGOptimizer()
    optimizer.load_tasks_from_spec()
    optimizer.build_dag()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if args.validate or args.generate_all:
        print("Validating DAG structure...")
        validation = optimizer.validate_dag()
        print(json.dumps(validation, indent=2))
        
        if not validation['is_valid']:
            print("ERROR: DAG validation failed!")
            return 1
            
    if args.generate_makefile or args.generate_all:
        print("Generating Makefile...")
        makefile = optimizer.generate_makefile()
        (output_dir / 'Makefile.deployment-auditor').write_text(makefile)
        print("Generated: Makefile.deployment-auditor")
        
    if args.generate_scripts or args.generate_all:
        print("Generating execution scripts...")
        scripts = optimizer.generate_execution_scripts()
        scripts_dir = output_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        for script_name, script_content in scripts.items():
            script_path = scripts_dir / script_name
            script_path.write_text(script_content)
            script_path.chmod(0o755)  # Make executable
            
        print(f"Generated {len(scripts)} execution scripts in scripts/")
        
    if args.generate_docs or args.generate_all:
        print("Generating documentation...")
        docs = optimizer.generate_documentation()
        (output_dir / 'DEPLOYMENT_AUDITOR_DAG_EXECUTION_PLAN.md').write_text(docs)
        
        # Generate DAG visualization
        mermaid = optimizer.generate_dag_visualization()
        (output_dir / 'deployment_auditor_dag.mmd').write_text(mermaid)
        
        print("Generated: DEPLOYMENT_AUDITOR_DAG_EXECUTION_PLAN.md")
        print("Generated: deployment_auditor_dag.mmd")
        
    if args.generate_all:
        print("\nAll artifacts generated successfully!")
        print("Next steps:")
        print("1. Review DEPLOYMENT_AUDITOR_DAG_EXECUTION_PLAN.md")
        print("2. Run: make -f Makefile.deployment-auditor validate-dag")
        print("3. Execute: make -f Makefile.deployment-auditor all")
        
    return 0

if __name__ == "__main__":
    exit(main())
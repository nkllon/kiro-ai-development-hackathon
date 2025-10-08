#!/usr/bin/env python3
"""
Multi-Dimensional Vocabulary Projector DAG Task Definitions
===========================================================

Converts the task list into DAG-compatible task definitions for parallel execution.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

@dataclass
class DAGTask:
    """DAG-compatible task definition."""
    task_id: str
    name: str
    description: str
    dependencies: List[str]
    estimated_duration: float  # minutes
    requirements: List[str]
    script_path: Optional[str] = None
    validation_command: Optional[str] = None
    parallel_safe: bool = True

class VocabularyProjectorDAGTasks:
    """DAG task definitions for Multi-Dimensional Vocabulary Projector."""
    
    def __init__(self):
        self.tasks = self._define_tasks()
    
    def _define_tasks(self) -> List[DAGTask]:
        """Define all tasks with dependencies and metadata."""
        return [
            # Task 5: Vocabulary data conversion and validation
            DAGTask(
                task_id="5.1",
                name="Convert vocabulary markdown to JSON",
                description="Parse existing docs/ubiquitous_language_vocabulary.md and create structured JSON",
                dependencies=[],
                estimated_duration=15.0,
                requirements=["1.1", "1.2", "1.3"],
                script_path="scripts/tasks/vocabulary_converter.py",
                validation_command="python -c 'import json; json.load(open(\"docs/ubiquitous_language_vocabulary.json\"))'",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="5.2",
                name="Enhance vocabulary data completeness",
                description="Add missing examples, synonyms, antonyms and validate relationships",
                dependencies=["5.1"],
                estimated_duration=20.0,
                requirements=["1.2", "1.5"],
                script_path="scripts/tasks/vocabulary_enhancer.py",
                validation_command="python scripts/tasks/vocabulary_validator.py",
                parallel_safe=True
            ),
            
            # Task 6: CLI interface and automation (can start after 5.1)
            DAGTask(
                task_id="6.1",
                name="Implement CLI entry point and argument parsing",
                description="Create VocabularyProjectorCLI class with comprehensive argument parsing",
                dependencies=["5.1"],
                estimated_duration=25.0,
                requirements=["6.1", "6.3"],
                script_path="scripts/tasks/cli_implementation.py",
                validation_command="python src/multi_dimensional_vocabulary_projector.py --help",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="6.2",
                name="Add incremental generation and validation support",
                description="Implement change detection and selective regeneration",
                dependencies=["6.1", "5.2"],
                estimated_duration=20.0,
                requirements=["6.2", "6.5"],
                script_path="scripts/tasks/incremental_generation.py",
                validation_command="python src/multi_dimensional_vocabulary_projector.py --validate-only",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="6.3",
                name="Build batch processing and CI/CD integration",
                description="Add batch processing, watch mode, and integration documentation",
                dependencies=["6.2"],
                estimated_duration=15.0,
                requirements=["6.3", "6.4"],
                script_path="scripts/tasks/batch_processing.py",
                validation_command="python src/multi_dimensional_vocabulary_projector.py --batch docs/*.json",
                parallel_safe=True
            ),
            
            # Task 7: Error handling (can run in parallel with CLI development)
            DAGTask(
                task_id="7.1",
                name="Enhance error handling and diagnostics",
                description="Add comprehensive error logging and custom exception classes",
                dependencies=["5.1"],
                estimated_duration=18.0,
                requirements=["5.4"],
                script_path="scripts/tasks/error_handling.py",
                validation_command="python -c 'from src.multi_dimensional_vocabulary_projector import VocabularyProjectorError'",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="7.2",
                name="Add extensibility framework for custom projections",
                description="Create plugin architecture and template-based output support",
                dependencies=["7.1"],
                estimated_duration=30.0,
                requirements=["5.1", "5.2"],
                script_path="scripts/tasks/extensibility_framework.py",
                validation_command="python scripts/tasks/test_plugin_system.py",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="7.3",
                name="Implement backward compatibility and schema versioning",
                description="Add schema versioning and migration utilities",
                dependencies=["7.1"],
                estimated_duration=22.0,
                requirements=["5.3"],
                script_path="scripts/tasks/schema_versioning.py",
                validation_command="python scripts/tasks/test_schema_migration.py",
                parallel_safe=True
            ),
            
            # Task 8: Testing framework (depends on core functionality)
            DAGTask(
                task_id="8.1",
                name="Implement comprehensive unit testing",
                description="Create unit tests for all projection algorithms and core functionality",
                dependencies=["5.2", "6.1", "7.1"],
                estimated_duration=35.0,
                requirements=["5.4"],
                script_path="scripts/tasks/unit_testing.py",
                validation_command="python -m pytest tests/unit/ -v",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="8.2",
                name="Add integration testing and test data",
                description="Create end-to-end tests and performance benchmarks",
                dependencies=["8.1", "6.2"],
                estimated_duration=25.0,
                requirements=["5.4"],
                script_path="scripts/tasks/integration_testing.py",
                validation_command="python -m pytest tests/integration/ -v",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="8.3",
                name="Implement output validation and quality assurance",
                description="Add markdown validation and cross-reference checking",
                dependencies=["8.1"],
                estimated_duration=20.0,
                requirements=["6.5"],
                script_path="scripts/tasks/output_validation.py",
                validation_command="python scripts/tasks/validate_projections.py",
                parallel_safe=True
            ),
            
            # Task 9: Documentation (can run in parallel with testing)
            DAGTask(
                task_id="9.1",
                name="Create user documentation",
                description="Write comprehensive user guides and troubleshooting documentation",
                dependencies=["6.3", "7.2"],
                estimated_duration=30.0,
                requirements=["5.4"],
                script_path="scripts/tasks/user_documentation.py",
                validation_command="test -f docs/vocabulary_projector_user_guide.md",
                parallel_safe=True
            ),
            
            DAGTask(
                task_id="9.2",
                name="Create developer documentation",
                description="Write developer guides and API reference documentation",
                dependencies=["7.2", "8.1"],
                estimated_duration=25.0,
                requirements=["5.1", "5.2"],
                script_path="scripts/tasks/developer_documentation.py",
                validation_command="test -f docs/vocabulary_projector_developer_guide.md",
                parallel_safe=True
            )
        ]
    
    def get_task_by_id(self, task_id: str) -> Optional[DAGTask]:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_parallel_groups(self) -> List[List[str]]:
        """Get groups of tasks that can run in parallel."""
        return [
            # Group 1: Foundation tasks
            ["5.1"],
            
            # Group 2: Parallel development tracks
            ["5.2", "6.1", "7.1"],
            
            # Group 3: Advanced features
            ["6.2", "7.2", "7.3"],
            
            # Group 4: Integration and testing
            ["6.3", "8.1"],
            
            # Group 5: Final validation and documentation
            ["8.2", "8.3", "9.1"],
            
            # Group 6: Final documentation
            ["9.2"]
        ]
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary with timing estimates."""
        total_duration = sum(task.estimated_duration for task in self.tasks)
        parallel_groups = self.get_parallel_groups()
        
        # Calculate parallel execution time
        parallel_duration = 0.0
        for group in parallel_groups:
            group_max_duration = max(
                self.get_task_by_id(task_id).estimated_duration 
                for task_id in group
            )
            parallel_duration += group_max_duration
        
        return {
            "total_tasks": len(self.tasks),
            "sequential_duration_minutes": total_duration,
            "parallel_duration_minutes": parallel_duration,
            "efficiency_gain": f"{((total_duration - parallel_duration) / total_duration * 100):.1f}%",
            "parallel_groups": len(parallel_groups),
            "estimated_completion": f"{parallel_duration / 60:.1f} hours"
        }

def main():
    """Display DAG task information."""
    dag_tasks = VocabularyProjectorDAGTasks()
    
    print("🎯 Multi-Dimensional Vocabulary Projector DAG Tasks")
    print("=" * 60)
    
    # Show execution summary
    summary = dag_tasks.get_execution_summary()
    print(f"📊 Execution Summary:")
    print(f"   Total Tasks: {summary['total_tasks']}")
    print(f"   Sequential Time: {summary['sequential_duration_minutes']:.0f} minutes")
    print(f"   Parallel Time: {summary['parallel_duration_minutes']:.0f} minutes")
    print(f"   Efficiency Gain: {summary['efficiency_gain']}")
    print(f"   Estimated Completion: {summary['estimated_completion']}")
    print()
    
    # Show parallel groups
    print("🔄 Parallel Execution Groups:")
    for i, group in enumerate(dag_tasks.get_parallel_groups(), 1):
        print(f"   Group {i}: {', '.join(group)}")
    print()
    
    # Show all tasks
    print("📋 Task Details:")
    for task in dag_tasks.tasks:
        deps = ", ".join(task.dependencies) if task.dependencies else "None"
        print(f"   {task.task_id}: {task.name}")
        print(f"      Dependencies: {deps}")
        print(f"      Duration: {task.estimated_duration:.0f} min")
        print(f"      Requirements: {', '.join(task.requirements)}")
        print()

if __name__ == "__main__":
    main()
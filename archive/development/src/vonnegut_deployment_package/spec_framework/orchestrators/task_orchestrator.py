"""
Task Orchestrator - Generate systematic implementation task breakdowns from design.

Implements incremental task generation with dependency management based on RM-DDD patterns.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..core.base import ReflectiveModule
from ..core.models import Specification, Task, Design


logger = logging.getLogger(__name__)


class TaskOrchestrator(ReflectiveModule):
    """
    Generate systematic implementation task breakdowns from design.
    
    Creates incremental, testable tasks with proper dependency management
    based on RM-DDD proven patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the task orchestrator."""
        super().__init__()
        self._config = config or {}
        self._task_templates = self._initialize_task_templates()
        
        logger.info("TaskOrchestrator initialized with systematic task generation")
    
    def _initialize_task_templates(self) -> Dict[str, Any]:
        """Initialize task templates based on RM-DDD patterns."""
        return {
            'foundation_tasks': [
                'Set up project structure',
                'Create core data models',
                'Implement validation framework',
                'Set up testing infrastructure'
            ],
            'implementation_tasks': [
                'Implement entity classes',
                'Create repository interfaces',
                'Implement service layer',
                'Create API endpoints'
            ],
            'integration_tasks': [
                'Integrate with external services',
                'Implement security measures',
                'Add monitoring and logging',
                'Create deployment configuration'
            ],
            'validation_tasks': [
                'Write unit tests',
                'Create integration tests',
                'Implement acceptance tests',
                'Validate against requirements'
            ]
        }
    
    def generate_tasks_from_design(
        self,
        specification: Specification
    ) -> List[Task]:
        """
        Generate systematic task breakdown from design.
        
        Args:
            specification: Specification with design
            
        Returns:
            List of generated tasks
        """
        if not specification.design:
            logger.error("Cannot generate tasks - specification has no design")
            return []
        
        tasks = []
        
        # Generate foundation tasks
        foundation_tasks = self._generate_foundation_tasks(specification)
        tasks.extend(foundation_tasks)
        
        # Generate implementation tasks
        implementation_tasks = self._generate_implementation_tasks(specification)
        tasks.extend(implementation_tasks)
        
        # Generate integration tasks
        integration_tasks = self._generate_integration_tasks(specification)
        tasks.extend(integration_tasks)
        
        # Generate validation tasks
        validation_tasks = self._generate_validation_tasks(specification)
        tasks.extend(validation_tasks)
        
        # Set up task dependencies
        self._setup_task_dependencies(tasks)
        
        logger.info(f"Generated {len(tasks)} tasks for specification {specification.name}")
        return tasks
    
    def _generate_foundation_tasks(self, specification: Specification) -> List[Task]:
        """Generate foundation tasks for the project."""
        tasks = []
        
        # Project structure task
        task = Task(
            title="Set up project structure and core interfaces",
            description="Create directory structure for models, services, repositories, and API components",
            requirements_references=[req.id for req in specification.requirements[:2]],  # Reference first 2 requirements
            estimated_effort=4
        )
        tasks.append(task)
        
        # Data models task
        task = Task(
            title="Implement core data models and validation",
            description="Create data model interfaces and types with validation functions",
            requirements_references=[req.id for req in specification.requirements],
            estimated_effort=8
        )
        tasks.append(task)
        
        return tasks
    
    def _generate_implementation_tasks(self, specification: Specification) -> List[Task]:
        """Generate implementation tasks based on design components."""
        tasks = []
        
        if not specification.design or not specification.design.components:
            return tasks
        
        # Generate tasks for each component
        for component_name, component_info in specification.design.components.items():
            task = Task(
                title=f"Implement {component_name} component",
                description=f"Create {component_name} with {component_info.get('description', 'business logic')}",
                requirements_references=component_info.get('requirements', []),
                estimated_effort=6
            )
            tasks.append(task)
        
        return tasks
    
    def _generate_integration_tasks(self, specification: Specification) -> List[Task]:
        """Generate integration and infrastructure tasks."""
        tasks = []
        
        # Security integration
        if specification.security_requirements:
            task = Task(
                title="Implement security integration",
                description="Add security measures and compliance validation",
                requirements_references=[req.id for req in specification.requirements if req.security_implications],
                estimated_effort=8
            )
            tasks.append(task)
        
        # Performance integration
        if specification.performance_requirements:
            task = Task(
                title="Implement performance monitoring",
                description="Add performance monitoring and optimization",
                requirements_references=[req.id for req in specification.requirements if req.performance_implications],
                estimated_effort=6
            )
            tasks.append(task)
        
        return tasks
    
    def _generate_validation_tasks(self, specification: Specification) -> List[Task]:
        """Generate validation and testing tasks."""
        tasks = []
        
        # Unit testing task
        task = Task(
            title="Create comprehensive unit tests",
            description="Implement unit tests for all components with >90% coverage",
            requirements_references=[req.id for req in specification.requirements],
            estimated_effort=12
        )
        tasks.append(task)
        
        # Integration testing task
        task = Task(
            title="Implement integration tests",
            description="Create integration tests for complete workflows",
            requirements_references=[req.id for req in specification.requirements],
            estimated_effort=8
        )
        tasks.append(task)
        
        return tasks
    
    def _setup_task_dependencies(self, tasks: List[Task]) -> None:
        """Set up dependencies between tasks."""
        if len(tasks) < 2:
            return
        
        # Simple dependency setup - foundation tasks first
        for i in range(1, len(tasks)):
            if i < 2:  # First two tasks depend on each other
                tasks[i].dependencies = [tasks[0].id]
            else:  # Later tasks depend on foundation tasks
                tasks[i].dependencies = [tasks[0].id, tasks[1].id]
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the task orchestrator."""
        return {
            "status": "healthy",
            "task_templates_loaded": len(self._task_templates),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if task orchestrator is ready for operation."""
        return len(self._task_templates) > 0
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "task_templates_count": float(len(self._task_templates))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        else:
            return "ready"
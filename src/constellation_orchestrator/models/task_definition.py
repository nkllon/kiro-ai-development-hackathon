"""Task definition models for Constellation Orchestrator."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskDefinition(BaseModel):
    """Comprehensive task definition with validation."""
    
    task_id: str = Field(..., description="Unique task identifier", min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, description="AI prompt to execute")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs this task depends on")
    
    # Execution parameters
    estimated_duration: Optional[int] = Field(None, ge=1, description="Estimated execution time in seconds")
    timeout: Optional[int] = Field(300, ge=1, le=3600, description="Maximum execution time in seconds")
    retry_count: int = Field(3, ge=0, le=10, description="Number of retry attempts on failure")
    
    # Metadata
    category: Optional[str] = Field(None, description="Task category for organization")
    priority: int = Field(1, ge=1, le=10, description="Task priority (1=highest, 10=lowest)")
    tags: List[str] = Field(default_factory=list, description="Task tags for filtering")
    
    # Output configuration
    output_format: str = Field("text", description="Expected output format")
    capture_logs: bool = Field(True, description="Whether to capture detailed execution logs")
    
    # Advanced configuration
    agent_requirements: Dict[str, Any] = Field(default_factory=dict, description="Specific agent requirements")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables for execution")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """Validate task ID format."""
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('task_id must contain only alphanumeric characters, underscores, hyphens, and dots')
        return v
    
    @validator('dependencies')
    def validate_dependencies(cls, v, values):
        """Validate dependencies don't include self-reference."""
        if 'task_id' in values and values['task_id'] in v:
            raise ValueError('Task cannot depend on itself')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        for tag in v:
            if not isinstance(tag, str) or len(tag.strip()) == 0:
                raise ValueError('All tags must be non-empty strings')
        return [tag.strip().lower() for tag in v]
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate output format."""
        allowed_formats = ['text', 'json', 'markdown', 'yaml', 'xml']
        if v.lower() not in allowed_formats:
            raise ValueError(f'output_format must be one of: {", ".join(allowed_formats)}')
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        schema_extra = {
            "example": {
                "task_id": "constellation_1_1",
                "prompt": "Analyze the system architecture and identify key components",
                "dependencies": [],
                "estimated_duration": 60,
                "timeout": 300,
                "retry_count": 3,
                "category": "analysis",
                "priority": 1,
                "tags": ["architecture", "analysis"],
                "output_format": "markdown",
                "capture_logs": True,
                "agent_requirements": {
                    "min_memory_mb": 512,
                    "preferred_model": "claude-3"
                },
                "environment_variables": {
                    "ANALYSIS_MODE": "detailed"
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.dict()
    
    def get_execution_key(self) -> str:
        """Get unique execution key for this task."""
        return f"task:{self.task_id}"
    
    def is_ready_to_execute(self, completed_tasks: set) -> bool:
        """Check if task is ready to execute based on dependencies."""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def get_dependency_count(self) -> int:
        """Get number of dependencies."""
        return len(self.dependencies)
    
    def has_dependencies(self) -> bool:
        """Check if task has any dependencies."""
        return len(self.dependencies) > 0
    
    def matches_filter(self, category: Optional[str] = None, tags: Optional[List[str]] = None, 
                      priority_range: Optional[tuple] = None) -> bool:
        """Check if task matches given filters."""
        # Category filter
        if category and self.category != category:
            return False
        
        # Tags filter (task must have at least one matching tag)
        if tags:
            if not any(tag.lower() in self.tags for tag in tags):
                return False
        
        # Priority range filter
        if priority_range:
            min_priority, max_priority = priority_range
            if not (min_priority <= self.priority <= max_priority):
                return False
        
        return True


class TaskBatch(BaseModel):
    """Collection of tasks for batch operations."""
    
    batch_id: str = Field(..., description="Unique batch identifier")
    tasks: List[TaskDefinition] = Field(..., description="Tasks in this batch")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Batch creation time")
    
    # Batch metadata
    description: Optional[str] = Field(None, description="Batch description")
    total_estimated_duration: Optional[int] = Field(None, description="Total estimated duration in seconds")
    
    @validator('tasks')
    def validate_unique_task_ids(cls, v):
        """Validate that all task IDs in batch are unique."""
        task_ids = [task.task_id for task in v]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError('All task IDs in batch must be unique')
        return v
    
    def get_task_by_id(self, task_id: str) -> Optional[TaskDefinition]:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_tasks_by_category(self, category: str) -> List[TaskDefinition]:
        """Get all tasks in a specific category."""
        return [task for task in self.tasks if task.category == category]
    
    def get_tasks_by_priority(self, priority: int) -> List[TaskDefinition]:
        """Get all tasks with specific priority."""
        return [task for task in self.tasks if task.priority == priority]
    
    def get_root_tasks(self) -> List[TaskDefinition]:
        """Get tasks with no dependencies (root tasks)."""
        return [task for task in self.tasks if not task.has_dependencies()]
    
    def calculate_total_estimated_duration(self) -> int:
        """Calculate total estimated duration for all tasks."""
        total = 0
        for task in self.tasks:
            if task.estimated_duration:
                total += task.estimated_duration
        return total
    
    def validate_dependencies(self) -> List[str]:
        """Validate all task dependencies exist within the batch."""
        errors = []
        task_ids = {task.task_id for task in self.tasks}
        
        for task in self.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    errors.append(f"Task '{task.task_id}' depends on '{dep}' which is not in the batch")
        
        return errors
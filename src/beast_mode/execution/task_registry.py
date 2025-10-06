"""
Task Registry for Beast Mode Framework
Manages task definitions and execution metadata
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, GracefulDegradationResult


@dataclass
class TaskMetadata:
    """Metadata for a registered task"""
    task_id: str
    name: str
    description: str
    dependencies: List[str]
    estimated_duration_minutes: float
    category: str = "general"
    priority: int = 0
    tags: List[str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


class TaskRegistry(ReflectiveModule):
    """
    Registry for managing task definitions and execution history
    
    Features:
    - Task metadata management
    - Dependency tracking
    - Execution history
    - Performance analytics
    """
    
    def __init__(self, registry_file: str = ".kiro/task-registry.json"):
        super().__init__()
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[str, TaskMetadata] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        self.logger = logging.getLogger("TaskRegistry")
        
        # Load existing registry
        self._load_registry()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "task_registry",
            "name": "Task Registry",
            "version": "1.0.0",
            "description": "Registry for managing task definitions and execution history",
            "total_tasks": len(self.tasks),
            "execution_history_count": len(self.execution_history)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        issues = []
        
        # Check registry file accessibility
        if not self.registry_file.parent.exists():
            issues.append("Registry directory does not exist")
        
        # Check for recent execution failures
        recent_failures = 0
        for execution in self.execution_history[-10:]:  # Last 10 executions
            summary = execution.get("summary", {})
            if summary.get("failed_tasks", 0) > 0:
                recent_failures += 1
        
        if recent_failures > 5:
            issues.append(f"High failure rate: {recent_failures}/10 recent executions had failures")
        
        # Determine status
        if not issues:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif len(issues) == 1 and "failure rate" not in issues[0]:
            status = ModuleStatus.WARNING
            health_score = 0.7
        else:
            status = ModuleStatus.ERROR
            health_score = 0.3
        
        return ModuleHealth(
            module_id="task_registry",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation"""
        try:
            # Try to save current state
            self._save_registry()
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=self.get_capabilities()
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
                remaining_capabilities=[
                    ModuleCapability.CORE_FUNCTIONALITY,
                    ModuleCapability.VALIDATION,
                    ModuleCapability.MONITORING
                ],
                error_message=str(e)
            )
        
        # Load existing registry
        self._load_registry()
    
    def _load_registry(self):
        """Load task registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                
                # Load tasks
                for task_data in data.get("tasks", []):
                    task = TaskMetadata(**task_data)
                    self.tasks[task.task_id] = task
                
                # Load execution history
                self.execution_history = data.get("execution_history", [])
                
                self.logger.info(f"Loaded {len(self.tasks)} tasks from registry")
                
            except Exception as e:
                self.logger.error(f"Failed to load task registry: {e}")
    
    def _save_registry(self):
        """Save task registry to file"""
        try:
            data = {
                "tasks": [asdict(task) for task in self.tasks.values()],
                "execution_history": self.execution_history,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save task registry: {e}")
    
    def register_task(self, task_id: str, name: str, description: str,
                     dependencies: List[str] = None, 
                     estimated_duration_minutes: float = 60,
                     category: str = "general",
                     priority: int = 0,
                     tags: List[str] = None) -> TaskMetadata:
        """Register a new task"""
        if dependencies is None:
            dependencies = []
        if tags is None:
            tags = []
        
        # Update existing task or create new one
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.name = name
            task.description = description
            task.dependencies = dependencies
            task.estimated_duration_minutes = estimated_duration_minutes
            task.category = category
            task.priority = priority
            task.tags = tags
            task.updated_at = datetime.now(timezone.utc).isoformat()
        else:
            task = TaskMetadata(
                task_id=task_id,
                name=name,
                description=description,
                dependencies=dependencies,
                estimated_duration_minutes=estimated_duration_minutes,
                category=category,
                priority=priority,
                tags=tags
            )
            self.tasks[task_id] = task
        
        self._save_registry()
        self.logger.info(f"Registered task: {task_id}")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskMetadata]:
        """Get task metadata by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, category: str = None, tags: List[str] = None) -> List[TaskMetadata]:
        """List tasks with optional filtering"""
        tasks = list(self.tasks.values())
        
        if category:
            tasks = [task for task in tasks if task.category == category]
        
        if tags:
            tasks = [task for task in tasks if any(tag in task.tags for tag in tags)]
        
        return sorted(tasks, key=lambda t: (t.priority, t.task_id), reverse=True)
    
    def get_dependencies(self, task_id: str, recursive: bool = False) -> List[str]:
        """Get task dependencies, optionally recursive"""
        if task_id not in self.tasks:
            return []
        
        dependencies = self.tasks[task_id].dependencies.copy()
        
        if recursive:
            all_deps = set(dependencies)
            to_process = dependencies.copy()
            
            while to_process:
                current = to_process.pop(0)
                if current in self.tasks:
                    for dep in self.tasks[current].dependencies:
                        if dep not in all_deps:
                            all_deps.add(dep)
                            to_process.append(dep)
            
            dependencies = list(all_deps)
        
        return dependencies
    
    def get_dependents(self, task_id: str, recursive: bool = False) -> List[str]:
        """Get tasks that depend on this task"""
        dependents = []
        
        for other_task_id, task in self.tasks.items():
            if task_id in task.dependencies:
                dependents.append(other_task_id)
        
        if recursive:
            all_dependents = set(dependents)
            to_process = dependents.copy()
            
            while to_process:
                current = to_process.pop(0)
                for other_task_id, task in self.tasks.items():
                    if current in task.dependencies and other_task_id not in all_dependents:
                        all_dependents.add(other_task_id)
                        to_process.append(other_task_id)
            
            dependents = list(all_dependents)
        
        return dependents
    
    def record_execution(self, execution_id: str, task_results: Dict[str, Any]):
        """Record execution results"""
        execution_record = {
            "execution_id": execution_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_results": task_results,
            "summary": {
                "total_tasks": len(task_results),
                "successful_tasks": sum(1 for r in task_results.values() if r.get("success", False)),
                "failed_tasks": sum(1 for r in task_results.values() if not r.get("success", True)),
                "total_duration_seconds": sum(
                    r.get("duration_seconds", 0) for r in task_results.values()
                )
            }
        }
        
        self.execution_history.append(execution_record)
        
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        
        self._save_registry()
        self.logger.info(f"Recorded execution: {execution_id}")
    
    def get_task_performance(self, task_id: str) -> Dict[str, Any]:
        """Get performance statistics for a task"""
        executions = []
        
        for execution in self.execution_history:
            task_results = execution.get("task_results", {})
            if task_id in task_results:
                result = task_results[task_id]
                if result.get("duration_seconds"):
                    executions.append({
                        "timestamp": execution["timestamp"],
                        "duration_seconds": result["duration_seconds"],
                        "success": result.get("success", False)
                    })
        
        if not executions:
            return {"executions": 0}
        
        durations = [e["duration_seconds"] for e in executions]
        successes = [e for e in executions if e["success"]]
        
        return {
            "executions": len(executions),
            "success_rate": len(successes) / len(executions),
            "avg_duration_seconds": sum(durations) / len(durations),
            "min_duration_seconds": min(durations),
            "max_duration_seconds": max(durations),
            "last_execution": executions[-1]["timestamp"],
            "recent_executions": executions[-10:]  # Last 10 executions
        }
    
    def analyze_critical_path(self) -> List[str]:
        """Analyze critical path through all registered tasks"""
        # Simple critical path calculation based on estimated durations
        # In a real implementation, you'd use more sophisticated algorithms
        
        # Build dependency graph
        graph = {}
        for task_id, task in self.tasks.items():
            graph[task_id] = {
                "dependencies": task.dependencies,
                "duration": task.estimated_duration_minutes
            }
        
        # Calculate longest path (critical path)
        def calculate_longest_path(task_id: str, memo: Dict[str, float] = None) -> float:
            if memo is None:
                memo = {}
            
            if task_id in memo:
                return memo[task_id]
            
            if task_id not in graph:
                memo[task_id] = 0
                return 0
            
            task_info = graph[task_id]
            max_dep_path = 0
            
            for dep in task_info["dependencies"]:
                dep_path = calculate_longest_path(dep, memo)
                max_dep_path = max(max_dep_path, dep_path)
            
            longest_path = max_dep_path + task_info["duration"]
            memo[task_id] = longest_path
            return longest_path
        
        # Find the task with the longest path
        longest_paths = {}
        for task_id in self.tasks:
            longest_paths[task_id] = calculate_longest_path(task_id)
        
        # Trace back the critical path
        critical_task = max(longest_paths.items(), key=lambda x: x[1])[0]
        critical_path = []
        
        current = critical_task
        while current and current in graph:
            critical_path.append(current)
            
            # Find the dependency that contributes to the longest path
            task_info = graph[current]
            next_task = None
            max_path = 0
            
            for dep in task_info["dependencies"]:
                if dep in longest_paths and longest_paths[dep] > max_path:
                    max_path = longest_paths[dep]
                    next_task = dep
            
            current = next_task
        
        critical_path.reverse()
        return critical_path
    
    def export_summary(self) -> Dict[str, Any]:
        """Export registry summary"""
        categories = {}
        for task in self.tasks.values():
            if task.category not in categories:
                categories[task.category] = 0
            categories[task.category] += 1
        
        total_estimated_duration = sum(
            task.estimated_duration_minutes for task in self.tasks.values()
        )
        
        return {
            "total_tasks": len(self.tasks),
            "categories": categories,
            "total_estimated_duration_minutes": total_estimated_duration,
            "total_executions": len(self.execution_history),
            "critical_path": self.analyze_critical_path(),
            "registry_file": str(self.registry_file),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
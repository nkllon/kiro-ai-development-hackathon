#!/usr/bin/env python3
"""
🚨 DAG REGISTRY - CIRCULAR DEPENDENCY PREVENTION
==============================================
Registry that enforces DAG structure and prevents circular dependencies.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Fix broken registry that allows circular dependencies
"""

from typing import Dict, Set, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class ModuleDependency:
    """Module dependency tracking."""
    module_id: str
    dependencies: Set[str]  # What this module depends on
    dependents: Set[str]    # What depends on this module
    registered_at: datetime
    version: str = "1.0.0"


class DAGRegistry:
    """
    Registry that enforces DAG structure and prevents circular dependencies.
    
    Features:
    - Tracks dependencies AND dependents (bidirectional)
    - Detects circular dependencies before registration
    - Enforces DAG structure (no cycles allowed)
    - Prevents registration if it would create a cycle
    """
    
    def __init__(self):
        self.modules: Dict[str, ModuleDependency] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}  # module_id -> dependencies
        self.dependent_graph: Dict[str, Set[str]] = {}   # module_id -> dependents
        self.registry_id = f"dag_registry_{uuid.uuid4().hex[:8]}"
        self.created_at = datetime.now()
    
    def register_module(self, module_id: str, dependencies: Set[str] = None) -> bool:
        """
        Register a module with DAG validation.
        
        Returns:
            bool: True if registration successful, False if would create cycle
        """
        dependencies = dependencies or set()
        
        # Check if registration would create a circular dependency
        if self._would_create_cycle(module_id, dependencies):
            print(f"❌ REGISTRATION REJECTED: {module_id} would create circular dependency")
            return False
        
        # Register the module
        self.modules[module_id] = ModuleDependency(
            module_id=module_id,
            dependencies=dependencies,
            dependents=set(),
            registered_at=datetime.now()
        )
        
        # Update dependency graphs
        self.dependency_graph[module_id] = dependencies.copy()
        self.dependent_graph[module_id] = set()
        
        # Update dependents for each dependency
        for dep in dependencies:
            if dep in self.dependent_graph:
                self.dependent_graph[dep].add(module_id)
            else:
                self.dependent_graph[dep] = {module_id}
        
        print(f"✅ MODULE REGISTERED: {module_id} with dependencies {dependencies}")
        return True
    
    def _would_create_cycle(self, module_id: str, dependencies: Set[str]) -> bool:
        """
        Check if adding this module would create a circular dependency.
        
        Uses DFS to detect cycles in the dependency graph.
        """
        # Create temporary graph with new module
        temp_graph = self.dependency_graph.copy()
        temp_graph[module_id] = dependencies
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in temp_graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes for cycles
        for node in temp_graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def get_dependencies(self, module_id: str) -> Set[str]:
        """Get dependencies for a module."""
        return self.modules.get(module_id, ModuleDependency("", set(), set(), datetime.now())).dependencies
    
    def get_dependents(self, module_id: str) -> Set[str]:
        """Get dependents for a module."""
        return self.dependent_graph.get(module_id, set())
    
    def get_dependency_chain(self, module_id: str) -> List[str]:
        """Get the full dependency chain for a module (topological sort)."""
        visited = set()
        result = []
        
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            
            # Visit dependencies first
            for dep in self.dependency_graph.get(node, set()):
                dfs(dep)
            
            result.append(node)
        
        dfs(module_id)
        return result
    
    def validate_dag(self) -> bool:
        """Validate that the entire registry is a DAG (no cycles)."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.dependency_graph:
            if node not in visited:
                if has_cycle(node):
                    return False
        
        return True
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "registry_id": self.registry_id,
            "total_modules": len(self.modules),
            "is_dag": self.validate_dag(),
            "created_at": self.created_at.isoformat(),
            "modules": list(self.modules.keys())
        }
    
    def remove_module(self, module_id: str) -> bool:
        """Remove a module and update dependent relationships."""
        if module_id not in self.modules:
            return False
        
        # Remove from dependents of dependencies
        for dep in self.modules[module_id].dependencies:
            if dep in self.dependent_graph:
                self.dependent_graph[dep].discard(module_id)
        
        # Remove from dependent relationships
        for dependent in self.modules[module_id].dependents:
            if dependent in self.dependency_graph:
                self.dependency_graph[dependent].discard(module_id)
        
        # Remove from registry
        del self.modules[module_id]
        del self.dependency_graph[module_id]
        del self.dependent_graph[module_id]
        
        print(f"✅ MODULE REMOVED: {module_id}")
        return True
    
    def __str__(self) -> str:
        return f"DAGRegistry(modules={len(self.modules)}, is_dag={self.validate_dag()})"
    
    def __repr__(self) -> str:
        return f"DAGRegistry(registry_id='{self.registry_id}', modules={list(self.modules.keys())})"


# Global DAG registry instance
dag_registry = DAGRegistry()


def register_module_safely(module_id: str, dependencies: Set[str] = None) -> bool:
    """Safely register a module with DAG validation."""
    return dag_registry.register_module(module_id, dependencies)


def get_dag_validation() -> bool:
    """Check if the registry is a valid DAG."""
    return dag_registry.validate_dag()


def get_registry_stats() -> Dict[str, Any]:
    """Get DAG registry statistics."""
    return dag_registry.get_registry_stats()

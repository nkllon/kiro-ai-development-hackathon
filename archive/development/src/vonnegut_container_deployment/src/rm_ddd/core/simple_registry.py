#!/usr/bin/env python3
"""
Simple Registry - No Database Nightmare
=====================================
Just a simple, working registry without over-engineering.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Keep it simple, stupid
"""

from typing import Dict, Set, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SimpleModule:
    """Simple module - no database complexity."""
    module_id: str
    dependencies: Set[str]
    dependents: Set[str]
    registered_at: datetime


class SimpleRegistry:
    """
    Simple registry - just works.
    
    No database, no complex relationships, no over-engineering.
    Just track what depends on what.
    """
    
    def __init__(self):
        self.modules: Dict[str, SimpleModule] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.dependent_graph: Dict[str, Set[str]] = {}
    
    def register(self, module_id: str, dependencies: Set[str] = None) -> bool:
        """Register a module - simple and clean."""
        dependencies = dependencies or set()
        
        # Check for circular dependencies
        if self._would_create_cycle(module_id, dependencies):
            return False
        
        # Register the module
        self.modules[module_id] = SimpleModule(
            module_id=module_id,
            dependencies=dependencies,
            dependents=set(),
            registered_at=datetime.now()
        )
        
        # Update graphs
        self.dependency_graph[module_id] = dependencies.copy()
        self.dependent_graph[module_id] = set()
        
        # Update dependents
        for dep in dependencies:
            if dep in self.dependent_graph:
                self.dependent_graph[dep].add(module_id)
            else:
                self.dependent_graph[dep] = {module_id}
        
        return True
    
    def _would_create_cycle(self, module_id: str, dependencies: Set[str]) -> bool:
        """Simple cycle detection."""
        temp_graph = self.dependency_graph.copy()
        temp_graph[module_id] = dependencies
        
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in temp_graph.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        return any(has_cycle(node) for node in temp_graph if node not in visited)
    
    def get_dependencies(self, module_id: str) -> Set[str]:
        """Get what this module depends on."""
        return self.dependency_graph.get(module_id, set())
    
    def get_dependents(self, module_id: str) -> Set[str]:
        """Get what depends on this module."""
        return self.dependent_graph.get(module_id, set())
    
    def is_dag(self) -> bool:
        """Check if registry is a valid DAG."""
        return not self._would_create_cycle("", set())
    
    def get_stats(self) -> Dict[str, any]:
        """Get simple stats."""
        return {
            "total_modules": len(self.modules),
            "is_dag": self.is_dag(),
            "modules": list(self.modules.keys())
        }


# Global simple registry
simple_registry = SimpleRegistry()


def register_module(module_id: str, dependencies: Set[str] = None) -> bool:
    """Register a module with the simple registry."""
    return simple_registry.register(module_id, dependencies)


def get_module_dependencies(module_id: str) -> Set[str]:
    """Get module dependencies."""
    return simple_registry.get_dependencies(module_id)


def get_module_dependents(module_id: str) -> Set[str]:
    """Get module dependents."""
    return simple_registry.get_dependents(module_id)


def is_registry_dag() -> bool:
    """Check if registry is a valid DAG."""
    return simple_registry.is_dag()


def get_registry_stats() -> Dict[str, any]:
    """Get registry statistics."""
    return simple_registry.get_stats()



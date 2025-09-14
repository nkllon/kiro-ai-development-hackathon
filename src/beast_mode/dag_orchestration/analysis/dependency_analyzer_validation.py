"""
Dependency Analyzer Validation

This module was extracted from dependency_analyzer.py
as part of RM-DDD compliance refactoring.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from ..models.dag_models import EcosystemDAG, SpecificationNode, TaskNode, CriticalPath
from .spec_parser import SpecParser, ParsedSpec
from .task_detector import TaskDetector, TaskDetectionResult
from .dependency_mapper import DependencyMapper, ConstraintGraph
from .critical_path_analyzer import CriticalPathAnalyzer, CriticalPathAnalysis
from .layer_processor import LayerProcessor, LayerProcessingResult
from datetime import datetime
from ..models.dag_models import ParallelGroup
from src.rm_ddd.core.health import ModuleHealth


def validate_ecosystem_integrity(self, ecosystem_dag: EcosystemDAG) -> List[str]:
    """
        Validate ecosystem integrity and return issues.
        
        Args:
            ecosystem_dag: Ecosystem DAG to validate
            
        Returns:
            List[str]: List of validation issues
        """
    issues = []
    task_ids = {task.task_id for task in ecosystem_dag.tasks}
    for task in ecosystem_dag.tasks:
        for dep_id in task.dependencies:
            if dep_id not in task_ids:
                issues.append(f'Task {task.task_id} has invalid dependency: {dep_id}')
        for dep_id in task.dependents:
            if dep_id not in task_ids:
                issues.append(f'Task {task.task_id} has invalid dependent: {dep_id}')
    for critical_path in ecosystem_dag.critical_paths:
        if len(set(critical_path.task_sequence)) != len(critical_path.task_sequence):
            issues.append(f'Critical path {critical_path.path_id} contains duplicate tasks')
    if ecosystem_dag.completion_percentage < 0 or ecosystem_dag.completion_percentage > 100:
        issues.append(f'Invalid completion percentage: {ecosystem_dag.completion_percentage}')
    return issues

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }


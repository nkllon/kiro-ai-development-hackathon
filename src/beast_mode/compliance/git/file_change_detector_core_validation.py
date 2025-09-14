"""
File Change Detector Core Validation

This module was extracted from file_change_detector_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from pathlib import Path
from typing import List, Dict, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from ...core.reflective_module import ReflectiveModule
from ..models import CommitInfo, FileChangeAnalysis
from ...utils.path_normalizer import PathNormalizer, normalize_path, safe_relative_to
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
from src.rm_ddd.core.health import ModuleHealth


def _validate_claimed_vs_implemented(self, task_mappings: List[TaskMapping], claimed_tasks: List[str]) -> None:
    """
        Validate claimed tasks against implemented tasks.
        
        Args:
            task_mappings: List of task mappings with confidence scores
            claimed_tasks: List of claimed completed tasks
        """
    self.logger.debug('Validating claimed tasks against implementations')
    for mapping in task_mappings:
        if claimed_tasks and mapping.task_id in claimed_tasks:
            if mapping.confidence_score > 0.6:
                mapping.evidence.append('Task claimed and well-supported by evidence')
            elif mapping.confidence_score > 0.3:
                mapping.evidence.append('Task claimed with moderate evidence')
            else:
                mapping.evidence.append('Task claimed but evidence is weak')
        elif mapping.confidence_score > 0.6:
            mapping.evidence.append('Strong implementation evidence but task not claimed')

def _validate_task_completion_claims(self, task_mappings: List[TaskMapping], claimed_tasks: Optional[List[str]]) -> Dict[str, Any]:
    """
        Validate task completion claims against evidence.
        
        Args:
            task_mappings: List of task mappings with confidence scores
            claimed_tasks: Optional list of claimed completed tasks
            
        Returns:
            Dictionary with validation results
        """
    if not claimed_tasks:
        return {'validation_performed': False, 'message': 'No claimed tasks provided for validation'}
    validated_tasks = []
    questionable_tasks = []
    missing_evidence_tasks = []
    unclaimed_implementations = []
    mapping_dict = {mapping.task_id: mapping for mapping in task_mappings}
    for claimed_task in claimed_tasks:
        if claimed_task in mapping_dict:
            mapping = mapping_dict[claimed_task]
            if mapping.confidence_score > 0.6:
                validated_tasks.append(claimed_task)
            elif mapping.confidence_score > 0.3:
                questionable_tasks.append(claimed_task)
            else:
                missing_evidence_tasks.append(claimed_task)
        else:
            missing_evidence_tasks.append(claimed_task)
    for mapping in task_mappings:
        if mapping.confidence_score > 0.6 and mapping.task_id not in claimed_tasks:
            unclaimed_implementations.append(mapping.task_id)
    validated_details = [{'task_id': task, 'status': 'validated'} for task in validated_tasks]
    questionable_details = []
    missing_evidence_details = []
    for task in questionable_tasks:
        if task in mapping_dict:
            questionable_details.append({'task_id': task, 'confidence': mapping_dict[task].confidence_score, 'status': 'questionable'})
    for task in missing_evidence_tasks:
        if task in mapping_dict:
            missing_evidence_details.append({'task_id': task, 'confidence': mapping_dict[task].confidence_score, 'status': 'missing_evidence'})
        else:
            missing_evidence_details.append({'task_id': task, 'confidence': 0.0, 'status': 'no_evidence'})
    return {'validation_performed': True, 'total_claimed_tasks': len(claimed_tasks), 'validated_tasks': validated_details, 'questionable_tasks': questionable_details, 'missing_evidence_tasks': missing_evidence_details, 'unclaimed_implementations': unclaimed_implementations, 'validation_summary': {'validated_count': len(validated_tasks), 'questionable_count': len(questionable_tasks), 'missing_evidence_count': len(missing_evidence_tasks), 'unclaimed_count': len(unclaimed_implementations)}}

def _validate_claimed_vs_implemented(self, task_mappings: List[TaskMapping], claimed_tasks: List[str]) -> None:
    """Validate claimed task completions against implementation evidence."""
    self.logger.info('Validating claimed tasks against implementation evidence')
    implementation_evidence = {mapping.task_id: mapping.confidence_score for mapping in task_mappings}
    for claimed_task in claimed_tasks:
        confidence = implementation_evidence.get(claimed_task, 0.0)
        task_mapping = next((m for m in task_mappings if m.task_id == claimed_task), None)
        if task_mapping:
            if confidence < 0.3:
                task_mapping.evidence.append(f'WARNING: Task claimed complete but low implementation evidence (confidence: {confidence:.2f})')
            elif confidence > 0.7:
                task_mapping.evidence.append(f'VALIDATED: Task completion claim supported by strong evidence (confidence: {confidence:.2f})')
            else:
                task_mapping.evidence.append(f'PARTIAL: Task completion claim has moderate evidence (confidence: {confidence:.2f})')

def _is_test_file(self, file_path: str) -> bool:
    """Check if a file is a test file."""
    return self._categorize_file(file_path) == FileCategory.TEST_CODE

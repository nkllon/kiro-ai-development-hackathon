"""
Consolidation Processing

This module was extracted from consolidation.py
as part of RM-DDD compliance refactoring.
"""

import ast
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import hashlib
import re
from datetime import datetime
from src.beast_mode.core.reflective_module import ReflectiveModule
from .governance import GovernanceController
from .models import OverlapSeverity, OverlapReport
import time
import time

def _parse_spec_comprehensively(self, spec_name: str) -> Optional[Dict[str, Any]]:
    """Parse a single spec to extract all relevant information"""
    spec_dir = self.specs_directory / spec_name
    if not spec_dir.exists():
        self.logger.warning(f'Spec directory not found: {spec_name}')
        return None
    try:
        requirements_file = spec_dir / 'requirements.md'
        design_file = spec_dir / 'design.md'
        tasks_file = spec_dir / 'tasks.md'
        requirements_content = requirements_file.read_text() if requirements_file.exists() else ''
        design_content = design_file.read_text() if design_file.exists() else ''
        tasks_content = tasks_file.read_text() if tasks_file.exists() else ''
        requirements = self._extract_requirements(requirements_content)
        interfaces = self._extract_interfaces_detailed(design_content)
        terminology = self._extract_terminology_detailed(requirements_content + design_content)
        functionality_keywords = self._extract_functionality_keywords_enhanced(requirements_content + design_content + tasks_content)
        dependencies = self._extract_dependencies(design_content + tasks_content)
        return {'name': spec_name, 'requirements_content': requirements_content, 'design_content': design_content, 'tasks_content': tasks_content, 'requirements': requirements, 'interfaces': interfaces, 'terminology': terminology, 'functionality_keywords': functionality_keywords, 'dependencies': dependencies, 'complexity_score': self._calculate_complexity_score(requirements_content, design_content), 'quality_score': self._calculate_quality_score(requirements_content, design_content)}
    except Exception as e:
        self.logger.error(f'Error parsing spec {spec_name}: {e}')
        return None

def _convert_to_unified_requirement(self, requirement: RequirementAnalysis) -> 'UnifiedRequirement':
    """Convert a single requirement to unified format"""
    return UnifiedRequirement(unified_id=f'UR_{self._generate_requirement_id()}', original_requirements=[requirement.requirement_id], merged_content=requirement.content, functionality_keywords=requirement.functionality_keywords, acceptance_criteria=requirement.acceptance_criteria, stakeholder_personas=requirement.stakeholder_personas, quality_score=requirement.quality_score, complexity_score=requirement.complexity_score, conflicts_resolved=[], merge_strategy='no_merge_needed', validation_status='pending')

def _infer_transformation_type(self, original_req: RequirementAnalysis, unified_req: RequirementAnalysis, similarity: float) -> str:
    """Infer transformation type based on similarity and characteristics"""
    if similarity > 0.9:
        return 'unchanged'
    elif similarity > 0.7:
        return 'merged'
    elif similarity > 0.5:
        return 'split'
    else:
        return 'transformed'

def _determine_transformation_type(self, original_req_id: str, unified_req_id: str, consolidation_plan: ConsolidationPlan) -> str:
    """Determine transformation type based on consolidation plan"""
    if unified_req_id == 'DEPRECATED':
        return 'deprecated'
    elif original_req_id == unified_req_id:
        return 'unchanged'
    else:
        return 'merged'

def _generate_transformation_rationale(self, original_req_id: str, unified_req_id: str, transformation_type: str, consolidation_plan: ConsolidationPlan) -> str:
    """Generate rationale for requirement transformation"""
    rationale_map = {'merged': f'Requirement merged as part of {consolidation_plan.consolidation_strategy.value} strategy', 'split': f'Requirement split to improve clarity as part of {consolidation_plan.consolidation_strategy.value} strategy', 'unchanged': 'Requirement preserved without changes', 'deprecated': 'Requirement deprecated due to functional overlap or obsolescence'}
    return rationale_map.get(transformation_type, f'Requirement transformed using {consolidation_plan.consolidation_strategy.value} strategy')

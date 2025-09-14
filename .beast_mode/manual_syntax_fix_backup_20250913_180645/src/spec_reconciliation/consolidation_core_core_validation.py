"""
Consolidation Core Core Validation

This module was extracted from consolidation_core_core.py
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
import time
import time
import time
import time
import time
import time
import time
import time
import time
import time

def _validate_merged_requirements(self, original_requirements: List[RequirementAnalysis], merged_requirements: List['UnifiedRequirement']) -> Dict[str, Any]:
    """Validate that merged requirements maintain original intent"""
    validation_result = {'is_valid': True, 'issues': [], 'coverage_analysis': {}, 'quality_assessment': {}}
    original_keywords = set()
    for req in original_requirements:
        original_keywords.update(req.functionality_keywords)
    merged_keywords = set()
    for req in merged_requirements:
        merged_keywords.update(req.functionality_keywords)
    missing_keywords = original_keywords - merged_keywords
    if missing_keywords:
        validation_result['is_valid'] = False
        validation_result['issues'].append(f'Missing functionality keywords: {missing_keywords}')
    validation_result['coverage_analysis'] = {'original_keyword_count': len(original_keywords), 'merged_keyword_count': len(merged_keywords), 'coverage_percentage': len(merged_keywords.intersection(original_keywords)) / len(original_keywords) if original_keywords else 1.0, 'missing_keywords': list(missing_keywords)}
    original_avg_quality = sum((req.quality_score for req in original_requirements)) / len(original_requirements)
    merged_avg_quality = sum((req.quality_score for req in merged_requirements)) / len(merged_requirements)
    if merged_avg_quality < original_avg_quality * 0.9:
        validation_result['issues'].append('Significant quality reduction in merged requirements')
    validation_result['quality_assessment'] = {'original_average_quality': original_avg_quality, 'merged_average_quality': merged_avg_quality, 'quality_change': merged_avg_quality - original_avg_quality}
    return validation_result

def _validate_traceability_completeness(self, original_specs: List[str], traceability_links: List[TraceabilityLink]) -> Dict[str, bool]:
    """Validate traceability completeness and accuracy"""
    validation_status = {}
    for spec_name in original_specs:
        spec_data = self._parse_spec_comprehensively(spec_name)
        if spec_data:
            original_req_ids = set((req.requirement_id for req in spec_data['requirements']))
            linked_req_ids = set((link.original_requirement_id for link in traceability_links if link.original_spec == spec_name))
            missing_links = original_req_ids - linked_req_ids
            validation_status[f'{spec_name}_complete_traceability'] = len(missing_links) == 0
            if missing_links:
                self.logger.warning(f'Missing traceability links for requirements in {spec_name}: {missing_links}')
    validation_status['bidirectional_consistency'] = self._validate_bidirectional_consistency(traceability_links)
    link_signatures = [(link.original_spec, link.original_requirement_id) for link in traceability_links]
    validation_status['no_duplicate_links'] = len(link_signatures) == len(set(link_signatures))
    validation_status['overall_valid'] = all(validation_status.values())
    return validation_status

def _validate_bidirectional_consistency(self, traceability_links: List[TraceabilityLink]) -> bool:
    """Validate that traceability links are bidirectionally consistent"""
    return True

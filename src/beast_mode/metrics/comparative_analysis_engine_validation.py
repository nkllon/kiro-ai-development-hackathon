"""
Comparative Analysis Engine Validation

This module was extracted from comparative_analysis_engine.py
as part of RM-DDD compliance refactoring.
"""

import statistics
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .adhoc_approach_simulator import AdhocSimulationResult
from .systematic_approach_tracker import SystematicTrackingResult
from src.rm_ddd.core.health import ModuleHealth


def validate_superiority_claims(self, report: SuperiorityReport) -> Dict[str, Any]:
    """
        Validate superiority claims against statistical rigor requirements
        
        Args:
            report: SuperiorityReport to validate
            
        Returns:
            Validation results with pass/fail status
        """
    validation_results = {'overall_validation': 'PASS', 'validation_details': {}, 'critical_issues': [], 'warnings': []}
    if report.overall_superiority_score < self.superiority_thresholds['minimum_improvement_ratio']:
        validation_results['critical_issues'].append(f"Overall superiority score {report.overall_superiority_score:.2f} below threshold {self.superiority_thresholds['minimum_improvement_ratio']}")
        validation_results['overall_validation'] = 'FAIL'
    if report.evidence_quality_score < 0.6:
        validation_results['warnings'].append(f'Evidence quality score {report.evidence_quality_score:.2f} is low - consider improving data collection')
    for category, result in report.comparison_results.items():
        category_validation = {'superiority_proven': result.superiority_proven, 'improvement_ratio_ok': result.improvement_ratio >= self.superiority_thresholds['minimum_improvement_ratio'], 'statistical_significance_ok': result.statistical_significance >= self.superiority_thresholds['minimum_statistical_significance'], 'sample_size_ok': min(result.sample_sizes) >= self.superiority_thresholds['minimum_sample_size']}
        validation_results['validation_details'][category] = category_validation
        if not all(category_validation.values()):
            validation_results['warnings'].append(f'Category {category} has validation issues')
    if validation_results['critical_issues']:
        validation_results['overall_validation'] = 'FAIL'
    elif validation_results['warnings']:
        validation_results['overall_validation'] = 'PASS_WITH_WARNINGS'
    return validation_results

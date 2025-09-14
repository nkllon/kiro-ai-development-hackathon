"""
Governance Processing

This module was extracted from governance.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from .models import ReflectiveModule
from src.rm_ddd.core.health import ModuleHealth


def _create_default_improvement_processes(self) -> List[ContinuousImprovementProcess]:
    """Create default continuous improvement processes"""
    return [ContinuousImprovementProcess(process_id='governance_effectiveness_review', trigger_conditions=['Monthly governance audit completion', 'Significant governance violations detected', 'Stakeholder feedback received', 'System performance degradation'], analysis_procedures=['Review governance metrics and trends', 'Analyze violation patterns and root causes', 'Collect stakeholder feedback', 'Benchmark against industry standards', 'Identify improvement opportunities'], improvement_actions=['Update governance policies and procedures', 'Enhance training programs', 'Improve automation and tooling', 'Refine validation criteria', 'Optimize workflow processes'], success_metrics=['Reduced governance violations', 'Improved consistency scores', 'Higher stakeholder satisfaction', 'Increased process efficiency', 'Better training effectiveness'], review_cycle_months=3)]

def create_continuous_improvement_process(self) -> Dict[str, Any]:
    """
        Create continuous improvement process incorporating lessons learned and system evolution.
        
        Returns:
            Dictionary containing continuous improvement process implementation results
        """
    improvement_results = {'processes_created': [], 'feedback_mechanisms': [], 'metrics_frameworks': [], 'implementation_status': 'completed'}
    for process in self.improvement_processes:
        process_result = {'process_id': process.process_id, 'trigger_conditions': process.trigger_conditions, 'analysis_procedures': process.analysis_procedures, 'improvement_actions': process.improvement_actions, 'success_metrics': process.success_metrics, 'review_cycle_months': process.review_cycle_months}
        improvement_results['processes_created'].append(process_result)
        feedback = {'process_id': process.process_id, 'feedback_channels': ['surveys', 'interviews', 'metrics', 'observations'], 'collection_frequency': 'continuous', 'analysis_frequency': f'every_{process.review_cycle_months}_months', 'stakeholder_groups': ['governance_team', 'implementation_teams', 'business_stakeholders']}
        improvement_results['feedback_mechanisms'].append(feedback)
        metrics = {'process_id': process.process_id, 'success_metrics': process.success_metrics, 'measurement_frequency': 'monthly', 'reporting_frequency': f'every_{process.review_cycle_months}_months', 'baseline_establishment': 'required', 'target_setting': 'data_driven'}
        improvement_results['metrics_frameworks'].append(metrics)
    self.logger.info(f'Created {len(self.improvement_processes)} continuous improvement processes')
    return improvement_results

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


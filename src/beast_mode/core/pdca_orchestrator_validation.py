"""
Pdca Orchestrator Validation

This module was extracted from pdca_orchestrator.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from .reflective_module import ReflectiveModule, HealthStatus
from ..intelligence.registry_intelligence_engine import ProjectRegistryIntelligenceEngine, IntelligenceQuery
from ..tool_health.makefile_health_manager import MakefileHealthManager
from src.rm_ddd.core.health import ModuleHealth


def check_with_rca(self, implementation: DoResult) -> CheckResult:
    """
        Check phase: Validate against model + perform RCA on failures
        Implements R2.4: Validate against model requirements and perform RCA on any failures
        """
    validation_id = f"check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    success_criteria_met = {}
    for criterion in implementation.plan.task.success_criteria:
        success_criteria_met[criterion] = self._validate_success_criterion(criterion, implementation)
    constraint_compliance = implementation.constraints_satisfied.copy()
    systematic_approach_score = implementation.code_quality_metrics['systematic_approach_score'] * 0.4 + implementation.code_quality_metrics['constraint_compliance_rate'] * 0.3 + (1.0 if implementation.systematic_approach_maintained else 0.0) * 0.3
    quality_assessment = {'evidence_quality': len(implementation.implementation_evidence) / len(implementation.plan.implementation_steps), 'systematic_consistency': implementation.systematic_approach_maintained, 'constraint_adherence': all(constraint_compliance.values()), 'performance_efficiency': implementation.performance_metrics['steps_completed'] / implementation.performance_metrics['steps_total']}
    issues_identified = []
    rca_performed = False
    failed_steps = [e for e in implementation.implementation_evidence if e.get('failed', False)]
    if failed_steps:
        rca_performed = True
        for failed_step in failed_steps:
            issue = {'type': 'implementation_failure', 'step': failed_step['step_number'], 'description': failed_step['step_description'], 'error': failed_step.get('error', 'Unknown error'), 'rca_analysis': self._perform_rca_on_failure(failed_step)}
            issues_identified.append(issue)
    violated_constraints = [c for c, satisfied in constraint_compliance.items() if not satisfied]
    if violated_constraints:
        rca_performed = True
        for constraint in violated_constraints:
            issue = {'type': 'constraint_violation', 'constraint': constraint, 'rca_analysis': self._perform_rca_on_constraint_violation(constraint, implementation)}
            issues_identified.append(issue)
    validation_passed = all(success_criteria_met.values()) and all(constraint_compliance.values()) and (systematic_approach_score >= 0.8) and (len(issues_identified) == 0)
    check_result = CheckResult(validation_id=validation_id, do_result=implementation, success_criteria_met=success_criteria_met, constraint_compliance=constraint_compliance, systematic_approach_score=systematic_approach_score, quality_assessment=quality_assessment, rca_performed=rca_performed, issues_identified=issues_identified, validation_passed=validation_passed)
    self.logger.info(f'Validation completed: {validation_id} - Passed: {validation_passed}')
    return check_result

def _validate_constraint_satisfaction(self, constraint: str, evidence: List[Dict]) -> bool:
    """Validate that a constraint is satisfied based on implementation evidence"""
    if constraint == 'C-03':
        return not any((e.get('workaround_rejected', False) for e in evidence))
    elif constraint == 'C-05':
        avg_time = sum((e.get('execution_time_seconds', 0) for e in evidence)) / len(evidence)
        return avg_time < 0.5
    else:
        return True

def _validate_success_criterion(self, criterion: str, implementation: DoResult) -> bool:
    """Validate that a success criterion is met"""
    if 'systematic' in criterion.lower():
        return implementation.systematic_approach_maintained
    elif 'constraint' in criterion.lower():
        return all(implementation.constraints_satisfied.values())
    elif 'evidence' in criterion.lower():
        return len(implementation.implementation_evidence) > 0
    else:
        return True

def validate_self_consistency(self) -> Dict[str, Any]:
    """
        Validate that Beast Mode successfully uses its own systematic methodology
        Implements UC-25: Self-consistency validation
        """
    self.logger.info('Performing self-consistency validation...')
    self_task = DevelopmentTask(task_id='self_consistency_validation', task_name='beast_mode_self_application', task_description='Validate that Beast Mode applies systematic PDCA to its own operations', task_context={'target': 'beast_mode_framework', 'validation_type': 'self_consistency', 'systematic_approach_required': True}, requirements=['R2.1', 'R2.2', 'R2.3', 'R2.4', 'R2.5'], constraints=['C-03'], success_criteria=['Beast Mode uses its own PDCA methodology', 'Registry consultation performed for self-decisions', 'Systematic approach maintained throughout', 'Self-improvement evidence collected'])
    self_pdca_result = self.execute_real_task_cycle(self_task)
    self_consistency_analysis = {'self_pdca_executed': True, 'systematic_approach_used': self_pdca_result.do_result.systematic_approach_maintained if self_pdca_result.do_result else False, 'registry_consulted': self_pdca_result.plan_result.confidence_level > 0.5 if self_pdca_result.plan_result else False, 'constraints_satisfied': all(self_pdca_result.do_result.constraints_satisfied.values()) if self_pdca_result.do_result else False, 'learning_captured': len(self_pdca_result.act_result.lessons_learned) > 0 if self_pdca_result.act_result else False, 'self_consistency_score': self._calculate_self_consistency_score(self_pdca_result), 'credibility_proof': self_pdca_result.cycle_success}
    self.logger.info(f"Self-consistency validation completed - Score: {self_consistency_analysis['self_consistency_score']:.2f}")
    return self_consistency_analysis

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


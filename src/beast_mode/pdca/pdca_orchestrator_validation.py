"""
Pdca Orchestrator Validation

This module was extracted from pdca_orchestrator.py
as part of RM-DDD compliance refactoring.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from ..core.reflective_module import ReflectiveModule

def _check_phase(self, task: PDCATask, do_result: Dict[str, Any]) -> Dict[str, Any]:
    """CHECK: Validate results against success criteria"""
    self.logger.info(f'🔍 CHECK phase: Validating results for {task.name}')
    implementation_result = do_result.get('implementation_result', {})
    validation_results = []
    overall_success = True
    for criterion in task.success_criteria:
        criterion_met = self._validate_success_criterion(criterion, implementation_result)
        validation_results.append({'criterion': criterion, 'met': criterion_met, 'details': f"Criterion {('passed' if criterion_met else 'failed')}: {criterion}"})
        if not criterion_met:
            overall_success = False
    rca_result = {}
    if not overall_success:
        rca_result = self._perform_basic_rca(task, do_result, validation_results)
    check_result = {'task_name': task.name, 'success': overall_success, 'validation_results': validation_results, 'success_rate': len([r for r in validation_results if r['met']]) / len(validation_results), 'rca_result': rca_result, 'validation_timestamp': datetime.now().isoformat()}
    status = 'PASSED' if overall_success else 'FAILED'
    self.logger.info(f"🔍 Validation {status}: {len([r for r in validation_results if r['met']])}/{len(validation_results)} criteria met")
    return check_result

def _validate_success_criterion(self, criterion: str, implementation_result: Dict[str, Any]) -> bool:
    """Validate a single success criterion"""
    if 'file' in criterion.lower() and 'created' in criterion.lower():
        return implementation_result.get('files_created', 0) > 0
    elif 'code' in criterion.lower() and 'implemented' in criterion.lower():
        return implementation_result.get('code_written', False)
    elif 'test' in criterion.lower():
        return implementation_result.get('tests_created', False)
    else:
        return implementation_result.get('success', False)

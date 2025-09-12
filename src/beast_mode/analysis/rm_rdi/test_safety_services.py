"""
Test Safety Services

This module was extracted from test_safety.py
as part of RM-DDD compliance refactoring.
"""

import os
import logging
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from .safety import OperatorSafetyManager, ResourceLimits, SafetyStatus
import inspect

class TestSafetyRuleEngine:
    """Safety rule engine that respects test mode settings"""

    def __init__(self, test_config: TestSafetyConfiguration):
        self.test_config = test_config
        self.logger = logging.getLogger('rm_rdi_analysis.test_safety_rules')

    def evaluate_operation_safety(self, operation: str, context: Dict[str, Any]=None) -> Dict[str, Any]:
        """Evaluate operation safety with detailed reasoning"""
        if context is None:
            context = {}
        is_allowed = self.test_config.is_operation_allowed(operation, context)
        evaluation = {'operation': operation, 'is_allowed': is_allowed, 'test_mode': self.test_config.test_mode, 'timestamp': datetime.now().isoformat(), 'context_provided': bool(context)}
        if is_allowed:
            if operation in self.test_config.allowed_operations:
                evaluation['reason'] = 'Operation explicitly allowed'
            elif self.test_config._is_test_context(context):
                evaluation['reason'] = 'Test context detected'
            else:
                evaluation['reason'] = 'Passed safety validation'
        elif operation in self.test_config.restricted_operations:
            evaluation['reason'] = 'Operation is restricted'
        elif not self.test_config.test_mode:
            evaluation['reason'] = 'Production mode - strict validation'
        else:
            evaluation['reason'] = 'Failed safety validation'
        return evaluation

    def get_allowed_operations(self) -> List[str]:
        """Get list of currently allowed operations"""
        return sorted(list(self.test_config.allowed_operations))

    def get_restricted_operations(self) -> List[str]:
        """Get list of restricted operations"""
        return sorted(list(self.test_config.restricted_operations))

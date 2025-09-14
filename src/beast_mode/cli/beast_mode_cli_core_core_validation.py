"""
Beast Mode Cli Core Core Validation

This module was extracted from beast_mode_cli_core_core.py
as part of RM-DDD compliance refactoring.
"""

import argparse
import json
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..integration.infrastructure_integration_manager import InfrastructureIntegrationManager
from ..integration.self_consistency_validator import SelfConsistencyValidator
from ..orchestration.tool_orchestration_engine import ToolOrchestrationEngine
from src.rm_ddd.core.health import ModuleHealth


def _execute_validate_command(self, args: List[str]) -> CLIResult:
    """Execute validation command"""
    try:
        validation_type = args[0] if args else 'all'
        if validation_type == 'infrastructure':
            result = self.integration_manager.validate_complete_integration()
            output = f"Infrastructure Validation: {result['overall_status']}\nHealth Score: {result['overall_health_score']:.2f}"
        elif validation_type == 'consistency':
            result = self.consistency_validator.validate_complete_self_consistency()
            output = f"Self-Consistency Validation: {('PASSED' if result.credibility_established else 'FAILED')}\nScore: {result.overall_consistency_score:.2f}"
        else:
            infra_result = self.integration_manager.validate_complete_integration()
            consistency_result = self.consistency_validator.validate_complete_self_consistency()
            output_lines = ['🦁 Beast Mode Framework - Complete Validation', '=' * 50, '', f"🔗 Infrastructure: {infra_result['overall_status']} ({infra_result['overall_health_score']:.2f})", f"🎯 Self-Consistency: {('PASSED' if consistency_result.credibility_established else 'FAILED')} ({consistency_result.overall_consistency_score:.2f})", '', f"✅ UC-25 Validation: {('SATISFIED' if consistency_result.credibility_established else 'NOT SATISFIED')}", f"🏆 Credibility: {('ESTABLISHED' if consistency_result.credibility_established else 'NOT ESTABLISHED')}"]
            output = '\n'.join(output_lines)
            result = {'infrastructure': infra_result, 'consistency': consistency_result}
        return CLIResult(command='validate', success=True, output=output, data=result)
    except Exception as e:
        return CLIResult(command='validate', success=False, output=f'Validation failed: {str(e)}')

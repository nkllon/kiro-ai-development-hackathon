"""
Automated Quality Gates Core Core Validation

This module was extracted from automated_quality_gates_core_core.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def _check_beast_mode_compliance(self, gate_results: List[QualityGateResult]) -> Dict[str, bool]:
    """Check compliance with Beast Mode specific requirements"""
    compliance_status = {}
    coverage_result = next((r for r in gate_results if r.gate_type == QualityGateType.COVERAGE), None)
    compliance_status['dr8_coverage_compliance'] = coverage_result is not None and coverage_result.score >= 0.9 and (coverage_result.status == QualityGateStatus.PASSED)
    security_result = next((r for r in gate_results if r.gate_type == QualityGateType.SECURITY), None)
    compliance_status['security_compliance'] = security_result is not None and security_result.status == QualityGateStatus.PASSED
    linting_result = next((r for r in gate_results if r.gate_type == QualityGateType.LINTING), None)
    formatting_result = next((r for r in gate_results if r.gate_type == QualityGateType.FORMATTING), None)
    compliance_status['code_quality_compliance'] = linting_result is not None and linting_result.status == QualityGateStatus.PASSED and (formatting_result is not None) and (formatting_result.status == QualityGateStatus.PASSED)
    doc_result = next((r for r in gate_results if r.gate_type == QualityGateType.DOCUMENTATION), None)
    compliance_status['documentation_compliance'] = doc_result is not None and doc_result.score >= 0.8 and (doc_result.status == QualityGateStatus.PASSED)
    compliance_status['overall_beast_mode_compliance'] = all(compliance_status.values())
    return compliance_status

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


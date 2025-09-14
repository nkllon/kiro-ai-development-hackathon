"""
Rdi Chain Orchestrator Processing

This module was extracted from rdi_chain_orchestrator.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import subprocess
import json
from ..autonomous.pdca_langgraph_orchestrator import PDCALangGraphOrchestrator
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def _convert_pdca_to_rdi_result(self, pdca_result: Dict[str, Any], chain_id: str) -> RDIValidationResult:
    """Convert PDCA execution result to RDI validation result"""
    issues = []
    if 'check_result' in pdca_result and pdca_result['check_result']:
        check_data = pdca_result['check_result']
        if 'validation_issues' in check_data:
            for issue_data in check_data['validation_issues']:
                issues.append(RDIChainIssue(chain_id=chain_id, issue_type=issue_data.get('type', 'unknown'), description=issue_data.get('description', ''), affected_files=issue_data.get('files', []), severity=issue_data.get('severity', 'medium'), mathematical_proof=issue_data.get('proof', '')))
    consistency = self._calculate_mathematical_consistency(pdca_result)
    recommendations = []
    if 'act_result' in pdca_result and pdca_result['act_result']:
        act_data = pdca_result['act_result']
        recommendations = act_data.get('recommendations', [])
    return RDIValidationResult(chain_id=chain_id, is_valid=len(issues) == 0, issues=issues, mathematical_consistency=consistency, recommendations=recommendations)

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


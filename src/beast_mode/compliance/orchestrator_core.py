import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..core.reflective_module import ReflectiveModule
from .interfaces import ComplianceValidator, ComplianceAnalyzer, ValidationContext
from .models import ComplianceAnalysisResult, Phase2ValidationResult, ComplianceIssue, ComplianceIssueType, IssueSeverity, CommitInfo, RDIComplianceStatus, RMComplianceStatus, TestCoverageStatus, TaskReconciliationStatus
from .rm.rm_validator import RMValidator
from .orchestrator_core_validation import *
from .orchestrator_core_core import *
from src.rm_ddd.core.health import ModuleHealth


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


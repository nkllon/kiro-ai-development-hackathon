from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json
from ..interfaces import ComplianceReporter
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType, RemediationStep, Phase2ValidationResult
from .report_generator_core_validation import *
from .report_generator_core_utils import *
from .report_generator_core_core import *
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


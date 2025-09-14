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
from ..core.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.model_driven_intelligence_engine import ModelDrivenIntelligenceEngine
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..quality.automated_quality_gates import AutomatedQualityGates
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..services.gke_service_interface import GKEServiceInterface
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from ..assessment.evidence_package_generator import EvidencePackageGenerator
from ..core.reflective_module import ReflectiveModule
from ..core.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.model_driven_intelligence_engine import ModelDrivenIntelligenceEngine
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..quality.automated_quality_gates import AutomatedQualityGates
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..services.gke_service_interface import GKEServiceInterface
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from ..assessment.evidence_package_generator import EvidencePackageGenerator
from ..core.reflective_module import ReflectiveModule
from ..core.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.model_driven_intelligence_engine import ModelDrivenIntelligenceEngine
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..quality.automated_quality_gates import AutomatedQualityGates
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..services.gke_service_interface import GKEServiceInterface
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from ..assessment.evidence_package_generator import EvidencePackageGenerator
from ..core.reflective_module import ReflectiveModule
from .self_consistency_validator_validation_validation_validation import *
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


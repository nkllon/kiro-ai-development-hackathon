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
from .self_consistency_validator_core_core_validation import *
from .self_consistency_validator_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth


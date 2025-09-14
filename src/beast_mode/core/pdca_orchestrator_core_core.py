import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from .reflective_module import ReflectiveModule, HealthStatus
from ..intelligence.registry_intelligence_engine import ProjectRegistryIntelligenceEngine, IntelligenceQuery
from ..tool_health.makefile_health_manager import MakefileHealthManager
from .pdca_orchestrator_core_core_validation import *
from .pdca_orchestrator_core_core_utils import *
from .pdca_orchestrator_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth


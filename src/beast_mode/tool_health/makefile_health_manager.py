import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from .makefile_health_manager_services import *
from .makefile_health_manager_validation import *
from .makefile_health_manager_core import *
from src.rm_ddd.core.health import ModuleHealth


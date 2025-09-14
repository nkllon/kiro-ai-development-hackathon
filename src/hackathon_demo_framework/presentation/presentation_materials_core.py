import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from ..models import DemoScript, HackathonConfig, SystematicEvidence, TechnicalAssessment
from .presentation_materials_core_core import *
from src.rm_ddd.core.health import ModuleHealth


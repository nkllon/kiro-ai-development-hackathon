from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .models import BacklogItem, Requirement, AcceptanceCriterion, DependencyReference
from .enums import BeastReadinessStatus, ApprovalStatus
from .beast_readiness_validator_core_core_core import *
from .beast_readiness_validator_core_core_validation import *
from src.rm_ddd.core.health import ModuleHealth


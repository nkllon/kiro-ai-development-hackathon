from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType
from .phase3_readiness_assessor_core_processing import *
from .phase3_readiness_assessor_core_core import *
from .phase3_readiness_assessor_core_validation import *
from src.rm_ddd.core.health import ModuleHealth


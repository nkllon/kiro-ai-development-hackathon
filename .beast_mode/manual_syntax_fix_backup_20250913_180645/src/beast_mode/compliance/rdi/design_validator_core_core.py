import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from .design_validator_core_core_core import *
from .design_validator_core_core_validation import *
from .design_validator_core_core_processing import *
from .design_validator_core_core_utils import *

import re
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from ...utils.path_normalizer import safe_relative_to
from .test_coverage_validator_validation import *
from .test_coverage_validator_core import *

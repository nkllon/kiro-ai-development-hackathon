import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from .requirement_tracer_validation import *
from .requirement_tracer_core import *
from .requirement_tracer_processing import *

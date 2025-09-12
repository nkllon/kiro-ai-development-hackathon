import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ...core.reflective_module import ReflectiveModule
from ..interfaces import ComplianceAnalyzer, ValidationContext
from ..models import ComplianceAnalysisResult, CommitInfo, FileChangeAnalysis, ComplianceIssue, ComplianceIssueType, IssueSeverity
import fnmatch
from .analyzer_core import *

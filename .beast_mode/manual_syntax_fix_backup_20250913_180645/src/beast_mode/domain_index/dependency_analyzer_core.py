import os
import ast
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import DomainSystemComponent
from .models import Domain, DomainCollection, DependencyGraph, HealthIssue, IssueSeverity, IssueCategory, ValidationResult
from .exceptions import DependencyAnalysisError
from .config import get_config
from ..utils.path_normalizer import PathNormalizer, safe_relative_to, normalize_path
from .dependency_analyzer_core_core import *

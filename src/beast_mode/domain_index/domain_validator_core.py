import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from .base import DomainSystemComponent
from .models import Domain, DomainCollection, ValidationResult, HealthIssue, IssueSeverity, IssueCategory, DependencyGraph
from .exceptions import DomainValidationError
import glob
import jsonschema
import glob
import glob
from .domain_validator_core_validation import *
from .domain_validator_core_core import *
from src.rm_ddd.core.health import ModuleHealth


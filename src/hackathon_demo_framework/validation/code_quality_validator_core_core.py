import logging
import ast
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from ..models import ValidationResult, TechnicalAssessment
from .code_quality_validator_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth


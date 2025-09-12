from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from .models import BacklogItem, MPMValidation, DependencySpec
from .enums import StrategicTrack, BeastReadinessStatus, ApprovalStatus, StakeholderType, RiskLevel
from .dependency_manager import BacklogDependencyManager
from .mpm_dashboard_core_core_validation import *
from .mpm_dashboard_core_core_core import *
from .mpm_dashboard_core_core_utils import *

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
from collections import defaultdict, deque
import logging
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .models import DependencySpec, BacklogItem
from .enums import DependencyType, RiskLevel, StrategicTrack
from .dependency_manager_services_core_core import *
from src.rm_ddd.core.health import ModuleHealth


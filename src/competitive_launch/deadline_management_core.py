import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from .models import MarketConditions, CompetitiveThreat
from .deadline_management_core_core import *
from src.rm_ddd.core.health import ModuleHealth


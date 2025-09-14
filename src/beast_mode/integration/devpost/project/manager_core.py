import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from ..models import DevpostProject, ProjectMetadata, DevpostConfig, ProjectConnection, SyncStatus, ValidationResult
from ..interfaces import ProjectManagerInterface
from ..config import DevpostConfigManager
from ....core.exceptions import ConfigurationError, ValidationError
import tomllib
import tomli as tomllib
import tomllib
import tomli as tomllib
from .manager_core_core import *
from src.rm_ddd.core.health import ModuleHealth

